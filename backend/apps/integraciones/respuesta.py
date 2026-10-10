import datetime
from dataclasses import dataclass
from enum import StrEnum


class Origen(StrEnum):
    FUENTE = "fuente"
    FOTO = "foto"
    MUESTRA = "muestra"


@dataclass(frozen=True)
class Respuesta[T]:
    """Lo que entrega un adaptador, con de dónde salió y de cuándo es.

    `obtenido_en` es cuándo se leyó de la fuente, aunque venga del caché; en una foto, la
    fecha en que se descargó. Es lo que la pantalla muestra para no fingir frescura.
    """

    datos: T
    origen: Origen
    obtenido_en: datetime.datetime

    def con(self, datos) -> "Respuesta":
        """La misma procedencia, con otros datos: un filtro sobre una lista cacheada."""
        return Respuesta(datos=datos, origen=self.origen, obtenido_en=self.obtenido_en)
