"""Permisos de circulación, según el contrato propuesto. Ver INSTRUCCIONES.md §2, §3 y §5.

Cada consulta entrega datos asociados a una persona, así que este adaptador **exige** un
`Contexto` y registra él mismo cada consulta en `cuentas.Acceso`: también la que sale del
caché, la que no encuentra nada y la que falla. Ningún llamador puede saltárselo.

Sin URL, responde la muestra sintética de `muestras/`, diciéndolo. Con URL y la fuente
caída, `FuenteNoDisponible`: nunca datos inventados sobre una patente que puede existir.
"""

import datetime
import functools
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.core import run
from apps.core.errores import ErrorNodo
from apps.cuentas.actuaciones import registrar_acceso
from apps.cuentas.models import Acceso, Perfil

from . import patente as patentes
from .cliente import pedir_json
from .errores import FuenteNoDisponible, NoEncontrado, ParametroInvalido
from .respuesta import Origen, Respuesta

NODO = "permisos-de-circulacion"
MUESTRA = Path(__file__).resolve().parent / "muestras" / "permisos.json"
ANIO_MINIMO = 1990

registro = logging.getLogger(__name__)


@dataclass(frozen=True)
class Contexto:
    """Quién consulta, por qué canal, y la petición con su procedimiento y trámite."""

    perfil: Perfil
    canal: str
    request: object = None

    def __post_init__(self):
        if not isinstance(self.perfil, Perfil):
            raise TypeError("Una consulta a datos de personas exige un perfil.")
        if self.canal not in Acceso.Canal.values:
            raise TypeError(f"Canal desconocido: {self.canal!r}.")

    def cabeceras(self) -> dict:
        """Los metadatos que viajan a la fuente. La identidad de la persona, no."""
        cabeceras = {
            "X-Procedimiento": getattr(self.request, "procedimiento", ""),
            "X-Id-Tramite": getattr(self.request, "id_tramite", ""),
        }
        return {nombre: valor for nombre, valor in cabeceras.items() if valor}


@dataclass(frozen=True)
class Vehiculo:
    patente: str
    marca: str
    modelo: str
    anio_fabricacion: int
    color: str = ""
    tipo: str = ""


@dataclass(frozen=True)
class ComunaDelPermiso:
    cut: str
    nombre: str


@dataclass(frozen=True)
class Cuota:
    numero: int
    monto: int
    fecha_pago: datetime.date
    medio_pago: str = ""


@dataclass(frozen=True)
class Permiso:
    anio: int
    estado: str
    comuna: ComunaDelPermiso
    monto_total: int
    vigente_hasta: datetime.date | None = None
    cuotas: tuple[Cuota, ...] = ()


@dataclass(frozen=True)
class TitularEmpresa:
    rut: str
    razon_social: str


@dataclass(frozen=True)
class PermisoProvisional:
    anio: int
    semestre: int
    comuna: ComunaDelPermiso
    titular: TitularEmpresa
    marca: str = ""
    modelo: str = ""


def _fecha(valor) -> datetime.date | None:
    return datetime.date.fromisoformat(valor) if valor else None


def _rut(texto: str) -> str:
    try:
        return run.formatear(*run.leer(texto))
    except ValueError:
        return str(texto)


def _comuna(datos: dict) -> ComunaDelPermiso:
    return ComunaDelPermiso(cut=str(datos["cut"]), nombre=str(datos["nombre"]))


def _vehiculo(datos: dict) -> Vehiculo:
    return Vehiculo(
        patente=str(datos["patente"]),
        marca=str(datos["marca"]),
        modelo=str(datos["modelo"]),
        anio_fabricacion=int(datos["anio_fabricacion"]),
        color=str(datos.get("color") or ""),
        tipo=str(datos.get("tipo") or ""),
    )


def _permisos(datos: list) -> list[Permiso]:
    return [
        Permiso(
            anio=int(p["anio"]),
            estado=str(p["estado"]),
            comuna=_comuna(p["comuna"]),
            monto_total=int(p["monto_total"]),
            vigente_hasta=_fecha(p.get("vigente_hasta")),
            cuotas=tuple(
                Cuota(
                    numero=int(c["numero"]),
                    monto=int(c["monto"]),
                    fecha_pago=_fecha(c["fecha_pago"]),
                    medio_pago=str(c.get("medio_pago") or ""),
                )
                for c in p.get("cuotas") or []
            ),
        )
        for p in datos
    ]


def _provisionales(datos: list) -> list[PermisoProvisional]:
    return [
        PermisoProvisional(
            anio=int(p["anio"]),
            semestre=int(p["semestre"]),
            comuna=_comuna(p["comuna"]),
            titular=TitularEmpresa(
                rut=_rut(p["titular"]["rut"]), razon_social=str(p["titular"]["razon_social"])
            ),
            marca=str(p.get("marca") or ""),
            modelo=str(p.get("modelo") or ""),
        )
        for p in datos
    ]


@functools.cache
def _muestra() -> dict:
    return json.loads(MUESTRA.read_text(encoding="utf-8"))["respuestas"]


class AdaptadorPermisos:
    def __init__(self, url: str | None = None, cache_segundos: int | None = None):
        self.url = (settings.PERMISOS_CIRCULACION_API_URL if url is None else url).rstrip("/")
        self.cache_segundos = (
            settings.PERMISOS_CIRCULACION_CACHE_SEGUNDOS
            if cache_segundos is None
            else cache_segundos
        )

    def vehiculo(self, patente: str, contexto: Contexto) -> Respuesta:
        patente = patentes.validar(patente)
        return self._consultar(
            "consultar_vehiculo", contexto, {"patente": patente}, f"/vehiculos/{patente}", _vehiculo
        )

    def permisos(
        self, patente: str, contexto: Contexto, desde_anio: int | None = None
    ) -> Respuesta:
        patente = patentes.validar(patente)
        parametros = {"patente": patente}
        ruta = f"/vehiculos/{patente}/permisos"
        if desde_anio is not None:
            if isinstance(desde_anio, bool) or not isinstance(desde_anio, int):
                raise ParametroInvalido(mensaje="desde_anio debe ser un año.")
            if desde_anio < ANIO_MINIMO:
                raise ParametroInvalido(
                    mensaje=f"desde_anio no puede ser anterior a {ANIO_MINIMO}."
                )
            parametros["desde_anio"] = desde_anio
            ruta += f"?desde_anio={desde_anio}"

        def convertir(datos):
            return [p for p in _permisos(datos) if desde_anio is None or p.anio >= desde_anio]

        return self._consultar("consultar_permisos", contexto, parametros, ruta, convertir)

    def provisionales(self, patente: str, contexto: Contexto) -> Respuesta:
        patente = patentes.validar_provisoria(patente)
        return self._consultar(
            "consultar_permisos_provisionales",
            contexto,
            {"patente": patente},
            f"/permisos-provisionales/{patente}",
            _provisionales,
        )

    def _consultar(self, operacion, contexto, parametros, ruta, convertir) -> Respuesta:
        if not isinstance(contexto, Contexto):
            raise TypeError("Consultar permisos de circulación exige un Contexto.")
        try:
            respuesta = self._obtener(ruta, convertir, contexto)
        except NoEncontrado:
            self._registrar(operacion, contexto, parametros, Acceso.Resultado.NO_ENCONTRADO)
            raise
        except ErrorNodo:
            self._registrar(operacion, contexto, parametros, Acceso.Resultado.ERROR)
            raise
        self._registrar(operacion, contexto, parametros, Acceso.Resultado.ENCONTRADO)
        return respuesta

    @staticmethod
    def _registrar(operacion, contexto, parametros, resultado):
        registrar_acceso(
            contexto.perfil,
            canal=contexto.canal,
            nodo=NODO,
            operacion=operacion,
            parametros=parametros,
            resultado=resultado,
            request=contexto.request,
        )

    def _obtener(self, ruta: str, convertir, contexto: Contexto) -> Respuesta:
        if not self.url:
            datos = _muestra().get(ruta.split("?", 1)[0])
            if datos is None:
                raise NoEncontrado("La muestra sintética no tiene esa patente.")
            return Respuesta(
                datos=convertir(datos), origen=Origen.MUESTRA, obtenido_en=timezone.now()
            )

        clave = f"integraciones:permisos:{ruta}"
        if (guardada := cache.get(clave)) is not None:
            return guardada
        datos = pedir_json(f"{self.url}{ruta}", cabeceras=contexto.cabeceras())
        try:
            respuesta = Respuesta(
                datos=convertir(datos), origen=Origen.FUENTE, obtenido_en=timezone.now()
            )
        except (KeyError, TypeError, ValueError, AttributeError):
            registro.warning("Permisos: la fuente respondió %s con una forma inesperada", ruta)
            raise FuenteNoDisponible() from None
        cache.set(clave, respuesta, self.cache_segundos)
        return respuesta
