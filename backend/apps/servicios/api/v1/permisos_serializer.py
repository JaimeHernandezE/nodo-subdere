from rest_framework import serializers

from .respuesta_serializer import sobre


class VehiculoSerializer(serializers.Serializer):
    patente = serializers.CharField()
    marca = serializers.CharField()
    modelo = serializers.CharField()
    anio_fabricacion = serializers.IntegerField()
    color = serializers.CharField()
    tipo = serializers.CharField()


class ComunaDelPermisoSerializer(serializers.Serializer):
    cut = serializers.CharField()
    nombre = serializers.CharField()


class CuotaSerializer(serializers.Serializer):
    numero = serializers.IntegerField()
    monto = serializers.IntegerField()
    fecha_pago = serializers.DateField()
    medio_pago = serializers.CharField()


class PermisoSerializer(serializers.Serializer):
    anio = serializers.IntegerField()
    estado = serializers.CharField()
    comuna = ComunaDelPermisoSerializer()
    monto_total = serializers.IntegerField()
    vigente_hasta = serializers.DateField(allow_null=True)
    cuotas = CuotaSerializer(many=True)


class TitularEmpresaSerializer(serializers.Serializer):
    rut = serializers.CharField()
    razon_social = serializers.CharField()


class PermisoProvisionalSerializer(serializers.Serializer):
    anio = serializers.IntegerField()
    semestre = serializers.IntegerField()
    comuna = ComunaDelPermisoSerializer()
    titular = TitularEmpresaSerializer()
    marca = serializers.CharField()
    modelo = serializers.CharField()


class ConsultaPermisosSerializer(serializers.Serializer):
    """`definitiva` trae el vehículo y sus permisos; `provisoria`, los provisionales."""

    tipo = serializers.ChoiceField(choices=["definitiva", "provisoria"])
    vehiculo = VehiculoSerializer(required=False)
    permisos = PermisoSerializer(many=True, required=False)
    provisionales = PermisoProvisionalSerializer(many=True, required=False)


PermisosRespuestaSerializer = sobre("PermisosRespuesta", ConsultaPermisosSerializer())
