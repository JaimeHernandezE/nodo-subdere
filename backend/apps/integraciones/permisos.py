"""Permisos de circulación, leídos de la API de fiscalización de SEM.

Ver INSTRUCCIONES.md §2, §3 y §5.

Cada consulta entrega datos asociados a una persona, así que este adaptador **exige** un
`Contexto` y registra él mismo cada consulta en `cuentas.Acceso`: también la que sale del
caché, la que no encuentra nada y la que falla. Ningún llamador puede saltárselo.

SEM entrega el vehículo y sus pagos en una sola respuesta, con su propia forma; acá se
traduce a las dataclasses del contrato propuesto, que es lo que expone el nodo.

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

from apps.core import foto_cut, run
from apps.core.cut import canonico
from apps.core.errores import ErrorNodo
from apps.cuentas.actuaciones import registrar_acceso
from apps.cuentas.models import Acceso, Perfil

from . import patente as patentes
from .cliente import pedir_json
from .cut import sin_tildes
from .errores import FuenteNoDisponible, NoEncontrado, ParametroInvalido
from .respuesta import Origen, Respuesta

NODO = "permisos-de-circulacion"
MUESTRA = Path(__file__).resolve().parent / "muestras" / "permisos.json"
ANIO_MINIMO = 1990
PROVISIONALES_SIN_CONECTAR = (
    "La consulta de permisos provisionales todavía no está conectada a la fuente."
)

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
    """SEM escribe las fechas como dd-mm-aaaa."""
    return datetime.datetime.strptime(valor, "%d-%m-%Y").date() if valor else None


def _rut(texto: str) -> str:
    try:
        return run.formatear(*run.leer(texto))
    except ValueError:
        return str(texto)


@functools.cache
def _comunas_por_nombre() -> dict[str, tuple[str, str]]:
    return {
        sin_tildes(fila["nombre"]): (canonico(fila["comuna_id"], "comuna"), fila["nombre"])
        for fila in foto_cut.leer("comunas")["datos"]
    }


def _comuna(nombre) -> ComunaDelPermiso:
    """SEM identifica la municipalidad por su RUT y su nombre; el CUT sale del nombre.

    Un nombre que no calza con la foto del CUT, o que viene vacío, queda sin código.
    """
    nombre = str(nombre or "").strip()
    cut, oficial = _comunas_por_nombre().get(sin_tildes(nombre), ("", nombre))
    return ComunaDelPermiso(cut=cut, nombre=oficial)


def _vehiculo(respuesta: dict) -> Vehiculo:
    datos = respuesta["data"]
    return Vehiculo(
        patente=str(datos["patente"]).upper(),
        marca=str(datos["marca"]),
        modelo=str(datos["modelo"]),
        anio_fabricacion=int(datos["ano_fabricacion"]),
        color=str(datos.get("color") or ""),
    )


def _cuota(pago: dict) -> tuple[Cuota, ...]:
    """`tipo_pago` es `T` para el pago total, o el número de la cuota."""
    fecha = _fecha(pago.get("fecha_pago_cuota"))
    if fecha is None:
        return ()
    tipo = str(pago["tipo_pago"]).strip().upper()
    numero = 1 if tipo == "T" else int(tipo)
    return (Cuota(numero=numero, monto=int(pago["monto_cuota"]), fecha_pago=fecha),)


def _permisos(respuesta: dict) -> list[Permiso]:
    """Un permiso por cada pago, sin agruparlos: ver INSTRUCCIONES.md §2."""
    return [
        Permiso(
            anio=int(p["ano"]),
            estado=str(p["estado"]),
            comuna=_comuna(p.get("institucion_nombre")),
            monto_total=int(p["monto_total"]),
            vigente_hasta=_fecha(p.get("fecha_vigencia")),
            cuotas=_cuota(p),
        )
        for p in respuesta["data"]["pagos"] or []
    ]


def _provisionales(datos: list) -> list[PermisoProvisional]:
    """El titular es la automotora; los datos de su representante no salen del adaptador."""
    provisionales = []
    for p in datos:
        automotora = (p.get("propietarios") or [{}])[0]
        provisionales.append(
            PermisoProvisional(
                anio=int(p["permiso_anio"]),
                semestre=int(p["permiso_semestre"]),
                comuna=_comuna(p.get("institucion_nombre")),
                titular=TitularEmpresa(
                    rut=_rut(automotora.get("automotora_rut") or ""),
                    razon_social=str(automotora.get("automotora_razon_social") or ""),
                ),
                marca=str(p.get("marca") or ""),
                modelo=str(p.get("modelo") or ""),
            )
        )
    return provisionales


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
            "consultar_vehiculo",
            contexto,
            {"patente": patente},
            f"/fiscalizaciones/{patente}",
            _vehiculo,
        )

    def permisos(
        self, patente: str, contexto: Contexto, desde_anio: int | None = None
    ) -> Respuesta:
        patente = patentes.validar(patente)
        parametros = {"patente": patente}
        if desde_anio is not None:
            if isinstance(desde_anio, bool) or not isinstance(desde_anio, int):
                raise ParametroInvalido(mensaje="desde_anio debe ser un año.")
            if desde_anio < ANIO_MINIMO:
                raise ParametroInvalido(
                    mensaje=f"desde_anio no puede ser anterior a {ANIO_MINIMO}."
                )
            parametros["desde_anio"] = desde_anio

        def convertir(datos):
            return [p for p in _permisos(datos) if desde_anio is None or p.anio >= desde_anio]

        return self._consultar(
            "consultar_permisos", contexto, parametros, f"/fiscalizaciones/{patente}", convertir
        )

    def provisionales(self, patente: str, contexto: Contexto) -> Respuesta:
        patente = patentes.validar_provisoria(patente)
        return self._consultar(
            "consultar_permisos_provisionales",
            contexto,
            {"patente": patente},
            f"/fiscalizaciones/provisionales/{patente}",
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
            datos = _muestra().get(ruta)
            if datos is None:
                raise NoEncontrado("La muestra sintética no tiene esa patente.")
            return Respuesta(
                datos=convertir(datos), origen=Origen.MUESTRA, obtenido_en=timezone.now()
            )

        if ruta.startswith("/fiscalizaciones/provisionales/"):
            # SEM pide dos parámetros más, que identifican a la municipalidad que consulta.
            registro.warning("Permisos: los provisionales aún no están conectados a SEM")
            raise FuenteNoDisponible(PROVISIONALES_SIN_CONECTAR)

        # El vehículo y sus permisos salen de la misma respuesta: se guarda una vez.
        clave = f"integraciones:permisos:{ruta}"
        guardada = cache.get(clave)
        datos, obtenido_en = guardada or (
            pedir_json(f"{self.url}{ruta}", cabeceras=contexto.cabeceras()),
            timezone.now(),
        )
        try:
            convertidos = convertir(datos)
        except (KeyError, TypeError, ValueError, AttributeError):
            registro.warning("Permisos: la fuente respondió %s con una forma inesperada", ruta)
            raise FuenteNoDisponible() from None
        if guardada is None:
            cache.set(clave, (datos, obtenido_en), self.cache_segundos)
        return Respuesta(datos=convertidos, origen=Origen.FUENTE, obtenido_en=obtenido_en)
