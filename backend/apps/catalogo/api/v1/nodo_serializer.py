from rest_framework import serializers

from apps.catalogo.models import CAMPOS_DE_FICHA, CAMPOS_EDITORIALES, Ambiente, Nodo

from .especificacion_serializer import EspecificacionSerializer


class _Grupo(serializers.Serializer):
    """Agrupa campos planos del modelo como en la ficha. Nulo si la ficha no lo declara."""

    def to_representation(self, instancia):
        datos = super().to_representation(instancia)
        return datos if any(datos.values()) else None


class ResponsableSerializer(serializers.Serializer):
    organismo = serializers.CharField(source="responsable_organismo")
    equipo = serializers.CharField(source="responsable_equipo")
    correo = serializers.EmailField(source="responsable_correo")


class OrigenSerializer(_Grupo):
    norma = serializers.CharField(source="origen_norma")
    nota = serializers.CharField(source="origen_nota")


class ProcedenciaSerializer(_Grupo):
    copia = serializers.CharField(source="procedencia_copia")
    fuente = serializers.CharField(source="procedencia_fuente")
    detalle = serializers.CharField(source="procedencia_detalle")


class AccesoSerializer(_Grupo):
    tipo = serializers.CharField(source="acceso_tipo")
    detalle = serializers.CharField(source="acceso_detalle")


class AmbienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambiente
        fields = ["nombre", "base", "datos"]
        read_only_fields = fields


class NodoResumenSerializer(serializers.ModelSerializer):
    """Lo que muestra una tarjeta del catálogo."""

    ambito = serializers.SlugRelatedField(slug_field="nombre", read_only=True)

    class Meta:
        model = Nodo
        fields = [
            "identificador",
            "nombre",
            "sigla",
            "ambito",
            "clase",
            "intercambio",
            "funcion",
            "madurez",
            "acceso_tipo",
            "visibilidad",
            "orden",
            "leido_en",
        ]
        read_only_fields = fields


class NodoSerializer(NodoResumenSerializer):
    """La ficha completa, agrupada como en el estándar."""

    responsable = ResponsableSerializer(source="*", read_only=True)
    origen = OrigenSerializer(source="*", read_only=True, allow_null=True)
    procedencia = ProcedenciaSerializer(source="*", read_only=True, allow_null=True)
    acceso = AccesoSerializer(source="*", read_only=True, allow_null=True)
    ambientes = AmbienteSerializer(many=True, read_only=True)
    especificacion = EspecificacionSerializer(
        source="especificacion_vigente", read_only=True, allow_null=True
    )

    class Meta(NodoResumenSerializer.Meta):
        fields = [
            *NodoResumenSerializer.Meta.fields,
            "descripcion",
            "instituciones",
            "responsable",
            "origen",
            "procedencia",
            "acceso",
            "ambientes",
            "especificacion",
            "nota_editorial",
            "commit",
        ]
        read_only_fields = fields


# Los nombres con que la respuesta muestra lo que viene de la ficha, además de los del modelo.
CAMPOS_DE_FICHA_EN_LA_RESPUESTA = frozenset(
    [
        *CAMPOS_DE_FICHA,
        "responsable",
        "origen",
        "procedencia",
        "acceso",
        "ambientes",
        "especificacion",
    ]
)


class NodoEditorialSerializer(serializers.ModelSerializer):
    """Lo único que una persona edita de un nodo."""

    class Meta:
        model = Nodo
        fields = list(CAMPOS_EDITORIALES)

    def validate_visibilidad(self, visibilidad):
        if impedimento := self.instance.impedimento_para(visibilidad):
            raise serializers.ValidationError(impedimento)
        return visibilidad
