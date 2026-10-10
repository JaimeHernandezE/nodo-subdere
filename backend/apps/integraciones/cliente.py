"""La única salida HTTP de los adaptadores. Ver INSTRUCCIONES.md §3 y §4."""

import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

from .errores import FuenteNoDisponible, NoEncontrado, RespuestaDemasiadoGrande

LIMITE_BYTES = 1024 * 1024

registro = logging.getLogger(__name__)


def pedir_json(url: str, *, cabeceras: dict | None = None, espera: float | None = None):
    """GET con tiempo de espera, un reintento ante red o 5xx, y el límite de 1 MB.

    Un 404 es `NoEncontrado`; todo lo demás que no sea 2xx es `FuenteNoDisponible`.
    """
    espera = settings.INTEGRACIONES_TIEMPO_ESPERA_SEGUNDOS if espera is None else espera
    pedido = urllib.request.Request(
        url, headers={"Accept": "application/json", **(cabeceras or {})}
    )
    for intento in (1, 2):
        try:
            with urllib.request.urlopen(pedido, timeout=espera) as respuesta:
                crudo = respuesta.read(LIMITE_BYTES + 1)
            break
        except urllib.error.HTTPError as error:
            if error.code == 404:
                raise NoEncontrado() from None
            if error.code >= 500 and intento == 1:
                continue
            # 401 y 403 son la credencial del nodo: configuración, no culpa de quien consulta.
            registro.warning("La fuente %s respondió %s", url, error.code)
            raise FuenteNoDisponible() from None
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if intento == 1:
                continue
            registro.warning("La fuente %s no respondió: %s", url, error)
            raise FuenteNoDisponible() from None

    if len(crudo) > LIMITE_BYTES:
        raise RespuestaDemasiadoGrande()
    try:
        return json.loads(crudo)
    except ValueError:
        registro.warning("La fuente %s respondió algo que no es JSON", url)
        raise FuenteNoDisponible() from None
