from rest_framework import serializers

from apps.wiki.models import Version

SIN_AUTOR = "Contenido inicial"
LIMITE_MARKDOWN = 200_000


class VersionResumenSerializer(serializers.ModelSerializer):
    """Una línea del historial."""

    autor = serializers.SerializerMethodField()
    vigente = serializers.SerializerMethodField()

    class Meta:
        model = Version
        fields = ["id", "resumen", "autor", "creado_en", "publicada", "publicada_en", "vigente"]
        read_only_fields = fields

    def get_autor(self, version) -> str:
        return version.autor.nombre if version.autor else SIN_AUTOR

    def get_vigente(self, version) -> bool:
        return version.pk == version.entrada.vigente_id


class VersionSerializer(VersionResumenSerializer):
    """Una versión con su Markdown y su HTML: la vista previa del editor."""

    html = serializers.CharField(read_only=True)

    class Meta(VersionResumenSerializer.Meta):
        fields = [*VersionResumenSerializer.Meta.fields, "markdown", "html"]
        read_only_fields = fields


class VersionNuevaSerializer(serializers.ModelSerializer):
    markdown = serializers.CharField(max_length=LIMITE_MARKDOWN, trim_whitespace=False)

    class Meta:
        model = Version
        fields = ["markdown", "resumen"]
