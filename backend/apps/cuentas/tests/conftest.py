import json
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.core.models import Municipio
from apps.core.run import digito_verificador
from apps.cuentas import autenticacion
from apps.cuentas.models import Perfil, Rol

EMISOR = "https://realm.prueba/realms/nodo"
AUDIENCIA = "nodo-api"


def generar_clave():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def jwk_publico(clave, kid: str) -> dict:
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(clave.public_key()))
    jwk.update(kid=kid, alg="RS256", use="sig")
    return jwk


class RealmFalso:
    """Hace de realm de Keycloak: publica un JWKS y firma tokens. Cuenta las descargas."""

    def __init__(self, clave):
        self.claves = {"k1": clave}
        self.descargas = 0

    def jwks(self) -> dict:
        self.descargas += 1
        return {"keys": [jwk_publico(clave, kid) for kid, clave in self.claves.items()]}

    def token(self, perfil: Perfil | None = None, *, kid="k1", clave=None, **reclamos) -> str:
        ahora = int(time.time())
        cuerpo = {
            "iss": EMISOR,
            "aud": AUDIENCIA,
            "sub": "sub-del-realm",
            "iat": ahora,
            "exp": ahora + 300,
            "name": "Nombre Desde El Token",
        }
        if perfil is not None:
            cuerpo["RolUnico"] = {"numero": perfil.run_numero, "DV": perfil.run_dv, "tipo": "RUN"}
        cuerpo.update(reclamos)
        cuerpo = {campo: valor for campo, valor in cuerpo.items() if valor is not None}
        firma = clave or self.claves[kid]
        return jwt.encode(cuerpo, firma, algorithm="RS256", headers={"kid": kid})


@pytest.fixture(autouse=True)
def _ambiente(settings):
    settings.KEYCLOAK_ISSUER = EMISOR
    settings.KEYCLOAK_AUDIENCE = AUDIENCIA
    settings.KEYCLOAK_JWKS_URL = ""
    settings.CUENTAS_EMISOR_LOCAL = False
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(scope="session")
def clave():
    return generar_clave()


@pytest.fixture
def realm(clave, monkeypatch):
    falso = RealmFalso(clave)
    monkeypatch.setattr(autenticacion, "_descargar_jwks", falso.jwks)
    return falso


@pytest.fixture
def santiago(db):
    return Municipio.objects.get(cut="13101")


@pytest.fixture
def valparaiso(db):
    return Municipio.objects.get(cut="05101")


def crear_perfil(numero: int, rol=Rol.LECTOR, municipio=None, **extra) -> Perfil:
    return Perfil.objects.create(
        run_numero=numero,
        run_dv=digito_verificador(numero),
        nombre=f"Persona {numero}",
        rol=rol,
        municipio=municipio,
        **extra,
    )


@pytest.fixture
def como(realm):
    """Un cliente de la API autenticado como `perfil`."""

    def _como(perfil: Perfil) -> APIClient:
        cliente = APIClient()
        cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {realm.token(perfil)}")
        return cliente

    return _como


@pytest.fixture
def administrador(db):
    return crear_perfil(11111111, rol=Rol.ADMINISTRADOR)


@pytest.fixture
def encargado(santiago):
    return crear_perfil(22222222, municipio=santiago, es_encargado=True)
