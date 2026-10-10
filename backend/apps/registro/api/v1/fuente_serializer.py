from rest_framework import serializers

from apps.registro.models import Fuente, problema_de_url

from .lectura_serializer import LecturaSerializer

CAMPOS_EDITABLES = ["url", "rama", "ruta_ficha", "activa"]


class LecturaResumenSerializer(LecturaSerializer):
    class Meta(LecturaSerializer.Meta):
        fields = ["id", "creado_en", "commit", "valida", "motivo", "perfil"]
        read_only_fields = fields


class FuenteSerializer(serializers.ModelSerializer):
    url = serializers.URLField(max_length=500)
    ultima_lectura = LecturaResumenSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Fuente
        fields = [
            "id",
            "tipo",
            *CAMPOS_EDITABLES,
            "nodo_identificador",
            "ultima_lectura",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "tipo", "nodo_identificador", "creado_en", "actualizado_en"]
        # La unicidad de (url, rama, ruta_ficha) se revisa en validate() con un motivo propio.
        validators = []

    def validate_url(self, url: str) -> str:
        url = url.strip().removesuffix("/")
        if problema := problema_de_url(url):
            raise serializers.ValidationError(problema)
        return url

    def validate_rama(self, rama: str) -> str:
        return rama.strip()

    def validate_ruta_ficha(self, ruta: str) -> str:
        ruta = ruta.strip().strip("/")
        if not ruta:
            raise serializers.ValidationError("Debe ser la ruta de la ficha en el repositorio.")
        return ruta

    def validate(self, datos: dict) -> dict:
        actual = self.instance
        direccion = {
            campo: datos.get(campo, getattr(actual, campo) if actual else None)
            for campo in ("url", "rama", "ruta_ficha")
        }
        direccion = {
            c: v if v is not None else Fuente._meta.get_field(c).default
            for c, v in direccion.items()
        }
        repetidas = Fuente.objects.filter(**direccion)
        if actual:
            repetidas = repetidas.exclude(pk=actual.pk)
        if repetidas.exists():
            raise serializers.ValidationError(
                {"url": ["Ya hay una fuente con esa dirección, rama y ruta."]}
            )
        return datos
