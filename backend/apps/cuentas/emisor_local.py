"""Emisor de tokens para desarrollo local, sin Keycloak.

Solo se acepta con `CUENTAS_EMISOR_LOCAL` activo, y `prod.py` no arranca si esa variable
existe. Después de verificar la firma, el token sigue el mismo camino que uno del realm.
"""

import time
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings

EMISOR = "nodo-local"
KID = "nodo-local"
ALGORITMO = "RS256"


def _ruta() -> Path:
    return Path(settings.CUENTAS_CLAVE_LOCAL)


def _clave_privada(crear: bool = False):
    ruta = _ruta()
    if not ruta.is_file():
        if not crear:
            return None
        clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_bytes(
            clave.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        return clave
    return serialization.load_pem_private_key(ruta.read_bytes(), password=None)


def clave_publica():
    """La clave para verificar, o None si nunca se emitió un token local."""
    clave = _clave_privada()
    return clave.public_key() if clave else None


def emitir(numero: int, dv: str, nombre: str, minutos: int = 60) -> str:
    ahora = int(time.time())
    reclamos = {
        "iss": EMISOR,
        "aud": EMISOR,
        "sub": f"local-{numero}",
        "iat": ahora,
        "exp": ahora + minutos * 60,
        "RolUnico": {"numero": numero, "DV": dv, "tipo": "RUN"},
        "name": nombre,
    }
    return jwt.encode(
        reclamos, _clave_privada(crear=True), algorithm=ALGORITMO, headers={"kid": KID}
    )
