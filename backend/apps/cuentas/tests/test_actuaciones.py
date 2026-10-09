import pytest
from django.db import IntegrityError
from rest_framework.test import APIRequestFactory

from apps.cuentas.actuaciones import registrar_acceso, registrar_bitacora
from apps.cuentas.models import Acceso, RegistroInmutable

from .conftest import crear_perfil

pytestmark = pytest.mark.django_db


@pytest.fixture
def acceso():
    return registrar_acceso(
        crear_perfil(12345678),
        canal="pantalla",
        nodo="permisos-circulacion",
        operacion="consultar_permiso_por_patente",
        parametros={"patente": "BBBB10"},
        resultado="encontrado",
    )


@pytest.fixture
def bitacora():
    return registrar_bitacora(crear_perfil(12345678), accion="publicar", objeto="catalogo.Nodo:cut")


def test_registrar_acceso_toma_el_contexto_de_la_peticion():
    peticion = APIRequestFactory().get("/")
    peticion.procedimiento, peticion.id_tramite = "fiscalizacion", "T-1"

    acceso = registrar_acceso(
        crear_perfil(12345678),
        canal="api",
        nodo="permisos-circulacion",
        operacion="consultar_permiso_por_patente",
        parametros={"patente": "BBBB10"},
        resultado="no_encontrado",
        request=peticion,
    )

    assert (acceso.procedimiento, acceso.id_tramite) == ("fiscalizacion", "T-1")


def test_no_hay_accesos_sin_perfil():
    with pytest.raises(IntegrityError):
        Acceso.objects.create(perfil=None, canal="api", nodo="x", operacion="y", resultado="error")


def test_una_entrada_de_bitacora_sin_perfil_necesita_nota():
    with pytest.raises(ValueError, match="nota"):
        registrar_bitacora(None, accion="sincronizar", objeto="registro.Fuente:1")

    entrada = registrar_bitacora(
        None, accion="sincronizar", objeto="registro.Fuente:1", nota="sincronización"
    )
    assert entrada.perfil is None


@pytest.mark.parametrize("modelo", ["acceso", "bitacora"])
class TestSoloCrecen:
    @pytest.fixture
    def registro(self, request, modelo):
        return request.getfixturevalue(modelo)

    def test_no_se_modifica_con_save(self, registro):
        registro.objeto = registro.operacion = "otra"
        with pytest.raises(RegistroInmutable):
            registro.save()

    def test_no_se_borra(self, registro):
        with pytest.raises(RegistroInmutable):
            registro.delete()

    def test_no_se_modifica_ni_se_borra_por_queryset(self, registro):
        modelo = type(registro)
        with pytest.raises(RegistroInmutable):
            modelo.objects.all().update(creado_en=None)
        with pytest.raises(RegistroInmutable):
            modelo.objects.filter(pk=registro.pk).delete()
        with pytest.raises(RegistroInmutable):
            modelo.objects.bulk_update([registro], ["creado_en"])
        assert modelo.objects.filter(pk=registro.pk).exists()
