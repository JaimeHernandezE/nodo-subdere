from rest_framework import status

from apps.core.errores import ErrorNodo


class FuenteNoDisponible(Exception):
    """No se pudo leer el repositorio. El mensaje es el motivo que queda en la lectura."""


class FuenteDeNodoRetirado(ErrorNodo):
    codigo = "FUENTE_DE_NODO_RETIRADO"
    mensaje = "El nodo de esta fuente está retirado: su repositorio no se lee."
    status = status.HTTP_409_CONFLICT


class FuenteInactiva(ErrorNodo):
    codigo = "FUENTE_INACTIVA"
    mensaje = "La fuente está dada de baja. Reactivarla es un cambio de un administrador."
    status = status.HTTP_409_CONFLICT
