from rest_framework import serializers

from apps.catalogo.models import Ambito


class AmbitoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambito
        fields = ["nombre", "orden"]
        read_only_fields = fields
