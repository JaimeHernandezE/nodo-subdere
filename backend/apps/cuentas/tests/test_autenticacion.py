import os
import subprocess
import sys
import time
import urllib.request

import pytest
from rest_framework.test import APIClient

from apps.cuentas import emisor_local
from apps.cuentas.models import Perfil

from .conftest import RealmFalso, crear_perfil, generar_clave

pytestmark = pytest.mark.django_db


def pedir_yo(token: str):
    cliente = APIClient()
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return cliente.get("/api/v1/yo")


def test_un_perfil_valido_entra_y_recibe_su_perfil(realm, santiago):
    perfil = crear_perfil(12345678, municipio=santiago)

    respuesta = pedir_yo(realm.token(perfil))

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": perfil.pk,
        "nombre": "Nombre Desde El Token",
        "rol": "lector",
        "municipio": {"cut": "13101", "nombre": "Santiago"},
        "es_encargado": False,
    }


def test_sin_token_da_401():
    respuesta = APIClient().get("/api/v1/yo")

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "NO_AUTENTICADO"


@pytest.mark.parametrize(
    "variante",
    ["firma_invalida", "aud_equivocado", "expirado", "iss_equivocado", "sin_exp", "basura"],
)
def test_un_token_invalido_da_401(realm, variante):
    perfil = crear_perfil(12345678)
    tokens = {
        "firma_invalida": lambda: realm.token(perfil, clave=generar_clave()),
        "aud_equivocado": lambda: realm.token(perfil, aud="otro-cliente"),
        "expirado": lambda: realm.token(perfil, exp=int(time.time()) - 10),
        "iss_equivocado": lambda: realm.token(perfil, iss="https://otro.realm/realms/x"),
        "sin_exp": lambda: realm.token(perfil, exp=None),
        "basura": lambda: "esto.no.es-un-token",
    }

    respuesta = pedir_yo(tokens[variante]())

    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "NO_AUTENTICADO"


def test_un_token_valido_sin_perfil_da_403_sin_perfil(realm):
    persona = Perfil(run_numero=12345678, run_dv="5")

    respuesta = pedir_yo(realm.token(persona))

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERFIL"


def test_un_perfil_inactivo_da_403_sin_perfil(realm):
    perfil = crear_perfil(12345678, activo=False)

    respuesta = pedir_yo(realm.token(perfil))

    assert respuesta.json()["error"]["codigo"] == "SIN_PERFIL"


@pytest.mark.parametrize(
    "rol_unico",
    [None, "12345678-5", {"numero": 12345678, "DV": "9"}, {"numero": "abc", "DV": "5"}],
)
def test_sin_rol_unico_utilizable_da_sin_perfil_y_avisa_en_el_log(realm, caplog, rol_unico):
    crear_perfil(12345678)

    respuesta = pedir_yo(realm.token(RolUnico=rol_unico))

    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "SIN_PERFIL"
    assert "RolUnico" in caplog.text
    assert "12345678" not in caplog.text


def test_el_perfil_se_encuentra_por_run_aunque_cambie_el_sub(realm):
    perfil = crear_perfil(12345678, sub="sub-antiguo")

    respuesta = pedir_yo(realm.token(perfil, sub="sub-nuevo", name="María Del Río"))

    assert respuesta.status_code == 200
    perfil.refresh_from_db()
    assert perfil.sub == "sub-nuevo"
    assert perfil.nombre == "María Del Río"


def test_el_nombre_estructurado_de_clave_unica_se_compone(realm):
    perfil = crear_perfil(12345678)
    nombre = {"nombres": ["María", "Carmen"], "apellidos": ["Del Río", "Gonzalez"]}

    pedir_yo(realm.token(perfil, name=nombre))

    perfil.refresh_from_db()
    assert perfil.nombre == "María Carmen Del Río Gonzalez"


def test_el_jwks_se_reutiliza_entre_peticiones(realm):
    perfil = crear_perfil(12345678)

    pedir_yo(realm.token(perfil))
    pedir_yo(realm.token(perfil))

    assert realm.descargas == 1


def test_una_rotacion_de_claves_se_resuelve_con_un_solo_refresco(realm):
    perfil = crear_perfil(12345678)
    pedir_yo(realm.token(perfil))
    realm.claves["k2"] = generar_clave()

    respuesta = pedir_yo(realm.token(perfil, kid="k2"))

    assert respuesta.status_code == 200
    assert realm.descargas == 2


def test_un_kid_desconocido_no_provoca_una_descarga_por_peticion(realm):
    perfil = crear_perfil(12345678)
    intrusa = generar_clave()

    primera = pedir_yo(realm.token(perfil, kid="inventado", clave=intrusa))
    segunda = pedir_yo(realm.token(perfil, kid="inventado", clave=intrusa))

    assert primera.status_code == segunda.status_code == 401
    assert realm.descargas == 2


def test_si_el_realm_no_responde_da_503(clave, monkeypatch):
    def caido(*args, **kwargs):
        raise OSError("sin conexión")

    monkeypatch.setattr(urllib.request, "urlopen", caido)
    perfil = crear_perfil(12345678)

    respuesta = pedir_yo(RealmFalso(clave).token(perfil))

    assert respuesta.status_code == 503
    assert respuesta.json()["error"]["codigo"] == "REALM_NO_DISPONIBLE"


class TestEmisorLocal:
    @pytest.fixture(autouse=True)
    def _clave_temporal(self, settings, tmp_path):
        settings.CUENTAS_CLAVE_LOCAL = tmp_path / "emisor_local.pem"

    def test_con_el_emisor_activo_el_token_local_sigue_el_mismo_camino(self, settings):
        settings.CUENTAS_EMISOR_LOCAL = True
        perfil = crear_perfil(12345678)

        respuesta = pedir_yo(emisor_local.emitir(12345678, "5", "Persona Local"))

        assert respuesta.status_code == 200
        perfil.refresh_from_db()
        assert perfil.sub == "local-12345678"

    def test_con_el_emisor_activo_un_run_sin_perfil_da_sin_perfil(self, settings):
        settings.CUENTAS_EMISOR_LOCAL = True

        respuesta = pedir_yo(emisor_local.emitir(12345678, "5", "Persona Local"))

        assert respuesta.json()["error"]["codigo"] == "SIN_PERFIL"

    def test_con_el_emisor_desactivado_el_token_local_da_401(self):
        crear_perfil(12345678)

        respuesta = pedir_yo(emisor_local.emitir(12345678, "5", "Persona Local"))

        assert respuesta.status_code == 401


def _arrancar_prod(tmp_path, **variables) -> subprocess.CompletedProcess:
    entorno = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": "config.settings.prod",
        "ARCHIVO_ENV": str(tmp_path / "no-existe"),
        "SECRET_KEY": "solo-para-la-prueba",
        "DATABASE_URL": "postgres://x:x@localhost:5432/x",
        "ALLOWED_HOSTS": "localhost",
        "CSRF_TRUSTED_ORIGINS": "https://localhost",
    }
    entorno.pop("CUENTAS_EMISOR_LOCAL", None)
    entorno.update(variables)
    return subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        env=entorno,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("valor", ["1", "0", ""])
def test_prod_no_arranca_si_existe_la_variable_del_emisor_local(tmp_path, valor):
    resultado = _arrancar_prod(tmp_path, CUENTAS_EMISOR_LOCAL=valor)

    assert resultado.returncode != 0
    assert "CUENTAS_EMISOR_LOCAL" in resultado.stderr


def test_prod_arranca_sin_la_variable_del_emisor_local(tmp_path):
    resultado = _arrancar_prod(tmp_path)

    assert resultado.returncode == 0, resultado.stderr
