import pytest
from django.utils import timezone

from apps.catalogo.models import Alias, Ambito, Especificacion, Formato, Nodo, Visibilidad
from apps.cuentas.models import Rol
from apps.cuentas.tests.conftest import _ambiente, clave, como, crear_perfil, realm  # noqa: F401

CONTRATO = "openapi: 3.0.3\ninfo:\n  title: Códigos Únicos Territoriales\n  version: 1.0.0\n"


def crear_nodo(identificador="cut", visibilidad=Visibilidad.PUBLICADO, **campos) -> Nodo:
    """Un nodo como lo deja la sincronización."""
    datos = {
        "nombre": "Códigos Únicos Territoriales",
        "sigla": "CUT",
        "ambito": Ambito.objects.get(nombre="Transversal"),
        "clase": "intercambio",
        "intercambio": "consulta",
        "funcion": "Regiones, provincias y comunas con su código.",
        "descripcion": "La lista oficial vigente.",
        "madurez": "En desarrollo",
        "instituciones": ["SUBDERE", "Municipalidades"],
        "responsable_organismo": "SUBDERE",
        "responsable_equipo": "Equipo SEM",
        "responsable_correo": "equipo.sem@subdere.gov.cl",
        "leido_en": timezone.now(),
        "commit": "5edefaba674fe792d4b309e9a0fd58bfa4e84616",
        **campos,
    }
    nodo = Nodo(identificador=identificador, visibilidad=visibilidad, **datos)
    nodo.save(desde_sincronizacion=True)
    return nodo


def especificar(nodo: Nodo, version="1.0.0", contenido=CONTRATO, vigente=True) -> Especificacion:
    especificacion = Especificacion(
        nodo=nodo,
        version=version,
        formato=Formato.OPENAPI_30 if contenido else Formato.DESCRIPCION,
        ruta="nodo/cut.openapi.yaml" if contenido else "",
        contenido=contenido,
        vigente=vigente,
    )
    especificacion.save(desde_sincronizacion=True)
    return especificacion


@pytest.fixture
def alias(db):
    """Un identificador antiguo de `cut`. El catálogo real parte sin alias."""
    return Alias.objects.create(identificador="codigos-territoriales", destino="cut")


@pytest.fixture
def publicado(db):
    nodo = crear_nodo()
    especificar(nodo)
    return nodo


@pytest.fixture
def lector(db):
    return crear_perfil(33333333)


@pytest.fixture
def curador(db):
    return crear_perfil(44444444, rol=Rol.CURADOR)
