from django.conf import settings


class ContextoMiddleware:
    """Deja `X-Procedimiento` y `X-Id-Tramite` en la petición.

    No valida que existan: cada endpoint decide si los exige.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.procedimiento = request.headers.get("X-Procedimiento", "").strip()
        request.id_tramite = request.headers.get("X-Id-Tramite", "").strip()
        return self.get_response(request)


class RobotsMiddleware:
    """Pide a los buscadores no indexar mientras el nodo esté oculto (`NODO_OCULTO`)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.NODO_OCULTO:
            response["X-Robots-Tag"] = "noindex, nofollow"
        return response
