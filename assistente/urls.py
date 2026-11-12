from django.urls import path

from .views import assistente, assistente_limpar, assistente_perguntar

urlpatterns = [
    path('', assistente, name='assistente'),
    path('perguntar/', assistente_perguntar, name='assistente-perguntar'),
    path('limpar/', assistente_limpar, name='assistente-limpar'),
]
