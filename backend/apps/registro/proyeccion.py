"""Proyectar una ficha válida sobre `catalogo`. Ver INSTRUCCIONES.md §4.

El único lugar del proyecto que llama a `save(desde_sincronizacion=True)` y
`delete(desde_sincronizacion=True)` sobre los modelos de `catalogo`.
"""

import datetime

from apps.catalogo.models import CAMPOS_DE_FICHA, Ambiente, Especificacion, Nodo
from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.models import Perfil

from .validacion import Ficha

CAMPOS_DE_LA_LECTURA = ("leido_en", "commit")


def instantanea(nodo: Nodo | None) -> dict:
    """La ficha proyectada, sin `leido_en` ni `commit`: lo que se compara y va a Bitacora."""
    if nodo is None:
        return {}
    datos = {}
    for campo in CAMPOS_DE_FICHA:
        if campo in CAMPOS_DE_LA_LECTURA:
            continue
        valor = getattr(nodo, campo)
        datos[campo] = valor.nombre if campo == "ambito" else valor
    vigente = nodo.especificacion_vigente
    datos["especificacion"] = vigente and {
        "version": vigente.version,
        "formato": vigente.formato,
        "ruta": vigente.ruta,
        "huella": vigente.huella,
        "publicada": vigente.publicada.isoformat() if vigente.publicada else None,
    }
    datos["ambientes"] = [
        {"nombre": a.nombre, "base": a.base, "datos": a.datos} for a in nodo.ambientes.all()
    ]
    return datos


def proyectar(
    ficha: Ficha, *, commit: str, leido_en: datetime.datetime, perfil: Perfil | None, nota: str
) -> Nodo:
    """Llamar dentro de una transacción. Deja `Bitacora` solo si cambió algo de la ficha."""
    nodo = Nodo.objects.filter(identificador=ficha.identificador).first()
    antes = instantanea(nodo)
    if nodo is None:
        nodo = Nodo(identificador=ficha.identificador)
    for campo, valor in ficha.nodo.items():
        setattr(nodo, campo, valor)
    nodo.leido_en, nodo.commit = leido_en, commit
    nodo.save(desde_sincronizacion=True)

    _proyectar_especificacion(nodo, ficha.especificacion, commit)
    _proyectar_ambientes(nodo, ficha.ambientes)

    despues = instantanea(nodo)
    if despues != antes:
        registrar_bitacora(
            perfil,
            accion="sincronizar_nodo",
            objeto=f"catalogo.Nodo:{nodo.identificador}",
            antes=antes,
            despues=despues,
            nota=nota,
        )
    return nodo


def _proyectar_especificacion(nodo: Nodo, datos: dict, commit: str):
    registrada = nodo.especificaciones.filter(version=datos["version"]).first()
    if registrada and registrada.vigente:
        return
    # Primero se apaga la que regía: hay una sola vigente por nodo.
    for vigente in nodo.especificaciones.filter(vigente=True):
        vigente.vigente = False
        vigente.save(desde_sincronizacion=True)
    if registrada:
        registrada.vigente = True
        registrada.save(desde_sincronizacion=True)
    else:
        Especificacion(nodo=nodo, vigente=True, commit=commit, **datos).save(
            desde_sincronizacion=True
        )


def _proyectar_ambientes(nodo: Nodo, declarados: list[dict]):
    actuales = {a.nombre: a for a in nodo.ambientes.all()}
    for datos in declarados:
        ambiente = actuales.pop(datos["nombre"], None) or Ambiente(nodo=nodo)
        if ambiente.pk and all(getattr(ambiente, c) == v for c, v in datos.items()):
            continue
        for campo, valor in datos.items():
            setattr(ambiente, campo, valor)
        ambiente.save(desde_sincronizacion=True)
    for sobrante in actuales.values():
        sobrante.delete(desde_sincronizacion=True)
