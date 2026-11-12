from django import template

register = template.Library()


@register.filter
def milhar(valor):
    """1234567 -> 1.234.567 (separador de milhar brasileiro)."""
    try:
        return f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return valor
