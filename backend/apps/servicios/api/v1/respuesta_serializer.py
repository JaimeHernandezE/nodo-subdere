"""El sobre de toda consulta de datos: de dónde salió y de cuándo es (INSTRUCCIONES.md §4)."""

from rest_framework import serializers

from apps.integraciones.respuesta import Origen, Respuesta

# De lo menos fresco a lo más: al juntar respuestas, manda la primera que aparezca.
FRESCURA = (Origen.MUESTRA, Origen.FOTO, Origen.FUENTE)


def combinar(*respuestas: Respuesta, datos) -> Respuesta:
    """Varias consultas en una respuesta: se informa el peor origen y la fecha más antigua."""
    origen = next(o for o in FRESCURA if any(r.origen == o for r in respuestas))
    return Respuesta(datos=datos, origen=origen, obtenido_en=min(r.obtenido_en for r in respuestas))


def envolver(respuesta: Respuesta) -> dict:
    return {
        "origen": respuesta.origen.value,
        "obtenido_en": respuesta.obtenido_en,
        "datos": respuesta.datos,
    }


def sobre(nombre: str, datos: serializers.Field) -> type[serializers.Serializer]:
    """Un serializador `{origen, obtenido_en, datos}` con `datos` del tipo dado."""
    return type(
        nombre,
        (serializers.Serializer,),
        {
            "origen": serializers.ChoiceField(choices=[o.value for o in Origen]),
            "obtenido_en": serializers.DateTimeField(),
            "datos": datos,
        },
    )
