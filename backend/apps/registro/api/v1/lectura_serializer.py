from rest_framework import serializers

from apps.registro.models import Lectura


class LecturaSerializer(serializers.ModelSerializer):
    perfil = serializers.CharField(
        source="perfil.nombre",
        allow_null=True,
        read_only=True,
        help_text="Quién pidió leer. Nulo: la tarea programada.",
    )

    class Meta:
        model = Lectura
        fields = ["id", "creado_en", "commit", "valida", "motivo", "perfil", "contenido"]
        read_only_fields = fields
