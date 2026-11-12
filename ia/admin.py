from django.contrib import admin

from .models import ConfiguracaoIA, CotaUsuarioIA, RequisicaoIA


@admin.register(ConfiguracaoIA)
class ConfiguracaoIAAdmin(admin.ModelAdmin):
    list_display = ['modelo', 'ativo', 'esforco', 'max_tokens', 'cota_mensal_padrao', 'atualizado_em']
    exclude = ['api_key']


@admin.register(CotaUsuarioIA)
class CotaUsuarioIAAdmin(admin.ModelAdmin):
    list_display = ['user', 'habilitado', 'cota_mensal', 'atualizado_em']
    list_filter = ['habilitado']
    search_fields = ['user__username']


@admin.register(RequisicaoIA)
class RequisicaoIAAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'origem', 'modelo', 'status', 'tokens_entrada', 'tokens_saida', 'duracao_ms', 'criado_em']
    list_filter = ['status', 'origem', 'modelo']
    search_fields = ['user__username', 'pergunta']
    list_select_related = ['user']
    readonly_fields = [campo.name for campo in RequisicaoIA._meta.fields]
