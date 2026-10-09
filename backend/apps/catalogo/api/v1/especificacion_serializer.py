from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.catalogo.models import Especificacion


class EspecificacionSerializer(serializers.ModelSerializer):
    archivo = serializers.SerializerMethodField(
        help_text="URL del archivo tal como se leyó. Nula si el nodo publica solo metadato."
    )

    class Meta:
        model = Especificacion
        fields = ["version", "formato", "ruta", "huella", "publicada", "commit", "archivo"]
        read_only_fields = fields

    @extend_schema_field(OpenApiTypes.URI)
    def get_archivo(self, especificacion: Especificacion) -> str | None:
        if not especificacion.tiene_archivo:
            return None
        ruta = reverse("nodo-especificacion-archivo", args=[especificacion.nodo.identificador])
        request = self.context.get("request")
        return request.build_absolute_uri(ruta) if request else ruta
