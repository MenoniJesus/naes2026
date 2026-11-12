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
    # Sacola.__str__ usa o estabelecimento dos produtos: sem o prefetch cada opção do select faria queries.
    sacola = django_filters.ModelChoiceFilter(
        queryset=Sacola.objects.prefetch_related('produtos__estabelecimento'),
        label='Sacola',
    )

    class Meta:
        model = Reserva
        fields = ['status', 'sacola']
