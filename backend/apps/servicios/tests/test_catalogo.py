import pytest
from rest_framework.test import APIClient

from apps.catalogo.models import Visibilidad
from apps.cuentas.models import Bitacora
from apps.servicios.models import Servicio

from .conftest import crear_nodo, crear_servicio

pytestmark = pytest.mark.django_db

anonimo = APIClient

NUEVO = {
    "slug": "consulta-permiso-circulacion",
    "nodo": "cut",
    "nombre": "Consulta de permiso de circulación",
    "funcion": "Escribir una patente y ver su permiso.",
    "descripcion": "Escribe la patente de un vehículo.",
    "tareas": ["Comprobar si un vehículo tiene el permiso vigente"],
    "fuentes": [{"dato": "El permiso", "origen": "La municipalidad que lo cobró"}],
    "estado": "en_construccion",
}


def codigo(respuesta) -> str:
    return respuesta.json()["error"]["codigo"]


def slugs(respuesta) -> list[str]:
    return [s["slug"] for s in respuesta.json()]


class TestListado:
    def test_sin_filtro_no_lista_servicios_de_nodos_ocultos(
        self, nodo_cut, nodo_oculto, lector, como
    ):
        crear_servicio(nodo_cut)
        crear_servicio(nodo_oculto, slug="consulta-permiso-circulacion")

        assert slugs(anonimo().get("/api/v1/servicios")) == ["buscador-cut"]
        assert slugs(como(lector).get("/api/v1/servicios")) == ["buscador-cut"]

    def test_la_respuesta_trae_lo_que_pinta_la_tarjeta(self, nodo_cut):
        crear_servicio(nodo_cut)

        (servicio,) = anonimo().get("/api/v1/servicios").json()

        assert servicio["nodo"] == "cut"
        assert servicio["estado"] == "en_construccion"
        assert servicio["fuentes"] == [{"dato": "Los códigos", "origen": "SUBDERE"}]
        assert set(servicio) >= {"nombre", "funcion", "descripcion", "tareas", "actualizado"}

    def test_por_nodo_acepta_un_alias(self, nodo_cut, alias):
        crear_servicio(nodo_cut)

        assert slugs(anonimo().get("/api/v1/servicios", {"nodo": "codigos-territoriales"})) == [
            "buscador-cut"
        ]

    def test_por_nodo_oculto_solo_con_sesion(self, nodo_oculto, lector, como):
        crear_servicio(nodo_oculto)
        filtro = {"nodo": "permisos-de-circulacion"}

        assert anonimo().get("/api/v1/servicios", filtro).json() == []
        assert slugs(como(lector).get("/api/v1/servicios", filtro)) == ["buscador-cut"]

    def test_por_nodo_retirado_o_inexistente_es_una_lista_vacia(self, lector, como):
        crear_servicio(crear_nodo("viejo", visibilidad=Visibilidad.RETIRADO))

        for nodo in ("viejo", "no-existe"):
            respuesta = como(lector).get("/api/v1/servicios", {"nodo": nodo})
            assert respuesta.status_code == 200
            assert respuesta.json() == []


class TestDetalle:
    def test_uno_publicado_lo_ve_cualquiera(self, nodo_cut):
        crear_servicio(nodo_cut)

        respuesta = anonimo().get("/api/v1/servicios/buscador-cut")

        assert respuesta.status_code == 200
        assert respuesta.json()["tareas"] == [
            "Escribir el nombre de una comuna y obtener su código"
        ]

    def test_uno_de_nodo_oculto_es_404_sin_sesion(self, nodo_oculto, lector, como):
        crear_servicio(nodo_oculto)

        assert anonimo().get("/api/v1/servicios/buscador-cut").status_code == 404
        assert como(lector).get("/api/v1/servicios/buscador-cut").status_code == 200

    def test_uno_que_no_existe_es_404(self, db):
        respuesta = anonimo().get("/api/v1/servicios/no-existe")

        assert respuesta.status_code == 404
        assert codigo(respuesta) == "NO_ENCONTRADO"


class TestCrear:
    def test_un_curador_crea_y_queda_en_la_bitacora(self, nodo_cut, curador, como):
        respuesta = como(curador).post("/api/v1/servicios", NUEVO, format="json")

        assert respuesta.status_code == 201
        assert respuesta.json()["nodo"] == "cut"
        entrada = Bitacora.objects.get(accion="crear_servicio")
        assert entrada.perfil == curador
        assert entrada.objeto == "servicios.Servicio:consulta-permiso-circulacion"
        assert entrada.despues["nodo"] == "cut"

    def test_un_lector_no_crea_y_sin_sesion_es_401(self, nodo_cut, lector, como):
        assert como(lector).post("/api/v1/servicios", NUEVO, format="json").status_code == 403
        assert anonimo().post("/api/v1/servicios", NUEVO, format="json").status_code == 401
        assert not Servicio.objects.exists()

    def test_no_se_crea_sobre_un_nodo_retirado(self, curador, como):
        crear_nodo("cut", visibilidad=Visibilidad.RETIRADO)

        respuesta = como(curador).post("/api/v1/servicios", NUEVO, format="json")

        assert respuesta.status_code == 400
        assert respuesta.json()["error"]["detalles"][0]["campo"] == "nodo"

    @pytest.mark.parametrize(
        "campo,valor",
        [
            ("tareas", ["", "Otra"]),
            ("tareas", "una sola"),
            ("fuentes", [{"dato": "Solo el dato"}]),
            ("estado", "sin_servicio"),
        ],
    )
    def test_valida_tareas_fuentes_y_estado(self, nodo_cut, curador, como, campo, valor):
        respuesta = como(curador).post("/api/v1/servicios", {**NUEVO, campo: valor}, format="json")

        assert respuesta.status_code == 400
        assert codigo(respuesta) == "VALIDACION_FALLIDA"


class TestEditar:
    def test_un_curador_edita_y_queda_antes_y_despues(self, nodo_cut, curador, como):
        crear_servicio(nodo_cut)

        respuesta = como(curador).patch(
            "/api/v1/servicios/buscador-cut", {"estado": "disponible"}, format="json"
        )

        assert respuesta.status_code == 200
        assert respuesta.json()["estado"] == "disponible"
        entrada = Bitacora.objects.get(accion="editar_servicio")
        assert entrada.antes["estado"] == "en_construccion"
        assert entrada.despues["estado"] == "disponible"

    def test_sin_cambios_no_escribe_bitacora(self, nodo_cut, curador, como):
        crear_servicio(nodo_cut)

        como(curador).patch(
            "/api/v1/servicios/buscador-cut", {"estado": "en_construccion"}, format="json"
        )

        assert not Bitacora.objects.filter(accion="editar_servicio").exists()

    @pytest.mark.parametrize("campo,valor", [("slug", "otro"), ("nodo", "otro"), ("color", "rojo")])
    def test_slug_y_nodo_no_cambian_ni_hay_campos_inventados(
        self, nodo_cut, curador, como, campo, valor
    ):
        crear_servicio(nodo_cut)

        respuesta = como(curador).patch(
            "/api/v1/servicios/buscador-cut", {campo: valor}, format="json"
        )

        assert respuesta.status_code == 400
        assert respuesta.json()["error"]["detalles"][0]["campo"] == campo
        assert Servicio.objects.get().slug == "buscador-cut"

    def test_un_lector_no_edita(self, nodo_cut, lector, como):
        crear_servicio(nodo_cut)

        respuesta = como(lector).patch(
            "/api/v1/servicios/buscador-cut", {"estado": "disponible"}, format="json"
        )

        assert respuesta.status_code == 403
        assert Servicio.objects.get().estado == "en_construccion"
