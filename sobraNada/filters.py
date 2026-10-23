import django_filters

from .models import Estabelecimento, Produto, Reserva, Sacola


class ProdutoFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nome')

    class Meta:
        model = Produto
        fields = ['name', 'estabelecimento', 'is_active']


class SacolaFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Título')
    estabelecimento = django_filters.ModelChoiceFilter(
        field_name='produtos__estabelecimento',
        queryset=Estabelecimento.objects.all(),
        label='Estabelecimento',
    )

    class Meta:
        model = Sacola
        fields = ['title', 'estabelecimento', 'status']


class ReservaFilter(django_filters.FilterSet):
    class Meta:
        model = Reserva
        fields = ['status', 'sacola']
