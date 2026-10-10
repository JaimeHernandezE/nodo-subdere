from rest_framework import status

from apps.core.errores import ErrorNodo


class VersionInmutable(ErrorNodo):
    """Una versión no se corrige ni se borra: una corrección es una versión nueva."""

    codigo = "VERSION_INMUTABLE"
    mensaje = "Una versión no se modifica ni se borra: una corrección es una versión nueva."
    status = status.HTTP_409_CONFLICT
