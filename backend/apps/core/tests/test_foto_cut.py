from apps.core import foto_cut


def _codigos(listado):
    campo = foto_cut.LISTADOS[listado]
    return {fila[campo] for fila in foto_cut.leer(listado)["datos"]}


def test_cada_listado_declara_fuente_y_fecha():
    for listado in foto_cut.LISTADOS:
        foto = foto_cut.leer(listado)
        assert foto["fuente"].startswith("https://")
        assert foto["fuente"].endswith(f"/{listado}")
        assert foto["descargado_en"]
        assert foto["datos"]


def test_la_foto_tiene_16_regiones_56_provincias_y_346_comunas():
    assert len(_codigos("regiones")) == 16
    assert len(_codigos("provincias")) == 56
    assert len(_codigos("comunas")) == 346


def test_toda_comuna_cae_en_una_provincia_y_toda_provincia_en_una_region():
    regiones = _codigos("regiones")
    provincias = _codigos("provincias")
    comunas = _codigos("comunas")

    assert {comuna // 100 for comuna in comunas} <= provincias
    assert {provincia // 10 for provincia in provincias} <= regiones


def test_no_hay_provincias_ni_regiones_vacias():
    provincias = _codigos("provincias")
    comunas = _codigos("comunas")

    assert provincias == {comuna // 100 for comuna in comunas}
    assert _codigos("regiones") == {provincia // 10 for provincia in provincias}
