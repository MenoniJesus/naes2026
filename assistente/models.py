from django.contrib.auth.models import User
from django.db import models

from ia.models import RequisicaoIA


class MensagemAssistente(models.Model):
    """Histórico da conversa de cada usuário com o assistente."""

    PAPEL_CHOICES = [
        ("user", "Usuário"),
        ("assistant", "Assistente"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mensagens_assistente", verbose_name="usuário")
    papel = models.CharField(max_length=10, choices=PAPEL_CHOICES, verbose_name="papel")
    conteudo = models.TextField(verbose_name="conteúdo")
    requisicao = models.ForeignKey(
        RequisicaoIA,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="requisição de IA",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    class Meta:
        ordering = ["criado_em", "pk"]
        verbose_name = "mensagem do assistente"
        verbose_name_plural = "mensagens do assistente"
        indexes = [models.Index(fields=["user", "criado_em"])]

    def __str__(self):
        return f"{self.get_papel_display()} - {self.user.username}: {self.conteudo[:40]}"
