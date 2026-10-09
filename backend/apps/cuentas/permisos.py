"""Permisos por rol. Las vistas los declaran; ninguna decide con `if` sobre el rol."""

from functools import cache

from rest_framework.permissions import BasePermission

from .models import Perfil


def _perfil(request) -> Perfil | None:
    usuario = getattr(request, "user", None)
    return usuario if isinstance(usuario, Perfil) else None


@cache
def RolMinimo(rol: str) -> type[BasePermission]:  # noqa: N802
    """Permiso que exige al menos `rol`. Uso: `permission_classes = [RolMinimo(Rol.CURADOR)]`."""

    class _RolMinimo(BasePermission):
        def has_permission(self, request, view):
            perfil = _perfil(request)
            return perfil is not None and perfil.rol_al_menos(rol)

    _RolMinimo.__name__ = f"RolMinimo_{rol}"
    return _RolMinimo


class GestionaEquipo(BasePermission):
    """Administradores en cualquier municipio; el encargado, solo en el suyo y no sobre sí mismo."""

    def has_permission(self, request, view):
        perfil = _perfil(request)
        return perfil is not None and (perfil.es_administrador or perfil.es_encargado)

    def has_object_permission(self, request, view, obj):
        perfil = _perfil(request)
        if perfil.es_administrador:
            return True
        return obj.municipio_id == perfil.municipio_id and obj.pk != perfil.pk


class VeEquipo(BasePermission):
    """Cualquier perfil de SUBDERE ve todos los equipos; uno municipal, solo el suyo."""

    def has_permission(self, request, view):
        perfil = _perfil(request)
        if perfil is None:
            return False
        if perfil.municipio_id is None:
            return True
        return perfil.municipio.cut == view.kwargs.get("cut")


def puede_ver_run(perfil: Perfil, municipio_id: int | None) -> bool:
    """El RUN de un integrante lo ven solo quienes administran ese equipo."""
    if perfil.es_administrador:
        return True
    return perfil.es_encargado and perfil.municipio_id == municipio_id
