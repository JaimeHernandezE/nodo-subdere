from rest_framework import serializers

from .respuesta_serializer import sobre


class UnidadSuperiorSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nombre = serializers.CharField()


class UnidadTerritorialSerializer(serializers.Serializer):
    """Una región, provincia o comuna, con los nombres de las unidades que la contienen."""

    nivel = serializers.ChoiceField(choices=["region", "provincia", "comuna"])
    codigo = serializers.CharField(help_text="Canónico: con los ceros a la izquierda.")
    nombre = serializers.CharField()
    provincia = UnidadSuperiorSerializer(allow_null=True, help_text="Solo en una comuna.")
    region = UnidadSuperiorSerializer(allow_null=True, help_text="Nulo en una región.")


CutBusquedaSerializer = sobre("CutBusqueda", UnidadTerritorialSerializer(many=True))
CutUnidadSerializer = sobre("CutUnidad", UnidadTerritorialSerializer())
