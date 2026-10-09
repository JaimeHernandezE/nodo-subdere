from django.urls import path

from .apoyo_view import AmbitosView, MunicipiosView
from .especificacion_view import EspecificacionArchivoView, EspecificacionView
from .nodos_view import NodoDetalleView, NodosView

urlpatterns = [
    path("ambitos", AmbitosView.as_view(), name="ambitos"),
    path("municipios", MunicipiosView.as_view(), name="municipios"),
    path("nodos", NodosView.as_view(), name="nodos"),
    path("nodos/<slug:identificador>", NodoDetalleView.as_view(), name="nodo"),
    path(
        "nodos/<slug:identificador>/especificacion",
        EspecificacionView.as_view(),
        name="nodo-especificacion",
    ),
    path(
        "nodos/<slug:identificador>/especificacion/archivo",
        EspecificacionArchivoView.as_view(),
        name="nodo-especificacion-archivo",
    ),
]
