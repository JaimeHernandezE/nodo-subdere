from rest_framework import status

from apps.core.errores import ErrorNodo


class CampoDeFicha(ErrorNodo):
    """Se intentó escribir a mano algo que viene de la ficha del servicio."""

    codigo = "CAMPO_DE_FICHA"
    mensaje = "Ese campo viene de la ficha del servicio: lo escribe solo la sincronización."
    status = status.HTTP_400_BAD_REQUEST


class NodoRetirado(ErrorNodo):
    codigo = "NODO_RETIRADO"
    mensaje = "Este nodo fue retirado del catálogo. Se conserva su última lectura."
    status = status.HTTP_410_GONE
