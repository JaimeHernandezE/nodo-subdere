"""Leer, validar y proyectar una fuente. Ver INSTRUCCIONES.md §4.

El comando `sincronizar_fuentes` y el endpoint `POST /fuentes/{id}/sincronizar` llaman a
`sincronizar`. Cuando la lectura falla no se borra ni se despublica nada: queda la
`Lectura` inválida con su motivo y la proyección anterior sigue vigente.
"""

import logging

from django.db import DatabaseError, transaction
from django.utils import timezone

from apps.catalogo.errores import CampoDeFicha
from apps.catalogo.models import Nodo, Visibilidad
from apps.cuentas.models import Perfil

from .errores import FuenteDeNodoRetirado, FuenteInactiva, RepositorioNoDisponible
from .lectores import Lector, LectorGitLab
from .models import Fuente, Lectura, TipoDeFuente
from .proyeccion import proyectar
from .validacion import FichaInvalida, validar

registro = logging.getLogger(__name__)


def lector_por_defecto() -> Lector:
    return LectorGitLab()


def nodo_retirado(fuente: Fuente) -> bool:
    return (
        bool(fuente.nodo_identificador)
        and Nodo.objects.filter(
            identificador=fuente.nodo_identificador, visibilidad=Visibilidad.RETIRADO
        ).exists()
    )


def sincronizables():
    """Fuentes activas de tipo repositorio cuyo nodo no está retirado."""
    retirados = Nodo.objects.filter(visibilidad=Visibilidad.RETIRADO).values("identificador")
    return Fuente.objects.filter(activa=True, tipo=TipoDeFuente.REPOSITORIO).exclude(
        nodo_identificador__in=retirados
    )


def sincronizar(fuente: Fuente, *, perfil: Perfil | None = None, lector: Lector | None = None):
    """Devuelve la `Lectura` creada, válida o no."""
    lector = lector or lector_por_defecto()
    with transaction.atomic():
        fuente = Fuente.objects.select_for_update().get(pk=fuente.pk)
        if not fuente.activa:
            raise FuenteInactiva("La fuente está inactiva: no se lee.")
        if fuente.tipo != TipoDeFuente.REPOSITORIO:
            raise FuenteInactiva("Una carga manual no tiene repositorio que leer.")
        if nodo_retirado(fuente):
            raise FuenteDeNodoRetirado(
                f"El nodo «{fuente.nodo_identificador}» está retirado: su fuente ya no se lee."
            )

        lectura = Lectura(fuente=fuente, perfil=perfil)
        try:
            leido = lector.leer_ficha(fuente)
        except RepositorioNoDisponible as error:
            lectura.valida, lectura.motivo = False, str(error)
            lectura.save()
            return lectura
        lectura.commit, lectura.contenido = leido.commit, leido.contenido

        try:
            ficha = validar(
                leido.contenido,
                fuente,
                lambda ruta: lector.leer_archivo(fuente, ruta, leido.commit),
            )
        except FichaInvalida as error:
            lectura.valida, lectura.motivo = False, error.motivo
            if not error.guardar_contenido:
                lectura.contenido = ""
            lectura.save()
            return lectura

        nota = (
            ""
            if perfil
            else (f"Sincronización programada: fuente {fuente.pk}, commit {leido.commit}")
        )
        try:
            with transaction.atomic():
                proyectar(
                    ficha,
                    commit=leido.commit,
                    leido_en=timezone.now(),
                    perfil=perfil,
                    nota=nota,
                )
        except (CampoDeFicha, DatabaseError) as error:
            registro.exception("No se pudo proyectar la fuente %s", fuente.pk)
            lectura.valida = False
            detalle = error.mensaje if isinstance(error, CampoDeFicha) else "error de la base."
            lectura.motivo = f"La ficha es válida pero no se pudo proyectar: {detalle}"
            lectura.save()
            return lectura

        if not fuente.nodo_identificador:
            fuente.nodo_identificador = ficha.identificador
            fuente.save(update_fields=["nodo_identificador", "actualizado_en"])
        lectura.valida = True
        lectura.save()
        return lectura
