from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import YoSerializer


class YoView(APIView):
    """El perfil propio. Es lo que el frontend pide al entrar para armar la interfaz."""

    @extend_schema(operation_id="yo", responses=YoSerializer)
    def get(self, request):
        return Response(YoSerializer(request.user).data)
