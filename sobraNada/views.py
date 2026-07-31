from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from .models import (
    Estado, Cidade, Endereco, Perfil,
    Categoria, Estabelecimento, Sacola,
    Reserva, Avaliacao, Notificacao
)

from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin

class BaseLoginMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login')

# ─────────────────────────────────────────
# ESTADO
# ─────────────────────────────────────────

class EstadoCreate(GroupRequiredMixin, CreateView):
    group_required = ['admin']
    model = Estado
    fields = ['name', 'uf']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estado-list')
    extra_context = {
        'titulo': 'Cadastro de Estado',
        'botao': 'Criar Estado'
    }

class EstadoUpdate(BaseLoginMixin, UpdateView):
    model = Estado
    fields = ['name', 'uf']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estado-list')
    extra_context = {
        'titulo': 'Editar Estado',
        'botao': 'Atualizar Estado'
    }

class EstadoDelete(BaseLoginMixin, DeleteView):
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

class EstadoDetail(BaseLoginMixin, DetailView):
    model = Estado
    template_name = 'sobraNada/detail/estado.html'


# ─────────────────────────────────────────
# CIDADE
# ─────────────────────────────────────────

class CidadeCreate(BaseLoginMixin, CreateView):
    model = Cidade
    fields = ['estado', 'name']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('cidade-list')
    extra_context = {
        'titulo': 'Cadastro de Cidade',
        'botao': 'Criar Cidade'
    }

class CidadeUpdate(BaseLoginMixin, UpdateView):
    model = Cidade
    fields = ['estado', 'name']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('cidade-list')
    extra_context = {
        'titulo': 'Editar Cidade',
        'botao': 'Atualizar Cidade'
    }

class CidadeDelete(BaseLoginMixin, DeleteView):
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

class CidadeDetail(BaseLoginMixin, DetailView):
    model = Cidade
    template_name = 'sobraNada/detail/cidade.html'


# ─────────────────────────────────────────
# ENDEREÇO
# ─────────────────────────────────────────

class EnderecoCreate(BaseLoginMixin, CreateView):
    model = Endereco
    fields = ['cidade', 'street', 'number', 'complement', 'neighborhood', 'zip_code']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('endereco-list')
    extra_context = {
        'titulo': 'Cadastro de Endereço',
        'botao': 'Criar Endereço'
    }

class EnderecoUpdate(BaseLoginMixin, UpdateView):
    model = Endereco
    fields = ['cidade', 'street', 'number', 'complement', 'neighborhood', 'zip_code']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('endereco-list')
    extra_context = {
        'titulo': 'Editar Endereço',
        'botao': 'Atualizar Endereço'
    }

class EnderecoDelete(BaseLoginMixin, DeleteView):
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

class EnderecoDetail(BaseLoginMixin, DetailView):
    model = Endereco
    template_name = 'sobraNada/detail/endereco.html'


# ─────────────────────────────────────────
# PERFIL
# ─────────────────────────────────────────

class PerfilCreate(BaseLoginMixin, CreateView):
    model = Perfil
    fields = ['user', 'phone', 'endereco']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('perfil-list')
    extra_context = {
        'titulo': 'Cadastro de Perfil',
        'botao': 'Criar Perfil'
    }

class PerfilUpdate(BaseLoginMixin, UpdateView):
    model = Perfil
    fields = ['user', 'phone', 'endereco']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('perfil-list')
    extra_context = {
        'titulo': 'Editar Perfil',
        'botao': 'Atualizar Perfil'
    }

class PerfilDelete(BaseLoginMixin, DeleteView):
    model = Perfil
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('perfil-list')
    extra_context = {
        'titulo': 'Excluir Perfil',
        'botao': 'Sim, excluir!'
    }

class PerfilList(BaseLoginMixin, ListView):
    model = Perfil
    template_name = 'sobraNada/list/perfil.html'

class PerfilDetail(BaseLoginMixin, DetailView):
    model = Perfil
    template_name = 'sobraNada/detail/perfil.html'


# ─────────────────────────────────────────
# CATEGORIA
# ─────────────────────────────────────────

class CategoriaCreate(BaseLoginMixin, CreateView):
    model = Categoria
    fields = ['name', 'description']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Cadastro de Categoria',
        'botao': 'Criar Categoria'
    }

class CategoriaUpdate(BaseLoginMixin, UpdateView):
    model = Categoria
    fields = ['name', 'description']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Editar Categoria',
        'botao': 'Atualizar Categoria'
    }

class CategoriaDelete(BaseLoginMixin, DeleteView):
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

class CategoriaDetail(BaseLoginMixin, DetailView):
    model = Categoria
    template_name = 'sobraNada/detail/categoria.html'


# ─────────────────────────────────────────
# ESTABELECIMENTO
# ─────────────────────────────────────────

class EstabelecimentoCreate(BaseLoginMixin, CreateView):
    model = Estabelecimento
    fields = ['user', 'endereco', 'categoria', 'name', 'description', 'photo', 'pickup_start', 'pickup_end', 'is_active']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estabelecimento-list')
    extra_context = {
        'titulo': 'Cadastro de Estabelecimento',
        'botao': 'Criar Estabelecimento'
    }

    def form_valid(self, form):
        form.instance.user = self.request.user

        url_sucesso = super().form_valid(form)

        print(self.object)
        self.object.nome = "ok - " + self.object.nome
        self.object.save()

        return url_sucesso
        

class EstabelecimentoUpdate(BaseLoginMixin, UpdateView):
    model = Estabelecimento
    fields = ['user', 'endereco', 'categoria', 'name', 'description', 'photo', 'pickup_start', 'pickup_end', 'is_active']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estabelecimento-list')
    extra_context = {
        'titulo': 'Editar Estabelecimento',
        'botao': 'Atualizar Estabelecimento'
    }

class EstabelecimentoDelete(BaseLoginMixin, DeleteView):
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

class EstabelecimentoDetail(BaseLoginMixin, DetailView):
    model = Estabelecimento
    template_name = 'sobraNada/detail/estabelecimento.html'


# ─────────────────────────────────────────
# SACOLA
# ─────────────────────────────────────────

class SacolaCreate(BaseLoginMixin, CreateView):
    model = Sacola
    fields = ['estabelecimento', 'title', 'description', 'original_price', 'sale_price',
              'total_quantity', 'available_quantity', 'expiry_date', 'pickup_start', 'pickup_end', 'status']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('sacola-list')
    extra_context = {
        'titulo': 'Cadastro de Sacola',
        'botao': 'Criar Sacola'
    }

class SacolaUpdate(BaseLoginMixin, UpdateView):
    model = Sacola
    fields = ['estabelecimento', 'title', 'description', 'original_price', 'sale_price',
              'total_quantity', 'available_quantity', 'expiry_date', 'pickup_start', 'pickup_end', 'status']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('sacola-list')
    extra_context = {
        'titulo': 'Editar Sacola',
        'botao': 'Atualizar Sacola'
    }

class SacolaDelete(BaseLoginMixin, DeleteView):
    model = Sacola
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('sacola-list')
    extra_context = {
        'titulo': 'Excluir Sacola',
        'botao': 'Sim, excluir!'
    }

class SacolaList(BaseLoginMixin, ListView):
    model = Sacola
    template_name = 'sobraNada/list/sacola.html'

class SacolaDetail(BaseLoginMixin, DetailView):
    model = Sacola
    template_name = 'sobraNada/detail/sacola.html'


# ─────────────────────────────────────────
# RESERVA
# ─────────────────────────────────────────

class ReservaCreate(BaseLoginMixin, CreateView):
    model = Reserva
    fields = ['user', 'sacola', 'quantity', 'status', 'pickup_code']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Cadastro de Reserva',
        'botao': 'Criar Reserva'
    }

class ReservaUpdate(BaseLoginMixin, UpdateView):
    model = Reserva
    fields = ['user', 'sacola', 'quantity', 'status', 'pickup_code', 'picked_up_at', 'cancelled_at']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Editar Reserva',
        'botao': 'Atualizar Reserva'
    }

class ReservaDelete(BaseLoginMixin, DeleteView):
    model = Reserva
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Excluir Reserva',
        'botao': 'Sim, excluir!'
    }

class ReservaList(BaseLoginMixin, ListView):
    model = Reserva
    template_name = 'sobraNada/list/reserva.html'

class ReservaDetail(BaseLoginMixin, DetailView):
    model = Reserva
    template_name = 'sobraNada/detail/reserva.html'


# ─────────────────────────────────────────
# AVALIAÇÃO
# ─────────────────────────────────────────

class AvaliacaoCreate(BaseLoginMixin, CreateView):
    model = Avaliacao
    fields = ['reserva', 'rating', 'comment']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('avaliacao-list')
    extra_context = {
        'titulo': 'Cadastro de Avaliação',
        'botao': 'Criar Avaliação'
    }

class AvaliacaoUpdate(BaseLoginMixin, UpdateView):
    model = Avaliacao
    fields = ['reserva', 'rating', 'comment']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('avaliacao-list')
    extra_context = {
        'titulo': 'Editar Avaliação',
        'botao': 'Atualizar Avaliação'
    }

class AvaliacaoDelete(BaseLoginMixin, DeleteView):
    model = Avaliacao
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('avaliacao-list')
    extra_context = {
        'titulo': 'Excluir Avaliação',
        'botao': 'Sim, excluir!'
    }

class AvaliacaoList(BaseLoginMixin, ListView):
    model = Avaliacao
    template_name = 'sobraNada/list/avaliacao.html'

class AvaliacaoDetail(BaseLoginMixin, DetailView):
    model = Avaliacao
    template_name = 'sobraNada/detail/avaliacao.html'


# ─────────────────────────────────────────
# NOTIFICAÇÃO
# ─────────────────────────────────────────

class NotificacaoCreate(BaseLoginMixin, CreateView):
    model = Notificacao
    fields = ['user', 'title', 'message', 'type', 'is_read']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('notificacao-list')
    extra_context = {
        'titulo': 'Cadastro de Notificação',
        'botao': 'Criar Notificação'
    }

class NotificacaoUpdate(BaseLoginMixin, UpdateView):
    model = Notificacao
    fields = ['user', 'title', 'message', 'type', 'is_read']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('notificacao-list')
    extra_context = {
        'titulo': 'Editar Notificação',
        'botao': 'Atualizar Notificação'
    }

class NotificacaoDelete(BaseLoginMixin, DeleteView):
    model = Notificacao
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('notificacao-list')
    extra_context = {
        'titulo': 'Excluir Notificação',
        'botao': 'Sim, excluir!'
    }

class NotificacaoList(BaseLoginMixin, ListView):
    model = Notificacao
    template_name = 'sobraNada/list/notificacao.html'

class NotificacaoDetail(BaseLoginMixin, DetailView):
    model = Notificacao
    template_name = 'sobraNada/detail/notificacao.html'