"""La única puerta para escribir en `Acceso` y `Bitacora` desde las demás aplicaciones."""

from .models import Acceso, Bitacora, Perfil


def registrar_acceso(
    perfil: Perfil,
    *,
    canal: str,
    nodo: str,
    operacion: str,
    parametros: dict,
    resultado: str,
    request=None,
) -> Acceso:
    """Registra una consulta que entregó datos de una persona.

    `parametros` lleva lo justo para saber qué se preguntó; nunca la respuesta.
    El procedimiento y el identificador de trámite salen de las cabeceras de la petición.
    """
    return Acceso.objects.create(
        perfil=perfil,
        canal=canal,
        nodo=nodo,
        operacion=operacion,
        parametros=parametros,
        procedimiento=getattr(request, "procedimiento", ""),
        id_tramite=getattr(request, "id_tramite", ""),
        resultado=resultado,
    )


def registrar_bitacora(
    perfil: Perfil | None,
    *,
    accion: str,
    objeto: str,
    antes: dict | None = None,
    despues: dict | None = None,
    nota: str = "",
) -> Bitacora:
    """Registra una acción editorial. Sin perfil, `nota` tiene que decir quién la hizo."""
    if perfil is None and not nota:
        raise ValueError("Una entrada de bitácora sin perfil necesita una nota que diga quién.")
    return Bitacora.objects.create(
        perfil=perfil,
        accion=accion,
        objeto=objeto,
        antes=antes or {},
        despues=despues or {},
        nota=nota,
    )
