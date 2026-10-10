import functools

from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import exceptions, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalogo.models import Nodo, Visibilidad
from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.autenticacion import AutenticacionOpcional
from apps.cuentas.models import Rol
from apps.cuentas.permisos import RolMinimo
from apps.wiki.markdown import renderizar
from apps.wiki.models import CAMPOS_EDITABLES, ORDEN_DE_SECCIONES, Entrada, Version

from .entrada_serializer import (
    EntradaEditorialSerializer,
    EntradaNuevaSerializer,
    EntradaResumenSerializer,
    EntradaSerializer,
    identificador_vigente,
)

ESTADOS = {"publicadas", "todas"}


@functools.lru_cache(maxsize=256)
def _html(version_id: int, markdown: str) -> str:
    """Una versión no cambia: su HTML se puede recordar. Nunca se guarda en la base."""
    return renderizar(markdown)


def html_de(version: Version) -> str:
    return _html(version.pk, version.markdown)


def _nodos_ocultos() -> set[str]:
    return set(
        Nodo.objects.filter(visibilidad=Visibilidad.OCULTO).values_list("identificador", flat=True)
    )


def oculta(entrada: Entrada, perfil) -> bool:
    """La entrada de un nodo oculto se ve solo con sesión, como el nodo."""
    if perfil is not None or not entrada.nodo:
        return False
    return Nodo.objects.filter(identificador=entrada.nodo, visibilidad=Visibilidad.OCULTO).exists()


def entrada_o_404(slug: str, perfil) -> Entrada:
    entrada = Entrada.objects.select_related("vigente").filter(slug=slug).first()
    if entrada is None or oculta(entrada, perfil):
        raise exceptions.NotFound()
    return entrada


def _orden(entrada: Entrada):
    return (ORDEN_DE_SECCIONES.get(entrada.seccion, 99), entrada.orden, entrada.titulo)


def _editables(entrada: Entrada) -> dict:
    return {campo: getattr(entrada, campo) for campo in CAMPOS_EDITABLES}


def _objeto(entrada: Entrada) -> str:
    return f"wiki.Entrada:{entrada.slug}"


class _ConEditor:
    authentication_classes = [AutenticacionOpcional]

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]
        return [RolMinimo(Rol.EDITOR)()]


@extend_schema_view(
    get=extend_schema(
        operation_id="wiki_listar",
        parameters=[
            OpenApiParameter(
                "nodo", OpenApiTypes.STR, description="Identificador o alias del nodo."
            ),
            OpenApiParameter(
                "estado",
                OpenApiTypes.STR,
                enum=sorted(ESTADOS),
                description="`todas` exige sesión e incluye las entradas sin publicar.",
            ),
        ],
    ),
    post=extend_schema(
        operation_id="wiki_crear",
        request=EntradaNuevaSerializer,
        responses={201: EntradaResumenSerializer},
    ),
)
class EntradasView(_ConEditor, generics.ListAPIView):
    """El índice de la wiki, por sección y orden. Sin sesión, solo lo publicado."""

    serializer_class = EntradaResumenSerializer
    pagination_class = None

    def get_queryset(self):
        parametros = self.request.query_params
        entradas = Entrada.objects.select_related("vigente")

        estado = parametros.get("estado", "publicadas")
        if estado not in ESTADOS:
            opciones = ", ".join(sorted(ESTADOS))
            raise exceptions.ValidationError({"estado": [f"Debe ser uno de: {opciones}."]})
        if estado == "todas" and self.request.user is None:
            raise exceptions.NotAuthenticated()
        if estado == "publicadas":
            entradas = entradas.filter(vigente__publicada=True)

        if nodo := parametros.get("nodo"):
            entradas = entradas.filter(nodo=identificador_vigente(nodo))
        if self.request.user is None:
            entradas = entradas.exclude(nodo__in=_nodos_ocultos())
        return sorted(entradas, key=_orden)

    def post(self, request):
        nueva = EntradaNuevaSerializer(data=request.data)
        nueva.is_valid(raise_exception=True)
        with transaction.atomic():
            entrada = nueva.save()
            registrar_bitacora(
                request.user,
                accion="crear_entrada",
                objeto=_objeto(entrada),
                despues=_editables(entrada),
            )
        return Response(EntradaResumenSerializer(entrada).data, status=status.HTTP_201_CREATED)


class EntradaDetalleView(_ConEditor, APIView):
    """Una entrada con su versión vigente. Sin versión publicada, 404."""

    @extend_schema(operation_id="wiki_ver", responses=EntradaSerializer)
    def get(self, request, slug):
        entrada = entrada_o_404(slug, request.user)
        if entrada.vigente is None or not entrada.vigente.publicada:
            raise exceptions.NotFound()
        entrada.html = html_de(entrada.vigente)
        return Response(EntradaSerializer(entrada).data)

    @extend_schema(
        operation_id="wiki_editar",
        request=EntradaEditorialSerializer,
        responses=EntradaResumenSerializer,
    )
    def patch(self, request, slug):
        if not isinstance(request.data, dict):
            raise exceptions.ValidationError({"cuerpo": ["Debe ser un objeto."]})
        if "slug" in request.data:
            raise exceptions.ValidationError({"slug": ["No cambia: otro slug es otra entrada."]})
        if desconocidos := sorted(set(request.data) - set(CAMPOS_EDITABLES)):
            raise exceptions.ValidationError({c: ["El campo no existe."] for c in desconocidos})

        with transaction.atomic():
            entrada = entrada_o_404(slug, request.user)
            editorial = EntradaEditorialSerializer(entrada, data=request.data, partial=True)
            editorial.is_valid(raise_exception=True)
            antes = _editables(entrada)
            editorial.save()
            despues = _editables(entrada)
            if antes != despues:
                registrar_bitacora(
                    request.user,
                    accion="editar_entrada",
                    objeto=_objeto(entrada),
                    antes=antes,
                    despues=despues,
                )
        return Response(EntradaResumenSerializer(entrada).data)
