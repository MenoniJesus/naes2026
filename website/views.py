from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

class IndexView(TemplateView):
    template_name = "website/modelo.html"

class ContatoView(TemplateView):
    template_name = "website/contato.html"


class RegisterView(CreateView):
    template_name = "website/registro.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
