import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from . import precificacao


def gerar_pickup_code() -> str:
    return uuid.uuid4().hex[:8].upper()


class Estado(models.Model):
    name = models.CharField(max_length=60, verbose_name="nome")
    uf = models.CharField(max_length=2, verbose_name="UF")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.uf})"


class Cidade(models.Model):
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name="nome")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.estado.uf}"


class Endereco(models.Model):
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)
    street = models.CharField(max_length=200, verbose_name="rua")
    number = models.CharField(max_length=20, verbose_name="número")
    complement = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="complemento"
    )
    neighborhood = models.CharField(max_length=100, verbose_name="bairro")
    zip_code = models.CharField(max_length=10, verbose_name="CEP")

    class Meta:
        ordering = ["street", "number"]

    def __str__(self):
        return f"{self.street}, {self.number} - {self.neighborhood}"


class Perfil(models.Model):
    """Perfil estendido do usuário com campos adicionais."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name="telefone")
    endereco = models.ForeignKey(
        Endereco,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}"


class Categoria(models.Model):
    name = models.CharField(max_length=60, verbose_name="nome")
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="descrição"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class Estabelecimento(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    endereco = models.ForeignKey(Endereco, on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name="nome")
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="descrição"
    )
    photo = models.ImageField(
        upload_to="estabelecimentos/",
        null=True,
        blank=True,
        verbose_name="foto"
    )
    pickup_start = models.TimeField(verbose_name="horário início retirada")
    pickup_end = models.TimeField(verbose_name="horário fim retirada")
    is_active = models.BooleanField(default=True, verbose_name="ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        if self.pickup_start and self.pickup_end and self.pickup_start >= self.pickup_end:
            raise ValidationError({
                "pickup_end": "O horário final da retirada deve ser depois do horário inicial."
            })


class Produto(models.Model):
    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name="nome")
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="descrição"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="preço"
    )
    is_active = models.BooleanField(default=True, verbose_name="ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.estabelecimento.name})"


class Sacola(models.Model):
    STATUS_CHOICES = [
        ("disponivel", "Disponível"),
        ("esgotada", "Esgotada"),
        ("expirada", "Expirada"),
    ]

    produtos = models.ManyToManyField(Produto, verbose_name="produtos")
    title = models.CharField(max_length=100, verbose_name="título")
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="descrição"
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="preço original"
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="preço de venda"
    )
    total_quantity = models.PositiveIntegerField(verbose_name="quantidade total")
    available_quantity = models.PositiveIntegerField(verbose_name="quantidade disponível")
    expiry_date = models.DateField(verbose_name="data de validade")
    pickup_start = models.TimeField(verbose_name="horário início retirada")
    pickup_end = models.TimeField(verbose_name="horário fim retirada")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="disponivel",
        verbose_name="status"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        estabelecimento = self.estabelecimento
        return f"{self.title} - {estabelecimento.name}" if estabelecimento else self.title

    @property
    def estabelecimento(self):
        """Vem dos produtos: o form garante que todos sejam do mesmo estabelecimento."""
        if not self.pk:
            return None
        # list(...all()) em vez de .first() para aproveitar o cache do prefetch_related.
        produtos = list(self.produtos.all())
        return produtos[0].estabelecimento if produtos else None

    def save(self, *args, **kwargs):
        if self._state.adding and self.available_quantity is None:
            self.available_quantity = self.total_quantity
        super().save(*args, **kwargs)

    def clean(self):
        erros = {}

        if self.sale_price is not None and self.sale_price <= 0:
            erros["sale_price"] = "O preço de venda deve ser maior que zero."
        elif self.sale_price is not None and self.original_price is not None:
            if self.sale_price >= self.original_price:
                erros["sale_price"] = (
                    "O preço de venda deve ser menor que o preço original "
                    f"(soma dos produtos: R$ {self.original_price})."
                )

        if self.total_quantity is not None and self.total_quantity < 1:
            erros["total_quantity"] = "A sacola precisa ter ao menos 1 unidade."

        if self.pickup_start and self.pickup_end and self.pickup_start >= self.pickup_end:
            erros["pickup_end"] = "O horário final da retirada deve ser depois do horário inicial."

        if self._state.adding and self.expiry_date and self.expiry_date < timezone.localdate():
            erros["expiry_date"] = "A validade não pode estar no passado."

        if erros:
            raise ValidationError(erros)

    def calcular_desconto(self, quantidade=1):
        """Desconto da faixa em que cai o total de `quantidade` unidades."""
        return precificacao.calcular_desconto(
            preco_venda=self.sale_price,
            quantidade=quantidade,
        )

    def reservar(self, quantidade: int):
        if quantidade < 1:
            raise ValueError("A quantidade mínima por reserva é 1 sacola.")
        if quantidade > self.available_quantity:
            raise ValueError("Quantidade indisponível no estoque desta sacola.")

        self.available_quantity -= quantidade
        if self.available_quantity == 0:
            self.status = "esgotada"
        self.save(update_fields=["available_quantity", "status"])

    def devolver(self, quantidade: int):
        """Repoe ao estoque as unidades de uma reserva cancelada."""
        self.available_quantity = min(self.available_quantity + quantidade, self.total_quantity)
        if self.status == "esgotada" and self.available_quantity > 0:
            self.status = "disponivel"
        self.save(update_fields=["available_quantity", "status"])


class Reserva(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("confirmada", "Confirmada"),
        ("retirada", "Retirada"),
        ("cancelada", "Cancelada"),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    sacola = models.ForeignKey(Sacola, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name="quantidade")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente",
        verbose_name="status"
    )
    pickup_code = models.CharField(
        max_length=20,
        default=gerar_pickup_code,
        editable=False,
        verbose_name="código de retirada",
        help_text="Código para confirmar a retirada"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="preço unitário com desconto"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="valor total"
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="desconto aplicado (%)"
    )
    reserved_at = models.DateTimeField(auto_now_add=True, verbose_name="reservado em")
    picked_up_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="retirado em"
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="cancelado em"
    )

    class Meta:
        ordering = ["-reserved_at"]

    def __str__(self):
        return f"Reserva #{self.pk} - {self.user.username}"

    @property
    def esta_ativa(self) -> bool:
        return self.status in ("pendente", "confirmada")

    def aplicar_desconto(self, desconto):
        """Congela na reserva os valores calculados no momento da compra."""
        self.unit_price = desconto.preco_unitario
        self.total_price = desconto.valor_final
        self.discount_percent = desconto.percentual_exibicao

    def cancelar(self):
        if not self.esta_ativa:
            raise ValueError("Esta reserva não pode mais ser cancelada.")

        self.sacola.devolver(self.quantity)
        self.status = "cancelada"
        self.cancelled_at = timezone.now()
        self.save(update_fields=["status", "cancelled_at"])


class Avaliacao(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField(
        verbose_name="nota",
        help_text="Nota de 1 a 5",
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name="comentário"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Avaliação #{self.pk} - {self.rating} estrelas"


class Notificacao(models.Model):
    TYPE_CHOICES = [
        ("reserva", "Reserva"),
        ("lembrete", "Lembrete"),
        ("promocao", "Promoção"),
        ("sistema", "Sistema"),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=100, verbose_name="título")
    message = models.TextField(verbose_name="mensagem")
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="sistema",
        verbose_name="tipo"
    )
    is_read = models.BooleanField(default=False, verbose_name="lida")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
