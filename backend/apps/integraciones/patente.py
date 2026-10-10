"""Patentes de vehículos, según el contrato de permisos de circulación.

Se normalizan y validan **antes** de llamar a la fuente: una patente mal escrita no
gasta una consulta ni deja un acceso a datos de nadie.

`PR` y cuatro dígitos calza con los dos patrones: es una provisoria y también tiene la
forma antigua de dos letras y cuatro dígitos. El contrato no lo resuelve; quien llama
decide cuál consulta.
"""

import re

from .errores import ParametroInvalido

PATENTE = re.compile(r"^([A-Z]{2}[0-9]{4}|[A-Z]{4}[0-9]{2})$")
PROVISORIA = re.compile(r"^PR[0-9]{4}$")
SEPARADORES = re.compile(r"[\s.\-·]")


def normalizar(texto) -> str:
    """Sin espacios, guiones ni puntos, y en mayúsculas: `bd-pf·18` es `BDPF18`."""
    if not isinstance(texto, str):
        raise ParametroInvalido(codigo="PATENTE_INVALIDA", mensaje="La patente debe ser texto.")
    return SEPARADORES.sub("", texto).upper()


def validar(texto) -> str:
    patente = normalizar(texto)
    if not PATENTE.match(patente):
        raise ParametroInvalido(
            codigo="PATENTE_INVALIDA",
            mensaje="La patente debe tener dos letras y cuatro dígitos, "
            "o cuatro letras y dos dígitos.",
        )
    return patente


def validar_provisoria(texto) -> str:
    patente = normalizar(texto)
    if not PROVISORIA.match(patente):
        raise ParametroInvalido(
            codigo="PATENTE_INVALIDA",
            mensaje="Una patente provisoria tiene el prefijo PR y cuatro dígitos.",
        )
    return patente


def es_provisoria(texto) -> bool:
    return isinstance(texto, str) and bool(PROVISORIA.match(normalizar(texto)))
