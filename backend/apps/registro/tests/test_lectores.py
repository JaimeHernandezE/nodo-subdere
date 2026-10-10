import base64
import io
import json
import urllib.error
import urllib.request

import pytest

from apps.registro.errores import FuenteNoDisponible
from apps.registro.lectores import LIMITE_BYTES, LectorGitLab
from apps.registro.models import Fuente, problema_de_url
from apps.registro.sincronizacion import sincronizar

from .conftest import API, URL, ficha

pytestmark = pytest.mark.django_db


class Respuesta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class GitLabFalso:
    """Reemplaza `urlopen`: anota cada pedido y responde lo que se le diga."""

    def __init__(self, *, datos=None, error=None):
        self.datos = datos
        self.error = error
        self.pedidos: list[urllib.request.Request] = []

    def __call__(self, pedido, timeout=None):
        self.pedidos.append(pedido)
        if self.error:
            raise self.error
        return Respuesta(json.dumps(self.datos).encode())


def archivo(contenido: str, **extra) -> dict:
    return {
        "content": base64.b64encode(contenido.encode()).decode(),
        "commit_id": "c" * 40,
        "last_commit_id": "d" * 40,
        **extra,
    }


def http(codigo: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://gitlab.prueba", codigo, "error", {}, None)


@pytest.fixture
def gitlab(monkeypatch):
    def _gitlab(**kwargs) -> GitLabFalso:
        falso = GitLabFalso(**kwargs)
        monkeypatch.setattr(urllib.request, "urlopen", falso)
        return falso

    return _gitlab


def test_ninguna_prueba_sale_a_la_red(fuente):
    with pytest.raises(AssertionError, match="salir a la red"):
        LectorGitLab().leer_ficha(fuente)


# Prueba 12: la cabeza de la rama, no el último commit que tocó la ficha


def test_la_ficha_se_lee_en_la_rama_y_vale_el_commit_de_la_cabeza(fuente, gitlab):
    falso = gitlab(datos=archivo("ficha: 1\n"))

    leido = LectorGitLab().leer_ficha(fuente)

    assert leido.commit == "c" * 40
    assert leido.contenido == "ficha: 1\n"
    pedido = falso.pedidos[0]
    assert pedido.full_url == (
        f"{API}/projects/modernizacion%2Fcut/repository/files/nodo%2Fficha.yaml?ref=main"
    )
    assert pedido.get_header("Private-token") == "token-de-prueba"


def test_un_archivo_se_lee_en_el_commit_pedido(fuente, gitlab):
    falso = gitlab(datos=archivo("openapi: 3.0.3\n"))

    LectorGitLab().leer_archivo(fuente, "nodo/cut.openapi.yaml", "c" * 40)

    assert falso.pedidos[0].full_url.endswith(f"nodo%2Fcut.openapi.yaml?ref={'c' * 40}")


def test_un_archivo_de_mas_de_1_mb_se_rechaza(fuente, gitlab):
    gitlab(datos=archivo("x", size=LIMITE_BYTES + 1))

    with pytest.raises(FuenteNoDisponible, match="1 MB"):
        LectorGitLab().leer_ficha(fuente)


def test_un_archivo_que_no_es_utf8_se_rechaza(fuente, gitlab):
    datos = archivo("")
    datos["content"] = base64.b64encode("ñ".encode("latin-1")).decode()
    gitlab(datos=datos)

    with pytest.raises(FuenteNoDisponible, match="UTF-8"):
        LectorGitLab().leer_ficha(fuente)


# Prueba 15 y los demás motivos


@pytest.mark.parametrize(
    ("error", "esperado"),
    [
        (http(401), "token del nodo (401)"),
        (http(403), "rol Reporter"),
        (http(404), "rol Reporter"),
        (http(500), "respondió 500"),
        (urllib.error.URLError("sin ruta"), "red de SUBDERE o por VPN"),
        (TimeoutError(), "no respondió"),
    ],
)
def test_cada_falla_de_gitlab_deja_un_motivo_que_dice_que_hacer(fuente, gitlab, error, esperado):
    gitlab(error=error)

    lectura = sincronizar(fuente)

    assert not lectura.valida
    assert esperado in lectura.motivo


def test_el_motivo_de_un_404_nombra_la_rama_y_la_ruta(fuente, gitlab):
    gitlab(error=http(404))
    lectura = sincronizar(fuente)

    assert "nodo/ficha.yaml en «main» de modernizacion/cut" in lectura.motivo


def test_sin_configuracion_no_se_pide_nada(fuente, gitlab, settings):
    settings.REGISTRO_GIT_TOKEN = ""
    falso = gitlab(datos=archivo(ficha()))

    lectura = sincronizar(fuente)

    assert "no está configurada" in lectura.motivo
    assert falso.pedidos == []


def test_un_contrato_que_falla_al_leerse_deja_el_motivo_del_archivo(fuente, monkeypatch):
    respuestas = iter([archivo(ficha())])

    def urlopen(pedido, timeout=None):
        try:
            return Respuesta(json.dumps(next(respuestas)).encode())
        except StopIteration:
            raise http(403) from None

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)

    lectura = sincronizar(fuente)

    assert lectura.commit == "c" * 40
    assert lectura.motivo.startswith("especificacion.archivo: GitLab no deja leer")


# La dirección de una fuente


@pytest.mark.parametrize(
    ("url", "problema"),
    [
        (URL, ""),
        (f"{URL}.git", ""),
        ("http://gitlab.prueba/modernizacion/cut", "https"),
        ("https://gitlab.prueba/cut", "grupo y el proyecto"),
        (f"{URL}?ref=main", "sin parámetros"),
        ("https://github.com/modernizacion/cut", "gitlab.prueba"),
    ],
)
def test_la_direccion_de_una_fuente(url, problema):
    if problema:
        assert problema in problema_de_url(url)
    else:
        assert problema_de_url(url) == ""


def test_el_proyecto_se_toma_de_la_direccion():
    assert Fuente(url=f"{URL}.git").proyecto == "modernizacion/cut"
