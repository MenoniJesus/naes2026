from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

GRUPO_ADMIN = 'admin'


def eh_admin(usuario) -> bool:
    if not usuario.is_authenticated:
        return False
    return usuario.is_superuser or usuario.groups.filter(name=GRUPO_ADMIN).exists()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Telas de gestão da IA: só superusuário ou grupo "admin"."""

    def test_func(self):
        return eh_admin(self.request.user)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Apenas administradores podem acessar esta tela.")
            return redirect('hub')
        return super().handle_no_permission()
