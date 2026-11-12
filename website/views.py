import logging

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from sobraNada.models import Sacola, Reserva

class IndexView(TemplateView):
    template_name = "website/modelo.html"


class HubView(LoginRequiredMixin, TemplateView):
    template_name = "website/hub.html"
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sacolas_recentes'] = Sacola.objects.prefetch_related('produtos__estabelecimento').order_by('-created_at')[:5]
        context['reservas_recentes'] = (
            Reserva.objects
            .filter(user=self.request.user)
            .select_related('user', 'sacola')
            .prefetch_related('sacola__produtos__estabelecimento')
            .order_by('-reserved_at')[:5]
        )
        return context

class ContatoView(TemplateView):
    template_name = "website/contato.html"


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = UserCreationForm
    template_name = "website/registro.html"
    success_url = reverse_lazy("login")
    success_message = "Conta criada com sucesso! Faça login para continuar."


logger = logging.getLogger("sobranada.csrf")


def csrf_falhou(request, reason=""):
    """Página amigável para falha de CSRF; o motivo vai para o log (visível no GAE)."""
    logger.warning(
        "CSRF recusado em %s %s: %s | origin=%s referer=%s cookie_csrf=%s",
        request.method, request.path, reason,
        request.META.get("HTTP_ORIGIN"), request.META.get("HTTP_REFERER"),
        "csrftoken" in request.COOKIES,
    )
    return render(request, "website/csrf_falhou.html", {"motivo": reason}, status=403)

