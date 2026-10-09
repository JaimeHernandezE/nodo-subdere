from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics

from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.models import Perfil
from apps.cuentas.permisos import GestionaEquipo

from .serializers import PerfilSerializer, instantanea


def _objeto(perfil: Perfil) -> str:
    return f"cuentas.Perfil:{perfil.pk}"


class _PerfilesDelActor:
    def get_queryset(self):
        perfiles = Perfil.objects.select_related("municipio")
        actor = self.request.user
        if not actor.es_administrador:
            perfiles = perfiles.filter(municipio=actor.municipio_id)
        return perfiles


@extend_schema_view(
    get=extend_schema(
        operation_id="perfiles_listar",
        parameters=[
            OpenApiParameter("municipio", OpenApiTypes.STR, description="Código CUT"),
            OpenApiParameter("rol", OpenApiTypes.STR),
            OpenApiParameter("activo", OpenApiTypes.BOOL),
        ],
    ),
    post=extend_schema(operation_id="perfiles_crear"),
)
class PerfilesView(_PerfilesDelActor, generics.ListCreateAPIView):
    """Administradores: todos los perfiles. Encargados: los de su municipio."""

    serializer_class = PerfilSerializer
    permission_classes = [GestionaEquipo]

    def get_queryset(self):
        perfiles = super().get_queryset()
        parametros = self.request.query_params
        if municipio := parametros.get("municipio"):
            perfiles = perfiles.filter(municipio__cut=municipio)
        if rol := parametros.get("rol"):
            perfiles = perfiles.filter(rol=rol)
        if (activo := parametros.get("activo")) in ("true", "false"):
            perfiles = perfiles.filter(activo=activo == "true")
        return perfiles

    @transaction.atomic
    def perform_create(self, serializer):
        perfil = serializer.save()
        registrar_bitacora(
            self.request.user,
            accion="crear_perfil",
            objeto=_objeto(perfil),
            despues=instantanea(perfil),
        )


@extend_schema_view(
    get=extend_schema(operation_id="perfiles_ver"),
    patch=extend_schema(operation_id="perfiles_modificar"),
)
class PerfilDetalleView(_PerfilesDelActor, generics.RetrieveUpdateAPIView):
    """Los perfiles no se borran: se desactivan con `activo: false`."""

    serializer_class = PerfilSerializer
    permission_classes = [GestionaEquipo]
    http_method_names = ["get", "patch", "head", "options"]

    @transaction.atomic
    def perform_update(self, serializer):
        antes = instantanea(serializer.instance)
        perfil = serializer.save()
        despues = instantanea(perfil)
        if antes != despues:
            registrar_bitacora(
                self.request.user,
                accion="modificar_perfil",
                objeto=_objeto(perfil),
                antes=antes,
                despues=despues,
            )
