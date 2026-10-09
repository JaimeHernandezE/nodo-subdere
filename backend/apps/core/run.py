"""Rol Único: dígito verificador y forma canónica.

El RUN de las personas y el RUT de las empresas usan el mismo algoritmo de módulo 11,
pero no son la misma cosa: por eso quien guarda uno guarda también su tipo. Estas
funciones aceptan los dos.

No hay norma que fije cómo se escribe un RUN. La forma canónica del nodo es la
convención de intercambio: sin puntos, con guion y la K en mayúscula (`12345678-5`).
Se normaliza al entrar el dato, nunca al comparar.
"""

MAXIMO_DIGITOS = 8


def digito_verificador(numero: int) -> str:
    """Calcula el dígito verificador por módulo 11. Devuelve `"0"`-`"9"` o `"K"`."""
    numero = _numero(numero)
    suma = 0
    factor = 2
    while numero:
        numero, digito = divmod(numero, 10)
        suma += digito * factor
        factor = 2 if factor == 7 else factor + 1
    resto = 11 - suma % 11
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def validar(numero: int | str, dv: str) -> tuple[int, str]:
    """Valida el par tal como lo entrega Clave Única y lo devuelve normalizado.

    `numero` es el cuerpo, sin puntos; `dv` es el dígito verificador como texto.
    """
    numero = _numero(numero)
    if not isinstance(dv, str) or len(dv.strip()) != 1:
        raise ValueError(f"Dígito verificador inválido: {dv!r}.")
    dv = dv.strip().upper()
    if dv != digito_verificador(numero):
        raise ValueError(f"El dígito verificador no corresponde: {numero}-{dv}.")
    return numero, dv


def leer(texto: str) -> tuple[int, str]:
    """Lee un RUN escrito por una persona: con o sin puntos, con o sin guion."""
    if not isinstance(texto, str):
        raise ValueError(f"RUN inválido: {texto!r}.")
    limpio = texto.strip().replace(".", "").replace("-", "")
    if len(limpio) < 2:
        raise ValueError(f"RUN inválido: {texto!r}.")
    return validar(limpio[:-1], limpio[-1])


def formatear(numero: int, dv: str) -> str:
    """Forma canónica de texto, para mostrar y comparar: `12345678-5`."""
    numero, dv = validar(numero, dv)
    return f"{numero}-{dv}"


def _numero(numero: int | str) -> int:
    if isinstance(numero, bool):
        raise ValueError(f"Número inválido: {numero!r}.")
    if isinstance(numero, str):
        texto = numero.strip()
        if not texto or not texto.isascii() or not texto.isdigit():
            raise ValueError(f"Número inválido: {numero!r}. Debe contener solo dígitos.")
        numero = int(texto)
    if not isinstance(numero, int) or numero <= 0:
        raise ValueError(f"Número inválido: {numero!r}.")
    if len(str(numero)) > MAXIMO_DIGITOS:
        raise ValueError(f"Número demasiado largo: {numero} tiene más de {MAXIMO_DIGITOS} dígitos.")
    return numero
