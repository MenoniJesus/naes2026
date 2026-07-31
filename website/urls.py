from django.urls import include, path

from .views import ContatoView, IndexView, RegisterView

# importar as views para gerenciamento de usuario
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("contato/", ContatoView.as_view(), name="contato"),
    path("register/", RegisterView.as_view(), name="register"),
    
    path("login/", LoginView.as_view(
        template_name="sobraNada/form.html",
        extra_context={
            'title': 'Login', 
            'botao': 'Entrar'
            }
    ), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("mudar-senha/", PasswordChangeView.as_view(template_name="sobraNada/form.html"), name="password_change"),
]