import pytest

from apps.catalogo.models import Visibilidad
from apps.catalogo.tests.conftest import (  # noqa: F401
    _ambiente,
    alias,
    clave,
    como,
    crear_nodo,
    curador,
    especificar,
    lector,
    realm,
)
from apps.integraciones.tests.conftest import (  # noqa: F401
    CUT,
    PERMISOS,
    _sin_red,
    fuente,
    http,
)
from apps.servicios.models import Estado, Servicio

PROCEDIMIENTO = {"HTTP_X_PROCEDIMIENTO": "fiscalizacion-transito", "HTTP_X_ID_TRAMITE": "T-1"}


def crear_servicio(nodo, slug="buscador-cut", **campos) -> Servicio:
    datos = {
        "nombre": "Buscador de códigos territoriales",
        "funcion": "Buscar el código de una comuna, provincia o región.",
        "descripcion": "Escribe un nombre o un código.",
        "tareas": ["Escribir el nombre de una comuna y obtener su código"],
        "fuentes": [{"dato": "Los códigos", "origen": "SUBDERE"}],
        "estado": Estado.EN_CONSTRUCCION,
        **campos,
    }
    return Servicio.objects.create(nodo=nodo, slug=slug, **datos)


@pytest.fixture
def nodo_cut(db):
    nodo = crear_nodo("cut")
    especificar(nodo)
    return nodo


@pytest.fixture
def nodo_oculto(db):
    return crear_nodo("permisos-de-circulacion", visibilidad=Visibilidad.OCULTO)
