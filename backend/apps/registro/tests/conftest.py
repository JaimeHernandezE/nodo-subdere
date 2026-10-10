import copy
import urllib.request

import pytest
import yaml

from apps.catalogo.tests.conftest import curador, lector  # noqa: F401
from apps.cuentas.tests.conftest import (  # noqa: F401
    _ambiente,
    administrador,
    clave,
    como,
    crear_perfil,
    realm,
)
from apps.registro import sincronizacion
from apps.registro.lectores import LectorFalso
from apps.registro.models import Fuente

API = "https://gitlab.prueba/api/v4"
URL = "https://gitlab.prueba/modernizacion/cut"
RUTA_FICHA = "nodo/ficha.yaml"
RUTA_CONTRATO = "nodo/cut.openapi.yaml"
COMMIT_1 = "1" * 40
COMMIT_2 = "2" * 40
QUITAR = object()

FICHA = {
    "ficha": 1,
    "id": "cut",
    "nombre": "Códigos Únicos Territoriales",
    "sigla": "CUT",
    "ambito": "Transversal",
    "clase": "intercambio",
    "intercambio": "consulta",
    "funcion": "Regiones, provincias y comunas con su Código Único Territorial.",
    "descripcion": "Este servicio entrega la lista oficial vigente.",
    "madurez": "En desarrollo",
    "responsable": {
        "organismo": "SUBDERE",
        "equipo": "Equipo SEM",
        "correo": "equipo.sem@subdere.gov.cl",
    },
    "instituciones": ["SUBDERE", "Municipalidades"],
    "especificacion": {
        "archivo": RUTA_CONTRATO,
        "formato": "openapi-3.0",
        "version": "1.0.0",
        "publicada": "2026-09-15",
    },
    "origen": {"norma": "Decreto Exento N° 1.115, de 2018", "nota": "Los fija el decreto."},
    "procedencia": {"copia": "exacta", "fuente": "Equipo SEM", "detalle": "Sin cambios."},
    "acceso": {"tipo": "abierto", "detalle": "Sin credencial."},
}


def ficha(**cambios) -> str:
    """La ficha de CUT en YAML, con `cambios`. `responsable__correo` entra en el grupo."""
    datos = copy.deepcopy(FICHA)
    for ruta, valor in cambios.items():
        *grupos, campo = ruta.split("__")
        destino = datos
        for grupo in grupos:
            destino = destino.setdefault(grupo, {})
        if valor is QUITAR:
            destino.pop(campo, None)
        else:
            destino[campo] = valor
    return yaml.safe_dump(datos, allow_unicode=True, sort_keys=False)


def contrato(version="1.0.0", openapi="3.0.3", extra="") -> str:
    return f"openapi: {openapi}\ninfo:\n  title: CUT\n  version: {version}\n{extra}"


@pytest.fixture(autouse=True)
def _sin_red(settings, monkeypatch):
    """Ninguna prueba sale a la red: la única puerta del lector de GitLab queda cerrada."""
    settings.REGISTRO_GIT_API_URL = API
    settings.REGISTRO_GIT_TOKEN = "token-de-prueba"

    def prohibido(*args, **kwargs):
        raise AssertionError("Una prueba intentó salir a la red.")

    monkeypatch.setattr(urllib.request, "urlopen", prohibido)


@pytest.fixture
def repositorio(monkeypatch):
    """El repositorio de CUT en memoria; la sincronización lo usa en vez de GitLab."""
    falso = LectorFalso({RUTA_FICHA: ficha(), RUTA_CONTRATO: contrato()}, commit=COMMIT_1)
    monkeypatch.setattr(sincronizacion, "lector_por_defecto", lambda: falso)
    return falso


@pytest.fixture
def fuente(db):
    return Fuente.objects.create(url=URL)
