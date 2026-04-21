from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from .models import (
    Estado, Cidade, Endereco, Perfil,
    Categoria, Estabelecimento, Sacola,
    Reserva, Avaliacao, Notificacao
)


# ─────────────────────────────────────────
# ESTADO
# ─────────────────────────────────────────

class EstadoCreate(CreateView):
    model = Estado
    fields = ['name', 'uf']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estado-list')
    extra_context = {
        'titulo': 'Cadastro de Estado',
        'botao': 'Criar Estado'
    }

class EstadoUpdate(UpdateView):
    model = Estado
    fields = ['name', 'uf']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estado-list')
    extra_context = {
        'titulo': 'Editar Estado',
        'botao': 'Atualizar Estado'
    }

class EstadoDelete(DeleteView):
    model = Estado
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estado-list')
    extra_context = {
        'titulo': 'Excluir Estado',
        'botao': 'Sim, excluir!'
    }

class EstadoList(ListView):
    model = Estado
    template_name = 'sobraNada/list/estado.html'

class EstadoDetail(DetailView):
    model = Estado
    template_name = 'sobraNada/detail/estado.html'


# ─────────────────────────────────────────
# CIDADE
# ─────────────────────────────────────────

class CidadeCreate(CreateView):
    model = Cidade
    fields = ['estado', 'name']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('cidade-list')
    extra_context = {
        'titulo': 'Cadastro de Cidade',
        'botao': 'Criar Cidade'
    }

class CidadeUpdate(UpdateView):
    model = Cidade
    fields = ['estado', 'name']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('cidade-list')
    extra_context = {
        'titulo': 'Editar Cidade',
        'botao': 'Atualizar Cidade'
    }

class CidadeDelete(DeleteView):
    model = Cidade
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('cidade-list')
    extra_context = {
        'titulo': 'Excluir Cidade',
        'botao': 'Sim, excluir!'
    }

class CidadeList(ListView):
    model = Cidade
    template_name = 'sobraNada/list/cidade.html'

class CidadeDetail(DetailView):
    model = Cidade
    template_name = 'sobraNada/detail/cidade.html'


# ─────────────────────────────────────────
# ENDEREÇO
# ─────────────────────────────────────────

class EnderecoCreate(CreateView):
    model = Endereco
    fields = ['cidade', 'street', 'number', 'complement', 'neighborhood', 'zip_code']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('endereco-list')
    extra_context = {
        'titulo': 'Cadastro de Endereço',
        'botao': 'Criar Endereço'
    }

class EnderecoUpdate(UpdateView):
    model = Endereco
    fields = ['cidade', 'street', 'number', 'complement', 'neighborhood', 'zip_code']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('endereco-list')
    extra_context = {
        'titulo': 'Editar Endereço',
        'botao': 'Atualizar Endereço'
    }

class EnderecoDelete(DeleteView):
    model = Endereco
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('endereco-list')
    extra_context = {
        'titulo': 'Excluir Endereço',
        'botao': 'Sim, excluir!'
    }

class EnderecoList(ListView):
    model = Endereco
    template_name = 'sobraNada/list/endereco.html'

class EnderecoDetail(DetailView):
    model = Endereco
    template_name = 'sobraNada/detail/endereco.html'


# ─────────────────────────────────────────
# PERFIL
# ─────────────────────────────────────────

class PerfilCreate(CreateView):
    model = Perfil
    fields = ['user', 'phone', 'endereco']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('perfil-list')
    extra_context = {
        'titulo': 'Cadastro de Perfil',
        'botao': 'Criar Perfil'
    }

class PerfilUpdate(UpdateView):
    model = Perfil
    fields = ['user', 'phone', 'endereco']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('perfil-list')
    extra_context = {
        'titulo': 'Editar Perfil',
        'botao': 'Atualizar Perfil'
    }

class PerfilDelete(DeleteView):
    model = Perfil
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('perfil-list')
    extra_context = {
        'titulo': 'Excluir Perfil',
        'botao': 'Sim, excluir!'
    }

class PerfilList(ListView):
    model = Perfil
    template_name = 'sobraNada/list/perfil.html'

class PerfilDetail(DetailView):
    model = Perfil
    template_name = 'sobraNada/detail/perfil.html'


# ─────────────────────────────────────────
# CATEGORIA
# ─────────────────────────────────────────

class CategoriaCreate(CreateView):
    model = Categoria
    fields = ['name', 'description']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Cadastro de Categoria',
        'botao': 'Criar Categoria'
    }

class CategoriaUpdate(UpdateView):
    model = Categoria
    fields = ['name', 'description']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Editar Categoria',
        'botao': 'Atualizar Categoria'
    }

class CategoriaDelete(DeleteView):
    model = Categoria
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('categoria-list')
    extra_context = {
        'titulo': 'Excluir Categoria',
        'botao': 'Sim, excluir!'
    }

class CategoriaList(ListView):
    model = Categoria
    template_name = 'sobraNada/list/categoria.html'

class CategoriaDetail(DetailView):
    model = Categoria
    template_name = 'sobraNada/detail/categoria.html'


# ─────────────────────────────────────────
# ESTABELECIMENTO
# ─────────────────────────────────────────

class EstabelecimentoCreate(CreateView):
    model = Estabelecimento
    fields = ['user', 'endereco', 'categoria', 'name', 'description', 'photo', 'pickup_start', 'pickup_end', 'is_active']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estabelecimento-list')
    extra_context = {
        'titulo': 'Cadastro de Estabelecimento',
        'botao': 'Criar Estabelecimento'
    }

class EstabelecimentoUpdate(UpdateView):
    model = Estabelecimento
    fields = ['user', 'endereco', 'categoria', 'name', 'description', 'photo', 'pickup_start', 'pickup_end', 'is_active']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estabelecimento-list')
    extra_context = {
        'titulo': 'Editar Estabelecimento',
        'botao': 'Atualizar Estabelecimento'
    }

class EstabelecimentoDelete(DeleteView):
    model = Estabelecimento
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('estabelecimento-list')
    extra_context = {
        'titulo': 'Excluir Estabelecimento',
        'botao': 'Sim, excluir!'
    }

class EstabelecimentoList(ListView):
    model = Estabelecimento
    template_name = 'sobraNada/list/estabelecimento.html'

class EstabelecimentoDetail(DetailView):
    model = Estabelecimento
    template_name = 'sobraNada/detail/estabelecimento.html'


# ─────────────────────────────────────────
# SACOLA
# ─────────────────────────────────────────

class SacolaCreate(CreateView):
    model = Sacola
    fields = ['estabelecimento', 'title', 'description', 'original_price', 'sale_price',
              'total_quantity', 'available_quantity', 'expiry_date', 'pickup_start', 'pickup_end', 'status']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('sacola-list')
    extra_context = {
        'titulo': 'Cadastro de Sacola',
        'botao': 'Criar Sacola'
    }

class SacolaUpdate(UpdateView):
    model = Sacola
    fields = ['estabelecimento', 'title', 'description', 'original_price', 'sale_price',
              'total_quantity', 'available_quantity', 'expiry_date', 'pickup_start', 'pickup_end', 'status']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('sacola-list')
    extra_context = {
        'titulo': 'Editar Sacola',
        'botao': 'Atualizar Sacola'
    }

class SacolaDelete(DeleteView):
    model = Sacola
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('sacola-list')
    extra_context = {
        'titulo': 'Excluir Sacola',
        'botao': 'Sim, excluir!'
    }

class SacolaList(ListView):
    model = Sacola
    template_name = 'sobraNada/list/sacola.html'

class SacolaDetail(DetailView):
    model = Sacola
    template_name = 'sobraNada/detail/sacola.html'


# ─────────────────────────────────────────
# RESERVA
# ─────────────────────────────────────────

class ReservaCreate(CreateView):
    model = Reserva
    fields = ['user', 'sacola', 'quantity', 'status', 'pickup_code']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Cadastro de Reserva',
        'botao': 'Criar Reserva'
    }

class ReservaUpdate(UpdateView):
    model = Reserva
    fields = ['user', 'sacola', 'quantity', 'status', 'pickup_code', 'picked_up_at', 'cancelled_at']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Editar Reserva',
        'botao': 'Atualizar Reserva'
    }

class ReservaDelete(DeleteView):
    model = Reserva
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('reserva-list')
    extra_context = {
        'titulo': 'Excluir Reserva',
        'botao': 'Sim, excluir!'
    }

class ReservaList(ListView):
    model = Reserva
    template_name = 'sobraNada/list/reserva.html'

class ReservaDetail(DetailView):
    model = Reserva
    template_name = 'sobraNada/detail/reserva.html'


# ─────────────────────────────────────────
# AVALIAÇÃO
# ─────────────────────────────────────────

class AvaliacaoCreate(CreateView):
    model = Avaliacao
    fields = ['reserva', 'rating', 'comment']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('avaliacao-list')
    extra_context = {
        'titulo': 'Cadastro de Avaliação',
        'botao': 'Criar Avaliação'
    }

class AvaliacaoUpdate(UpdateView):
    model = Avaliacao
    fields = ['reserva', 'rating', 'comment']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('avaliacao-list')
    extra_context = {
        'titulo': 'Editar Avaliação',
        'botao': 'Atualizar Avaliação'
    }

class AvaliacaoDelete(DeleteView):
    model = Avaliacao
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('avaliacao-list')
    extra_context = {
        'titulo': 'Excluir Avaliação',
        'botao': 'Sim, excluir!'
    }

class AvaliacaoList(ListView):
    model = Avaliacao
    template_name = 'sobraNada/list/avaliacao.html'

class AvaliacaoDetail(DetailView):
    model = Avaliacao
    template_name = 'sobraNada/detail/avaliacao.html'


# ─────────────────────────────────────────
# NOTIFICAÇÃO
# ─────────────────────────────────────────

class NotificacaoCreate(CreateView):
    model = Notificacao
    fields = ['user', 'title', 'message', 'type', 'is_read']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('notificacao-list')
    extra_context = {
        'titulo': 'Cadastro de Notificação',
        'botao': 'Criar Notificação'
    }

class NotificacaoUpdate(UpdateView):
    model = Notificacao
    fields = ['user', 'title', 'message', 'type', 'is_read']
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('notificacao-list')
    extra_context = {
        'titulo': 'Editar Notificação',
        'botao': 'Atualizar Notificação'
    }

class NotificacaoDelete(DeleteView):
    model = Notificacao
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('notificacao-list')
    extra_context = {
        'titulo': 'Excluir Notificação',
        'botao': 'Sim, excluir!'
    }

class NotificacaoList(ListView):
    model = Notificacao
    template_name = 'sobraNada/list/notificacao.html'

class NotificacaoDetail(DetailView):
    model = Notificacao
    template_name = 'sobraNada/detail/notificacao.html'