from decimal import Decimal

from django import forms
from django.db.models import Q

from . import precificacao
from .models import (
    Avaliacao, Cidade, Endereco, Estabelecimento, Notificacao, Perfil, Produto, Reserva, Sacola,
)

WIDGET_DATA = forms.DateInput(attrs={"type": "date"})
WIDGET_HORA = forms.TimeInput(attrs={"type": "time"})


class EstabelecimentoForm(forms.ModelForm):
    """O dono e sempre o usuario logado, por isso `user` fica fora do formulario."""

    class Meta:
        model = Estabelecimento
        fields = [
            "endereco", "categoria", "name", "description",
            "photo", "pickup_start", "pickup_end", "is_active",
        ]
        widgets = {"pickup_start": WIDGET_HORA, "pickup_end": WIDGET_HORA}


class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ["cidade", "street", "number", "complement", "neighborhood", "zip_code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cidade.__str__ mostra a UF: sem o select_related cada opção faria uma query.
        self.fields["cidade"].queryset = Cidade.objects.select_related("estado")


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["phone", "endereco"]


class NotificacaoForm(forms.ModelForm):
    class Meta:
        model = Notificacao
        fields = ["title", "message", "type", "is_read"]


class ProdutoForm(forms.ModelForm):
    """O estabelecimento e sempre o do usuario logado (definido na view)."""

    class Meta:
        model = Produto
        fields = ["name", "description", "price", "is_active"]


class SacolaForm(forms.ModelForm):
    """O estabelecimento e o preco original vem dos produtos.

    `available_quantity` e `status` sao controlados pelo sistema.
    """

    class Meta:
        model = Sacola
        fields = [
            "produtos", "title", "description", "sale_price",
            "total_quantity", "expiry_date", "pickup_start", "pickup_end",
        ]
        widgets = {
            "expiry_date": WIDGET_DATA,
            "pickup_start": WIDGET_HORA,
            "pickup_end": WIDGET_HORA,
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        produtos = Produto.objects.filter(is_active=True).select_related("estabelecimento")
        if usuario is not None:
            produtos = produtos.filter(estabelecimento__user=usuario)
        self.fields["produtos"].queryset = produtos

    def clean_produtos(self):
        produtos = self.cleaned_data["produtos"]
        if len({produto.estabelecimento_id for produto in produtos}) > 1:
            raise forms.ValidationError(
                "Todos os produtos da sacola precisam ser do mesmo estabelecimento."
            )
        return produtos

    def clean(self):
        dados = super().clean()
        produtos = dados.get("produtos")

        # Roda antes de _post_clean, entao Sacola.clean() ja valida contra este valor.
        if produtos:
            self.instance.original_price = sum(
                (produto.price for produto in produtos), Decimal("0.00")
            )

        return dados


class SacolaUpdateForm(SacolaForm):
    class Meta(SacolaForm.Meta):
        fields = SacolaForm.Meta.fields + ["status"]


class ReservaForm(forms.ModelForm):
    """Calcula o desconto no `clean` e o expoe em `self.desconto` para a view."""

    class Meta:
        model = Reserva
        fields = ["sacola", "quantity"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.desconto = None
        self.fields["sacola"].queryset = (
            Sacola.objects
            .filter(status="disponivel", available_quantity__gt=0)
            .prefetch_related("produtos__estabelecimento")
        )
        self.fields["quantity"].initial = 1

    def clean(self):
        dados = super().clean()
        sacola = dados.get("sacola")
        quantidade = dados.get("quantity")

        if sacola and quantidade is not None:
            if quantidade > sacola.available_quantity:
                self.add_error("quantity", "Quantidade indisponível no estoque desta sacola.")
            else:
                try:
                    self.desconto = sacola.calcular_desconto(quantidade)
                except ValueError as erro:
                    self.add_error("quantity", str(erro))

        return dados


class ReservaUpdateForm(forms.ModelForm):
    """So a quantidade pode mudar; o estoque e o preco sao recalculados na view."""

    class Meta:
        model = Reserva
        fields = ["quantity"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.desconto = None

    def clean_quantity(self):
        quantidade = self.cleaned_data["quantity"]
        sacola = self.instance.sacola

        if not self.instance.esta_ativa:
            raise forms.ValidationError("Só é possível alterar reservas pendentes ou confirmadas.")

        # As unidades ja seguras por esta reserva voltam para o estoque disponivel.
        disponivel = sacola.available_quantity + self.instance.quantity
        if quantidade > disponivel:
            raise forms.ValidationError("Quantidade indisponível no estoque desta sacola.")

        try:
            self.desconto = sacola.calcular_desconto(quantidade)
        except ValueError as erro:
            raise forms.ValidationError(str(erro))

        return quantidade


class AvaliacaoForm(forms.ModelForm):
    """Só permite avaliar reservas retiradas pelo proprio usuario e ainda sem nota."""

    class Meta:
        model = Avaliacao
        fields = ["reserva", "rating", "comment"]

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        elegiveis = Reserva.objects.filter(status="retirada")
        if usuario is not None:
            elegiveis = elegiveis.filter(user=usuario)

        if self.instance.pk:
            elegiveis = elegiveis.filter(
                Q(avaliacao__isnull=True) | Q(pk=self.instance.reserva_id)
            )
        else:
            elegiveis = elegiveis.filter(avaliacao__isnull=True)

        # Reserva.__str__ usa o username.
        self.fields["reserva"].queryset = elegiveis.select_related("user")
