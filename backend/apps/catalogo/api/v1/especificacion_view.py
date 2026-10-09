from pathlib import PurePosixPath

from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogo.models import Especificacion
from apps.cuentas.autenticacion import AutenticacionOpcional

from .especificacion_serializer import EspecificacionSerializer
from .nodos_view import resolver_nodo


def _vigente(request, identificador: str) -> Especificacion:
    especificacion = resolver_nodo(identificador, request.user).especificacion_vigente
    if especificacion is None:
        raise exceptions.NotFound()
    return especificacion


def _tipo_de_contenido(ruta: str) -> str:
    if PurePosixPath(ruta).suffix.lower() == ".json":
        return "application/json; charset=utf-8"
    return "application/yaml; charset=utf-8"


class EspecificacionView(APIView):
    """La especificación vigente del nodo, con las mismas reglas de visibilidad que el nodo."""

    authentication_classes = [AutenticacionOpcional]
    permission_classes = [AllowAny]

    @extend_schema(operation_id="nodos_especificacion", responses=EspecificacionSerializer)
    def get(self, request, identificador):
        especificacion = _vigente(request, identificador)
        return Response(EspecificacionSerializer(especificacion, context={"request": request}).data)


class EspecificacionArchivoView(APIView):
    """El archivo tal como se leyó del repositorio, byte por byte."""

    authentication_classes = [AutenticacionOpcional]
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def perform_content_negotiation(self, request, force=False):
        # La respuesta buena no pasa por un renderer; los errores van siempre en JSON,
        # aunque la petición pida YAML.
        return super().perform_content_negotiation(request, force=True)

    @extend_schema(
        operation_id="nodos_especificacion_archivo",
        responses={
            (200, "application/yaml"): OpenApiResponse(OpenApiTypes.STR),
            (200, "application/json"): OpenApiResponse(OpenApiTypes.STR),
        },
    )
    def get(self, request, identificador):
        especificacion = _vigente(request, identificador)
        if not especificacion.tiene_archivo:
            raise exceptions.NotFound()
        respuesta = HttpResponse(
            especificacion.contenido.encode("utf-8"),
            content_type=_tipo_de_contenido(especificacion.ruta),
        )
        respuesta["ETag"] = f'"{especificacion.huella}"'
        nombre = PurePosixPath(especificacion.ruta).name
        respuesta["Content-Disposition"] = f'inline; filename="{nombre}"'
        return respuesta
