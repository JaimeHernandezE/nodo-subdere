from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Municipio
from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.models import Perfil, Rol
from apps.cuentas.permisos import RolMinimo, VeEquipo

from .serializers import DesignarEncargadoSerializer, IntegranteSerializer, PerfilSerializer


class EquipoView(APIView):
    """El equipo de un municipio. El RUN, solo para quien lo administra."""

    permission_classes = [VeEquipo]

    @extend_schema(operation_id="municipios_equipo", responses=IntegranteSerializer(many=True))
    def get(self, request, cut):
        municipio = get_object_or_404(Municipio, cut=cut)
        integrantes = municipio.perfiles.order_by("-es_encargado", "nombre")
        contexto = {"request": request}
        return Response(IntegranteSerializer(integrantes, many=True, context=contexto).data)


class EncargadoView(APIView):
    """Designa o reemplaza al encargado. El anterior queda como perfil común de su municipio."""

    permission_classes = [RolMinimo(Rol.ADMINISTRADOR)]

    @extend_schema(
        operation_id="municipios_designar_encargado",
        request=DesignarEncargadoSerializer,
        responses=PerfilSerializer,
    )
    def put(self, request, cut):
        entrada = DesignarEncargadoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)

        with transaction.atomic():
            municipio = get_object_or_404(Municipio.objects.select_for_update(), cut=cut)
            nuevo = Perfil.objects.filter(
                pk=entrada.validated_data["perfil"], municipio=municipio, activo=True
            ).first()
            if nuevo is None:
                raise serializers.ValidationError(
                    {"perfil": ["Debe ser un perfil activo de este municipio."]}
                )

            anterior = Perfil.objects.filter(municipio=municipio, es_encargado=True).first()
            if anterior != nuevo:
                if anterior is not None:
                    anterior.es_encargado = False
                    anterior.save(update_fields=["es_encargado", "actualizado_en"])
                nuevo.es_encargado = True
                nuevo.save(update_fields=["es_encargado", "actualizado_en"])
                registrar_bitacora(
                    request.user,
                    accion="designar_encargado",
                    objeto=f"core.Municipio:{municipio.cut}",
                    antes={"encargado": anterior.run if anterior else None},
                    despues={"encargado": nuevo.run},
                )

        return Response(PerfilSerializer(nuevo, context={"request": request}).data)
