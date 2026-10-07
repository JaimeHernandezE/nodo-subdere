import pytest

from apps.core.cut import canonico


@pytest.mark.parametrize(
    ("codigo", "nivel", "esperado"),
    [
        (1, "region", "01"),
        (13, "region", "13"),
        (11, "provincia", "011"),
        (131, "provincia", "131"),
        (1101, "comuna", "01101"),
        (13101, "comuna", "13101"),
        ("1101", "comuna", "01101"),
        ("01101", "comuna", "01101"),
        (" 1101 ", "comuna", "01101"),
    ],
)
def test_rellena_con_ceros_en_los_tres_niveles(codigo, nivel, esperado):
    assert canonico(codigo, nivel) == esperado


@pytest.mark.parametrize(
    ("codigo", "nivel"),
    [(100, "region"), (1101, "provincia"), (131011, "comuna")],
)
def test_rechaza_codigos_demasiado_largos(codigo, nivel):
    with pytest.raises(ValueError, match="demasiado largo"):
        canonico(codigo, nivel)


@pytest.mark.parametrize("codigo", ["", "11a01", "-1101", "1.101", "١١٠١", True])
def test_rechaza_lo_que_no_son_digitos(codigo):
    with pytest.raises(ValueError, match="inválido"):
        canonico(codigo, "comuna")


def test_rechaza_niveles_desconocidos():
    with pytest.raises(ValueError, match="Nivel desconocido"):
        canonico(1101, "distrito")
