from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
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
        context['reservas_recentes'] = Reserva.objects.select_related('user', 'sacola').order_by('-reserved_at')[:5]
        return context

class ContatoView(TemplateView):
    template_name = "website/contato.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "website/registro.html"
    success_url = reverse_lazy("login")