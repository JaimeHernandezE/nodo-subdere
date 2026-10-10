import datetime
import json

import pytest

from apps.core import run
from apps.cuentas.models import Acceso
from apps.integraciones import patente
from apps.integraciones.errores import FuenteNoDisponible, NoEncontrado, ParametroInvalido
from apps.integraciones.permisos import MUESTRA, AdaptadorPermisos, Contexto
from apps.integraciones.respuesta import Origen

from .conftest import PERMISOS, http

pytestmark = pytest.mark.django_db


def accesos():
    return list(Acceso.objects.values_list("operacion", "resultado"))


# Lo que entrega


def test_el_vehiculo_sigue_el_contrato(fuente, contexto):
    respuesta = AdaptadorPermisos().vehiculo("bd-pf·18", contexto)

    assert respuesta.origen == Origen.FUENTE
    assert (respuesta.datos.patente, respuesta.datos.marca, respuesta.datos.anio_fabricacion) == (
        "BDPF18",
        "TOYOTA",
        2019,
    )


def test_los_permisos_traen_comuna_y_cuotas(fuente, contexto):
    permisos = AdaptadorPermisos().permisos("BDPF18", contexto).datos

    assert [p.anio for p in permisos] == [2026, 2024]
    assert permisos[0].comuna.cut == "13101"
    assert permisos[0].cuotas[1].fecha_pago == datetime.date(2026, 8, 14)
    assert permisos[1].vigente_hasta is None


def test_desde_anio_viaja_a_la_fuente_y_se_respeta(fuente, contexto):
    fuente.rutas[f"{PERMISOS}/vehiculos/BDPF18/permisos?desde_anio=2025"] = fuente.rutas[
        f"{PERMISOS}/vehiculos/BDPF18/permisos"
    ]

    permisos = AdaptadorPermisos().permisos("BDPF18", contexto, desde_anio=2025).datos

    assert [p.anio for p in permisos] == [2026]
    assert Acceso.objects.get().parametros == {"patente": "BDPF18", "desde_anio": 2025}


def test_los_provisionales_normalizan_el_rut_de_la_empresa(fuente, contexto):
    provisional = AdaptadorPermisos().provisionales("PR0909", contexto).datos[0]

    assert provisional.titular.rut == "77777777-7"
    assert provisional.semestre == 2


def test_los_metadatos_de_trazabilidad_viajan_a_la_fuente(fuente, contexto):
    AdaptadorPermisos().vehiculo("BDPF18", contexto)

    pedido = fuente.pedidos[0]
    assert pedido.get_header("X-procedimiento") == "fiscalizacion-transito"
    assert pedido.get_header("X-id-tramite") == "T-1"
    assert not any("55555555" in str(v) for v in pedido.headers.values())


# Prueba 3: formato antes de la fuente


@pytest.mark.parametrize("texto", ["", "BDPF1", "BDPF188", "B1PF18", "ÑAPF18", 123])
def test_una_patente_mal_formada_falla_antes_de_llamar_a_la_fuente(fuente, contexto, texto):
    with pytest.raises(ParametroInvalido) as error:
        AdaptadorPermisos().vehiculo(texto, contexto)

    assert error.value.codigo == "PATENTE_INVALIDA"
    assert fuente.pedidos == []
    assert not Acceso.objects.exists()


def test_una_provisoria_exige_el_prefijo_pr(fuente, contexto):
    with pytest.raises(ParametroInvalido):
        AdaptadorPermisos().provisionales("BDPF18", contexto)
    assert patente.es_provisoria("pr-0909")


@pytest.mark.parametrize("desde_anio", [1989, "2024", True])
def test_desde_anio_invalido_falla_antes_de_la_fuente(fuente, contexto, desde_anio):
    with pytest.raises(ParametroInvalido):
        AdaptadorPermisos().permisos("BDPF18", contexto, desde_anio=desde_anio)
    assert fuente.pedidos == []


# Prueba 4: caída no es no encontrado


def test_una_patente_inexistente_es_no_encontrado(fuente, contexto):
    with pytest.raises(NoEncontrado):
        AdaptadorPermisos().vehiculo("ZZZZ99", contexto)

    assert accesos() == [("consultar_vehiculo", "no_encontrado")]


@pytest.mark.parametrize("falla", [http(503), http(401), http(403), TimeoutError()])
def test_la_fuente_caida_es_fuente_no_disponible_y_nunca_la_muestra(fuente, contexto, falla):
    fuente.rutas[f"{PERMISOS}/vehiculos/BDPF18"] = falla

    with pytest.raises(FuenteNoDisponible) as error:
        AdaptadorPermisos().vehiculo("BDPF18", contexto)

    assert error.value.status == 503
    assert accesos() == [("consultar_vehiculo", "error")]


def test_una_forma_inesperada_de_la_fuente_es_fuente_no_disponible(fuente, contexto):
    fuente.rutas[f"{PERMISOS}/vehiculos/BDPF18"] = {"patente": "BDPF18"}

    with pytest.raises(FuenteNoDisponible):
        AdaptadorPermisos().vehiculo("BDPF18", contexto)


# Prueba 6: caché


def test_el_cache_evita_la_segunda_llamada_y_la_hace_al_expirar(fuente, contexto, reloj):
    permisos = AdaptadorPermisos(cache_segundos=300)

    permisos.vehiculo("BDPF18", contexto)
    permisos.vehiculo("BDPF18", contexto)
    assert len(fuente.pedidos) == 1

    reloj(301)
    permisos.vehiculo("BDPF18", contexto)
    assert len(fuente.pedidos) == 2


# Prueba 7: un acceso por consulta


def test_cada_consulta_escribe_exactamente_un_acceso_tambien_desde_el_cache(
    fuente, contexto, fiscalizador
):
    permisos = AdaptadorPermisos()

    permisos.vehiculo("BDPF18", contexto)
    permisos.vehiculo("BDPF18", contexto)
    permisos.permisos("BDPF18", contexto)

    assert len(fuente.pedidos) == 2
    assert accesos() == [
        ("consultar_permisos", "encontrado"),
        ("consultar_vehiculo", "encontrado"),
        ("consultar_vehiculo", "encontrado"),
    ]
    acceso = Acceso.objects.filter(operacion="consultar_permisos").get()
    assert acceso.perfil == fiscalizador
    assert acceso.canal == "pantalla"
    assert acceso.nodo == "permisos-de-circulacion"
    assert (acceso.procedimiento, acceso.id_tramite) == ("fiscalizacion-transito", "T-1")
    assert acceso.parametros == {"patente": "BDPF18"}


def test_sin_contexto_no_hay_consulta(fuente, fiscalizador):
    with pytest.raises(TypeError):
        AdaptadorPermisos().vehiculo("BDPF18")
    with pytest.raises(TypeError):
        AdaptadorPermisos().vehiculo("BDPF18", None)
    with pytest.raises(TypeError):
        Contexto(perfil=None, canal="pantalla")
    with pytest.raises(TypeError):
        Contexto(perfil=fiscalizador, canal="correo")
    assert fuente.pedidos == []
    assert not Acceso.objects.exists()


# Prueba 8: la muestra


def test_sin_url_responde_la_muestra_marcada(fuente, contexto, settings):
    settings.PERMISOS_CIRCULACION_API_URL = ""
    permisos = AdaptadorPermisos()

    vehiculo = permisos.vehiculo("ZZZZ10", contexto)
    provisionales = permisos.provisionales("PR0001", contexto)

    assert vehiculo.origen == provisionales.origen == Origen.MUESTRA
    assert provisionales.datos[0].titular.rut == "77777777-7"
    assert fuente.pedidos == []
    assert len(accesos()) == 2


def test_la_muestra_tambien_dice_no_encontrado(contexto, settings):
    settings.PERMISOS_CIRCULACION_API_URL = ""
    with pytest.raises(NoEncontrado):
        AdaptadorPermisos().vehiculo("BDPF18", contexto)


def test_las_patentes_y_los_rut_de_la_muestra_pasan_la_validacion():
    respuestas = json.loads(MUESTRA.read_text(encoding="utf-8"))["respuestas"]

    for ruta, datos in respuestas.items():
        valor = ruta.split("/")[2]
        if ruta.startswith("/permisos-provisionales/"):
            assert patente.validar_provisoria(valor) == valor
            for permiso in datos:
                run.leer(permiso["titular"]["rut"])
        else:
            assert patente.validar(valor) == valor
