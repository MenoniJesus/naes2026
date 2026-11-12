import markdown as markdown_lib
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

TAGS_PERMITIDAS = {
    "p", "br", "hr", "strong", "em", "del", "code", "pre", "blockquote",
    "ul", "ol", "li", "h3", "h4", "h5", "h6",
    "table", "thead", "tbody", "tr", "th", "td", "a",
}
ATRIBUTOS_PERMITIDOS = {"a": {"href", "title"}}


def renderizar_markdown(texto: str) -> str:
    """Markdown -> HTML, sanitizado com nh3 (remove scripts, eventos, iframes, javascript:...)."""
    html = markdown_lib.markdown(texto or "", extensions=["fenced_code", "tables", "sane_lists"])
    return nh3.clean(
        html,
        tags=TAGS_PERMITIDAS,
        attributes=ATRIBUTOS_PERMITIDOS,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer nofollow",
    )


@register.filter(name="markdown_seguro")
def markdown_seguro(texto):
    return mark_safe(renderizar_markdown(texto))
