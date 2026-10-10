from django.urls import path

from .entradas_view import EntradaDetalleView, EntradasView
from .versiones_view import PublicarView, VersionDetalleView, VersionesView

urlpatterns = [
    path("wiki", EntradasView.as_view(), name="wiki"),
    path("wiki/<slug:slug>", EntradaDetalleView.as_view(), name="wiki-entrada"),
    path("wiki/<slug:slug>/versiones", VersionesView.as_view(), name="wiki-versiones"),
    path(
        "wiki/<slug:slug>/versiones/<int:version_id>",
        VersionDetalleView.as_view(),
        name="wiki-version",
    ),
    path(
        "wiki/<slug:slug>/versiones/<int:version_id>/publicar",
        PublicarView.as_view(),
        name="wiki-version-publicar",
    ),
]
