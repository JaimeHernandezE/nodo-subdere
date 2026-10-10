import datetime

import pytest
from rest_framework.test import APIClient

from apps.cuentas.models import Acceso, Perfil
from apps.cuentas.tests.conftest import crear_perfil
from apps.integraciones.respuesta import Origen, Respuesta
from apps.servicios.api.v1.respuesta_serializer import combinar

from .conftest import PERMISOS, PROCEDIMIENTO, http

pytestmark = pytest.mark.django_db

RUTA = "/api/v1/servicios/permisos/{}"


@pytest.fixture
def fiscalizador(db):
    return crear_perfil(55555555)


@pytest.fixture
def cliente(fiscalizador, como):
    return como(fiscalizador)


def consultar(cliente, patente: str, cabeceras=PROCEDIMIENTO, **parametros):
    return cliente.get(RUTA.format(patente), parametros, **cabeceras)


def codigo(respuesta) -> str:
    return respuesta.json()["error"]["codigo"]


class TestQuienPuede:
    def test_sin_sesion_da_401(self, fuente):
        respuesta = consultar(APIClient(), "BDPF18")

        assert respuesta.status_code == 401
        assert codigo(respuesta) == "NO_AUTENTICADO"

    def test_sin_perfil_activo_da_403(self, fuente, realm):
        sin_perfil = APIClient()
        token = realm.token(Perfil(run_numero=12345678, run_dv="5"))
        sin_perfil.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        respuesta = consultar(sin_perfil, "BDPF18")

        assert respuesta.status_code == 403
        assert codigo(respuesta) == "SIN_PERFIL"

    def test_sin_procedimiento_da_400_sin_consultar_ni_registrar(self, fuente, cliente):
        respuesta = consultar(cliente, "BDPF18", cabeceras={})

        assert respuesta.status_code == 400
        assert codigo(respuesta) == "PROCEDIMIENTO_REQUERIDO"
        assert fuente.pedidos == []
        assert not Acceso.objects.exists()


class TestConsulta:
    def test_trae_el_vehiculo_y_sus_permisos(self, fuente, cliente):
        respuesta = consultar(cliente, "bd-pf18")

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["origen"] == "fuente"
        assert cuerpo["datos"]["tipo"] == "definitiva"
        assert cuerpo["datos"]["vehiculo"]["marca"] == "TOYOTA"
        assert [p["anio"] for p in cuerpo["datos"]["permisos"]] == [2026, 2024]
        assert cuerpo["datos"]["permisos"][0]["cuotas"][0]["fecha_pago"] == "2026-03-18"
        assert "provisionales" not in cuerpo["datos"]

    def test_cada_operacion_deja_su_acceso_con_el_contexto_y_sin_la_respuesta(
        self, fuente, cliente, fiscalizador
    ):
        consultar(cliente, "BDPF18")

        accesos = Acceso.objects.order_by("id")
        assert [a.operacion for a in accesos] == ["consultar_vehiculo", "consultar_permisos"]
        for acceso in accesos:
            assert acceso.perfil == fiscalizador
            assert acceso.canal == "pantalla"
            assert acceso.nodo == "permisos-de-circulacion"
            assert acceso.procedimiento == "fiscalizacion-transito"
            assert acceso.id_tramite == "T-1"
            assert acceso.parametros == {"patente": "BDPF18"}
            assert acceso.resultado == "encontrado"

    def test_el_procedimiento_viaja_a_la_fuente(self, fuente, cliente):
        consultar(cliente, "BDPF18")

        assert all(
            p.get_header("X-procedimiento") == "fiscalizacion-transito" for p in fuente.pedidos
        )

    def test_desde_anio_filtra_y_queda_en_el_acceso(self, fuente, cliente):
        ruta = f"{PERMISOS}/vehiculos/BDPF18/permisos?desde_anio=2025"
        fuente.rutas[ruta] = fuente.rutas[f"{PERMISOS}/vehiculos/BDPF18/permisos"]

        respuesta = consultar(cliente, "BDPF18", desde_anio="2025")

        assert [p["anio"] for p in respuesta.json()["datos"]["permisos"]] == [2026]
        acceso = Acceso.objects.get(operacion="consultar_permisos")
        assert acceso.parametros == {"patente": "BDPF18", "desde_anio": 2025}

    @pytest.mark.parametrize("desde_anio", ["dos mil", "1980"])
    def test_un_desde_anio_invalido_da_400_antes_de_consultar(self, fuente, cliente, desde_anio):
        respuesta = consultar(cliente, "BDPF18", desde_anio=desde_anio)

        assert respuesta.status_code == 400
        assert fuente.pedidos == []
        assert not Acceso.objects.exists()

    def test_una_patente_pr_consulta_los_provisionales(self, fuente, cliente):
        respuesta = consultar(cliente, "PR0909")

        assert respuesta.status_code == 200
        datos = respuesta.json()["datos"]
        assert datos["tipo"] == "provisoria"
        assert datos["provisionales"][0]["titular"]["rut"] == "77777777-7"
        assert fuente.urls() == [f"{PERMISOS}/permisos-provisionales/PR0909"]
        assert Acceso.objects.get().operacion == "consultar_permisos_provisionales"

    @pytest.mark.parametrize("patente", ["XX", "BDPF1", "1234AB"])
    def test_una_patente_mal_formada_se_rechaza_antes_de_la_fuente(self, fuente, cliente, patente):
        respuesta = consultar(cliente, patente)

        assert respuesta.status_code == 400
        assert codigo(respuesta) == "PATENTE_INVALIDA"
        assert fuente.pedidos == []
        assert not Acceso.objects.exists()

    def test_un_vehiculo_inexistente_da_404_sin_pedir_sus_permisos(self, fuente, cliente):
        respuesta = consultar(cliente, "AB1234")

        assert respuesta.status_code == 404
        assert codigo(respuesta) == "NO_ENCONTRADO"
        assert fuente.urls() == [f"{PERMISOS}/vehiculos/AB1234"]
        assert Acceso.objects.get().resultado == "no_encontrado"


class TestDegradacion:
    def test_con_la_fuente_caida_da_503_y_nunca_la_muestra(self, fuente, cliente):
        fuente.rutas[f"{PERMISOS}/vehiculos/ZZZZ10"] = http(503)

        respuesta = consultar(cliente, "ZZZZ10")

        assert respuesta.status_code == 503
        assert codigo(respuesta) == "FUENTE_NO_DISPONIBLE"
        assert Acceso.objects.get().resultado == "error"

    def test_sin_fuente_configurada_responde_la_muestra_marcada(self, settings, cliente):
        settings.PERMISOS_CIRCULACION_API_URL = ""

        respuesta = consultar(cliente, "ZZZZ10")

        assert respuesta.status_code == 200
        assert respuesta.json()["origen"] == "muestra"


class TestCombinar:
    AHORA = datetime.datetime(2026, 10, 10, 12, tzinfo=datetime.UTC)
    ANTES = datetime.datetime(2026, 10, 9, 12, tzinfo=datetime.UTC)

    @pytest.mark.parametrize(
        "origenes,esperado",
        [
            ((Origen.FUENTE, Origen.FUENTE), Origen.FUENTE),
            ((Origen.FUENTE, Origen.FOTO), Origen.FOTO),
            ((Origen.FOTO, Origen.MUESTRA), Origen.MUESTRA),
        ],
    )
    def test_informa_el_peor_origen_y_la_fecha_mas_antigua(self, origenes, esperado):
        respuestas = [
            Respuesta(datos=None, origen=origenes[0], obtenido_en=self.AHORA),
            Respuesta(datos=None, origen=origenes[1], obtenido_en=self.ANTES),
        ]

        combinada = combinar(*respuestas, datos="x")

        assert (combinada.origen, combinada.obtenido_en, combinada.datos) == (
            esperado,
            self.ANTES,
            "x",
        )
