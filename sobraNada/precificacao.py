"""Desconto por faixa de valor da reserva.

Este modulo nao depende do Django: recebe e devolve apenas tipos primitivos,
para que a regra possa ser exercitada isoladamente.

Faixas sobre o valor total da reserva (preco da sacola x quantidade):

    ate R$ 100,00           ->   0%
    R$ 100,01 a R$ 250,00   ->  10%
    R$ 250,01 a R$ 500,00   ->  20%
    R$ 500,01 a R$ 1.000,00 ->  25%
    acima de R$ 1.000,00    ->  30%
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENTAVOS = Decimal("0.01")


@dataclass(frozen=True)
class Desconto:
    valor_bruto: Decimal
    percentual: Decimal
    valor_desconto: Decimal
    valor_final: Decimal
    preco_unitario: Decimal

    @property
    def percentual_exibicao(self) -> Decimal:
        """Percentual em base 100, pronto para a tela (ex.: 20.00)."""
        return arredondar(self.percentual * 100)

    @property
    def tem_desconto(self) -> bool:
        return self.percentual > 0


def arredondar(valor) -> Decimal:
    return Decimal(valor).quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def percentual_por_valor(valor) -> Decimal:
    valor = Decimal(valor)
    if valor <= Decimal("100.00"):
        return Decimal("0.00")
    if valor <= Decimal("250.00"):
        return Decimal("0.10")
    if valor <= Decimal("500.00"):
        return Decimal("0.20")
    if valor <= Decimal("1000.00"):
        return Decimal("0.25")
    return Decimal("0.30")


def calcular_desconto(*, preco_venda, quantidade: int) -> Desconto:
    """Aplica a faixa de desconto sobre o total da reserva.

    Levanta ValueError quando o preco ou a quantidade sao invalidos.
    """
    preco_venda = Decimal(preco_venda)

    if preco_venda <= 0:
        raise ValueError("O preço de venda deve ser maior que zero.")
    if quantidade < 1:
        raise ValueError("A quantidade mínima por reserva é 1 sacola.")

    valor_bruto = arredondar(preco_venda * quantidade)
    percentual = percentual_por_valor(valor_bruto)
    valor_desconto = arredondar(valor_bruto * percentual)
    valor_final = valor_bruto - valor_desconto

    return Desconto(
        valor_bruto=valor_bruto,
        percentual=percentual,
        valor_desconto=valor_desconto,
        valor_final=valor_final,
        preco_unitario=arredondar(valor_final / quantidade),
    )


# Desconto por faixa de valor do carrinho de produtos.
#
# Faixas sobre o valor total do carrinho (soma de preco x quantidade de cada item):
#
#     ate R$ 149,99           ->   0%
#     R$ 150,00 a R$ 249,99   ->  20%
#     R$ 250,00 a R$ 499,99   ->  25%
#     a partir de R$ 500,00   ->  35%

FAIXAS_CARRINHO = (
    (Decimal("500.00"), Decimal("0.35")),
    (Decimal("250.00"), Decimal("0.25")),
    (Decimal("150.00"), Decimal("0.20")),
)


@dataclass(frozen=True)
class DescontoCarrinho:
    valor_bruto: Decimal
    percentual: Decimal
    valor_desconto: Decimal
    valor_final: Decimal

    @property
    def percentual_exibicao(self) -> Decimal:
        """Percentual em base 100, pronto para a tela (ex.: 20.00)."""
        return arredondar(self.percentual * 100)

    @property
    def tem_desconto(self) -> bool:
        return self.percentual > 0


def percentual_por_valor_carrinho(valor) -> Decimal:
    valor = Decimal(valor)
    for minimo, percentual in FAIXAS_CARRINHO:
        if valor >= minimo:
            return percentual
    return Decimal("0.00")


def calcular_desconto_carrinho(valor_bruto) -> DescontoCarrinho:
    valor_bruto = arredondar(valor_bruto)
    percentual = percentual_por_valor_carrinho(valor_bruto)
    valor_desconto = arredondar(valor_bruto * percentual)
    valor_final = valor_bruto - valor_desconto

    return DescontoCarrinho(
        valor_bruto=valor_bruto,
        percentual=percentual,
        valor_desconto=valor_desconto,
        valor_final=valor_final,
    )
