from django.db import models
from django.contrib.auth.models import User


class Estado(models.Model):
    name = models.CharField(max_length=60, verbose_name="nome")
    uf = models.CharField(max_length=2, verbose_name="UF")

    def __str__(self):
        return f"{self.name} ({self.uf})"


class Cidade(models.Model):
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, verbose_name="nome")

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

    def __str__(self):
        return f"{self.user.username}"


class Categoria(models.Model):
    name = models.CharField(max_length=60, verbose_name="nome")
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="descrição"
    )

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

    def __str__(self):
        return f"{self.name}"


class Sacola(models.Model):
    STATUS_CHOICES = [
        ("disponivel", "Disponível"),
        ("esgotada", "Esgotada"),
        ("expirada", "Expirada"),
    ]

    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.PROTECT)
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

    def __str__(self):
        return f"{self.title} - {self.estabelecimento.name}"


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
        verbose_name="código de retirada",
        help_text="Código para confirmar a retirada"
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

    def __str__(self):
        return f"Reserva #{self.pk} - {self.user.username}"


class Avaliacao(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField(
        verbose_name="nota",
        help_text="Nota de 1 a 5"
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name="comentário"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

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

    def __str__(self):
        return f"{self.title} - {self.user.username}"
