from rest_framework import exceptions, status

from apps.core.errores import ErrorNodo


# Estas dos se lanzan durante la autenticación. Heredan además de la excepción de DRF
# para que la petición quede marcada como no autenticada y nada vuelva a autenticarla
# al armar la respuesta.
class SinPerfil(ErrorNodo, exceptions.PermissionDenied):
    codigo = "SIN_PERFIL"
    mensaje = "Se autenticó correctamente, pero no tiene un perfil activo en el nodo."
    status = status_code = status.HTTP_403_FORBIDDEN


class RealmNoDisponible(ErrorNodo, exceptions.APIException):
    codigo = "REALM_NO_DISPONIBLE"
    mensaje = "No se pudo verificar la identidad: el servicio de autenticación no responde."
    status = status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class PerfilExistente(ErrorNodo):
    codigo = "PERFIL_EXISTENTE"
    mensaje = "Ya existe un perfil para ese RUN. Moverlo de municipio lo hace un administrador."
    status = status.HTTP_409_CONFLICT
