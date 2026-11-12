from django.urls import include, path, reverse_lazy

from .views import ContatoView, HubView, IndexView, RegisterView

# importar as views para gerenciamento de usuario
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("hub/", HubView.as_view(), name="hub"),
    path("contato/", ContatoView.as_view(), name="contato"),
    path("register/", RegisterView.as_view(), name="register"),
    
    path("login/", LoginView.as_view(
        template_name="sobraNada/form.html",
        extra_context={
            'titulo': 'Login',
            'botao': 'Entrar'
            }
    ), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("mudar-senha/", PasswordChangeView.as_view(
        template_name="sobraNada/form.html",
        success_url=reverse_lazy("hub"),
        extra_context={'titulo': 'Alterar senha', 'botao': 'Salvar nova senha'},
    ), name="password_change"),
]