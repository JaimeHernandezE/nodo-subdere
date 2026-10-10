import pytest
from rest_framework.test import APIClient

from apps.core import foto_cut
from apps.cuentas.models import Acceso

from .conftest import CUT, http

pytestmark = pytest.mark.django_db


def buscar(texto: str):
    return APIClient().get("/api/v1/servicios/cut/buscar", {"q": texto})


def por_codigo(codigo: str):
    return APIClient().get(f"/api/v1/servicios/cut/codigo/{codigo}")


def test_busca_por_nombre_sin_tildes_y_trae_sus_superiores(fuente):
    respuesta = buscar("nunoa")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["origen"] == "fuente"
    (nunoa,) = cuerpo["datos"]
    assert (nunoa["nivel"], nunoa["codigo"], nunoa["nombre"]) == ("comuna", "13120", "Ñuñoa")
    assert nunoa["provincia"] == {"codigo": "131", "nombre": "Santiago"}
    assert nunoa["region"]["codigo"] == "13"


def test_una_busqueda_de_menos_de_dos_caracteres_da_400(fuente):
    respuesta = buscar(" a ")

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION_FALLIDA"
    assert fuente.pedidos == []


@pytest.mark.parametrize(
    "codigo,nivel,canonico",
    [("1101", "comuna", "01101"), ("011", "provincia", "011"), ("1", "region", "01")],
)
def test_el_camino_inverso_devuelve_el_codigo_canonico(fuente, codigo, nivel, canonico):
    respuesta = por_codigo(codigo)

    assert respuesta.status_code == 200
    unidad = respuesta.json()["datos"]
    assert (unidad["nivel"], unidad["codigo"]) == (nivel, canonico)


def test_una_region_no_tiene_superiores_y_una_provincia_solo_region(fuente):
    region = por_codigo("13").json()["datos"]
    provincia = por_codigo("131").json()["datos"]

    assert region["provincia"] is None and region["region"] is None
    assert provincia["provincia"] is None
    assert provincia["region"]["codigo"] == "13"


def test_un_codigo_mal_formado_da_400_y_uno_inexistente_404(fuente):
    mal = por_codigo("abc")
    inexistente = por_codigo("99999")

    assert (mal.status_code, mal.json()["error"]["codigo"]) == (400, "CODIGO_INVALIDO")
    assert (inexistente.status_code, inexistente.json()["error"]["codigo"]) == (
        404,
        "NO_ENCONTRADO",
    )


def test_con_la_fuente_caida_responde_la_foto_y_lo_dice(fuente):
    for listado in foto_cut.LISTADOS:
        fuente.rutas[f"{CUT}/{listado}"] = http(503)

    respuesta = buscar("nunoa")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["origen"] == "foto"
    assert cuerpo["obtenido_en"].startswith(foto_cut.leer("comunas")["descargado_en"][:10])
    assert [u["codigo"] for u in cuerpo["datos"]] == ["13120"]


def test_es_publico_y_no_escribe_accesos(fuente):
    cliente = APIClient()
    cliente.credentials(HTTP_AUTHORIZATION="Bearer basura")

    assert cliente.get("/api/v1/servicios/cut/codigo/13120").status_code == 200
    assert not Acceso.objects.exists()
