from django.urls import path

from .fuentes_view import FuenteDetalleView, FuentesView, LecturasView, SincronizarFuenteView

urlpatterns = [
    path("fuentes", FuentesView.as_view(), name="fuentes"),
    path("fuentes/<int:pk>", FuenteDetalleView.as_view(), name="fuente"),
    path(
        "fuentes/<int:pk>/sincronizar", SincronizarFuenteView.as_view(), name="fuente-sincronizar"
    ),
    path("fuentes/<int:pk>/lecturas", LecturasView.as_view(), name="fuente-lecturas"),
]
