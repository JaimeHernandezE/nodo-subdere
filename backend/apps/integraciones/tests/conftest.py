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
PERMISOS = "https://permisos.prueba/api/bum/v1"

# Respuestas grabadas: los ejemplos del contrato propuesto (fiscalizacion.openapi.yaml).
VEHICULO = {
    "patente": "BDPF18",
    "marca": "TOYOTA",
    "modelo": "YARIS",
    "color": "BLANCO",
    "anio_fabricacion": 2019,
    "tipo": "AUTOMOVIL",
}
PERMISOS_DEL_VEHICULO = [
    {
        "anio": 2026,
        "estado": "VIGENTE",
        "comuna": {"cut": "13101", "nombre": "Santiago"},
        "monto_total": 214300,
        "vigente_hasta": "2027-03-31",
        "cuotas": [
            {"numero": 1, "monto": 107150, "fecha_pago": "2026-03-18", "medio_pago": "EN LINEA"},
            {"numero": 2, "monto": 107150, "fecha_pago": "2026-08-14", "medio_pago": "EN LINEA"},
        ],
    },
    {
        "anio": 2024,
        "estado": "VENCIDO",
        "comuna": {"cut": "13101", "nombre": "Santiago"},
        "monto_total": 198000,
        "cuotas": [],
    },
]
PROVISIONALES = [
    {
        "anio": 2026,
        "semestre": 2,
        "comuna": {"cut": "13123", "nombre": "Providencia"},
        "marca": "HONDA",
        "modelo": "PILOT",
        "titular": {"rut": "77.777.777-7", "razon_social": "AUTOMOTORA DE EJEMPLO SPA"},
    }
]


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
    falsa.rutas[f"{PERMISOS}/vehiculos/BDPF18"] = VEHICULO
    falsa.rutas[f"{PERMISOS}/vehiculos/BDPF18/permisos"] = PERMISOS_DEL_VEHICULO
    falsa.rutas[f"{PERMISOS}/permisos-provisionales/PR0909"] = PROVISIONALES
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
