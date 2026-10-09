import pytest
from django.db import IntegrityError

from apps.cuentas.models import Bitacora, Rol

from .conftest import crear_perfil

pytestmark = pytest.mark.django_db


def test_la_base_no_admite_dos_encargados_en_un_municipio(encargado, santiago):
    with pytest.raises(IntegrityError):
        crear_perfil(12345678, municipio=santiago, es_encargado=True)


def test_un_perfil_sin_municipio_no_puede_ser_encargado():
    perfil = crear_perfil(12345678, es_encargado=True)

    assert perfil.es_encargado is False


def test_desactivar_al_encargado_le_quita_la_marca(encargado):
    encargado.activo = False
    encargado.save()

    encargado.refresh_from_db()
    assert encargado.es_encargado is False


class TestDesignarEncargado:
    def url(self, cut="13101"):
        return f"/api/v1/municipios/{cut}/encargado"

    def test_un_administrador_reemplaza_al_encargado(
        self, como, administrador, encargado, santiago
    ):
        nuevo = crear_perfil(12345678, municipio=santiago)

        respuesta = como(administrador).put(self.url(), {"perfil": nuevo.pk})

        assert respuesta.status_code == 200, respuesta.json()
        nuevo.refresh_from_db()
        encargado.refresh_from_db()
        assert nuevo.es_encargado
        assert not encargado.es_encargado
        assert encargado.activo

    def test_la_designacion_queda_en_la_bitacora(self, como, administrador, encargado, santiago):
        nuevo = crear_perfil(12345678, municipio=santiago)

        como(administrador).put(self.url(), {"perfil": nuevo.pk})

        entrada = Bitacora.objects.get(accion="designar_encargado")
        assert entrada.perfil == administrador
        assert entrada.objeto == "core.Municipio:13101"
        assert entrada.antes == {"encargado": encargado.run}
        assert entrada.despues == {"encargado": "12345678-5"}

    def test_un_municipio_sin_encargado_recibe_uno(self, como, administrador, santiago):
        nuevo = crear_perfil(12345678, municipio=santiago)

        como(administrador).put(self.url(), {"perfil": nuevo.pk})

        assert Bitacora.objects.get(accion="designar_encargado").antes == {"encargado": None}

    def test_solo_un_administrador_designa(self, como, encargado, santiago):
        nuevo = crear_perfil(12345678, municipio=santiago)
        curador = crear_perfil(33333333, rol=Rol.CURADOR)

        assert como(encargado).put(self.url(), {"perfil": nuevo.pk}).status_code == 403
        assert como(curador).put(self.url(), {"perfil": nuevo.pk}).status_code == 403

    def test_el_perfil_tiene_que_ser_de_ese_municipio(self, como, administrador, valparaiso):
        ajeno = crear_perfil(12345678, municipio=valparaiso)

        respuesta = como(administrador).put(self.url(), {"perfil": ajeno.pk})

        assert respuesta.status_code == 400
        ajeno.refresh_from_db()
        assert not ajeno.es_encargado

    def test_el_perfil_tiene_que_estar_activo(self, como, administrador, santiago):
        inactivo = crear_perfil(12345678, municipio=santiago, activo=False)

        respuesta = como(administrador).put(self.url(), {"perfil": inactivo.pk})

        assert respuesta.status_code == 400


class TestVerEquipo:
    def url(self, cut="13101"):
        return f"/api/v1/municipios/{cut}/equipo"

    def test_un_perfil_municipal_no_ve_el_equipo_de_otro(self, como, valparaiso, encargado):
        ajeno = crear_perfil(12345678, municipio=valparaiso)

        assert como(ajeno).get(self.url("13101")).status_code == 403

    def test_un_perfil_municipal_ve_su_equipo_sin_run(self, como, santiago, encargado):
        lector = crear_perfil(12345678, municipio=santiago)

        respuesta = como(lector).get(self.url())

        assert respuesta.status_code == 200
        assert {integrante["id"] for integrante in respuesta.json()} == {encargado.pk, lector.pk}
        assert all("run" not in integrante for integrante in respuesta.json())

    def test_un_lector_de_subdere_ve_cualquier_equipo_sin_run(self, como, encargado):
        lector = crear_perfil(12345678)

        respuesta = como(lector).get(self.url())

        assert respuesta.status_code == 200
        assert respuesta.json()[0]["id"] == encargado.pk
        assert "run" not in respuesta.json()[0]

    def test_el_encargado_ve_el_run_de_su_equipo(self, como, encargado):
        respuesta = como(encargado).get(self.url())

        assert respuesta.json()[0]["run"] == encargado.run

    def test_un_administrador_ve_el_run(self, como, administrador, encargado):
        respuesta = como(administrador).get(self.url())

        assert respuesta.json()[0]["run"] == encargado.run

    def test_un_municipio_inexistente_da_404(self, como, administrador):
        assert como(administrador).get(self.url("99999")).status_code == 404
