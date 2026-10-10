import pytest

from apps.cuentas.models import Acceso
from apps.integraciones.cut import AdaptadorCUT, Comuna, Provincia, Region
from apps.integraciones.errores import NoEncontrado, ParametroInvalido
from apps.integraciones.respuesta import Origen

from .conftest import CUT, http

pytestmark = pytest.mark.django_db


# Prueba 2: canónico en los tres niveles


def test_los_codigos_se_rellenan_a_su_forma_canonica_en_los_tres_niveles(fuente):
    cut = AdaptadorCUT()

    assert Region("01", "Tarapacá") in cut.regiones().datos
    assert Provincia("011", "Iquique") in cut.provincias().datos
    assert Comuna("01101", "Iquique") in cut.comunas().datos
    assert cut.comunas().origen == Origen.FUENTE


def test_la_jerarquia_sale_del_codigo(fuente):
    cut = AdaptadorCUT()

    provincias = cut.provincias(region="1").datos
    comunas = cut.comunas(provincia="11").datos

    assert {p.codigo for p in provincias} == {"011", "014"}
    assert {c.codigo for c in comunas} == {"01101", "01107"}
    assert comunas[0].region == "01"


@pytest.mark.parametrize(
    ("codigo", "esperado"),
    [("1", Region), ("13", Region), ("011", Provincia), ("1101", Comuna), ("13101", Comuna)],
)
def test_por_codigo_decide_el_nivel_por_el_largo(fuente, codigo, esperado):
    assert isinstance(AdaptadorCUT().por_codigo(codigo).datos, esperado)


def test_un_codigo_que_no_existe_es_no_encontrado(fuente):
    with pytest.raises(NoEncontrado):
        AdaptadorCUT().por_codigo("99999")


@pytest.mark.parametrize("codigo", ["", "abc", "123456", "13-101", "１３"])
def test_un_codigo_mal_formado_falla_antes_de_llamar_a_la_fuente(fuente, codigo):
    with pytest.raises(ParametroInvalido) as error:
        AdaptadorCUT().por_codigo(codigo)

    assert error.value.codigo == "CODIGO_INVALIDO"
    assert fuente.pedidos == []


def test_filtrar_por_una_region_que_no_existe_es_no_encontrado(fuente):
    with pytest.raises(NoEncontrado):
        AdaptadorCUT().provincias(region="99")


# buscar


@pytest.mark.parametrize("texto", ["nunoa", "ÑUÑOA", " Ñuñoa "])
def test_buscar_ignora_tildes_y_mayusculas(fuente, texto):
    encontradas = AdaptadorCUT().buscar(texto).datos
    assert Comuna("13120", "Ñuñoa") in encontradas


def test_buscar_recorre_los_tres_niveles(fuente):
    nombres = {(u.nivel, u.codigo) for u in AdaptadorCUT().buscar("iquique").datos}
    assert nombres == {("provincia", "011"), ("comuna", "01101")}


def test_buscar_vacio_no_devuelve_nada(fuente):
    assert AdaptadorCUT().buscar("  ").datos == []


# Prueba 5: fuente caída, la foto


@pytest.mark.parametrize("falla", [http(503), http(401), TimeoutError()])
def test_con_la_fuente_caida_responde_la_foto_diciendolo(fuente, falla):
    fuente.rutas[f"{CUT}/comunas"] = falla

    respuesta = AdaptadorCUT().comunas()

    assert respuesta.origen == Origen.FOTO
    assert respuesta.obtenido_en.isoformat() == "2026-10-07T19:11:16+00:00"
    assert Comuna("13101", "Santiago") in respuesta.datos


def test_una_forma_inesperada_tambien_cae_a_la_foto(fuente):
    fuente.rutas[f"{CUT}/regiones"] = [{"codigo": 1}]
    assert AdaptadorCUT().regiones().origen == Origen.FOTO


def test_sin_url_responde_la_foto_sin_llamar(fuente, settings):
    settings.CUT_API_URL = ""

    respuesta = AdaptadorCUT().regiones()

    assert respuesta.origen == Origen.FOTO
    assert fuente.pedidos == []


def test_si_una_parte_de_la_busqueda_sale_de_la_foto_el_todo_lo_dice(fuente):
    fuente.rutas[f"{CUT}/provincias"] = http(500)
    assert AdaptadorCUT().buscar("santiago").origen == Origen.FOTO


# Prueba 6: caché


def test_el_cache_evita_la_segunda_llamada_y_la_hace_al_expirar(fuente, reloj):
    cut = AdaptadorCUT(cache_segundos=60)

    cut.regiones()
    cut.regiones()
    assert fuente.urls().count(f"{CUT}/regiones") == 1

    reloj(61)
    cut.regiones()
    assert fuente.urls().count(f"{CUT}/regiones") == 2


def test_con_la_fuente_caida_la_foto_se_recuerda_un_minuto_y_despues_se_reintenta(fuente, reloj):
    fuente.rutas[f"{CUT}/regiones"] = http(404)
    cut = AdaptadorCUT()
    assert cut.regiones().origen == Origen.FOTO
    assert cut.regiones().origen == Origen.FOTO
    assert fuente.urls().count(f"{CUT}/regiones") == 1

    fuente.rutas[f"{CUT}/regiones"] = [{"region_id": 1, "nombre": "Tarapacá"}]
    reloj(61)
    assert cut.regiones().origen == Origen.FUENTE


def test_si_un_listado_encuentra_la_fuente_caida_los_otros_no_la_esperan(fuente):
    fuente.rutas[f"{CUT}/comunas"] = TimeoutError()
    cut = AdaptadorCUT()

    cut.comunas()
    assert cut.buscar("santiago").origen == Origen.FOTO

    assert fuente.urls() == [f"{CUT}/comunas", f"{CUT}/comunas"]


# Prueba 7: el CUT no escribe accesos


def test_el_cut_no_escribe_accesos(fuente):
    cut = AdaptadorCUT()
    cut.comunas()
    cut.buscar("santiago")
    cut.por_codigo("13101")

    assert not Acceso.objects.exists()
