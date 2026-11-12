import django_filters
from django import forms
from django.contrib.auth.models import User

from .models import RequisicaoIA

WIDGET_DATA = forms.DateInput(attrs={"type": "date"})


class RequisicaoIAFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.order_by('username'), label='Usuário')
    origem = django_filters.CharFilter(lookup_expr='icontains', label='Origem')
    desde = django_filters.DateFilter(field_name='criado_em', lookup_expr='date__gte', label='Desde', widget=WIDGET_DATA)
    ate = django_filters.DateFilter(field_name='criado_em', lookup_expr='date__lte', label='Até', widget=WIDGET_DATA)

    class Meta:
        model = RequisicaoIA
        fields = ['user', 'status', 'origem', 'desde', 'ate']


class UsuarioIAFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr='icontains', label='Usuário')
    habilitado = django_filters.ChoiceFilter(
        label='Acesso à IA',
        choices=[('sim', 'Habilitado'), ('nao', 'Bloqueado')],
        method='filtrar_habilitado',
    )

    class Meta:
        model = User
        fields = ['username', 'habilitado']

    def filtrar_habilitado(self, queryset, nome, valor):
        # Sem registro de cota o usuário está habilitado por padrão.
        if valor == 'nao':
            return queryset.filter(cota_ia__habilitado=False)
        return queryset.exclude(cota_ia__habilitado=False)
