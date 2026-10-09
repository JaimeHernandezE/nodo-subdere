import pytest

from apps.core.run import digito_verificador, formatear, leer, validar


@pytest.mark.parametrize(
    ("numero", "esperado"),
    [
        (12345678, "5"),
        (10000013, "K"),
        (1000030, "0"),
        (76086428, "5"),
        (1, "9"),
    ],
)
def test_calcula_el_digito_verificador(numero, esperado):
    assert digito_verificador(numero) == esperado


@pytest.mark.parametrize(
    ("numero", "dv", "esperado"),
    [
        (12345678, "5", (12345678, "5")),
        ("12345678", "5", (12345678, "5")),
        (10000013, "k", (10000013, "K")),
        (10000013, " K ", (10000013, "K")),
    ],
)
def test_valida_y_normaliza_el_par_de_clave_unica(numero, dv, esperado):
    assert validar(numero, dv) == esperado


def test_rechaza_un_digito_verificador_que_no_corresponde():
    with pytest.raises(ValueError, match="no corresponde"):
        validar(12345678, "9")


@pytest.mark.parametrize("dv", ["", "55", None, 5])
def test_rechaza_digitos_verificadores_mal_formados(dv):
    with pytest.raises(ValueError, match="Dígito verificador inválido"):
        validar(12345678, dv)


@pytest.mark.parametrize("numero", [0, -1, True, "", "12.345.678", "١٢٣", 1.5])
def test_rechaza_numeros_invalidos(numero):
    with pytest.raises(ValueError, match="inválido"):
        validar(numero, "5")


def test_rechaza_numeros_demasiado_largos():
    with pytest.raises(ValueError, match="demasiado largo"):
        digito_verificador(123456789)


@pytest.mark.parametrize(
    "texto",
    ["12.345.678-5", "12345678-5", "123456785", " 12345678-5 "],
)
def test_lee_las_formas_habituales(texto):
    assert leer(texto) == (12345678, "5")


def test_lee_la_k_en_minuscula():
    assert leer("10.000.013-k") == (10000013, "K")


@pytest.mark.parametrize("texto", ["", "5", "12345678-9", "abc-5", None])
def test_rechaza_textos_que_no_son_un_run_valido(texto):
    with pytest.raises(ValueError):
        leer(texto)


def test_la_forma_canonica_va_sin_puntos_con_guion_y_k_mayuscula():
    assert formatear(12345678, "5") == "12345678-5"
    assert formatear(10000013, "k") == "10000013-K"
