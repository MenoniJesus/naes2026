from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

class IndexView(TemplateView):
    template_name = "website/modelo.html"

class ContatoView(TemplateView):
    template_name = "website/contato.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "website/registro.html"
    success_url = reverse_lazy("login")