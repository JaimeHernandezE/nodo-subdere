from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.models import Rol
from apps.cuentas.permisos import RolMinimo
from apps.wiki.models import Entrada, Version

from .entradas_view import entrada_o_404, html_de
from .version_serializer import VersionNuevaSerializer, VersionResumenSerializer, VersionSerializer


def _version_o_404(entrada: Entrada, version_id: int) -> Version:
    version = entrada.versiones.select_related("autor", "entrada").filter(pk=version_id).first()
    if version is None:
        raise exceptions.NotFound()
    return version


class VersionesView(APIView):
    """El historial de una entrada. Una edición es siempre una versión nueva, en borrador."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [RolMinimo(Rol.EDITOR)()]
        return [RolMinimo(Rol.LECTOR)()]

    @extend_schema(operation_id="wiki_versiones", responses=VersionResumenSerializer(many=True))
    def get(self, request, slug):
        entrada = entrada_o_404(slug, request.user)
        versiones = entrada.versiones.select_related("autor", "entrada")
        return Response(VersionResumenSerializer(versiones, many=True).data)

    @extend_schema(
        operation_id="wiki_versiones_crear",
        request=VersionNuevaSerializer,
        responses={201: VersionSerializer},
    )
    def post(self, request, slug):
        entrada = entrada_o_404(slug, request.user)
        nueva = VersionNuevaSerializer(data=request.data)
        nueva.is_valid(raise_exception=True)
        version = nueva.save(entrada=entrada, autor=request.user)
        version.html = html_de(version)
        return Response(VersionSerializer(version).data, status=status.HTTP_201_CREATED)


class VersionDetalleView(APIView):
    """Una versión con su Markdown y su HTML."""

    permission_classes = [RolMinimo(Rol.LECTOR)]

    @extend_schema(operation_id="wiki_versiones_ver", responses=VersionSerializer)
    def get(self, request, slug, version_id):
        version = _version_o_404(entrada_o_404(slug, request.user), version_id)
        version.html = html_de(version)
        return Response(VersionSerializer(version).data)


class PublicarView(APIView):
    """Marca una versión como vigente. Publicar una antigua es volver atrás."""

    permission_classes = [RolMinimo(Rol.EDITOR)]

    @extend_schema(
        operation_id="wiki_versiones_publicar", request=None, responses=VersionSerializer
    )
    def post(self, request, slug, version_id):
        with transaction.atomic():
            entrada = Entrada.objects.select_for_update().filter(slug=slug).first()
            if entrada is None:
                raise exceptions.NotFound()
            version = _version_o_404(entrada, version_id)
            anterior = entrada.vigente_id
            if anterior != version.pk:
                if not version.publicada:
                    version.publicada = True
                    version.publicada_en = timezone.now()
                    version.save()
                entrada.vigente = version
                entrada.save(update_fields=["vigente", "actualizado_en"])
                registrar_bitacora(
                    request.user,
                    accion="publicar_entrada",
                    objeto=f"wiki.Entrada:{entrada.slug}",
                    antes={"version": anterior},
                    despues={"version": version.pk},
                )
        version.entrada = entrada
        version.html = html_de(version)
        return Response(VersionSerializer(version).data)
