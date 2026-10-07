"""El sobre único de errores de la API (INSTRUCCIONES.md §6).

    {"error": {"codigo": "PATENTE_INVALIDA", "mensaje": "...", "detalles": []}}

Es el único lugar que conoce ese formato: si el de PISEE llega a ser otro (X-121),
cambiarlo es este módulo.
"""

import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404, JsonResponse
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import set_rollback

logger = logging.getLogger(__name__)

MENSAJE_INTERNO = "Ocurrió un error interno. Quedó registrado para revisión."


class ErrorNodo(Exception):
    """Base de las excepciones propias. Las demás aplicaciones heredan de acá."""

    codigo = "ERROR"
    mensaje = "No se pudo completar la solicitud."
    status = status.HTTP_400_BAD_REQUEST

    def __init__(self, mensaje=None, *, codigo=None, status=None, detalles=None):
        self.mensaje = mensaje or self.mensaje
        self.codigo = codigo or self.codigo
        self.status = status or self.status
        self.detalles = detalles or []
        super().__init__(self.mensaje)


# Orden importa: subclases antes que sus bases.
_TRADUCCIONES = [
    (exceptions.ValidationError, "VALIDACION_FALLIDA", "Los datos enviados no son válidos."),
    (exceptions.ParseError, "CUERPO_INVALIDO", "El cuerpo de la petición no se pudo leer."),
    (exceptions.AuthenticationFailed, "NO_AUTENTICADO", "Las credenciales no son válidas."),
    (exceptions.NotAuthenticated, "NO_AUTENTICADO", "Esta operación requiere autenticarse."),
    (exceptions.PermissionDenied, "PERMISO_DENEGADO", "No tiene permiso para esta operación."),
    (exceptions.NotFound, "NO_ENCONTRADO", "El recurso no existe."),
    (exceptions.MethodNotAllowed, "METODO_NO_PERMITIDO", "Método no permitido en esta ruta."),
    (exceptions.NotAcceptable, "FORMATO_NO_ACEPTABLE", "No se puede responder en ese formato."),
    (exceptions.UnsupportedMediaType, "TIPO_NO_SOPORTADO", "Tipo de contenido no soportado."),
    (exceptions.Throttled, "DEMASIADAS_PETICIONES", "Demasiadas peticiones. Intente más tarde."),
]


def sobre(codigo: str, mensaje: str, detalles: list | None = None) -> dict:
    return {"error": {"codigo": codigo, "mensaje": mensaje, "detalles": detalles or []}}


def _aplanar(detalle, campo: str | None = None) -> list[dict]:
    """Convierte el detalle anidado de DRF en una lista de {campo, mensaje}."""
    if isinstance(detalle, dict):
        resultado = []
        for clave, valor in detalle.items():
            nombre = clave if campo is None else f"{campo}.{clave}"
            resultado.extend(_aplanar(valor, nombre))
        return resultado
    if isinstance(detalle, list):
        resultado = []
        for indice, valor in enumerate(detalle):
            anidado = isinstance(valor, dict | list)
            nombre = f"{campo}[{indice}]" if anidado and campo else campo
            resultado.extend(_aplanar(valor, nombre))
        return resultado
    return [{"campo": campo, "mensaje": str(detalle)}]


def _cabeceras(exc: exceptions.APIException) -> dict:
    cabeceras = {}
    if getattr(exc, "auth_header", None):
        cabeceras["WWW-Authenticate"] = exc.auth_header
    if getattr(exc, "wait", None):
        cabeceras["Retry-After"] = str(int(exc.wait))
    return cabeceras


def manejador_de_excepciones(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, ErrorNodo):
        set_rollback()
        return Response(sobre(exc.codigo, exc.mensaje, exc.detalles), status=exc.status)

    if isinstance(exc, exceptions.APIException):
        set_rollback()
        codigo, mensaje = next(
            (
                (codigo, mensaje)
                for clase, codigo, mensaje in _TRADUCCIONES
                if isinstance(exc, clase)
            ),
            ("ERROR_DE_PETICION", "No se pudo completar la solicitud."),
        )

        detalles = _aplanar(exc.detail) if isinstance(exc, exceptions.ValidationError) else []
        return Response(
            sobre(codigo, mensaje, detalles), status=exc.status_code, headers=_cabeceras(exc)
        )

    vista = context.get("view")
    logger.exception("Excepción no prevista en %s", type(vista).__name__ if vista else "?")
    set_rollback()
    return Response(
        sobre("ERROR_INTERNO", MENSAJE_INTERNO), status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def vista_404(request, exception=None):
    return JsonResponse(
        sobre("NO_ENCONTRADO", "La ruta no existe."), status=status.HTTP_404_NOT_FOUND
    )


def vista_500(request):
    return JsonResponse(
        sobre("ERROR_INTERNO", MENSAJE_INTERNO), status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
