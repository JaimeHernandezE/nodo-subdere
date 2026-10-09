import pytest
from django.db import IntegrityError

from apps.cuentas.models import Bitacora, Perfil, Rol

from .conftest import crear_perfil

pytestmark = pytest.mark.django_db


def test_los_roles_son_acumulativos():
    curador = Perfil(rol=Rol.CURADOR)

    assert curador.rol_al_menos(Rol.LECTOR)
    assert curador.rol_al_menos(Rol.EDITOR)
    assert curador.rol_al_menos(Rol.CURADOR)
    assert not curador.rol_al_menos(Rol.ADMINISTRADOR)


def test_un_curador_no_puede_crear_perfiles(como):
    curador = crear_perfil(33333333, rol=Rol.CURADOR)

    respuesta = como(curador).post("/api/v1/perfiles", {"run": "12345678-5", "nombre": "X"})

    assert respuesta.status_code == 403
    assert not Perfil.objects.filter(run_numero=12345678).exists()


def test_un_administrador_crea_un_perfil_de_subdere_con_cualquier_rol(como, administrador):
    respuesta = como(administrador).post(
        "/api/v1/perfiles", {"run": "12.345.678-5", "nombre": "Ana", "rol": "curador"}
    )

    assert respuesta.status_code == 201, respuesta.json()
    assert respuesta.json()["run"] == "12345678-5"
    assert respuesta.json()["municipio"] is None
    assert respuesta.json()["rol"] == "curador"


@pytest.mark.parametrize("segundo", ["12345678-5", "12.345.678-5", "123456785"])
def test_no_hay_dos_perfiles_para_el_mismo_run(como, administrador, segundo):
    como(administrador).post("/api/v1/perfiles", {"run": "12.345.678-5", "nombre": "Ana"})

    respuesta = como(administrador).post("/api/v1/perfiles", {"run": segundo, "nombre": "Otra"})

    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "PERFIL_EXISTENTE"
    assert Perfil.objects.filter(run_numero=12345678).count() == 1


def test_la_base_rechaza_un_run_duplicado():
    crear_perfil(12345678)

    with pytest.raises(IntegrityError):
        crear_perfil(12345678)


def test_un_run_invalido_da_400(como, administrador):
    respuesta = como(administrador).post("/api/v1/perfiles", {"run": "12345678-9", "nombre": "X"})

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION_FALLIDA"


def test_el_run_se_guarda_separado_y_su_texto_se_calcula():
    perfil = crear_perfil(10000013)

    assert (perfil.run_numero, perfil.run_dv, perfil.run_tipo) == (10000013, "K", "RUN")
    assert perfil.run == "10000013-K"


def test_el_run_no_se_cambia_despues_de_crear(como, administrador):
    perfil = crear_perfil(12345678)

    como(administrador).patch(f"/api/v1/perfiles/{perfil.pk}", {"run": "10000013-K"})

    perfil.refresh_from_db()
    assert perfil.run == "12345678-5"


def test_los_perfiles_no_se_borran(como, administrador):
    perfil = crear_perfil(12345678)

    respuesta = como(administrador).delete(f"/api/v1/perfiles/{perfil.pk}")

    assert respuesta.status_code == 405
    assert Perfil.objects.filter(pk=perfil.pk).exists()


class TestEncargado:
    def test_crea_un_lector_en_su_municipio_sin_indicarlo(self, como, encargado):
        respuesta = como(encargado).post("/api/v1/perfiles", {"run": "12345678-5", "nombre": "Ana"})

        assert respuesta.status_code == 201, respuesta.json()
        assert respuesta.json()["municipio"] == "13101"
        assert respuesta.json()["rol"] == "lector"

    def test_no_crea_en_otro_municipio(self, como, encargado, valparaiso):
        respuesta = como(encargado).post(
            "/api/v1/perfiles", {"run": "12345678-5", "nombre": "Ana", "municipio": "05101"}
        )

        assert respuesta.status_code == 403

    def test_no_crea_perfiles_de_subdere(self, como, encargado):
        respuesta = como(encargado).post(
            "/api/v1/perfiles",
            {"run": "12345678-5", "nombre": "Ana", "municipio": None},
            format="json",
        )

        assert respuesta.status_code == 403

    def test_no_crea_con_otro_rol(self, como, encargado):
        respuesta = como(encargado).post(
            "/api/v1/perfiles", {"run": "12345678-5", "nombre": "Ana", "rol": "editor"}
        )

        assert respuesta.status_code == 403

    def test_no_marca_a_nadie_como_encargado(self, como, encargado):
        respuesta = como(encargado).post(
            "/api/v1/perfiles", {"run": "12345678-5", "nombre": "Ana", "es_encargado": True}
        )

        assert respuesta.status_code == 201
        assert respuesta.json()["es_encargado"] is False

    def test_no_se_modifica_a_si_mismo(self, como, encargado):
        respuesta = como(encargado).patch(f"/api/v1/perfiles/{encargado.pk}", {"activo": False})

        assert respuesta.status_code == 403
        encargado.refresh_from_db()
        assert encargado.activo

    def test_desactiva_y_reactiva_a_su_equipo(self, como, encargado, santiago):
        integrante = crear_perfil(12345678, municipio=santiago)
        cliente = como(encargado)

        url = f"/api/v1/perfiles/{integrante.pk}"

        assert cliente.patch(url, {"activo": False}).status_code == 200
        integrante.refresh_from_db()
        assert not integrante.activo

        assert cliente.patch(url, {"activo": True}).status_code == 200
        integrante.refresh_from_db()
        assert integrante.activo

    def test_no_cambia_el_rol_de_su_equipo(self, como, encargado, santiago):
        integrante = crear_perfil(12345678, municipio=santiago)

        respuesta = como(encargado).patch(f"/api/v1/perfiles/{integrante.pk}", {"rol": "editor"})

        assert respuesta.status_code == 403

    def test_no_ve_ni_toca_perfiles_de_otro_municipio(self, como, encargado, valparaiso):
        ajeno = crear_perfil(12345678, municipio=valparaiso)
        cliente = como(encargado)

        assert cliente.patch(f"/api/v1/perfiles/{ajeno.pk}", {"activo": False}).status_code == 404
        listado = cliente.get("/api/v1/perfiles").json()
        assert ajeno.pk not in [perfil["id"] for perfil in listado]

    def test_un_run_de_otro_municipio_da_409_sin_decir_cual(self, como, encargado, valparaiso):
        crear_perfil(12345678, municipio=valparaiso)

        respuesta = como(encargado).post("/api/v1/perfiles", {"run": "12345678-5", "nombre": "Ana"})

        assert respuesta.status_code == 409
        assert respuesta.json()["error"]["codigo"] == "PERFIL_EXISTENTE"
        assert "Valparaíso" not in respuesta.content.decode()
        assert "05101" not in respuesta.content.decode()


def test_un_lector_municipal_no_administra_perfiles(como, santiago):
    lector = crear_perfil(33333333, municipio=santiago)

    assert como(lector).get("/api/v1/perfiles").status_code == 403


class TestBitacora:
    def test_crear_un_perfil_deja_el_despues(self, como, administrador):
        respuesta = como(administrador).post(
            "/api/v1/perfiles", {"run": "12345678-5", "nombre": "Ana"}
        )

        entrada = Bitacora.objects.get(accion="crear_perfil")
        assert entrada.perfil == administrador
        assert entrada.objeto == f"cuentas.Perfil:{respuesta.json()['id']}"
        assert entrada.antes == {}
        assert entrada.despues["run"] == "12345678-5"

    def test_modificar_un_perfil_deja_el_antes_y_el_despues(self, como, administrador):
        perfil = crear_perfil(12345678)

        como(administrador).patch(f"/api/v1/perfiles/{perfil.pk}", {"rol": "editor"})

        entrada = Bitacora.objects.get(accion="modificar_perfil")
        assert entrada.antes["rol"] == "lector"
        assert entrada.despues["rol"] == "editor"

    def test_un_cambio_que_no_cambia_nada_no_deja_entrada(self, como, administrador):
        perfil = crear_perfil(12345678)

        como(administrador).patch(f"/api/v1/perfiles/{perfil.pk}", {"rol": "lector"})

        assert not Bitacora.objects.filter(accion="modificar_perfil").exists()
