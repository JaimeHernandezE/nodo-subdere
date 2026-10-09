"""Autenticación con el access token del realm de Keycloak.

Keycloak autentica; el perfil del nodo autoriza. La persona se identifica por el RUN que
trae el claim `RolUnico`, no por el `sub`, que es del realm y puede cambiar.
"""

import json
import logging
import urllib.request

import jwt
from django.conf import settings
from django.core.cache import cache
from rest_framework import authentication, exceptions

from apps.core import run

from . import emisor_local
from .errores import RealmNoDisponible, SinPerfil
from .models import Perfil

logger = logging.getLogger(__name__)

ALGORITMOS = ["RS256"]
CACHE_JWKS = "cuentas:jwks"
CACHE_REFRESCO = "cuentas:jwks:refresco"
# Un kid desconocido fuerza a lo más una descarga por ventana: una rotación de claves
# no deja a nadie afuera, y un token inventado no provoca una descarga por petición.
REFRESCO_MINIMO_SEGUNDOS = 60
LARGO_NOMBRE = 200


def _token_invalido() -> exceptions.AuthenticationFailed:
    return exceptions.AuthenticationFailed("El token no es válido.")


def _url_jwks() -> str:
    if settings.KEYCLOAK_JWKS_URL:
        return settings.KEYCLOAK_JWKS_URL
    return f"{settings.KEYCLOAK_ISSUER.rstrip('/')}/protocol/openid-connect/certs"


def _descargar_jwks() -> dict:
    try:
        with urllib.request.urlopen(_url_jwks(), timeout=5) as respuesta:
            return json.load(respuesta)
    except (OSError, ValueError) as error:
        logger.error("No se pudo descargar el JWKS del realm: %s", error)
        raise RealmNoDisponible() from error


def _jwks(forzar: bool = False) -> dict:
    if not forzar:
        jwks = cache.get(CACHE_JWKS)
        if jwks is not None:
            return jwks
    jwks = _descargar_jwks()
    cache.set(CACHE_JWKS, jwks, settings.KEYCLOAK_JWKS_CACHE_SEGUNDOS)
    return jwks


def _buscar_clave(jwks: dict, kid: str | None):
    for clave in jwks.get("keys", []):
        if clave.get("kid") == kid:
            try:
                return jwt.PyJWK(clave).key
            except jwt.PyJWTError:
                return None
    return None


def _clave_del_realm(kid: str | None):
    clave = _buscar_clave(_jwks(), kid)
    if clave is None and cache.add(CACHE_REFRESCO, True, REFRESCO_MINIMO_SEGUNDOS):
        clave = _buscar_clave(_jwks(forzar=True), kid)
    if clave is None:
        raise _token_invalido()
    return clave


def verificar(token: str) -> dict:
    """Verifica firma, emisor, audiencia y expiración. Devuelve los reclamos."""
    try:
        kid = jwt.get_unverified_header(token).get("kid")
        emisor = jwt.decode(token, options={"verify_signature": False}).get("iss")
    except jwt.PyJWTError as error:
        raise _token_invalido() from error

    if settings.CUENTAS_EMISOR_LOCAL and emisor == emisor_local.EMISOR:
        clave = emisor_local.clave_publica()
        emisor_esperado = audiencia = emisor_local.EMISOR
    elif settings.KEYCLOAK_ISSUER and emisor == settings.KEYCLOAK_ISSUER:
        clave = _clave_del_realm(kid)
        emisor_esperado, audiencia = settings.KEYCLOAK_ISSUER, settings.KEYCLOAK_AUDIENCE
    else:
        raise _token_invalido()

    if clave is None:
        raise _token_invalido()
    try:
        return jwt.decode(
            token,
            clave,
            algorithms=ALGORITMOS,
            audience=audiencia,
            issuer=emisor_esperado,
            options={"require": ["exp", "iss", "aud"]},
        )
    except jwt.PyJWTError as error:
        raise _token_invalido() from error


def _nombre(reclamos: dict) -> str:
    nombre = reclamos.get("name")
    if isinstance(nombre, dict):
        partes = [*nombre.get("nombres", []), *nombre.get("apellidos", [])]
    elif isinstance(nombre, str):
        partes = [nombre]
    else:
        partes = [
            reclamos.get("firstName") or reclamos.get("given_name"),
            reclamos.get("lastName") or reclamos.get("family_name"),
        ]
    texto = " ".join(str(parte).strip() for parte in partes if parte and str(parte).strip())
    return texto[:LARGO_NOMBRE]


def resolver_perfil(reclamos: dict) -> Perfil:
    rol_unico = reclamos.get("RolUnico")
    try:
        if not isinstance(rol_unico, dict):
            raise ValueError("sin RolUnico")
        numero, _ = run.validar(rol_unico.get("numero"), rol_unico.get("DV"))
    except ValueError:
        logger.warning(
            "Token válido sin un RolUnico utilizable (sub=%s). Revisar los mapeos del realm.",
            reclamos.get("sub"),
        )
        raise SinPerfil() from None

    tipo = str(rol_unico.get("tipo") or "RUN").strip().upper()
    perfil = (
        Perfil.objects.select_related("municipio")
        .filter(run_tipo=tipo, run_numero=numero, activo=True)
        .first()
    )
    if perfil is None:
        raise SinPerfil()

    sub = str(reclamos.get("sub") or "")
    nombre = _nombre(reclamos) or perfil.nombre
    if (perfil.sub, perfil.nombre) != (sub, nombre):
        perfil.sub, perfil.nombre = sub, nombre
        perfil.save(update_fields=["sub", "nombre", "actualizado_en"])
    return perfil


class AutenticacionRealm(authentication.BaseAuthentication):
    def authenticate(self, request):
        partes = authentication.get_authorization_header(request).split()
        if not partes or partes[0].lower() != b"bearer":
            return None
        if len(partes) != 2:
            raise _token_invalido()
        try:
            token = partes[1].decode("ascii")
        except UnicodeError as error:
            raise _token_invalido() from error

        reclamos = verificar(token)
        return resolver_perfil(reclamos), reclamos

    def authenticate_header(self, request):
        return 'Bearer realm="nodo"'
