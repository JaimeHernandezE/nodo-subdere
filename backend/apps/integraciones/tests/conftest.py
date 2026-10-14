import copy
import io
import json
import time
import urllib.error
import urllib.request
from types import SimpleNamespace

import pytest
from django.core.cache import cache

from apps.core import foto_cut
from apps.cuentas.models import Acceso
from apps.cuentas.tests.conftest import crear_perfil
from apps.integraciones.permisos import Contexto

CUT = "https://cut.prueba/api/utilitarios"
PERMISOS = "https://permisos.prueba/api/bum"


def pago(ano, tipo_pago, fecha_pago, estado, institucion="SANTIAGO", **campos):
    return {
        "ano": ano,
        "monto_cuota": 107150,
        "fecha_pago_cuota": fecha_pago,
        "tipo_pago": tipo_pago,
        "fecha_vigencia": f"31-03-{ano + 1}",
        "monto_total": 214300,
        "institucion_id": 69070100,
        "institucion_nombre": institucion,
        "nro_serie_documento": None,
        "codigo_sii": None,
        "estado": estado,
        **campos,
    }


# Respuesta grabada con la forma de la API de fiscalización de SEM, y datos sintéticos.
FISCALIZACION = {
    "data": {
        "id": 1,
        "patente": "BDPF18",
        "marca": "TOYOTA",
        "modelo": "YARIS",
        "color": "BLANCO",
        "ano_fabricacion": 2019,
        "chasis": "SINTETICO0000001",
        "pagos": [
            pago(2026, "2", "14-08-2026", "VIGENTE"),
            pago(2026, "1", "18-03-2026", "VIGENTE"),
            pago(2024, "T", "12-03-2024", "VENCIDO", institucion="", fecha_vigencia=None),
        ],
    }
}


class Respuesta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def http(codigo: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://fuente.prueba", codigo, "error", {}, None)


class FuenteFalsa:
    """Reemplaza `urlopen`. `rutas` va de URL a un cuerpo JSON, a bytes o a una excepción."""

    def __init__(self):
        self.rutas: dict = {}
        self.pedidos: list[urllib.request.Request] = []

    def __call__(self, pedido, timeout=None):
        self.pedidos.append(pedido)
        respuesta = self.rutas.get(pedido.full_url, http(404))
        if isinstance(respuesta, BaseException):
            raise respuesta
        if isinstance(respuesta, bytes):
            return Respuesta(respuesta)
        return Respuesta(json.dumps(respuesta).encode())

    def urls(self) -> list[str]:
        return [p.full_url for p in self.pedidos]


@pytest.fixture(autouse=True)
def _sin_red(settings, monkeypatch):
    """Ninguna prueba sale a la red, y cada una parte con el caché vacío."""
    settings.CUT_API_URL = CUT
    settings.PERMISOS_CIRCULACION_API_URL = PERMISOS

    def prohibido(*args, **kwargs):
        raise AssertionError("Una prueba intentó salir a la red.")

    monkeypatch.setattr(urllib.request, "urlopen", prohibido)
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def fuente(monkeypatch):
    falsa = FuenteFalsa()
    for listado in foto_cut.LISTADOS:
        falsa.rutas[f"{CUT}/{listado}"] = foto_cut.leer(listado)["datos"]
    falsa.rutas[f"{PERMISOS}/fiscalizaciones/BDPF18"] = copy.deepcopy(FISCALIZACION)
    monkeypatch.setattr(urllib.request, "urlopen", falsa)
    return falsa


@pytest.fixture
def reloj(monkeypatch):
    """Adelanta el reloj que usa el caché."""
    base = time.time()
    estado = {"segundos": 0}
    monkeypatch.setattr(time, "time", lambda: base + estado["segundos"])

    def adelantar(segundos: int):
        estado["segundos"] += segundos

    return adelantar


@pytest.fixture
def fiscalizador(db):
    return crear_perfil(55555555)


@pytest.fixture
def contexto(fiscalizador):
    peticion = SimpleNamespace(procedimiento="fiscalizacion-transito", id_tramite="T-1")
    return Contexto(perfil=fiscalizador, canal=Acceso.Canal.PANTALLA, request=peticion)
