from django.urls import path
from .views import (
    EstadoCreate, EstadoUpdate, EstadoDelete, EstadoList, EstadoDetail,
    CidadeCreate, CidadeUpdate, CidadeDelete, CidadeList, CidadeDetail,
    EnderecoCreate, EnderecoUpdate, EnderecoDelete, EnderecoList, EnderecoDetail,
    PerfilCreate, PerfilUpdate, PerfilDelete, PerfilList, PerfilDetail,
    CategoriaCreate, CategoriaUpdate, CategoriaDelete, CategoriaList, CategoriaDetail,
    EstabelecimentoCreate, EstabelecimentoUpdate, EstabelecimentoDelete, EstabelecimentoList, EstabelecimentoDetail,
    ProdutoCreate, ProdutoUpdate, ProdutoDelete, ProdutoList, ProdutoDetail,
    SacolaCreate, SacolaUpdate, SacolaDelete, SacolaList, SacolaDetail,
    ReservaCreate, ReservaUpdate, ReservaCancelar, ReservaDelete, ReservaList, ReservaDetail,
    AvaliacaoCreate, AvaliacaoUpdate, AvaliacaoDelete, AvaliacaoList, AvaliacaoDetail,
    NotificacaoCreate, NotificacaoUpdate, NotificacaoDelete, NotificacaoList, NotificacaoDetail,
)

urlpatterns = [
    # Estado
    path('cadastrar/estado/', EstadoCreate.as_view(), name='estado-create'),
    path('atualizar/estado/<int:pk>/', EstadoUpdate.as_view(), name='estado-update'),
    path('excluir/estado/<int:pk>/', EstadoDelete.as_view(), name='estado-delete'),
    path('listar/estado/', EstadoList.as_view(), name='estado-list'),
    path('detalhar/estado/<int:pk>/', EstadoDetail.as_view(), name='estado-detail'),

    # Cidade
    path('cadastrar/cidade/', CidadeCreate.as_view(), name='cidade-create'),
    path('atualizar/cidade/<int:pk>/', CidadeUpdate.as_view(), name='cidade-update'),
    path('excluir/cidade/<int:pk>/', CidadeDelete.as_view(), name='cidade-delete'),
    path('listar/cidade/', CidadeList.as_view(), name='cidade-list'),
    path('detalhar/cidade/<int:pk>/', CidadeDetail.as_view(), name='cidade-detail'),

    # Endereço
    path('cadastrar/endereco/', EnderecoCreate.as_view(), name='endereco-create'),
    path('atualizar/endereco/<int:pk>/', EnderecoUpdate.as_view(), name='endereco-update'),
    path('excluir/endereco/<int:pk>/', EnderecoDelete.as_view(), name='endereco-delete'),
    path('listar/endereco/', EnderecoList.as_view(), name='endereco-list'),
    path('detalhar/endereco/<int:pk>/', EnderecoDetail.as_view(), name='endereco-detail'),

    # Perfil
    path('cadastrar/perfil/', PerfilCreate.as_view(), name='perfil-create'),
    path('atualizar/perfil/<int:pk>/', PerfilUpdate.as_view(), name='perfil-update'),
    path('excluir/perfil/<int:pk>/', PerfilDelete.as_view(), name='perfil-delete'),
    path('listar/perfil/', PerfilList.as_view(), name='perfil-list'),
    path('detalhar/perfil/<int:pk>/', PerfilDetail.as_view(), name='perfil-detail'),

    # Categoria
    path('cadastrar/categoria/', CategoriaCreate.as_view(), name='categoria-create'),
    path('atualizar/categoria/<int:pk>/', CategoriaUpdate.as_view(), name='categoria-update'),
    path('excluir/categoria/<int:pk>/', CategoriaDelete.as_view(), name='categoria-delete'),
    path('listar/categoria/', CategoriaList.as_view(), name='categoria-list'),
    path('detalhar/categoria/<int:pk>/', CategoriaDetail.as_view(), name='categoria-detail'),

    # Estabelecimento
    path('cadastrar/estabelecimento/', EstabelecimentoCreate.as_view(), name='estabelecimento-create'),
    path('atualizar/estabelecimento/<int:pk>/', EstabelecimentoUpdate.as_view(), name='estabelecimento-update'),
    path('excluir/estabelecimento/<int:pk>/', EstabelecimentoDelete.as_view(), name='estabelecimento-delete'),
    path('listar/estabelecimento/', EstabelecimentoList.as_view(), name='estabelecimento-list'),
    path('detalhar/estabelecimento/<int:pk>/', EstabelecimentoDetail.as_view(), name='estabelecimento-detail'),

    # Produto
    path('cadastrar/produto/', ProdutoCreate.as_view(), name='produto-create'),
    path('atualizar/produto/<int:pk>/', ProdutoUpdate.as_view(), name='produto-update'),
    path('excluir/produto/<int:pk>/', ProdutoDelete.as_view(), name='produto-delete'),
    path('listar/produto/', ProdutoList.as_view(), name='produto-list'),
    path('detalhar/produto/<int:pk>/', ProdutoDetail.as_view(), name='produto-detail'),

    # Sacola
    path('cadastrar/sacola/', SacolaCreate.as_view(), name='sacola-create'),
    path('atualizar/sacola/<int:pk>/', SacolaUpdate.as_view(), name='sacola-update'),
    path('excluir/sacola/<int:pk>/', SacolaDelete.as_view(), name='sacola-delete'),
    path('listar/sacola/', SacolaList.as_view(), name='sacola-list'),
    path('detalhar/sacola/<int:pk>/', SacolaDetail.as_view(), name='sacola-detail'),

    # Reserva
    path('cadastrar/reserva/', ReservaCreate.as_view(), name='reserva-create'),
    path('atualizar/reserva/<int:pk>/', ReservaUpdate.as_view(), name='reserva-update'),
    path('cancelar/reserva/<int:pk>/', ReservaCancelar.as_view(), name='reserva-cancelar'),
    path('excluir/reserva/<int:pk>/', ReservaDelete.as_view(), name='reserva-delete'),
    path('listar/reserva/', ReservaList.as_view(), name='reserva-list'),
    path('detalhar/reserva/<int:pk>/', ReservaDetail.as_view(), name='reserva-detail'),

    # Avaliação
    path('cadastrar/avaliacao/', AvaliacaoCreate.as_view(), name='avaliacao-create'),
    path('atualizar/avaliacao/<int:pk>/', AvaliacaoUpdate.as_view(), name='avaliacao-update'),
    path('excluir/avaliacao/<int:pk>/', AvaliacaoDelete.as_view(), name='avaliacao-delete'),
    path('listar/avaliacao/', AvaliacaoList.as_view(), name='avaliacao-list'),
    path('detalhar/avaliacao/<int:pk>/', AvaliacaoDetail.as_view(), name='avaliacao-detail'),

    # Notificação
    path('cadastrar/notificacao/', NotificacaoCreate.as_view(), name='notificacao-create'),
    path('atualizar/notificacao/<int:pk>/', NotificacaoUpdate.as_view(), name='notificacao-update'),
    path('excluir/notificacao/<int:pk>/', NotificacaoDelete.as_view(), name='notificacao-delete'),
    path('listar/notificacao/', NotificacaoList.as_view(), name='notificacao-list'),
    path('detalhar/notificacao/<int:pk>/', NotificacaoDetail.as_view(), name='notificacao-detail'),
]