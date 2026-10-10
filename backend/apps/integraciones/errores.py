from rest_framework import status

from apps.core.errores import ErrorNodo


class FuenteNoDisponible(ErrorNodo):
    """La fuente no respondió, o rechazó la credencial del nodo. No es culpa de quien consulta."""

    codigo = "FUENTE_NO_DISPONIBLE"
    mensaje = "La fuente de estos datos no está respondiendo. Intente más tarde."
    status = status.HTTP_503_SERVICE_UNAVAILABLE


class ParametroInvalido(ErrorNodo):
    """Se rechaza antes de llamar a la fuente. El código dice cuál parámetro."""

    codigo = "PARAMETRO_INVALIDO"
    mensaje = "El dato consultado no tiene un formato válido."
    status = status.HTTP_400_BAD_REQUEST


class NoEncontrado(ErrorNodo):
    """La fuente respondió, y no tiene ese dato. Distinto de que no responda."""

    codigo = "NO_ENCONTRADO"
    mensaje = "La fuente no tiene registro para lo consultado."
    status = status.HTTP_404_NOT_FOUND


class RespuestaDemasiadoGrande(ErrorNodo):
    codigo = "RESPUESTA_DEMASIADO_GRANDE"
    mensaje = "La fuente entregó una respuesta más grande que el límite declarado (1 MB)."
    status = status.HTTP_502_BAD_GATEWAY
