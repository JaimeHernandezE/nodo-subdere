from django.urls import path

from .municipios_view import EncargadoView, EquipoView
from .perfiles_view import PerfilDetalleView, PerfilesView
from .yo_view import YoView

urlpatterns = [
    path("yo", YoView.as_view(), name="yo"),
    path("perfiles", PerfilesView.as_view(), name="perfiles"),
    path("perfiles/<int:pk>", PerfilDetalleView.as_view(), name="perfil"),
    path("municipios/<str:cut>/equipo", EquipoView.as_view(), name="municipio-equipo"),
    path("municipios/<str:cut>/encargado", EncargadoView.as_view(), name="municipio-encargado"),
]
