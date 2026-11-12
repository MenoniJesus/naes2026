from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class ConfiguracaoIA(models.Model):
    """Configuração única da IA, editável pela tela de configuração (sempre pk=1)."""

    ESFORCO_CHOICES = [
        ("", "Padrão do modelo"),
        ("low", "Baixo (respostas rápidas)"),
        ("medium", "Médio"),
        ("high", "Alto"),
    ]

    ativo = models.BooleanField(default=True, verbose_name="IA ativa")
    modelo = models.CharField(
        max_length=60,
        default="claude-opus-5-5",
        verbose_name="modelo",
        help_text="ID do modelo Claude, ex.: claude-opus-5-5, claude-sonnet-5-5, claude-haiku-5-5.",
    )
    api_key = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="chave da API",
        help_text="Deixe em branco para usar a variável de ambiente ANTHROPIC_API_KEY.",
    )
    max_tokens = models.PositiveIntegerField(
        default=2048,
        verbose_name="máximo de tokens por resposta",
    )
    esforco = models.CharField(
        max_length=10,
        choices=ESFORCO_CHOICES,
        default="low",
        blank=True,
        verbose_name="esforço",
        help_text="Quanto o modelo raciocina antes de responder. Baixo é suficiente para um assistente.",
    )
    usar_fallback = models.BooleanField(
        default=True,
        verbose_name="usar fallback em recusas",
        help_text="Se o modelo recusar por segurança, a API tenta outro modelo automaticamente "
                  "(disponível para Opus 5.5, Opus 5, Sonnet 5.5 e Fable 5.1).",
    )
    timeout_segundos = models.PositiveIntegerField(default=60, verbose_name="timeout (segundos)")
    cota_mensal_padrao = models.PositiveIntegerField(
        default=100_000,
        verbose_name="cota mensal padrão (tokens)",
        help_text="Vale para usuários sem cota própria definida em “IA por usuário”.",
    )
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="atualizado em")
    atualizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="atualizado por",
    )

    class Meta:
        verbose_name = "configuração da IA"
        verbose_name_plural = "configuração da IA"

    def __str__(self):
        return f"Configuração da IA ({self.modelo})"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def carregar(cls):
        configuracao, _ = cls.objects.get_or_create(pk=1)
        return configuracao

    @property
    def tem_chave_propria(self) -> bool:
        return bool(self.api_key)


class CotaUsuarioIA(models.Model):
    """Permissão e cota mensal de tokens de cada usuário (tela “IA por usuário”)."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cota_ia", verbose_name="usuário")
    habilitado = models.BooleanField(default=True, verbose_name="pode usar a IA")
    cota_mensal = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="cota mensal (tokens)",
        help_text="Deixe em branco para usar a cota padrão da configuração.",
    )
    observacao = models.CharField(max_length=200, blank=True, verbose_name="observação")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="atualizado em")

    class Meta:
        ordering = ["user__username"]
        verbose_name = "cota de IA do usuário"
        verbose_name_plural = "cotas de IA dos usuários"

    def __str__(self):
        return f"Cota de IA - {self.user.username}"

    def cota_efetiva(self, configuracao=None) -> int:
        if self.cota_mensal is not None:
            return self.cota_mensal
        return (configuracao or ConfiguracaoIA.carregar()).cota_mensal_padrao


class RequisicaoIAQuerySet(models.QuerySet):
    def do_mes(self, referencia=None):
        referencia = timezone.localtime(referencia or timezone.now())
        inicio = referencia.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.filter(criado_em__gte=inicio)

    def tokens_consumidos(self) -> int:
        totais = self.aggregate(entrada=Sum("tokens_entrada"), saida=Sum("tokens_saida"))
        return (totais["entrada"] or 0) + (totais["saida"] or 0)


class RequisicaoIA(models.Model):
    """Auditoria de cada chamada feita por `ia.services.chamar_ia`."""

    STATUS_CHOICES = [
        ("sucesso", "Sucesso"),
        ("erro", "Erro"),
        ("recusada", "Recusada pelo modelo"),
        ("bloqueada", "Bloqueada (cota ou permissão)"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requisicoes_ia",
        verbose_name="usuário",
    )
    origem = models.CharField(max_length=40, verbose_name="origem")
    modelo = models.CharField(max_length=60, verbose_name="modelo")
    pergunta = models.TextField(verbose_name="pergunta")
    resposta = models.TextField(blank=True, verbose_name="resposta")
    mensagens_enviadas = models.PositiveIntegerField(default=0, verbose_name="mensagens enviadas")
    tokens_entrada = models.PositiveIntegerField(default=0, verbose_name="tokens de entrada")
    tokens_saida = models.PositiveIntegerField(default=0, verbose_name="tokens de saída")
    duracao_ms = models.PositiveIntegerField(default=0, verbose_name="duração (ms)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="status")
    erro = models.TextField(blank=True, verbose_name="erro")
    id_requisicao_api = models.CharField(max_length=100, blank=True, verbose_name="ID na API")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    objects = RequisicaoIAQuerySet.as_manager()

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "requisição de IA"
        verbose_name_plural = "requisições de IA"
        indexes = [models.Index(fields=["user", "criado_em"])]

    def __str__(self):
        return f"Requisição #{self.pk} - {self.origem} ({self.get_status_display()})"

    @property
    def tokens_total(self) -> int:
        return self.tokens_entrada + self.tokens_saida
