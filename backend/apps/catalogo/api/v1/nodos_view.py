from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import exceptions, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogo.errores import CampoDeFicha, NodoRetirado
from apps.catalogo.models import CAMPOS_EDITORIALES, Alias, Nodo, Visibilidad
from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.autenticacion import AutenticacionOpcional
from apps.cuentas.models import Rol
from apps.cuentas.permisos import RolMinimo

from .nodo_serializer import (
    CAMPOS_DE_FICHA_EN_LA_RESPUESTA,
    NodoEditorialSerializer,
    NodoResumenSerializer,
    NodoSerializer,
)

FILTROS = {
    "ambito": "ambito__nombre",
    "clase": "clase",
    "madurez": "madurez",
    "intercambio": "intercambio",
}
VISIBILIDADES_CON_SESION = {"todas", *Visibilidad.values}


def resolver_nodo(identificador: str, perfil, *, admitir_retirado: bool = False) -> Nodo:
    """El nodo por su identificador o por un alias, con las reglas de visibilidad.

    Sin sesión, un oculto es un 404 igual que uno que no existe: no se confirma que esté.
    """
    nodos = Nodo.objects.select_related("ambito")
    nodo = nodos.filter(identificador=identificador).first()
    if nodo is None:
        destino = Alias.objects.filter(identificador=identificador).values_list(
            "destino", flat=True
        )
        nodo = nodos.filter(identificador__in=destino).first()
    if nodo is None:
        raise exceptions.NotFound()
    if nodo.visibilidad == Visibilidad.OCULTO and perfil is None:
        raise exceptions.NotFound()
    if nodo.visibilidad == Visibilidad.RETIRADO and not admitir_retirado:
        raise NodoRetirado(detalles=[{"campo": "leido_en", "valor": nodo.leido_en.isoformat()}])
    return nodo


def _editorial(nodo: Nodo) -> dict:
    return {campo: getattr(nodo, campo) for campo in CAMPOS_EDITORIALES}


@extend_schema_view(
    get=extend_schema(
        operation_id="nodos_listar",
        parameters=[
            OpenApiParameter("ambito", OpenApiTypes.STR, description="Nombre del ámbito"),
            OpenApiParameter("clase", OpenApiTypes.STR),
            OpenApiParameter("madurez", OpenApiTypes.STR),
            OpenApiParameter("intercambio", OpenApiTypes.STR),
            OpenApiParameter(
                "visibilidad",
                OpenApiTypes.STR,
                enum=sorted(VISIBILIDADES_CON_SESION),
                description="Exige sesión. Sin el parámetro, solo los publicados.",
            ),
        ],
    )
)
class NodosView(generics.ListAPIView):
    """El catálogo. Sin sesión, solo lo publicado."""

    serializer_class = NodoResumenSerializer
    authentication_classes = [AutenticacionOpcional]
    permission_classes = [AllowAny]

    def get_queryset(self):
        parametros = self.request.query_params
        nodos = Nodo.objects.select_related("ambito")

        visibilidad = parametros.get("visibilidad")
        if visibilidad is None:
            nodos = nodos.publicados()
        elif self.request.user is None:
            raise exceptions.NotAuthenticated()
        elif visibilidad not in VISIBILIDADES_CON_SESION:
            opciones = ", ".join(sorted(VISIBILIDADES_CON_SESION))
            raise exceptions.ValidationError({"visibilidad": [f"Debe ser una de: {opciones}."]})
        elif visibilidad != "todas":
            nodos = nodos.filter(visibilidad=visibilidad)

        for parametro, campo in FILTROS.items():
            if valor := parametros.get(parametro):
                nodos = nodos.filter(**{campo: valor})
        return nodos


class NodoDetalleView(APIView):
    """La ficha de un nodo. La lee cualquiera si está publicado; la edita un curador."""

    authentication_classes = [AutenticacionOpcional]

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [RolMinimo(Rol.CURADOR)()]
        return [AllowAny()]

    @extend_schema(operation_id="nodos_ver", responses=NodoSerializer)
    def get(self, request, identificador):
        nodo = resolver_nodo(identificador, request.user)
        return Response(NodoSerializer(nodo, context={"request": request}).data)

    @extend_schema(
        operation_id="nodos_editar", request=NodoEditorialSerializer, responses=NodoSerializer
    )
    def patch(self, request, identificador):
        if not isinstance(request.data, dict):
            raise exceptions.ValidationError({"cuerpo": ["Debe ser un objeto."]})
        if de_ficha := sorted(set(request.data) & CAMPOS_DE_FICHA_EN_LA_RESPUESTA):
            raise CampoDeFicha(
                detalles=[
                    {"campo": c, "mensaje": "Viene de la ficha del servicio."} for c in de_ficha
                ]
            )
        if desconocidos := sorted(set(request.data) - set(CAMPOS_EDITORIALES)):
            raise exceptions.ValidationError({c: ["El campo no existe."] for c in desconocidos})

        with transaction.atomic():
            nodo = resolver_nodo(identificador, request.user, admitir_retirado=True)
            editorial = NodoEditorialSerializer(nodo, data=request.data, partial=True)
            editorial.is_valid(raise_exception=True)
            antes = _editorial(nodo)
            editorial.save()
            despues = _editorial(nodo)
            if antes != despues:
                registrar_bitacora(
                    request.user,
                    accion="editar_nodo",
                    objeto=f"catalogo.Nodo:{nodo.identificador}",
                    antes=antes,
                    despues=despues,
                )
        return Response(NodoSerializer(nodo, context={"request": request}).data)
