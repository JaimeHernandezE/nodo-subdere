from django.urls import path

from .cut_view import CutBuscarView, CutCodigoView
from .permisos_view import PermisosView
from .servicios_view import ServicioDetalleView, ServiciosView

# Las consultas de datos van antes de `<slug>` y tienen más de un segmento: no chocan.
urlpatterns = [
    path("servicios", ServiciosView.as_view(), name="servicios"),
    path("servicios/cut/buscar", CutBuscarView.as_view(), name="servicios-cut-buscar"),
    path("servicios/cut/codigo/<str:codigo>", CutCodigoView.as_view(), name="servicios-cut-codigo"),
    path("servicios/permisos/<str:patente>", PermisosView.as_view(), name="servicios-permisos"),
    path("servicios/<slug:slug>", ServicioDetalleView.as_view(), name="servicio"),
]
