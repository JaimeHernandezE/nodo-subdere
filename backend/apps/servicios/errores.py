from rest_framework import status

from apps.core.errores import ErrorNodo


class ProcedimientoRequerido(ErrorNodo):
    """Consultar datos de una persona exige decir para qué trámite."""

    codigo = "PROCEDIMIENTO_REQUERIDO"
    mensaje = "La consulta exige la cabecera X-Procedimiento con el trámite que la motiva."
    status = status.HTTP_400_BAD_REQUEST
