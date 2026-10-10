import time

import pytest
from rest_framework.test import APIClient

from apps.catalogo.models import Nodo, Visibilidad
from apps.cuentas.models import Bitacora

from .conftest import CONTRATO, crear_nodo, especificar

pytestmark = pytest.mark.django_db

anonimo = APIClient


def codigo(respuesta) -> str:
    return respuesta.json()["error"]["codigo"]


class TestListado:
    def test_sin_sesion_solo_lista_los_publicados(self, publicado):
        crear_nodo("oculto", visibilidad=Visibilidad.OCULTO)
        crear_nodo("retirado", visibilidad=Visibilidad.RETIRADO)

        respuesta = anonimo().get("/api/v1/nodos")

        assert respuesta.status_code == 200
        assert [n["identificador"] for n in respuesta.json()] == ["cut"]

    def test_pedir_otra_visibilidad_sin_sesion_da_401(self, publicado):
        respuesta = anonimo().get("/api/v1/nodos", {"visibilidad": "todas"})

        assert respuesta.status_code == 401
        assert codigo(respuesta) == "NO_AUTENTICADO"

    def test_con_sesion_lista_todas_o_una_visibilidad(self, publicado, lector, como):
        crear_nodo("oculto", visibilidad=Visibilidad.OCULTO)
        crear_nodo("retirado", visibilidad=Visibilidad.RETIRADO)
        cliente = como(lector)

        todas = cliente.get("/api/v1/nodos", {"visibilidad": "todas"}).json()
        ocultos = cliente.get("/api/v1/nodos", {"visibilidad": "oculto"}).json()

        assert {n["identificador"] for n in todas} == {"cut", "oculto", "retirado"}
        assert [n["visibilidad"] for n in ocultos] == ["oculto"]

    def test_una_visibilidad_desconocida_da_400(self, lector, como):
        respuesta = como(lector).get("/api/v1/nodos", {"visibilidad": "borrador"})

        assert respuesta.status_code == 400
        assert codigo(respuesta) == "VALIDACION_FALLIDA"

    def test_filtra_por_ambito_clase_madurez_e_intercambio(self, publicado):
        otro = crear_nodo("sgm-core", clase="plataforma", intercambio="", madurez="Deseable")
        especificar(otro)

        def pedir(**filtros):
            return [n["identificador"] for n in anonimo().get("/api/v1/nodos", filtros).json()]

        assert pedir(clase="plataforma") == ["sgm-core"]
        assert pedir(madurez="En desarrollo") == ["cut"]
        assert pedir(intercambio="consulta") == ["cut"]
        assert pedir(ambito="SGM") == []


class TestOculto:
    RUTAS = [
        "/api/v1/nodos/{}",
        "/api/v1/nodos/{}/especificacion",
        "/api/v1/nodos/{}/especificacion/archivo",
    ]

    @pytest.fixture
    def oculto(self, db):
        nodo = crear_nodo(visibilidad=Visibilidad.OCULTO)
        especificar(nodo)
        return nodo

    @pytest.mark.parametrize("ruta", RUTAS)
    @pytest.mark.parametrize("identificador", ["cut", "codigos-territoriales"])
    def test_sin_sesion_es_un_404_tambien_por_alias(self, oculto, alias, ruta, identificador):
        respuesta = anonimo().get(ruta.format(identificador))

        assert respuesta.status_code == 404
        assert codigo(respuesta) == "NO_ENCONTRADO"

    def test_el_404_de_un_oculto_es_igual_al_de_uno_que_no_existe(self, oculto):
        oculto_ = anonimo().get("/api/v1/nodos/cut")
        inexistente = anonimo().get("/api/v1/nodos/no-existe")

        assert oculto_.json() == inexistente.json()

    @pytest.mark.parametrize("ruta", RUTAS)
    def test_con_un_perfil_responde(self, oculto, lector, como, ruta):
        respuesta = como(lector).get(ruta.format("cut"))

        assert respuesta.status_code == 200

    def test_con_un_perfil_la_ficha_dice_su_visibilidad(self, oculto, lector, como):
        assert como(lector).get("/api/v1/nodos/cut").json()["visibilidad"] == "oculto"


class TestTokenQueNoSirve:
    @pytest.fixture
    def vencido(self, realm, lector):
        cliente = APIClient()
        token = realm.token(lector, exp=int(time.time()) - 10)
        cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return cliente

    def test_no_impide_leer_un_publicado(self, publicado, vencido):
        assert vencido.get("/api/v1/nodos/cut").status_code == 200
        assert vencido.get("/api/v1/nodos").status_code == 200

    def test_no_da_acceso_a_un_oculto(self, vencido):
        especificar(crear_nodo("oculto", visibilidad=Visibilidad.OCULTO))

        assert vencido.get("/api/v1/nodos/oculto").status_code == 404

    def test_un_token_sin_perfil_tampoco(self, realm):
        crear_nodo("oculto", visibilidad=Visibilidad.OCULTO)
        cliente = APIClient()
        cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {realm.token(None)}")

        assert cliente.get("/api/v1/nodos/oculto").status_code == 404


class TestFicha:
    def test_por_alias_responde_con_el_identificador_vigente(self, publicado, alias):
        respuesta = anonimo().get("/api/v1/nodos/codigos-territoriales")

        assert respuesta.status_code == 200
        assert respuesta.json()["identificador"] == "cut"

    def test_agrupa_como_la_ficha_y_trae_la_lectura(self, publicado):
        ficha = anonimo().get("/api/v1/nodos/cut").json()

        assert ficha["responsable"] == {
            "organismo": "SUBDERE",
            "equipo": "Equipo SEM",
            "correo": "equipo.sem@subdere.gov.cl",
        }
        assert ficha["procedencia"] is None
        assert ficha["ambito"] == "Transversal"
        assert ficha["commit"] == publicado.commit
        assert ficha["leido_en"]
        assert ficha["especificacion"]["version"] == "1.0.0"
        assert ficha["especificacion"]["archivo"].endswith(
            "/api/v1/nodos/cut/especificacion/archivo"
        )

    def test_no_trae_wiki_ni_servicios(self, publicado):
        ficha = anonimo().get("/api/v1/nodos/cut").json()

        assert "wiki" not in ficha
        assert "servicios" not in ficha


class TestRetirado:
    @pytest.fixture
    def retirado(self, db):
        nodo = crear_nodo(visibilidad=Visibilidad.RETIRADO)
        especificar(nodo)
        return nodo

    @pytest.mark.parametrize("ruta", ["/api/v1/nodos/cut", "/api/v1/nodos/cut/especificacion"])
    def test_responde_410_con_la_fecha_de_la_ultima_lectura(self, retirado, ruta):
        respuesta = anonimo().get(ruta)

        assert respuesta.status_code == 410
        error = respuesta.json()["error"]
        assert error["codigo"] == "NODO_RETIRADO"
        assert error["detalles"] == [{"campo": "leido_en", "valor": retirado.leido_en.isoformat()}]


class TestArchivo:
    def test_lo_devuelve_tal_como_se_guardo(self, publicado):
        respuesta = anonimo().get("/api/v1/nodos/cut/especificacion/archivo")

        assert respuesta.status_code == 200
        assert respuesta.content == CONTRATO.encode("utf-8")
        assert respuesta["Content-Type"] == "application/yaml; charset=utf-8"
        assert respuesta["ETag"] == f'"{publicado.especificacion_vigente.huella}"'

    def test_pedirlo_como_yaml_no_cambia_nada(self, publicado):
        respuesta = anonimo().get(
            "/api/v1/nodos/cut/especificacion/archivo", HTTP_ACCEPT="application/yaml"
        )

        assert respuesta.status_code == 200

    def test_solo_metadato_da_404_en_el_archivo(self, db):
        especificar(crear_nodo(), contenido="")

        metadatos = anonimo().get("/api/v1/nodos/cut/especificacion")
        archivo = anonimo().get(
            "/api/v1/nodos/cut/especificacion/archivo", HTTP_ACCEPT="application/yaml"
        )

        assert metadatos.json()["archivo"] is None
        assert metadatos.json()["formato"] == "descripcion"
        assert archivo.status_code == 404
        assert codigo(archivo) == "NO_ENCONTRADO"


class TestEdicion:
    def test_un_campo_de_ficha_da_400_campo_de_ficha(self, publicado, curador, como):
        respuesta = como(curador).patch("/api/v1/nodos/cut", {"funcion": "x"}, format="json")

        assert respuesta.status_code == 400
        assert codigo(respuesta) == "CAMPO_DE_FICHA"
        assert Nodo.objects.get(pk=publicado.pk).funcion == publicado.funcion

    @pytest.mark.parametrize("campo", ["responsable", "especificacion", "identificador"])
    def test_tambien_los_agrupados_y_el_identificador(self, publicado, curador, como, campo):
        respuesta = como(curador).patch("/api/v1/nodos/cut", {campo: "x"}, format="json")

        assert codigo(respuesta) == "CAMPO_DE_FICHA"

    def test_un_campo_que_no_existe_da_400_validacion(self, publicado, curador, como):
        respuesta = como(curador).patch("/api/v1/nodos/cut", {"color": "rojo"}, format="json")

        assert respuesta.status_code == 400
        assert codigo(respuesta) == "VALIDACION_FALLIDA"

    def test_edita_los_editoriales_y_deja_bitacora(self, publicado, curador, como):
        respuesta = como(curador).patch(
            "/api/v1/nodos/cut",
            {"visibilidad": "oculto", "nota_editorial": "En revisión."},
            format="json",
        )

        assert respuesta.status_code == 200
        assert respuesta.json()["visibilidad"] == "oculto"
        entrada = Bitacora.objects.get(accion="editar_nodo")
        assert entrada.perfil == curador
        assert entrada.objeto == "catalogo.Nodo:cut"
        assert entrada.antes["visibilidad"] == "publicado"
        assert entrada.despues["visibilidad"] == "oculto"

    def test_sin_cambios_no_deja_bitacora(self, publicado, curador, como):
        como(curador).patch("/api/v1/nodos/cut", {"visibilidad": "publicado"}, format="json")

        assert not Bitacora.objects.exists()

    def test_no_publica_sin_especificacion_vigente(self, curador, como):
        crear_nodo(visibilidad=Visibilidad.OCULTO)

        respuesta = como(curador).patch(
            "/api/v1/nodos/cut", {"visibilidad": "publicado"}, format="json"
        )

        assert respuesta.status_code == 400
        assert codigo(respuesta) == "VALIDACION_FALLIDA"
        assert respuesta.json()["error"]["detalles"][0]["campo"] == "visibilidad"

    def test_de_retirado_solo_se_pasa_a_oculto(self, curador, como):
        especificar(crear_nodo(visibilidad=Visibilidad.RETIRADO))
        cliente = como(curador)

        publicar = cliente.patch("/api/v1/nodos/cut", {"visibilidad": "publicado"}, format="json")
        ocultar = cliente.patch("/api/v1/nodos/cut", {"visibilidad": "oculto"}, format="json")

        assert publicar.status_code == 400
        assert ocultar.status_code == 200

    def test_un_lector_no_edita_y_sin_sesion_es_401(self, publicado, lector, como):
        cuerpo = {"orden": 2}

        assert como(lector).patch("/api/v1/nodos/cut", cuerpo, format="json").status_code == 403
        assert anonimo().patch("/api/v1/nodos/cut", cuerpo, format="json").status_code == 401


class TestApoyo:
    def test_ambitos_y_municipios_son_publicos(self, db):
        ambitos = anonimo().get("/api/v1/ambitos")
        municipios = anonimo().get("/api/v1/municipios")

        assert [a["nombre"] for a in ambitos.json()] == ["SGM", "Transversal"]
        assert len(municipios.json()) == 346
        assert municipios.json()[0] == {"cut": "01101", "nombre": "Iquique"}

    def test_el_esquema_describe_el_catalogo(self, db):
        rutas = anonimo().get("/api/v1/schema/", {"format": "json"}).json()["paths"]

        assert "/api/v1/nodos/{identificador}/especificacion/archivo" in rutas
