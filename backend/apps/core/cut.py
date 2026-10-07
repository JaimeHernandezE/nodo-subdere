"""Forma canónica del Código Único Territorial.

La fuente entrega los códigos como enteros (`1101`); la forma canónica es texto con
ceros a la izquierda (`"01101"`). La explicación para humanos vive en la entrada de
wiki del CUT.
"""

LARGO = {"region": 2, "provincia": 3, "comuna": 5}


def canonico(codigo: int | str, nivel: str) -> str:
    """Rellena con ceros hasta el largo del nivel.

    Rechaza un código más largo que su nivel; no rechaza uno más corto, lo rellena.
    """
    if nivel not in LARGO:
        niveles = ", ".join(LARGO)
        raise ValueError(f"Nivel desconocido: {nivel!r}. Debe ser uno de: {niveles}.")

    if isinstance(codigo, bool):
        raise ValueError(f"Código inválido: {codigo!r}.")

    texto = str(codigo).strip()
    if not texto or not texto.isascii() or not texto.isdigit():
        raise ValueError(f"Código inválido: {codigo!r}. Debe contener solo dígitos.")

    largo = LARGO[nivel]
    if len(texto) > largo:
        raise ValueError(
            f"Código demasiado largo para {nivel}: {codigo!r} tiene {len(texto)} dígitos "
            f"y el máximo es {largo}."
        )

    return texto.zfill(largo)
