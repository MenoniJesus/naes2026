from django.contrib import admin

from .models import MensagemAssistente


@admin.register(MensagemAssistente)
class MensagemAssistenteAdmin(admin.ModelAdmin):
    list_display = ['user', 'papel', 'conteudo', 'criado_em']
    list_filter = ['papel']
    search_fields = ['user__username', 'conteudo']
    list_select_related = ['user']
