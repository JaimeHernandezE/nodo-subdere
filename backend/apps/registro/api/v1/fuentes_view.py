from django.db import transaction
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.models import Rol
from apps.cuentas.permisos import RolMinimo
from apps.registro import sincronizacion
from apps.registro.models import Fuente

from .fuente_serializer import CAMPOS_EDITABLES, FuenteSerializer
from .lectura_serializer import LecturaSerializer


def _objeto(fuente: Fuente) -> str:
    return f"registro.Fuente:{fuente.pk}"


def _direccion(fuente: Fuente) -> dict:
    return model_to_dict(fuente, CAMPOS_EDITABLES)


@extend_schema_view(
    get=extend_schema(operation_id="fuentes_listar"),
    post=extend_schema(operation_id="fuentes_registrar"),
)
class FuentesView(generics.ListCreateAPIView):
    """Las fuentes registradas. Registrar una la lee en el acto, aunque la lectura falle."""

    serializer_class = FuenteSerializer
    queryset = Fuente.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [RolMinimo(Rol.ADMINISTRADOR)()]
        return [RolMinimo(Rol.LECTOR)()]

    def perform_create(self, serializer):
        with transaction.atomic():
            fuente = serializer.save()
            registrar_bitacora(
                self.request.user,
                accion="registrar_fuente",
                objeto=_objeto(fuente),
                despues=_direccion(fuente),
            )
        sincronizacion.sincronizar(fuente, perfil=self.request.user)
        fuente.refresh_from_db()


@extend_schema_view(
    get=extend_schema(operation_id="fuentes_ver"),
    patch=extend_schema(operation_id="fuentes_modificar"),
)
class FuenteDetalleView(generics.RetrieveUpdateAPIView):
    """Cambiar la dirección es el traspaso de custodia; `activa: false`, dar de baja la fuente."""

    serializer_class = FuenteSerializer
    queryset = Fuente.objects.all()
    http_method_names = ["get", "patch", "head", "options"]

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [RolMinimo(Rol.ADMINISTRADOR)()]
        return [RolMinimo(Rol.LECTOR)()]

    def perform_update(self, serializer):
        with transaction.atomic():
            antes = _direccion(serializer.instance)
            fuente = serializer.save()
            despues = _direccion(fuente)
            if antes != despues:
                registrar_bitacora(
                    self.request.user,
                    accion="modificar_fuente",
                    objeto=_objeto(fuente),
                    antes=antes,
                    despues=despues,
                )


class SincronizarFuenteView(APIView):
    """Vuelve a leer ahora. Responde con la lectura, válida o no."""

    permission_classes = [RolMinimo(Rol.CURADOR)]

    @extend_schema(operation_id="fuentes_sincronizar", request=None, responses=LecturaSerializer)
    def post(self, request, pk):
        fuente = get_object_or_404(Fuente, pk=pk)
        lectura = sincronizacion.sincronizar(fuente, perfil=request.user)
        return Response(LecturaSerializer(lectura).data, status=status.HTTP_200_OK)


@extend_schema_view(get=extend_schema(operation_id="fuentes_lecturas"))
class LecturasView(generics.ListAPIView):
    """El historial de lecturas de una fuente, de la más reciente a la más antigua."""

    serializer_class = LecturaSerializer
    permission_classes = [RolMinimo(Rol.LECTOR)]

    def get_queryset(self):
        fuente = get_object_or_404(Fuente, pk=self.kwargs["pk"])
        return fuente.lecturas.select_related("perfil")
