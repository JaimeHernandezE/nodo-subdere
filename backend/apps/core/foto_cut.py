"""Lectura de la foto versionada del CUT en `apps/core/datos/`.

La foto es la copia fechada de los tres listados de la fuente. La regenera a mano el
comando `descargar_cut`; la leen la migración de carga y las pruebas, sin red.
"""

import json
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parent / "datos"

# nombre del archivo y del endpoint -> campo que trae el código
LISTADOS = {
    "regiones": "region_id",
    "provincias": "provincia_id",
    "comunas": "comuna_id",
}


def leer(listado: str, directorio: Path = DIRECTORIO) -> dict:
    """Devuelve {"fuente", "descargado_en", "datos"} del listado pedido."""
    if listado not in LISTADOS:
        raise ValueError(f"Listado desconocido: {listado!r}.")
    return json.loads((directorio / f"{listado}.json").read_text(encoding="utf-8"))
