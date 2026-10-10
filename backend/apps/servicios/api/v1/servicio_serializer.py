from rest_framework import serializers

from apps.catalogo.models import Nodo
from apps.servicios.models import CAMPOS_EDITABLES, Servicio


class FuenteDelDatoSerializer(serializers.Serializer):
    dato = serializers.CharField(max_length=300)
    origen = serializers.CharField(max_length=300)


class ServicioSerializer(serializers.ModelSerializer):
    nodo = serializers.SlugRelatedField(slug_field="identificador", read_only=True)
    tareas = serializers.ListField(child=serializers.CharField(), read_only=True)
    fuentes = FuenteDelDatoSerializer(many=True, read_only=True)
    actualizado = serializers.DateTimeField(source="actualizado_en", read_only=True)

    class Meta:
        model = Servicio
        fields = ["slug", "nodo", *CAMPOS_EDITABLES, "actualizado"]
        read_only_fields = fields


class ServicioEditorialSerializer(serializers.ModelSerializer):
    """Lo que un curador escribe de un servicio. `slug` y `nodo` solo al crearlo."""

    tareas = serializers.ListField(child=serializers.CharField(max_length=300), allow_empty=True)
    fuentes = FuenteDelDatoSerializer(many=True, required=False)

    class Meta:
        model = Servicio
        fields = list(CAMPOS_EDITABLES)

    def validate_fuentes(self, fuentes):
        return [{"dato": f["dato"], "origen": f["origen"]} for f in fuentes]


class ServicioNuevoSerializer(ServicioEditorialSerializer):
    nodo = serializers.SlugRelatedField(
        slug_field="identificador",
        queryset=Nodo.objects.vigentes(),
        error_messages={"does_not_exist": "No hay un nodo vigente con ese identificador."},
    )

    class Meta(ServicioEditorialSerializer.Meta):
        fields = ["slug", "nodo", *CAMPOS_EDITABLES]
