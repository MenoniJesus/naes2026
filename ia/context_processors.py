from django.utils.functional import SimpleLazyObject

from .permissoes import eh_admin


def ia(request):
    # Lazy: a query de grupos só roda se o template usar a variável.
    return {'usuario_admin': SimpleLazyObject(lambda: eh_admin(request.user))}
