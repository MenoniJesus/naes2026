from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, UpdateView

from .filters import RequisicaoIAFilter, UsuarioIAFilter
from .forms import ConfiguracaoIAForm, CotaUsuarioIAForm
from .models import ConfiguracaoIA, CotaUsuarioIA, RequisicaoIA
from .permissoes import AdminRequiredMixin, eh_admin
from .services import ErroIA, situacao_do_usuario, testar_conexao


def inicio_do_mes():
    return timezone.localtime().replace(day=1, hour=0, minute=0, second=0, microsecond=0)


# ─────────────────────────────────────────
# REQUISIÇÕES (auditoria)
# ─────────────────────────────────────────

class RequisicaoList(AdminRequiredMixin, ListView):
    model = RequisicaoIA
    template_name = 'ia/requisicao_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        self.filterset = RequisicaoIAFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['tokens_filtrados'] = self.filterset.qs.tokens_consumidos()
        return context


class RequisicaoDetail(AdminRequiredMixin, DetailView):
    model = RequisicaoIA
    template_name = 'ia/requisicao_detail.html'

    def get_queryset(self):
        return super().get_queryset().select_related('user')


# ─────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────

class ConfiguracaoUpdate(AdminRequiredMixin, UpdateView):
    model = ConfiguracaoIA
    form_class = ConfiguracaoIAForm
    template_name = 'ia/configuracao.html'
    success_url = reverse_lazy('ia-configuracao')

    def get_object(self, queryset=None):
        return ConfiguracaoIA.carregar()

    def form_valid(self, form):
        form.instance.atualizado_por = self.request.user
        messages.success(self.request, "Configuração da IA salva com sucesso.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ultimo_teste'] = RequisicaoIA.objects.filter(origem='teste_conexao').first()
        return context


@login_required
@require_POST
def configuracao_testar(request):
    if not eh_admin(request.user):
        raise PermissionDenied

    try:
        resposta = testar_conexao(request.user)
    except ErroIA as erro:
        messages.error(request, f"Falha na conexão: {erro.mensagem}")
    else:
        messages.success(
            request,
            f"Conexão OK com {resposta.requisicao.modelo}: respondeu em {resposta.duracao_ms} ms "
            f"usando {resposta.tokens_total} tokens.",
        )
    return redirect('ia-configuracao')


# ─────────────────────────────────────────
# IA POR USUÁRIO
# ─────────────────────────────────────────

class UsuarioIAList(AdminRequiredMixin, ListView):
    model = User
    template_name = 'ia/usuario_list.html'
    paginate_by = 20

    def get_queryset(self):
        do_mes = Q(requisicoes_ia__criado_em__gte=inicio_do_mes())
        queryset = (
            User.objects
            .select_related('cota_ia')
            .annotate(consumo_mes=Coalesce(
                Sum(F('requisicoes_ia__tokens_entrada') + F('requisicoes_ia__tokens_saida'), filter=do_mes),
                0,
            ))
            .order_by('username')
        )
        self.filterset = UsuarioIAFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        configuracao = ConfiguracaoIA.carregar()
        for usuario in context['object_list']:
            # Sem registro em CotaUsuarioIA o acesso reverso lança AttributeError.
            cota = getattr(usuario, 'cota_ia', None)
            usuario.ia_habilitado = cota.habilitado if cota else True
            usuario.ia_cota = cota.cota_efetiva(configuracao) if cota else configuracao.cota_mensal_padrao
            usuario.ia_cota_propria = bool(cota and cota.cota_mensal is not None)
            usuario.ia_situacao = {
                'consumo': usuario.consumo_mes,
                'cota': usuario.ia_cota,
                'percentual': min(round(usuario.consumo_mes * 100 / usuario.ia_cota), 100) if usuario.ia_cota else 100,
            }
        context['filter'] = self.filterset
        context['configuracao'] = configuracao
        return context


class UsuarioIAUpdate(AdminRequiredMixin, UpdateView):
    model = CotaUsuarioIA
    form_class = CotaUsuarioIAForm
    template_name = 'ia/usuario_form.html'
    success_url = reverse_lazy('ia-usuario-list')

    def get_object(self, queryset=None):
        self.usuario = get_object_or_404(User, pk=self.kwargs['user_pk'])
        cota, _ = CotaUsuarioIA.objects.get_or_create(user=self.usuario)
        return cota

    def form_valid(self, form):
        messages.success(self.request, f"Acesso à IA de “{self.usuario.username}” atualizado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.usuario
        context['situacao'] = situacao_do_usuario(self.usuario)
        return context


# ─────────────────────────────────────────
# MEU CONSUMO
# ─────────────────────────────────────────

class MeuConsumo(LoginRequiredMixin, ListView):
    model = RequisicaoIA
    template_name = 'ia/meu_consumo.html'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['situacao'] = situacao_do_usuario(self.request.user)
        context['por_mes'] = (
            RequisicaoIA.objects
            .filter(user=self.request.user)
            .annotate(mes=TruncMonth('criado_em'))
            .values('mes')
            .annotate(
                tokens=Coalesce(Sum(F('tokens_entrada') + F('tokens_saida')), 0),
                chamadas=Count('id'),
            )
            .order_by('-mes')[:6]
        )
        return context
