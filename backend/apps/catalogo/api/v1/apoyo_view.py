from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.catalogo.models import Ambito
from apps.core.models import Municipio
from apps.cuentas.api.v1.serializers import MunicipioResumenSerializer

from .ambito_serializer import AmbitoSerializer


@extend_schema_view(get=extend_schema(operation_id="ambitos_listar"))
class AmbitosView(generics.ListAPIView):
    queryset = Ambito.objects.all()
    serializer_class = AmbitoSerializer
    authentication_classes = []
    permission_classes = [AllowAny]


@extend_schema_view(get=extend_schema(operation_id="municipios_listar"))
class MunicipiosView(generics.ListAPIView):
    """Las 346 comunas con su código CUT, de `core.Municipio`."""

    queryset = Municipio.objects.all()
    serializer_class = MunicipioResumenSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
