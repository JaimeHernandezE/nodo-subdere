import pytest
from django.utils import timezone

from apps.catalogo.tests.conftest import (  # noqa: F401
    _ambiente,
    alias,
    clave,
    como,
    crear_nodo,
    curador,
    lector,
    realm,
)
from apps.cuentas.models import Rol
from apps.cuentas.tests.conftest import crear_perfil
from apps.wiki.models import Entrada, Version


def crear_entrada(slug="prueba", markdown="## Hola\n\nUn párrafo.", publicada=True, **campos):
    """Una entrada con una versión, vigente y publicada si se pide."""
    datos = {"titulo": "Prueba", "descripcion": "Una entrada de prueba.", **campos}
    entrada = Entrada.objects.create(slug=slug, **datos)
    version = Version.objects.create(
        entrada=entrada,
        markdown=markdown,
        resumen="Primera",
        publicada=publicada,
        publicada_en=timezone.now() if publicada else None,
    )
    if publicada:
        entrada.vigente = version
        entrada.save(update_fields=["vigente"])
    return entrada


@pytest.fixture
def editor(db):
    return crear_perfil(55555555, rol=Rol.EDITOR)


@pytest.fixture
def entrada(db):
    return crear_entrada()
