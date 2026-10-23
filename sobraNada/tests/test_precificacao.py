from decimal import Decimal

from sobraNada.precificacao import calcular_desconto_carrinho

casos = [
    (Decimal("100.00"), Decimal("0.00"), Decimal("0.00"), Decimal("100.00")),
    (Decimal("149.99"), Decimal("0.00"), Decimal("0.00"), Decimal("149.99")),
    (Decimal("150.00"), Decimal("0.20"), Decimal("30.00"), Decimal("120.00")),
    (Decimal("249.99"), Decimal("0.20"), Decimal("50.00"), Decimal("199.99")),
    (Decimal("250.00"), Decimal("0.25"), Decimal("62.50"), Decimal("187.50")),
    (Decimal("499.99"), Decimal("0.25"), Decimal("125.00"), Decimal("374.99")),
    (Decimal("500.00"), Decimal("0.35"), Decimal("175.00"), Decimal("325.00")),
    (Decimal("501.00"), Decimal("0.35"), Decimal("175.35"), Decimal("325.65")),
]


def test_calcular_desconto_carrinho():
    for valor_bruto, percentual, valor_desconto, valor_final in casos:
        desconto = calcular_desconto_carrinho(valor_bruto)
        assert desconto.percentual == percentual
        assert desconto.valor_desconto == valor_desconto
        assert desconto.valor_final == valor_final
