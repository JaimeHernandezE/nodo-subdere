"""Permisos de circulación por patente: datos de una persona. Ver INSTRUCCIONES.md §3.

El `Acceso` lo escribe el adaptador; esta vista arma el `Contexto` y revisa lo que se
puede revisar antes de llamarlo, para que una consulta mal hecha no deje acceso.
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cuentas.models import Acceso, Rol
from apps.cuentas.permisos import RolMinimo
from apps.integraciones import patente as patentes
from apps.integraciones.permisos import ANIO_MINIMO, AdaptadorPermisos, Contexto
from apps.servicios.errores import ProcedimientoRequerido

from .permisos_serializer import PermisosRespuestaSerializer
from .respuesta_serializer import combinar, envolver


def _desde_anio(texto: str | None) -> int | None:
    if texto is None or texto == "":
        return None
    try:
        anio = int(texto)
    except ValueError:
        raise exceptions.ValidationError({"desde_anio": ["Debe ser un año."]}) from None
    if anio < ANIO_MINIMO:
        raise exceptions.ValidationError(
            {"desde_anio": [f"No puede ser anterior a {ANIO_MINIMO}."]}
        )
    return anio


class PermisosView(APIView):
    """El vehículo y sus permisos; una patente `PR` y cuatro dígitos, sus provisionales."""

    permission_classes = [RolMinimo(Rol.LECTOR)]

    @extend_schema(
        operation_id="servicios_permisos",
        parameters=[
            OpenApiParameter(
                "X-Procedimiento",
                OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description="El trámite que motiva la consulta. Queda en el registro de accesos.",
            ),
            OpenApiParameter("X-Id-Tramite", OpenApiTypes.STR, location=OpenApiParameter.HEADER),
            OpenApiParameter(
                "desde_anio",
                OpenApiTypes.INT,
                description="Solo para una patente definitiva.",
            ),
        ],
        responses=PermisosRespuestaSerializer,
    )
    def get(self, request, patente):
        if not getattr(request, "procedimiento", ""):
            raise ProcedimientoRequerido()
        desde_anio = _desde_anio(request.query_params.get("desde_anio"))
        contexto = Contexto(perfil=request.user, canal=Acceso.Canal.PANTALLA, request=request)
        adaptador = AdaptadorPermisos()

        if patentes.es_provisoria(patente):
            provisionales = adaptador.provisionales(patente, contexto)
            respuesta = provisionales.con(
                {"tipo": "provisoria", "provisionales": provisionales.datos}
            )
        else:
            patente = patentes.validar(patente)
            vehiculo = adaptador.vehiculo(patente, contexto)
            permisos = adaptador.permisos(patente, contexto, desde_anio=desde_anio)
            respuesta = combinar(
                vehiculo,
                permisos,
                datos={
                    "tipo": "definitiva",
                    "vehiculo": vehiculo.datos,
                    "permisos": permisos.datos,
                },
            )

        return Response(PermisosRespuestaSerializer(envolver(respuesta)).data)
