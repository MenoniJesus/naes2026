from django.urls import path

from .views import (
    ConfiguracaoUpdate, MeuConsumo, RequisicaoDetail, RequisicaoList,
    UsuarioIAList, UsuarioIAUpdate, configuracao_testar,
)

urlpatterns = [
    path('requisicoes/', RequisicaoList.as_view(), name='ia-requisicao-list'),
    path('requisicoes/<int:pk>/', RequisicaoDetail.as_view(), name='ia-requisicao-detail'),
    path('configuracao/', ConfiguracaoUpdate.as_view(), name='ia-configuracao'),
    path('configuracao/testar/', configuracao_testar, name='ia-configuracao-testar'),
    path('usuarios/', UsuarioIAList.as_view(), name='ia-usuario-list'),
    path('usuarios/<int:user_pk>/', UsuarioIAUpdate.as_view(), name='ia-usuario-update'),
    path('meu-consumo/', MeuConsumo.as_view(), name='ia-meu-consumo'),
]
