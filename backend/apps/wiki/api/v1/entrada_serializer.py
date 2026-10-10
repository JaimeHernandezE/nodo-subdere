from rest_framework import serializers

from apps.catalogo.models import Alias, Nodo
from apps.wiki.models import CAMPOS_EDITABLES, Entrada


def identificador_vigente(texto: str) -> str:
    """Un alias, al identificador al que apunta. Lo demás, tal cual."""
    destino = Alias.objects.filter(identificador=texto).values_list("destino", flat=True).first()
    return destino or texto


class EntradaResumenSerializer(serializers.ModelSerializer):
    """Lo que muestra el índice."""

    publicada = serializers.SerializerMethodField()
    publicada_en = serializers.DateTimeField(
        source="vigente.publicada_en", read_only=True, allow_null=True, default=None
    )

    class Meta:
        model = Entrada
        fields = [
            "slug",
            "titulo",
            "descripcion",
            "seccion",
            "orden",
            "nodo",
            "publicada",
            "publicada_en",
        ]
        read_only_fields = fields

    def get_publicada(self, entrada) -> bool:
        return entrada.vigente_id is not None


class EntradaSerializer(EntradaResumenSerializer):
    """Una entrada con su versión vigente, como HTML saneado. Sin autor."""

    version = serializers.IntegerField(source="vigente_id", read_only=True)
    html = serializers.CharField(read_only=True)

    class Meta(EntradaResumenSerializer.Meta):
        fields = [*EntradaResumenSerializer.Meta.fields, "version", "html"]
        read_only_fields = fields


class EntradaEditorialSerializer(serializers.ModelSerializer):
    """Lo que un editor escribe de una entrada. El contenido va en versiones."""

    class Meta:
        model = Entrada
        fields = list(CAMPOS_EDITABLES)

    def validate_nodo(self, nodo: str) -> str:
        if not nodo:
            return ""
        identificador = identificador_vigente(nodo)
        if not Nodo.objects.filter(identificador=identificador).exists():
            raise serializers.ValidationError("No hay un nodo con ese identificador.")
        return identificador


class EntradaNuevaSerializer(EntradaEditorialSerializer):
    class Meta(EntradaEditorialSerializer.Meta):
        fields = ["slug", *CAMPOS_EDITABLES]
