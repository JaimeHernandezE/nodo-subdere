"""El CUT es dato abierto: público, sin sesión y sin `Acceso`. Ver INSTRUCCIONES.md §3."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.integraciones.cut import AdaptadorCUT, Comuna, Provincia
from apps.integraciones.respuesta import Respuesta

from .cut_serializer import CutBusquedaSerializer, CutUnidadSerializer
from .respuesta_serializer import combinar, envolver

MINIMO_BUSQUEDA = 2


def _con_superiores(cut: AdaptadorCUT, respuesta: Respuesta, unidades) -> Respuesta:
    """Agrega a cada unidad los nombres de su provincia y su región, desde los listados."""
    regiones, provincias = cut.regiones(), cut.provincias()
    nombres = {u.codigo: u.nombre for u in [*regiones.datos, *provincias.datos]}

    def superior(codigo: str | None) -> dict | None:
        return None if codigo is None else {"codigo": codigo, "nombre": nombres.get(codigo, "")}

    datos = [
        {
            "nivel": u.nivel,
            "codigo": u.codigo,
            "nombre": u.nombre,
            "provincia": superior(u.provincia if isinstance(u, Comuna) else None),
            "region": superior(u.region if isinstance(u, Provincia | Comuna) else None),
        }
        for u in unidades
    ]
    return combinar(respuesta, regiones, provincias, datos=datos)


class _Publica(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]


class CutBuscarView(_Publica):
    """Busca por nombre en los tres niveles, sin tildes ni mayúsculas."""

    @extend_schema(
        operation_id="servicios_cut_buscar",
        parameters=[
            OpenApiParameter(
                "q", OpenApiTypes.STR, required=True, description="Al menos dos caracteres."
            )
        ],
        responses=CutBusquedaSerializer,
    )
    def get(self, request):
        texto = request.query_params.get("q", "").strip()
        if len(texto) < MINIMO_BUSQUEDA:
            raise exceptions.ValidationError(
                {"q": [f"Escriba al menos {MINIMO_BUSQUEDA} caracteres."]}
            )
        cut = AdaptadorCUT()
        encontradas = cut.buscar(texto)
        respuesta = _con_superiores(cut, encontradas, encontradas.datos)
        return Response(CutBusquedaSerializer(envolver(respuesta)).data)


class CutCodigoView(_Publica):
    """El camino inverso: de un código a la unidad territorial, con o sin ceros."""

    @extend_schema(operation_id="servicios_cut_codigo", responses=CutUnidadSerializer)
    def get(self, request, codigo):
        cut = AdaptadorCUT()
        unidad = cut.por_codigo(codigo)
        respuesta = _con_superiores(cut, unidad, [unidad.datos])
        return Response(CutUnidadSerializer(envolver(respuesta.con(respuesta.datos[0]))).data)
