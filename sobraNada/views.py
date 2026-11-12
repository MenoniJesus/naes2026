from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from braces.views import GroupRequiredMixin

from .carrinho import Carrinho
from .filters import ProdutoFilter, ReservaFilter, SacolaFilter
from .forms import (
    AvaliacaoForm, EnderecoForm, EstabelecimentoForm, NotificacaoForm, PerfilForm,
    ProdutoForm, ReservaForm, ReservaUpdateForm, SacolaForm, SacolaUpdateForm,
)
from .models import (
    Estado, Cidade, Endereco, Perfil,
    Categoria, Estabelecimento, Produto, Sacola,
    Reserva, Avaliacao, Notificacao
)

AJUDA_SACOLA = (
    "O preço original é calculado automaticamente somando o preço dos produtos "
    "escolhidos, e o estabelecimento da sacola vem desses mesmos produtos."
)

AJUDA_DESCONTO = (
    "Desconto por faixa do total da reserva (preço da sacola x quantidade): "
    "até R$ 100,00 sem desconto · R$ 100,01 a 250,00: 10% · "
    "R$ 250,01 a 500,00: 20% · R$ 500,01 a 1.000,00: 25% · acima de R$ 1.000,00: 30%."
)

AJUDA_DESCONTO_CARRINHO = (
    "Desconto por faixa do total do carrinho: "
    "até R$ 149,99 sem desconto · R$ 150,00 a 249,99: 20% · "
    "R$ 250,00 a 499,99: 25% · a partir de R$ 500,00: 35%."
)


class BaseLoginMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login')


class DonoMixin:
    """Restringe o queryset da view aos registros do usuário logado."""
    campo_dono = 'user'

    def get_queryset(self):
        # distinct() porque o dono pode vir por uma relação M2M (ex.: sacola -> produtos).
        return super().get_queryset().filter(**{self.campo_dono: self.request.user}).distinct()


class MensagemMixin:
    """Mensagem de sucesso em cadastro, alteração e exclusão.

    Exclusões barradas por on_delete=PROTECT viram mensagem de erro em vez de erro 500.
    """

    def form_valid(self, form):
        existente = self.object is not None
        nome = str(self.object) if existente else ''
        try:
            resposta = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f'Não foi possível excluir "{nome}": existem outros registros vinculados a ele.'
            )
            return redirect(self.get_success_url())

        verbose = self.model._meta.verbose_name
        if isinstance(self, DeleteView):
            texto = f'Registro de {verbose} "{nome}" excluído com sucesso.'
        elif existente:
            texto = f'Alterações em {verbose} "{self.object}" salvas com sucesso.'
        else:
            texto = f'Registro de {verbose} "{self.object}" cadastrado com sucesso.'
        messages.success(self.request, texto)
        return resposta


class EstabelecimentoObrigatorioMixin:
    """Produtos e sacolas só podem ser cadastrados por quem já tem um estabelecimento."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not hasattr(request.user, 'estabelecimento'):
            messages.warning(request, "Cadastre o seu estabelecimento antes de continuar.")
            return redirect('estabelecimento-create')
        return super().dispatch(request, *args, **kwargs)


class UsuarioFormKwargsMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs


class RegistroUnicoMixin:
    """Impede um segundo cadastro quando o usuário já possui o registro."""
    relacao_existente = None
    rota_existente = None
    aviso_existente = ''

    def dispatch(self, request, *args, **kwargs):
        existente = getattr(request.user, self.relacao_existente, None)
        if existente is not None:
            messages.info(request, self.aviso_existente)
            return redirect(self.rota_existente, pk=existente.pk)
        return super().dispatch(request, *args, **kwargs)


# ─────────────────────────────────────────
# ESTADO
# ─────────────────────────────────────────

class EstadoCreate(MensagemMixin, GroupRequiredMixin, CreateView):
    group_required = ['admin']
    model = Estado
    fields = ['name', 'uf']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estado-list')
    extra_context = {
        'titulo': 'Cadastro de Estado',
        'botao': 'Criar Estado'
    }

class EstadoUpdate(MensagemMixin, GroupRequiredMixin, UpdateView):
    group_required = ['admin']
    model = Estado
    fields = ['name', 'uf']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estado-list')
    extra_context = {
        'titulo': 'Editar Estado',
        'botao': 'Atualizar Estado'
    }

class EstadoDelete(MensagemMixin, GroupRequiredMixin, DeleteView):
    group_required = ['admin']
    model = Estado
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estado-list')
    extra_context = {
        'titulo': 'Excluir Estado',
        'botao': 'Sim, excluir!'
    }

class EstadoList(BaseLoginMixin, ListView):
    model = Estado
    template_name = 'sobraNada/list/estado.html'
    paginate_by = 30

class EstadoDetail(BaseLoginMixin, DetailView):
    model = Estado
    template_name = 'sobraNada/detail/estado.html'


# ─────────────────────────────────────────
# CIDADE
# ─────────────────────────────────────────

class CidadeCreate(MensagemMixin, BaseLoginMixin, CreateView):
    model = Cidade
    fields = ['estado', 'name']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('cidade-list')
    extra_context = {
        'titulo': 'Cadastro de Cidade',
        'botao': 'Criar Cidade'
    }

class CidadeUpdate(MensagemMixin, BaseLoginMixin, UpdateView):
    model = Cidade
    fields = ['estado', 'name']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('cidade-list')
    extra_context = {
        'titulo': 'Editar Cidade',
        'botao': 'Atualizar Cidade'
    }

class CidadeDelete(MensagemMixin, BaseLoginMixin, DeleteView):
    model = Cidade
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('cidade-list')
    extra_context = {
        'titulo': 'Excluir Cidade',
        'botao': 'Sim, excluir!'
    }

class CidadeList(BaseLoginMixin, ListView):
    model = Cidade
    template_name = 'sobraNada/list/cidade.html'
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().select_related('estado')

class CidadeDetail(BaseLoginMixin, DetailView):
    model = Cidade
    template_name = 'sobraNada/detail/cidade.html'

    def get_queryset(self):
        return super().get_queryset().select_related('estado')


# ─────────────────────────────────────────
# ENDEREÇO
# ─────────────────────────────────────────

class EnderecoCreate(MensagemMixin, BaseLoginMixin, CreateView):
    model = Endereco
    form_class = EnderecoForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('endereco-list')
    extra_context = {
        'titulo': 'Cadastro de Endereço',
        'botao': 'Criar Endereço'
    }

class EnderecoUpdate(MensagemMixin, BaseLoginMixin, UpdateView):
    model = Endereco
    form_class = EnderecoForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('endereco-list')
    extra_context = {
        'titulo': 'Editar Endereço',
        'botao': 'Atualizar Endereço'
    }

class EnderecoDelete(MensagemMixin, BaseLoginMixin, DeleteView):
    model = Endereco
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('endereco-list')
    extra_context = {
        'titulo': 'Excluir Endereço',
        'botao': 'Sim, excluir!'
    }

class EnderecoList(BaseLoginMixin, ListView):
    model = Endereco
    template_name = 'sobraNada/list/endereco.html'
    paginate_by = 30

    def get_queryset(self):
        # Cidade.__str__ usa o estado: sem cidade__estado seria uma query por linha.
        return super().get_queryset().select_related('cidade__estado')

class EnderecoDetail(BaseLoginMixin, DetailView):
    model = Endereco
    template_name = 'sobraNada/detail/endereco.html'

    def get_queryset(self):
        return super().get_queryset().select_related('cidade__estado')


# ─────────────────────────────────────────
# PERFIL
# ─────────────────────────────────────────

class PerfilCreate(MensagemMixin, BaseLoginMixin, RegistroUnicoMixin, CreateView):
    model = Perfil
    form_class = PerfilForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('perfil-list')
    relacao_existente = 'perfil'
    rota_existente = 'perfil-update'
    aviso_existente = "Você já possui um perfil. Edite os dados por aqui."
    extra_context = {
        'titulo': 'Cadastro de Perfil',
        'botao': 'Criar Perfil'
    }

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PerfilUpdate(MensagemMixin, BaseLoginMixin, DonoMixin, UpdateView):
    model = Perfil
    form_class = PerfilForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('perfil-list')
    extra_context = {
        'titulo': 'Editar Perfil',
        'botao': 'Atualizar Perfil'
    }

class PerfilDelete(MensagemMixin, BaseLoginMixin, DonoMixin, DeleteView):
    model = Perfil
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('perfil-list')
    extra_context = {
        'titulo': 'Excluir Perfil',
        'botao': 'Sim, excluir!'
    }

class PerfilList(BaseLoginMixin, DonoMixin, ListView):
    model = Perfil
    template_name = 'sobraNada/list/perfil.html'
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().select_related('user')

class PerfilDetail(BaseLoginMixin, DonoMixin, DetailView):
    model = Perfil
    template_name = 'sobraNada/detail/perfil.html'

    def get_queryset(self):
        return super().get_queryset().select_related('user', 'endereco')


# ─────────────────────────────────────────
# CATEGORIA
# ─────────────────────────────────────────

class CategoriaCreate(MensagemMixin, GroupRequiredMixin, CreateView):
    group_required = ['admin']
    model = Categoria
    fields = ['name', 'description']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Cadastro de Categoria',
        'botao': 'Criar Categoria'
    }

class CategoriaUpdate(MensagemMixin, GroupRequiredMixin, UpdateView):
    group_required = ['admin']
    model = Categoria
    fields = ['name', 'description']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Editar Categoria',
        'botao': 'Atualizar Categoria'
    }

class CategoriaDelete(MensagemMixin, GroupRequiredMixin, DeleteView):
    group_required = ['admin']
    model = Categoria
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Excluir Categoria',
        'botao': 'Sim, excluir!'
    }

class CategoriaList(BaseLoginMixin, ListView):
    model = Categoria
    template_name = 'sobraNada/list/categoria.html'
    paginate_by = 30

class CategoriaDetail(BaseLoginMixin, DetailView):
    model = Categoria
    template_name = 'sobraNada/detail/categoria.html'


# ─────────────────────────────────────────
# ESTABELECIMENTO
# ─────────────────────────────────────────

class EstabelecimentoCreate(MensagemMixin, BaseLoginMixin, RegistroUnicoMixin, CreateView):
    model = Estabelecimento
    form_class = EstabelecimentoForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estabelecimento-list')
    relacao_existente = 'estabelecimento'
    rota_existente = 'estabelecimento-update'
    aviso_existente = "Cada usuário pode ter apenas um estabelecimento."
    extra_context = {
        'titulo': 'Cadastro de Estabelecimento',
        'botao': 'Criar Estabelecimento'
    }

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class EstabelecimentoUpdate(MensagemMixin, BaseLoginMixin, DonoMixin, UpdateView):
    model = Estabelecimento
    form_class = EstabelecimentoForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estabelecimento-list')
    extra_context = {
        'titulo': 'Editar Estabelecimento',
        'botao': 'Atualizar Estabelecimento'
    }

class EstabelecimentoDelete(MensagemMixin, BaseLoginMixin, DonoMixin, DeleteView):
    model = Estabelecimento
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estabelecimento-list')
    extra_context = {
        'titulo': 'Excluir Estabelecimento',
        'botao': 'Sim, excluir!'
    }

class EstabelecimentoList(BaseLoginMixin, ListView):
    model = Estabelecimento
    template_name = 'sobraNada/list/estabelecimento.html'
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().select_related('categoria')

class EstabelecimentoDetail(BaseLoginMixin, DetailView):
    model = Estabelecimento
    template_name = 'sobraNada/detail/estabelecimento.html'

    def get_queryset(self):
        return super().get_queryset().select_related('categoria', 'endereco')


# ─────────────────────────────────────────
# PRODUTO
# ─────────────────────────────────────────

class ProdutoCreate(MensagemMixin, BaseLoginMixin, EstabelecimentoObrigatorioMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('produto-list')
    extra_context = {
        'titulo': 'Cadastro de Produto',
        'botao': 'Criar Produto'
    }

    def form_valid(self, form):
        form.instance.estabelecimento = self.request.user.estabelecimento
        return super().form_valid(form)

class ProdutoUpdate(MensagemMixin, BaseLoginMixin, DonoMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    campo_dono = 'estabelecimento__user'
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('produto-list')
    extra_context = {
        'titulo': 'Editar Produto',
        'botao': 'Atualizar Produto'
    }

class ProdutoDelete(MensagemMixin, BaseLoginMixin, DonoMixin, DeleteView):
    model = Produto
    campo_dono = 'estabelecimento__user'
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('produto-list')
    extra_context = {
        'titulo': 'Excluir Produto',
        'botao': 'Sim, excluir!'
    }

class ProdutoList(BaseLoginMixin, ListView):
    model = Produto
    template_name = 'sobraNada/list/produto.html'
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset().select_related('estabelecimento')
        self.filterset = ProdutoFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class ProdutoDetail(BaseLoginMixin, DetailView):
    model = Produto
    template_name = 'sobraNada/detail/produto.html'

    def get_queryset(self):
        return super().get_queryset().select_related('estabelecimento')


# ─────────────────────────────────────────
# SACOLA
# ─────────────────────────────────────────

class SacolaCreate(MensagemMixin, BaseLoginMixin, EstabelecimentoObrigatorioMixin, UsuarioFormKwargsMixin, CreateView):
    model = Sacola
    form_class = SacolaForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('sacola-list')
    extra_context = {
        'titulo': 'Cadastro de Sacola',
        'botao': 'Criar Sacola',
        'ajuda': AJUDA_SACOLA,
    }


class SacolaUpdate(MensagemMixin, BaseLoginMixin, DonoMixin, UsuarioFormKwargsMixin, UpdateView):
    model = Sacola
    form_class = SacolaUpdateForm
    campo_dono = 'produtos__estabelecimento__user'
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('sacola-list')
    extra_context = {
        'titulo': 'Editar Sacola',
        'botao': 'Atualizar Sacola',
        'ajuda': AJUDA_SACOLA,
    }

    def form_valid(self, form):
        # Mexer no total repassa a diferença para o estoque ainda não reservado.
        delta = form.cleaned_data['total_quantity'] - form.initial['total_quantity']
        form.instance.available_quantity = max(form.instance.available_quantity + delta, 0)
        return super().form_valid(form)


class SacolaDelete(MensagemMixin, BaseLoginMixin, DonoMixin, DeleteView):
    model = Sacola
    campo_dono = 'produtos__estabelecimento__user'
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('sacola-list')
    extra_context = {
        'titulo': 'Excluir Sacola',
        'botao': 'Sim, excluir!'
    }

class SacolaList(BaseLoginMixin, ListView):
    model = Sacola
    template_name = 'sobraNada/list/sacola.html'
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('produtos__estabelecimento')
        self.filterset = SacolaFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class SacolaDetail(BaseLoginMixin, DetailView):
    model = Sacola
    template_name = 'sobraNada/detail/sacola.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('produtos__estabelecimento')


# ─────────────────────────────────────────
# RESERVA
# ─────────────────────────────────────────

class ReservaCreate(BaseLoginMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Nova Reserva',
        'botao': 'Reservar',
        'ajuda': AJUDA_DESCONTO,
    }

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.aplicar_desconto(form.desconto)

        with transaction.atomic():
            sacola = Sacola.objects.select_for_update().get(pk=form.instance.sacola_id)
            try:
                sacola.reservar(form.instance.quantity)
            except ValueError as erro:
                transaction.set_rollback(True)
                form.add_error('quantity', str(erro))
                return self.form_invalid(form)

            resposta = super().form_valid(form)

            Notificacao.objects.create(
                user=self.request.user,
                title="Reserva registrada",
                message=(
                    f"Sua reserva de {self.object.quantity}x \"{sacola.title}\" "
                    f"saiu por R$ {self.object.total_price}. "
                    f"Código de retirada: {self.object.pickup_code}."
                ),
                type="reserva",
            )

        messages.success(
            self.request,
            f"Reserva feita! Código de retirada: {self.object.pickup_code}"
        )
        return resposta


class ReservaUpdate(BaseLoginMixin, DonoMixin, UpdateView):
    model = Reserva
    form_class = ReservaUpdateForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Alterar Quantidade da Reserva',
        'botao': 'Atualizar Reserva',
        'ajuda': AJUDA_DESCONTO,
    }

    def get_object(self, queryset=None):
        reserva = super().get_object(queryset)
        # O form já terá substituído a quantidade pela nova quando form_valid rodar.
        self.quantidade_original = reserva.quantity
        return reserva

    def form_valid(self, form):
        with transaction.atomic():
            sacola = Sacola.objects.select_for_update().get(pk=self.object.sacola_id)
            sacola.devolver(self.quantidade_original)
            try:
                sacola.reservar(form.cleaned_data['quantity'])
            except ValueError as erro:
                transaction.set_rollback(True)
                form.add_error('quantity', str(erro))
                return self.form_invalid(form)

            form.instance.aplicar_desconto(form.desconto)
            resposta = super().form_valid(form)

        messages.success(
            self.request,
            f"Reserva #{self.object.pk} alterada para {self.object.quantity} unidade(s): "
            f"R$ {self.object.total_price}."
        )
        return resposta


class ReservaCancelar(BaseLoginMixin, DonoMixin, UpdateView):
    model = Reserva
    fields = []
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Cancelar Reserva',
        'botao': 'Sim, cancelar reserva!',
        'perigo': True,
        'confirmacao': 'Deseja realmente cancelar',
    }

    def form_valid(self, form):
        try:
            self.object.cancelar()
        except ValueError as erro:
            messages.error(self.request, str(erro))
        else:
            messages.success(self.request, "Reserva cancelada e estoque devolvido.")
        return redirect(self.success_url)


class ReservaDelete(BaseLoginMixin, DonoMixin, DeleteView):
    model = Reserva
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Excluir Reserva',
        'botao': 'Sim, excluir!'
    }

    def form_valid(self, form):
        numero = self.object.pk
        try:
            with transaction.atomic():
                if self.object.esta_ativa:
                    self.object.sacola.devolver(self.object.quantity)
                resposta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "Esta reserva já foi avaliada e não pode ser excluída.")
            return redirect(self.success_url)

        messages.success(self.request, f"Reserva #{numero} excluída com sucesso.")
        return resposta


class ReservaList(BaseLoginMixin, ListView):
    model = Reserva
    template_name = 'sobraNada/list/reserva.html'
    paginate_by = 30

    def get_queryset(self):
        usuario = self.request.user
        queryset = (
            super().get_queryset()
            .filter(Q(user=usuario) | Q(sacola__produtos__estabelecimento__user=usuario))
            .select_related('user', 'sacola')
            # Sacola.__str__ usa o estabelecimento dos produtos.
            .prefetch_related('sacola__produtos__estabelecimento')
            .distinct()
        )
        self.filterset = ReservaFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

class ReservaDetail(BaseLoginMixin, DetailView):
    model = Reserva
    template_name = 'sobraNada/detail/reserva.html'

    def get_queryset(self):
        usuario = self.request.user
        return super().get_queryset().filter(
            Q(user=usuario) | Q(sacola__produtos__estabelecimento__user=usuario)
        ).select_related('user', 'sacola').prefetch_related('sacola__produtos__estabelecimento').distinct()


# ─────────────────────────────────────────
# AVALIAÇÃO
# ─────────────────────────────────────────

class AvaliacaoCreate(MensagemMixin, BaseLoginMixin, UsuarioFormKwargsMixin, CreateView):
    model = Avaliacao
    form_class = AvaliacaoForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('avaliacao-list')
    extra_context = {
        'titulo': 'Cadastro de Avaliação',
        'botao': 'Criar Avaliação'
    }

class AvaliacaoUpdate(MensagemMixin, BaseLoginMixin, DonoMixin, UsuarioFormKwargsMixin, UpdateView):
    model = Avaliacao
    form_class = AvaliacaoForm
    campo_dono = 'reserva__user'
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('avaliacao-list')
    extra_context = {
        'titulo': 'Editar Avaliação',
        'botao': 'Atualizar Avaliação'
    }

class AvaliacaoDelete(MensagemMixin, BaseLoginMixin, DonoMixin, DeleteView):
    model = Avaliacao
    campo_dono = 'reserva__user'
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('avaliacao-list')
    extra_context = {
        'titulo': 'Excluir Avaliação',
        'botao': 'Sim, excluir!'
    }

class AvaliacaoList(BaseLoginMixin, ListView):
    model = Avaliacao
    template_name = 'sobraNada/list/avaliacao.html'
    paginate_by = 30

    def get_queryset(self):
        # Reserva.__str__ usa o username.
        return super().get_queryset().select_related('reserva__user')

class AvaliacaoDetail(BaseLoginMixin, DetailView):
    model = Avaliacao
    template_name = 'sobraNada/detail/avaliacao.html'

    def get_queryset(self):
        return super().get_queryset().select_related('reserva__user')


# ─────────────────────────────────────────
# NOTIFICAÇÃO
# ─────────────────────────────────────────

class NotificacaoCreate(MensagemMixin, BaseLoginMixin, CreateView):
    model = Notificacao
    form_class = NotificacaoForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('notificacao-list')
    extra_context = {
        'titulo': 'Cadastro de Notificação',
        'botao': 'Criar Notificação'
    }

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NotificacaoUpdate(MensagemMixin, BaseLoginMixin, DonoMixin, UpdateView):
    model = Notificacao
    form_class = NotificacaoForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('notificacao-list')
    extra_context = {
        'titulo': 'Editar Notificação',
        'botao': 'Atualizar Notificação'
    }

class NotificacaoDelete(MensagemMixin, BaseLoginMixin, DonoMixin, DeleteView):
    model = Notificacao
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('notificacao-list')
    extra_context = {
        'titulo': 'Excluir Notificação',
        'botao': 'Sim, excluir!'
    }

class NotificacaoList(BaseLoginMixin, DonoMixin, ListView):
    model = Notificacao
    template_name = 'sobraNada/list/notificacao.html'
    paginate_by = 30

    def get_queryset(self):
        return super().get_queryset().select_related('user')

class NotificacaoDetail(BaseLoginMixin, DonoMixin, DetailView):
    model = Notificacao
    template_name = 'sobraNada/detail/notificacao.html'


# ─────────────────────────────────────────
# CARRINHO
# ─────────────────────────────────────────

@login_required
def carrinho_detail(request):
    itens, desconto = Carrinho(request).calcular()
    return render(request, 'sobraNada/carrinho.html', {
        'itens': itens,
        'desconto': desconto,
        'ajuda': AJUDA_DESCONTO_CARRINHO,
    })


@login_required
@require_POST
def carrinho_adicionar(request, pk):
    produto = get_object_or_404(Produto, pk=pk, is_active=True)
    try:
        quantidade = int(request.POST.get('quantidade', 1))
    except ValueError:
        quantidade = 1
    quantidade = max(quantidade, 1)

    Carrinho(request).adicionar(produto, quantidade)
    messages.success(request, f'"{produto.name}" adicionado ao carrinho.')
    return redirect('carrinho-detail')


@login_required
@require_POST
def carrinho_atualizar(request, pk):
    try:
        quantidade = int(request.POST.get('quantidade', 1))
    except ValueError:
        quantidade = 1

    Carrinho(request).atualizar(pk, quantidade)
    return redirect('carrinho-detail')


@login_required
@require_POST
def carrinho_remover(request, pk):
    Carrinho(request).remover(pk)
    return redirect('carrinho-detail')


@login_required
@require_POST
def carrinho_limpar(request):
    Carrinho(request).limpar()
    return redirect('carrinho-detail')
