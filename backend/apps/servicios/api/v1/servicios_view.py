from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import exceptions, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogo.api.v1.nodos_view import resolver_nodo
from apps.catalogo.models import Visibilidad
from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.autenticacion import AutenticacionOpcional
from apps.cuentas.models import Rol
from apps.cuentas.permisos import RolMinimo
from apps.servicios.models import CAMPOS_EDITABLES, Servicio

from .servicio_serializer import (
    ServicioEditorialSerializer,
    ServicioNuevoSerializer,
    ServicioSerializer,
)

INMUTABLES = ("slug", "nodo")


def _editables(servicio: Servicio) -> dict:
    return {campo: getattr(servicio, campo) for campo in CAMPOS_EDITABLES}


def _objeto(servicio: Servicio) -> str:
    return f"servicios.Servicio:{servicio.slug}"


class _ConCurador:
    authentication_classes = [AutenticacionOpcional]

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]
        return [RolMinimo(Rol.CURADOR)()]


@extend_schema_view(
    get=extend_schema(
        operation_id="servicios_listar",
        parameters=[
            OpenApiParameter(
                "nodo",
                OpenApiTypes.STR,
                description="Identificador o alias del nodo. Un oculto exige sesión.",
            ),
        ],
    ),
    post=extend_schema(
        operation_id="servicios_crear",
        request=ServicioNuevoSerializer,
        responses={201: ServicioSerializer},
    ),
)
class ServiciosView(_ConCurador, generics.ListAPIView):
    """Los servicios de nodos publicados, o los de un nodo. Los crea un curador."""

    serializer_class = ServicioSerializer

    def get_queryset(self):
        servicios = Servicio.objects.select_related("nodo")
        identificador = self.request.query_params.get("nodo")
        if identificador is None:
            return servicios.filter(nodo__visibilidad=Visibilidad.PUBLICADO)
        try:
            nodo = resolver_nodo(identificador, self.request.user, admitir_retirado=True)
        except exceptions.NotFound:
            return servicios.none()
        if nodo.visibilidad == Visibilidad.RETIRADO:
            return servicios.none()
        return servicios.filter(nodo=nodo)

    def post(self, request):
        nuevo = ServicioNuevoSerializer(data=request.data)
        nuevo.is_valid(raise_exception=True)
        with transaction.atomic():
            servicio = nuevo.save()
            registrar_bitacora(
                request.user,
                accion="crear_servicio",
                objeto=_objeto(servicio),
                despues={"nodo": servicio.nodo.identificador, **_editables(servicio)},
            )
        return Response(ServicioSerializer(servicio).data, status=status.HTTP_201_CREATED)


class ServicioDetalleView(_ConCurador, APIView):
    """Un servicio. Si su nodo no está publicado, solo con sesión."""

    def _servicio(self, slug: str) -> Servicio:
        servicio = Servicio.objects.select_related("nodo").filter(slug=slug).first()
        if servicio is None:
            raise exceptions.NotFound()
        if servicio.nodo.visibilidad != Visibilidad.PUBLICADO and self.request.user is None:
            raise exceptions.NotFound()
        return servicio

    @extend_schema(operation_id="servicios_ver", responses=ServicioSerializer)
    def get(self, request, slug):
        return Response(ServicioSerializer(self._servicio(slug)).data)

    @extend_schema(
        operation_id="servicios_editar",
        request=ServicioEditorialSerializer,
        responses=ServicioSerializer,
    )
    def patch(self, request, slug):
        if not isinstance(request.data, dict):
            raise exceptions.ValidationError({"cuerpo": ["Debe ser un objeto."]})
        if inmutables := sorted(set(request.data) & set(INMUTABLES)):
            raise exceptions.ValidationError(
                {c: ["No cambia: otro nodo o slug es otro servicio."] for c in inmutables}
            )
        if desconocidos := sorted(set(request.data) - set(CAMPOS_EDITABLES)):
            raise exceptions.ValidationError({c: ["El campo no existe."] for c in desconocidos})

        with transaction.atomic():
            servicio = self._servicio(slug)
            editorial = ServicioEditorialSerializer(servicio, data=request.data, partial=True)
            editorial.is_valid(raise_exception=True)
            antes = _editables(servicio)
            editorial.save()
            despues = _editables(servicio)
            if antes != despues:
                registrar_bitacora(
                    request.user,
                    accion="editar_servicio",
                    objeto=_objeto(servicio),
                    antes=antes,
                    despues=despues,
                )
        return Response(ServicioSerializer(servicio).data)
