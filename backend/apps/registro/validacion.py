"""Validar una ficha leída. Ver INSTRUCCIONES.md §3.

Las ocho reglas corren en orden y la primera que falla detiene el resto. Cada falla es un
`FichaInvalida` con un motivo en español que nombra el campo: lo lee quien escribió la
ficha, no quien programó el nodo.
"""

import datetime
import re
from collections.abc import Callable
from dataclasses import dataclass, field

import yaml
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.catalogo.models import (
    Alias,
    Ambiente,
    Ambito,
    Clase,
    Copia,
    Datos,
    Especificacion,
    Formato,
    Intercambio,
    Madurez,
    Nodo,
    NombreDeAmbiente,
    TipoDeAcceso,
    huella,
)
from apps.core import run

from .errores import RepositorioNoDisponible
from .models import Fuente

VERSIONES_DEL_ESTANDAR = (1,)

CLAVES = {
    "ficha",
    "id",
    "nombre",
    "sigla",
    "ambito",
    "clase",
    "intercambio",
    "funcion",
    "descripcion",
    "madurez",
    "responsable",
    "instituciones",
    "especificacion",
    "ambientes",
    "origen",
    "procedencia",
    "acceso",
}
SUBCLAVES = {
    "responsable": {"organismo", "equipo", "correo"},
    "especificacion": {"archivo", "formato", "version", "publicada"},
    "origen": {"norma", "nota"},
    "procedencia": {"copia", "fuente", "detalle"},
    "acceso": {"tipo", "detalle"},
}
CLAVES_DE_AMBIENTE = {"nombre", "base", "datos"}

CAMPO_EN_LA_FICHA = {
    "identificador": "id",
    "responsable_organismo": "responsable.organismo",
    "responsable_equipo": "responsable.equipo",
    "responsable_correo": "responsable.correo",
    "origen_norma": "origen.norma",
    "origen_nota": "origen.nota",
    "procedencia_copia": "procedencia.copia",
    "procedencia_fuente": "procedencia.fuente",
    "procedencia_detalle": "procedencia.detalle",
    "acceso_tipo": "acceso.tipo",
    "acceso_detalle": "acceso.detalle",
}
CAMPO_DE_ESPECIFICACION = {
    "version": "especificacion.version",
    "formato": "especificacion.formato",
    "ruta": "especificacion.archivo",
    "publicada": "especificacion.publicada",
}
PREFIJO_OPENAPI = {Formato.OPENAPI_30: "3.0.", Formato.OPENAPI_31: "3.1."}

PATRON_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PATRON_RUN = re.compile(r"(?<![\w.])(\d{1,2}\.\d{3}\.\d{3}|\d{7,8})\s?-\s?([\dkK])(?!\w)")
PATRON_CORREO = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


class FichaInvalida(Exception):
    """`guardar_contenido` es falso cuando el YAML trae datos personales: no se archiva."""

    def __init__(self, motivo: str, *, guardar_contenido: bool = True):
        super().__init__(motivo)
        self.motivo = motivo
        self.guardar_contenido = guardar_contenido


@dataclass
class Ficha:
    """Una ficha válida, con los nombres de los modelos de `catalogo`."""

    identificador: str
    nodo: dict
    especificacion: dict
    ambientes: list[dict] = field(default_factory=list)


def validar(contenido: str, fuente: Fuente, leer_archivo: Callable[[str], str]) -> Ficha:
    """`leer_archivo(ruta)` lee en el mismo *commit* que la ficha."""
    datos = _regla_1_yaml_y_version(contenido)
    ficha = _regla_2_campos(datos)
    _regla_3_identificador(ficha.identificador, fuente)
    _regla_4_y_5_especificacion(ficha.especificacion, leer_archivo)
    _regla_6_correo(ficha.nodo["responsable_correo"])
    _regla_7_datos_personales(datos, ficha.nodo["responsable_correo"])
    _regla_8_version_registrada(ficha)
    return ficha


# 1. YAML y versión del estándar


def _regla_1_yaml_y_version(contenido: str) -> dict:
    try:
        datos = yaml.safe_load(contenido)
    except yaml.YAMLError as error:
        marca = getattr(error, "problem_mark", None)
        donde = f" (línea {marca.line + 1})" if marca else ""
        problema = getattr(error, "problem", None) or "sintaxis inválida"
        raise FichaInvalida(f"La ficha no es YAML válido{donde}: {problema}.") from None
    if not isinstance(datos, dict):
        raise FichaInvalida("La ficha tiene que ser un grupo de campos, empezando por «ficha: 1».")
    version = datos.get("ficha")
    if version is None:
        raise FichaInvalida("ficha: falta. Es la versión del estándar, por ejemplo «ficha: 1».")
    if isinstance(version, bool) or version not in VERSIONES_DEL_ESTANDAR:
        conocidas = ", ".join(str(v) for v in VERSIONES_DEL_ESTANDAR)
        raise FichaInvalida(
            f"ficha: versión del estándar desconocida ({version!r}). "
            f"Este nodo conoce: {conocidas}. No adivina."
        )
    return datos


# 2. Campos, tipos y listas cerradas


def _tipo(valor) -> str:
    if isinstance(valor, bool):
        return "un sí/no"
    if isinstance(valor, int | float):
        return "un número"
    if isinstance(valor, datetime.date):
        return "una fecha"
    if isinstance(valor, list):
        return "una lista"
    if isinstance(valor, dict):
        return "un grupo de campos"
    return "otra cosa"


def _texto(valor, campo: str, *, obligatorio: bool = True) -> str:
    if valor is None or valor == "":
        if obligatorio:
            raise FichaInvalida(f"{campo}: falta y es obligatorio.")
        return ""
    if not isinstance(valor, str):
        raise FichaInvalida(f"{campo}: tiene que ser texto, y YAML leyó {_tipo(valor)}.")
    texto = valor.strip()
    if obligatorio and not texto:
        raise FichaInvalida(f"{campo}: falta y es obligatorio.")
    return texto


def _version(valor, campo: str) -> str:
    if isinstance(valor, int | float) and not isinstance(valor, bool):
        raise FichaInvalida(
            f'{campo}: escribirla como texto, entre comillas («"{valor}"»). YAML la leyó '
            f"como el número {valor!r}, y así «1.10» se vuelve «1.1»."
        )
    return _texto(valor, campo)


def _de_lista(valor, campo: str, opciones: type[models.TextChoices], **kwargs) -> str:
    texto = _texto(valor, campo, **kwargs)
    if texto and texto not in opciones.values:
        permitidos = ", ".join(opciones.values)
        raise FichaInvalida(f"{campo}: «{texto}» no es un valor permitido. Valores: {permitidos}.")
    return texto


def _grupo(datos: dict, clave: str, *, obligatorio: bool = False) -> dict:
    valor = datos.get(clave)
    if valor is None:
        if obligatorio:
            raise FichaInvalida(f"{clave}: falta y es obligatorio.")
        return {}
    if not isinstance(valor, dict):
        raise FichaInvalida(
            f"{clave}: tiene que ser un grupo de campos, y YAML leyó {_tipo(valor)}."
        )
    _sin_claves_desconocidas(valor, SUBCLAVES[clave], prefijo=f"{clave}.")
    return valor


def _sin_claves_desconocidas(datos: dict, conocidas: set[str], *, prefijo: str = ""):
    desconocidas = sorted(str(c) for c in datos if c not in conocidas)
    if desconocidas:
        lista = ", ".join(f"{prefijo}{c}" for c in desconocidas)
        raise FichaInvalida(
            f"Campos que el estándar no define: {lista}. Revisar si es un error de tipeo."
        )


def _fecha(valor, campo: str) -> datetime.date:
    if isinstance(valor, datetime.datetime):
        return valor.date()
    if isinstance(valor, datetime.date):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.date.fromisoformat(valor.strip())
        except ValueError:
            pass
    if valor is None or valor == "":
        raise FichaInvalida(f"{campo}: falta y es obligatorio.")
    raise FichaInvalida(f"{campo}: tiene que ser una fecha AAAA-MM-DD.")


def _limpiar(objeto: models.Model, nombres: dict[str, str], excluidos: list[str]):
    """Largos y formatos los valida el propio modelo; cada error se vuelve un motivo."""
    try:
        objeto.clean_fields(exclude=excluidos)
    except ValidationError as error:
        campo, mensajes = next(iter(error.message_dict.items()))
        raise FichaInvalida(f"{nombres.get(campo, campo)}: {mensajes[0]}") from None


def _regla_2_campos(datos: dict) -> Ficha:
    _sin_claves_desconocidas(datos, CLAVES)

    identificador = _texto(datos.get("id"), "id")
    if not PATRON_ID.match(identificador):
        raise FichaInvalida(
            f"id: «{identificador}» tiene que usar solo minúsculas, números y guiones, "
            "sin guion al inicio ni al final."
        )
    nombre_de_ambito = _texto(datos.get("ambito"), "ambito")
    ambito = Ambito.objects.filter(nombre=nombre_de_ambito).first()
    if ambito is None:
        conocidos = ", ".join(Ambito.objects.values_list("nombre", flat=True))
        raise FichaInvalida(
            f"ambito: «{nombre_de_ambito}» no es un ámbito del nodo. Ámbitos: {conocidos}."
        )
    clase = _de_lista(datos.get("clase"), "clase", Clase)
    if clase == Clase.INTERCAMBIO:
        intercambio = _de_lista(datos.get("intercambio"), "intercambio", Intercambio)
    elif datos.get("intercambio") not in (None, ""):
        raise FichaInvalida(
            "intercambio: una plataforma no lo lleva. No es algo que el municipio consulte "
            "ni entregue."
        )
    else:
        intercambio = ""

    instituciones = datos.get("instituciones")
    if not isinstance(instituciones, list) or not instituciones:
        raise FichaInvalida("instituciones: tiene que ser una lista con al menos una institución.")
    instituciones = [_texto(i, f"instituciones[{n}]") for n, i in enumerate(instituciones, start=1)]

    responsable = _grupo(datos, "responsable", obligatorio=True)
    origen = _grupo(datos, "origen")
    procedencia = _grupo(datos, "procedencia")
    acceso = _grupo(datos, "acceso")
    nodo = {
        "nombre": _texto(datos.get("nombre"), "nombre"),
        "sigla": _texto(datos.get("sigla"), "sigla", obligatorio=False),
        "ambito": ambito,
        "clase": clase,
        "intercambio": intercambio,
        "funcion": _texto(datos.get("funcion"), "funcion"),
        "descripcion": _texto(datos.get("descripcion"), "descripcion"),
        "madurez": _de_lista(datos.get("madurez"), "madurez", Madurez),
        "instituciones": instituciones,
        "responsable_organismo": _texto(responsable.get("organismo"), "responsable.organismo"),
        "responsable_equipo": _texto(
            responsable.get("equipo"), "responsable.equipo", obligatorio=False
        ),
        "responsable_correo": _texto(responsable.get("correo"), "responsable.correo"),
        "origen_norma": _texto(origen.get("norma"), "origen.norma", obligatorio=False),
        "origen_nota": _texto(origen.get("nota"), "origen.nota", obligatorio=False),
        "procedencia_copia": _de_lista(
            procedencia.get("copia"), "procedencia.copia", Copia, obligatorio=False
        ),
        "procedencia_fuente": _texto(
            procedencia.get("fuente"), "procedencia.fuente", obligatorio=False
        ),
        "procedencia_detalle": _texto(
            procedencia.get("detalle"), "procedencia.detalle", obligatorio=False
        ),
        "acceso_tipo": _de_lista(
            acceso.get("tipo"), "acceso.tipo", TipoDeAcceso, obligatorio=False
        ),
        "acceso_detalle": _texto(acceso.get("detalle"), "acceso.detalle", obligatorio=False),
    }
    _limpiar(
        Nodo(identificador=identificador, leido_en=timezone.now(), **nodo),
        CAMPO_EN_LA_FICHA,
        excluidos=["ambito", "visibilidad", "orden", "nota_editorial"],
    )

    datos_de_especificacion = _grupo(datos, "especificacion", obligatorio=True)
    especificacion = {
        "ruta": _texto(
            datos_de_especificacion.get("archivo"), "especificacion.archivo", obligatorio=False
        ),
        "formato": _de_lista(
            datos_de_especificacion.get("formato"), "especificacion.formato", Formato
        ),
        "version": _version(datos_de_especificacion.get("version"), "especificacion.version"),
        "publicada": _fecha(datos_de_especificacion.get("publicada"), "especificacion.publicada"),
        "contenido": "",
    }
    _limpiar(
        Especificacion(**especificacion),
        CAMPO_DE_ESPECIFICACION,
        excluidos=["nodo", "contenido", "huella", "vigente", "commit"],
    )

    return Ficha(
        identificador=identificador,
        nodo=nodo,
        especificacion=especificacion,
        ambientes=_ambientes(datos.get("ambientes")),
    )


def _ambientes(valor) -> list[dict]:
    if valor is None:
        return []
    if not isinstance(valor, list):
        raise FichaInvalida(f"ambientes: tiene que ser una lista, y YAML leyó {_tipo(valor)}.")
    ambientes = []
    for n, datos in enumerate(valor, start=1):
        campo = f"ambientes[{n}]"
        if not isinstance(datos, dict):
            raise FichaInvalida(f"{campo}: tiene que ser un grupo de campos.")
        _sin_claves_desconocidas(datos, CLAVES_DE_AMBIENTE, prefijo=f"{campo}.")
        ambiente = {
            "nombre": _de_lista(datos.get("nombre"), f"{campo}.nombre", NombreDeAmbiente),
            "base": _texto(datos.get("base"), f"{campo}.base"),
            "datos": _de_lista(datos.get("datos"), f"{campo}.datos", Datos),
        }
        if any(a["nombre"] == ambiente["nombre"] for a in ambientes):
            raise FichaInvalida(f"{campo}.nombre: «{ambiente['nombre']}» está repetido.")
        _limpiar(
            Ambiente(**ambiente),
            {c: f"{campo}.{c}" for c in CLAVES_DE_AMBIENTE},
            excluidos=["nodo"],
        )
        ambientes.append(ambiente)
    return ambientes


# 3. El identificador


def _regla_3_identificador(identificador: str, fuente: Fuente):
    if fuente.nodo_identificador and identificador != fuente.nodo_identificador:
        raise FichaInvalida(
            f"id: esta fuente proyecta «{fuente.nodo_identificador}» y la ficha dice "
            f"«{identificador}». El id es inmutable: uno distinto es un servicio nuevo, que se "
            "registra como otra fuente."
        )
    alias = Alias.objects.filter(identificador=identificador).first()
    if alias:
        raise FichaInvalida(
            f"id: «{identificador}» es un nombre antiguo de «{alias.destino}» y sigue "
            "resolviendo hacia él. No se puede usar para otro servicio."
        )
    otra = Fuente.objects.filter(nodo_identificador=identificador).exclude(pk=fuente.pk)
    tomado_sin_fuente = (
        not fuente.nodo_identificador and Nodo.objects.filter(identificador=identificador).exists()
    )
    if otra.exists() or tomado_sin_fuente:
        raise FichaInvalida(f"id: «{identificador}» ya es el de otro nodo del catálogo.")


# 4 y 5. El contrato


def _regla_4_y_5_especificacion(especificacion: dict, leer_archivo: Callable[[str], str]):
    ruta, formato = especificacion["ruta"], especificacion["formato"]
    if not ruta:
        if formato != Formato.DESCRIPCION:
            raise FichaInvalida(
                f"especificacion.formato: sin archivo el formato es «descripcion», no «{formato}»."
            )
        return
    if formato not in PREFIJO_OPENAPI:
        raise FichaInvalida(
            "especificacion.formato: con archivo, el formato es «openapi-3.0» u «openapi-3.1»."
        )
    try:
        contenido = leer_archivo(ruta)
    except RepositorioNoDisponible as error:
        raise FichaInvalida(f"especificacion.archivo: {error}") from None
    try:
        documento = yaml.safe_load(contenido)
    except yaml.YAMLError:
        raise FichaInvalida(
            f"especificacion.archivo: {ruta} no se pudo leer como YAML ni como JSON."
        ) from None
    if not isinstance(documento, dict):
        raise FichaInvalida(f"especificacion.archivo: {ruta} no es un documento OpenAPI.")
    openapi = documento.get("openapi")
    if not isinstance(openapi, str):
        raise FichaInvalida(
            f"especificacion.archivo: {ruta} no declara el campo «openapi» como texto."
        )
    if not openapi.startswith(PREFIJO_OPENAPI[formato]):
        raise FichaInvalida(
            f"especificacion.formato: la ficha dice «{formato}» y el archivo declara "
            f"openapi {openapi}."
        )

    info = documento.get("info")
    version_del_archivo = info.get("version") if isinstance(info, dict) else None
    if version_del_archivo is None:
        raise FichaInvalida(f"especificacion.archivo: {ruta} no tiene info.version.")
    version_del_archivo = _version(version_del_archivo, "info.version del archivo")
    if version_del_archivo != especificacion["version"]:
        raise FichaInvalida(
            f"especificacion.version: la ficha declara «{especificacion['version']}» y "
            f"info.version del archivo dice «{version_del_archivo}»."
        )
    especificacion["contenido"] = contenido


# 6. Correo institucional


def _regla_6_correo(correo: str):
    dominio = correo.rsplit("@", 1)[-1].lower()
    publicos = {d.strip().lower() for d in settings.REGISTRO_DOMINIOS_NO_INSTITUCIONALES}
    if dominio in publicos:
        raise FichaInvalida(
            f"responsable.correo: {dominio} es un proveedor de correo público. "
            "El responsable se identifica con un correo institucional."
        )


# 7. Sin datos personales


def _textos(valor, ruta: str = ""):
    if isinstance(valor, str):
        yield ruta, valor
    elif isinstance(valor, dict):
        for clave, interior in valor.items():
            yield from _textos(interior, f"{ruta}.{clave}" if ruta else str(clave))
    elif isinstance(valor, list):
        for n, interior in enumerate(valor, start=1):
            yield from _textos(interior, f"{ruta}[{n}]")


def _hay_run(texto: str) -> bool:
    for coincidencia in PATRON_RUN.finditer(texto):
        try:
            run.validar(coincidencia.group(1).replace(".", ""), coincidencia.group(2))
        except ValueError:
            continue
        return True
    return False


def _regla_7_datos_personales(datos: dict, correo_responsable: str):
    for ruta, texto in _textos(datos):
        if ruta == "responsable.correo":
            continue
        if _hay_run(texto):
            raise FichaInvalida(
                f"{ruta}: trae lo que parece un RUN. La ficha no lleva datos personales: "
                "el único contacto es responsable.correo.",
                guardar_contenido=False,
            )
        for correo in PATRON_CORREO.findall(texto):
            if correo.lower() != correo_responsable.lower():
                raise FichaInvalida(
                    f"{ruta}: trae un correo distinto del del responsable. La ficha no lleva "
                    "datos personales: el único contacto es responsable.correo.",
                    guardar_contenido=False,
                )


# 8. Una versión registrada no cambia


def _regla_8_version_registrada(ficha: Ficha):
    version = ficha.especificacion["version"]
    registrada = Especificacion.objects.filter(
        nodo__identificador=ficha.identificador, version=version
    ).first()
    if registrada and registrada.huella != huella(ficha.especificacion["contenido"]):
        raise FichaInvalida(
            f"especificacion.version: la versión {version} ya está registrada con otro "
            "contenido. Ninguna versión se corrige: un contrato distinto lleva una versión nueva."
        )
