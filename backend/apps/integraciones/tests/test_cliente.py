import urllib.error

import pytest

from apps.integraciones.cliente import LIMITE_BYTES, pedir_json
from apps.integraciones.errores import (
    FuenteNoDisponible,
    NoEncontrado,
    RespuestaDemasiadoGrande,
)

URL = "https://fuente.prueba/datos"


def test_ninguna_prueba_sale_a_la_red():
    with pytest.raises(AssertionError, match="salir a la red"):
        pedir_json(URL)


def test_un_404_es_no_encontrado_sin_reintento(fuente):
    with pytest.raises(NoEncontrado):
        pedir_json(URL)
    assert len(fuente.pedidos) == 1


@pytest.mark.parametrize("falla", [401, 403])
def test_la_credencial_rechazada_es_fuente_no_disponible_sin_reintento(fuente, falla):
    fuente.rutas[URL] = urllib.error.HTTPError(URL, falla, "error", {}, None)

    with pytest.raises(FuenteNoDisponible) as error:
        pedir_json(URL)

    assert error.value.codigo == "FUENTE_NO_DISPONIBLE"
    assert len(fuente.pedidos) == 1


@pytest.mark.parametrize(
    "falla",
    [urllib.error.HTTPError(URL, 502, "error", {}, None), urllib.error.URLError("sin ruta")],
)
def test_red_o_5xx_se_reintenta_una_vez(fuente, falla):
    fuente.rutas[URL] = falla

    with pytest.raises(FuenteNoDisponible):
        pedir_json(URL)

    assert len(fuente.pedidos) == 2


def test_una_respuesta_de_mas_de_1_mb_se_rechaza(fuente):
    fuente.rutas[URL] = b"[" + b"0," * (LIMITE_BYTES // 2) + b"0]"

    with pytest.raises(RespuestaDemasiadoGrande) as error:
        pedir_json(URL)

    assert (error.value.status, error.value.codigo) == (502, "RESPUESTA_DEMASIADO_GRANDE")


def test_algo_que_no_es_json_es_fuente_no_disponible(fuente):
    fuente.rutas[URL] = b"<html>mantenimiento</html>"
    with pytest.raises(FuenteNoDisponible):
        pedir_json(URL)


def test_el_error_llega_al_sobre_unico(fuente):
    from apps.core.errores import manejador_de_excepciones

    respuesta = manejador_de_excepciones(FuenteNoDisponible(), {})

    assert respuesta.status_code == 503
    assert respuesta.data["error"]["codigo"] == "FUENTE_NO_DISPONIBLE"
