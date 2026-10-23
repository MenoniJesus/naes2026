from django.contrib import admin

from .models import (
    Estado, Cidade, Endereco, Perfil,
    Categoria, Estabelecimento, Produto, Sacola,
    Reserva, Avaliacao, Notificacao,
)


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['name', 'uf']
    search_fields = ['name', 'uf']


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ['name', 'estado']
    list_filter = ['estado']
    search_fields = ['name']


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ['street', 'number', 'neighborhood', 'cidade', 'zip_code']
    list_filter = ['cidade']
    search_fields = ['street', 'neighborhood', 'zip_code']


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'endereco']
    search_fields = ['user__username', 'phone']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Estabelecimento)
class EstabelecimentoAdmin(admin.ModelAdmin):
    list_display = ['name', 'categoria', 'user', 'is_active']
    list_filter = ['categoria', 'is_active']
    search_fields = ['name']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['name', 'estabelecimento', 'price', 'is_active']
    list_filter = ['estabelecimento', 'is_active']
    search_fields = ['name']


@admin.register(Sacola)
class SacolaAdmin(admin.ModelAdmin):
    list_display = ['title', 'sale_price', 'available_quantity', 'total_quantity', 'status']
    list_filter = ['status']
    search_fields = ['title']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'sacola', 'quantity', 'status', 'pickup_code']
    list_filter = ['status']
    search_fields = ['user__username', 'pickup_code']


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read']
    search_fields = ['title', 'user__username']
