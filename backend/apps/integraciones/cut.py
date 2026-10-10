"""El Código Único Territorial, desde su fuente en SEM. Ver INSTRUCCIONES.md §2 y §5.

La fuente entrega tres listados planos —código entero y nombre—. Acá se rellenan los
códigos a su forma canónica y la jerarquía sale del código: la provincia `011` es de la
región `01`. Sin URL, o con la fuente caída, responde la foto versionada de `core`,
diciéndolo. El CUT es dato abierto: no escribe `Acceso`.
"""

import datetime
import functools
import logging
import unicodedata
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.core import foto_cut
from apps.core.cut import canonico
from apps.core.errores import ErrorNodo

from .cliente import pedir_json
from .errores import NoEncontrado, ParametroInvalido
from .respuesta import Origen, Respuesta

registro = logging.getLogger(__name__)

NIVELES = {"regiones": "region", "provincias": "provincia", "comunas": "comuna"}

# Con la fuente caída, los tres listados van directo a la foto este tiempo: si no, cada
# consulta vuelve a esperar el tiempo de espera completo antes de caer, y la pantalla se
# cuelga igual.
RESPALDO_SEGUNDOS = 60
CLAVE_CAIDA = "integraciones:cut:caida"


@dataclass(frozen=True)
class Region:
    codigo: str
    nombre: str
    nivel = "region"


@dataclass(frozen=True)
class Provincia:
    codigo: str
    nombre: str
    nivel = "provincia"

    @property
    def region(self) -> str:
        return self.codigo[:2]


@dataclass(frozen=True)
class Comuna:
    codigo: str
    nombre: str
    nivel = "comuna"

    @property
    def provincia(self) -> str:
        return self.codigo[:3]

    @property
    def region(self) -> str:
        return self.codigo[:2]


Unidad = Region | Provincia | Comuna
CLASES = {"regiones": Region, "provincias": Provincia, "comunas": Comuna}


def sin_tildes(texto: str) -> str:
    """«Ñuñoa» y «nunoa» se comparan iguales."""
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c)).casefold().strip()


def _codigo(codigo, nivel: str) -> str:
    try:
        return canonico(codigo, nivel)
    except ValueError as error:
        raise ParametroInvalido(codigo="CODIGO_INVALIDO", mensaje=str(error)) from None


def _unidades(listado: str, filas) -> list[Unidad]:
    nivel = NIVELES[listado]
    campo = foto_cut.LISTADOS[listado]
    clase = CLASES[listado]
    unidades = [clase(codigo=canonico(f[campo], nivel), nombre=str(f["nombre"])) for f in filas]
    return sorted(unidades, key=lambda u: u.codigo)


@functools.cache
def _foto(listado: str) -> Respuesta:
    foto = foto_cut.leer(listado)
    return Respuesta(
        datos=_unidades(listado, foto["datos"]),
        origen=Origen.FOTO,
        obtenido_en=datetime.datetime.fromisoformat(foto["descargado_en"]),
    )


def _juntar(*respuestas: Respuesta, datos) -> Respuesta:
    """Si alguna parte salió de la foto, el todo también: se informa lo menos fresco."""
    origen = Origen.FOTO if any(r.origen == Origen.FOTO for r in respuestas) else Origen.FUENTE
    return Respuesta(datos=datos, origen=origen, obtenido_en=min(r.obtenido_en for r in respuestas))


class AdaptadorCUT:
    def __init__(self, url: str | None = None, cache_segundos: int | None = None):
        self.url = (settings.CUT_API_URL if url is None else url).rstrip("/")
        self.cache_segundos = (
            settings.CUT_CACHE_SEGUNDOS if cache_segundos is None else cache_segundos
        )

    def regiones(self) -> Respuesta:
        return self._listado("regiones")

    def provincias(self, region: str | None = None) -> Respuesta:
        provincias = self._listado("provincias")
        if region is None:
            return provincias
        region = self._existente(_codigo(region, "region"), self.regiones())
        return provincias.con([p for p in provincias.datos if p.region == region])

    def comunas(self, provincia: str | None = None) -> Respuesta:
        comunas = self._listado("comunas")
        if provincia is None:
            return comunas
        provincia = self._existente(_codigo(provincia, "provincia"), self.provincias())
        return comunas.con([c for c in comunas.datos if c.provincia == provincia])

    def por_codigo(self, codigo: str) -> Respuesta:
        """El nivel lo da el largo: 1-2 dígitos región, 3 provincia, 4-5 comuna."""
        texto = str(codigo).strip()
        if not texto.isascii() or not texto.isdigit() or not 1 <= len(texto) <= 5:
            raise ParametroInvalido(
                codigo="CODIGO_INVALIDO",
                mensaje="Un código territorial tiene entre uno y cinco dígitos.",
            )
        nivel, listado = (
            ("region", "regiones")
            if len(texto) <= 2
            else ("provincia", "provincias")
            if len(texto) == 3
            else ("comuna", "comunas")
        )
        canonizado = _codigo(texto, nivel)
        respuesta = self._listado(listado)
        for unidad in respuesta.datos:
            if unidad.codigo == canonizado:
                return respuesta.con(unidad)
        raise NoEncontrado(f"No hay ninguna unidad territorial con el código {canonizado}.")

    def buscar(self, texto: str) -> Respuesta:
        """Por nombre, en los tres niveles, sin tildes ni mayúsculas."""
        buscado = sin_tildes(texto or "")
        partes = [self._listado(listado) for listado in NIVELES]
        if not buscado:
            return _juntar(*partes, datos=[])
        encontradas = [
            unidad
            for parte in partes
            for unidad in parte.datos
            if buscado in sin_tildes(unidad.nombre)
        ]
        return _juntar(*partes, datos=encontradas)

    @staticmethod
    def _existente(codigo: str, respuesta: Respuesta) -> str:
        if not any(u.codigo == codigo for u in respuesta.datos):
            raise NoEncontrado(f"No existe el código {codigo}.")
        return codigo

    def _listado(self, listado: str) -> Respuesta:
        if not self.url:
            return _foto(listado)
        clave = f"integraciones:cut:{listado}"
        if (guardada := cache.get(clave)) is not None:
            return guardada
        if cache.get(CLAVE_CAIDA):
            return _foto(listado)
        try:
            filas = pedir_json(f"{self.url}/{listado}")
            respuesta = Respuesta(
                datos=_unidades(listado, filas), origen=Origen.FUENTE, obtenido_en=timezone.now()
            )
        except (ErrorNodo, KeyError, TypeError, ValueError) as error:
            # Caída, 404, demasiado grande o una forma que no se entiende: la foto, diciéndolo.
            registro.warning("CUT: %s cae a la foto (%s)", listado, type(error).__name__)
            cache.set(CLAVE_CAIDA, True, min(RESPALDO_SEGUNDOS, self.cache_segundos))
            return _foto(listado)
        cache.set(clave, respuesta, self.cache_segundos)
        return respuesta
