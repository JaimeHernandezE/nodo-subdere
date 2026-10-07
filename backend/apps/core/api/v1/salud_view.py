from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class SaludView(APIView):
    """Responde si la API está arriba. Sin detalles de infraestructura ni de la base."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="salud",
        responses=inline_serializer(
            name="Salud",
            fields={"estado": serializers.CharField(), "version": serializers.CharField()},
        ),
    )
    def get(self, request):
        return Response({"estado": "ok", "version": settings.VERSION_DESPLIEGUE})
