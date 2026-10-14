import base64
import hashlib
import io
import json
import urllib.error
import urllib.parse
import urllib.request

import pytest

from apps.registro.errores import RepositorioNoDisponible
from apps.registro.lectores import LIMITE_BYTES, LectorGitLab
from apps.registro.models import Fuente, problema_de_url
from apps.registro.sincronizacion import sincronizar

from .conftest import API, RUTA_CONTRATO, RUTA_FICHA, URL, ficha

pytestmark = pytest.mark.django_db

ID_PROYECTO = 7
CABEZA = "c" * 40


class Respuesta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _sha(ruta: str) -> str:
    return hashlib.sha1(ruta.encode()).hexdigest()


class GitLabFalso:
    """Reemplaza `urlopen`: anota cada pedido y responde como la API de GitLab.

    `archivos` va de ruta a la respuesta de su blob, todos en la rama `main`, cuya cabeza es
    `CABEZA`. `errores` va de ruta a la excepción con que termina el pedido de su blob.
    `error`, si se da, termina cualquier pedido.
    """

    def __init__(self, *, archivos=None, errores=None, error=None):
        self.archivos = dict(archivos or {})
        self.errores = dict(errores or {})
        self.error = error
        self.pedidos: list[urllib.request.Request] = []

    def __call__(self, pedido, timeout=None):
        self.pedidos.append(pedido)
        if self.error:
            raise self.error
        partes = urllib.parse.urlsplit(pedido.full_url)
        consulta = dict(urllib.parse.parse_qsl(partes.query))
        camino = partes.path.removeprefix(urllib.parse.urlsplit(API).path)
        repositorio = f"/projects/{ID_PROYECTO}/repository"
        if camino == "/projects":
            datos = [{"id": ID_PROYECTO, "path_with_namespace": "modernizacion/cut"}]
        elif camino == f"{repositorio}/commits":
            datos = [{"id": CABEZA}] if consulta["ref_name"] == "main" else []
        elif camino == f"{repositorio}/tree":
            datos = [
                {"name": ruta.rpartition("/")[2], "type": "blob", "id": _sha(ruta)}
                for ruta in self.archivos
                if ruta.rpartition("/")[0] == consulta.get("path", "")
            ]
        elif camino.startswith(f"{repositorio}/blobs/"):
            ruta = next(r for r in self.archivos if _sha(r) == camino.rpartition("/")[2])
            if ruta in self.errores:
                raise self.errores[ruta]
            datos = self.archivos[ruta]
        else:
            raise AssertionError(f"Pedido inesperado: {pedido.full_url}")
        return Respuesta(json.dumps(datos).encode())


def archivo(contenido: str, **extra) -> dict:
    return {"content": base64.b64encode(contenido.encode()).decode(), **extra}


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
    falso = gitlab(archivos={RUTA_FICHA: archivo("ficha: 1\n")})

    leido = LectorGitLab().leer_ficha(fuente)

    assert leido.commit == CABEZA
    assert leido.contenido == "ficha: 1\n"
    urls = [pedido.full_url for pedido in falso.pedidos]
    assert urls[1] == f"{API}/projects/{ID_PROYECTO}/repository/commits?ref_name=main&per_page=1"
    assert f"ref={CABEZA}" in urls[2]
    assert all(pedido.get_header("Private-token") == "token-de-prueba" for pedido in falso.pedidos)


def test_ninguna_direccion_lleva_una_barra_codificada_en_el_camino(fuente, gitlab):
    falso = gitlab(archivos={RUTA_FICHA: archivo("ficha: 1\n")})

    LectorGitLab().leer_ficha(fuente)

    assert all("%2F" not in urllib.parse.urlsplit(p.full_url).path for p in falso.pedidos)


def test_un_archivo_se_lee_en_el_commit_pedido(fuente, gitlab):
    falso = gitlab(archivos={RUTA_CONTRATO: archivo("openapi: 3.0.3\n")})

    contenido = LectorGitLab().leer_archivo(fuente, RUTA_CONTRATO, CABEZA)

    assert contenido == "openapi: 3.0.3\n"
    assert not any("/commits" in pedido.full_url for pedido in falso.pedidos)
    arbol = next(p.full_url for p in falso.pedidos if "/tree" in p.full_url)
    assert f"ref={CABEZA}" in arbol


def test_el_proyecto_se_busca_una_sola_vez_por_lector(fuente, gitlab):
    falso = gitlab(archivos={RUTA_FICHA: archivo("ficha: 1\n"), RUTA_CONTRATO: archivo("x")})
    lector = LectorGitLab()

    leido = lector.leer_ficha(fuente)
    lector.leer_archivo(fuente, RUTA_CONTRATO, leido.commit)

    busquedas = [
        p for p in falso.pedidos if urllib.parse.urlsplit(p.full_url).path.endswith("/projects")
    ]
    assert len(busquedas) == 1


def test_una_rama_que_no_existe_da_el_motivo_del_404(fuente, gitlab):
    gitlab(archivos={RUTA_FICHA: archivo("ficha: 1\n")})
    fuente.rama = "otra"

    with pytest.raises(RepositorioNoDisponible, match="«otra»"):
        LectorGitLab().leer_ficha(fuente)


def test_un_archivo_que_no_esta_da_el_motivo_del_404(fuente, gitlab):
    gitlab(archivos={})

    with pytest.raises(RepositorioNoDisponible, match="rol Reporter"):
        LectorGitLab().leer_ficha(fuente)


def test_un_archivo_de_mas_de_1_mb_se_rechaza(fuente, gitlab):
    gitlab(archivos={RUTA_FICHA: archivo("x", size=LIMITE_BYTES + 1)})

    with pytest.raises(RepositorioNoDisponible, match="1 MB"):
        LectorGitLab().leer_ficha(fuente)


def test_un_archivo_que_no_es_utf8_se_rechaza(fuente, gitlab):
    datos = archivo("")
    datos["content"] = base64.b64encode("ñ".encode("latin-1")).decode()
    gitlab(archivos={RUTA_FICHA: datos})

    with pytest.raises(RepositorioNoDisponible, match="UTF-8"):
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
    falso = gitlab(archivos={RUTA_FICHA: archivo(ficha())})

    lectura = sincronizar(fuente)

    assert "no está configurada" in lectura.motivo
    assert falso.pedidos == []


def test_un_contrato_que_falla_al_leerse_deja_el_motivo_del_archivo(fuente, gitlab):
    gitlab(
        archivos={RUTA_FICHA: archivo(ficha()), RUTA_CONTRATO: archivo("")},
        errores={RUTA_CONTRATO: http(403)},
    )

    lectura = sincronizar(fuente)

    assert lectura.commit == CABEZA
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
