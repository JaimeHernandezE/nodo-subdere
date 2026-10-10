import pytest
from rest_framework.test import APIClient

from apps.catalogo.models import Visibilidad
from apps.cuentas.models import Bitacora
from apps.wiki.errores import VersionInmutable
from apps.wiki.models import Entrada, Version

from .conftest import crear_entrada, crear_nodo

pytestmark = pytest.mark.django_db

INICIALES = 11


def crear_nodo_oculto():
    return crear_nodo("cut", visibilidad=Visibilidad.OCULTO)


def crear_nodo_publicado():
    return crear_nodo("cut")


def slugs(respuesta) -> list[str]:
    assert respuesta.status_code == 200, respuesta.content
    return [entrada["slug"] for entrada in respuesta.json()]


class TestModelo:
    def test_version_no_se_corrige(self, entrada):
        version = entrada.vigente
        version.markdown = "Otro texto"
        with pytest.raises(VersionInmutable):
            version.save()

    def test_version_publicada_no_vuelve_a_borrador(self, entrada):
        version = entrada.vigente
        version.publicada = False
        with pytest.raises(VersionInmutable):
            version.save()

    def test_version_no_se_borra(self, entrada):
        with pytest.raises(VersionInmutable):
            entrada.vigente.delete()
        with pytest.raises(VersionInmutable):
            Version.objects.filter(entrada=entrada).delete()

    def test_update_masivo_del_contenido_no_se_permite(self, entrada):
        with pytest.raises(VersionInmutable):
            Version.objects.filter(entrada=entrada).update(markdown="x")


class TestIndice:
    def test_sin_sesion_lista_lo_publicado_por_seccion(self):
        lista = slugs(APIClient().get("/api/v1/wiki"))
        assert len(lista) == INICIALES
        assert lista[0] == "inicio"
        assert lista[1:5] == ["recorrido", "consumir", "conectar", "ficha"]
        assert lista[-2:] == ["glosario", "decisiones"]

    def test_borrador_no_aparece_sin_sesion(self):
        crear_entrada("borrador", publicada=False)
        assert "borrador" not in slugs(APIClient().get("/api/v1/wiki"))

    def test_todas_exige_sesion(self):
        respuesta = APIClient().get("/api/v1/wiki", {"estado": "todas"})
        assert respuesta.status_code == 401

    def test_todas_incluye_borradores(self, como, lector):
        crear_entrada("borrador", publicada=False)
        lista = slugs(como(lector).get("/api/v1/wiki", {"estado": "todas"}))
        assert "borrador" in lista

    def test_estado_desconocido(self):
        respuesta = APIClient().get("/api/v1/wiki", {"estado": "otras"})
        assert respuesta.status_code == 400
        assert respuesta.json()["error"]["codigo"] == "VALIDACION_FALLIDA"

    def test_filtra_por_nodo(self):
        assert slugs(APIClient().get("/api/v1/wiki", {"nodo": "cut"})) == ["cut"]

    def test_filtra_por_alias_del_nodo(self, alias):
        lista = slugs(APIClient().get("/api/v1/wiki", {"nodo": "codigos-territoriales"}))
        assert lista == ["cut"]

    def test_entrada_de_nodo_oculto_solo_con_sesion(self, como, lector):
        crear_nodo_oculto()
        assert "cut" not in slugs(APIClient().get("/api/v1/wiki"))
        assert "cut" in slugs(como(lector).get("/api/v1/wiki"))

    def test_entrada_de_nodo_publicado_se_ve(self):
        crear_nodo_publicado()
        assert "cut" in slugs(APIClient().get("/api/v1/wiki"))


class TestEntrada:
    def test_entrada_publicada_trae_html(self, entrada):
        respuesta = APIClient().get("/api/v1/wiki/prueba")
        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo["version"] == entrada.vigente_id
        assert '<h2 id="hola">Hola</h2>' in cuerpo["html"]
        assert cuerpo["publicada"] is True

    def test_sin_version_publicada_es_404(self):
        crear_entrada("borrador", publicada=False)
        respuesta = APIClient().get("/api/v1/wiki/borrador")
        assert respuesta.status_code == 404

    def test_inexistente_es_404(self):
        assert APIClient().get("/api/v1/wiki/no-existe").status_code == 404

    def test_entrada_de_nodo_oculto_es_404_sin_sesion(self, como, lector):
        crear_nodo_oculto()
        assert APIClient().get("/api/v1/wiki/cut").status_code == 404
        assert como(lector).get("/api/v1/wiki/cut").status_code == 200


class TestCrearYEditar:
    NUEVA = {
        "slug": "nueva",
        "titulo": "Nueva",
        "descripcion": "Una entrada nueva.",
        "seccion": "referencia",
        "orden": 3,
    }

    def test_editor_crea_entrada_con_bitacora(self, como, editor):
        respuesta = como(editor).post("/api/v1/wiki", self.NUEVA, format="json")
        assert respuesta.status_code == 201, respuesta.content
        assert respuesta.json()["publicada"] is False
        registro = Bitacora.objects.get(accion="crear_entrada")
        assert registro.objeto == "wiki.Entrada:nueva"
        assert registro.perfil == editor
        assert registro.despues["titulo"] == "Nueva"

    def test_lector_no_crea_entradas(self, como, lector):
        respuesta = como(lector).post("/api/v1/wiki", self.NUEVA, format="json")
        assert respuesta.status_code == 403

    def test_sin_sesion_no_crea_entradas(self):
        respuesta = APIClient().post("/api/v1/wiki", self.NUEVA, format="json")
        assert respuesta.status_code == 401

    def test_slug_repetido(self, como, editor, entrada):
        cuerpo = {**self.NUEVA, "slug": "prueba"}
        assert como(editor).post("/api/v1/wiki", cuerpo, format="json").status_code == 400

    def test_nodo_inexistente(self, como, editor):
        cuerpo = {**self.NUEVA, "nodo": "no-existe"}
        respuesta = como(editor).post("/api/v1/wiki", cuerpo, format="json")
        assert respuesta.status_code == 400
        assert "nodo" in str(respuesta.json()["error"]["detalles"])

    def test_nodo_por_alias_queda_con_su_identificador(self, como, editor, alias):
        crear_nodo_publicado()
        cuerpo = {**self.NUEVA, "nodo": "codigos-territoriales"}
        respuesta = como(editor).post("/api/v1/wiki", cuerpo, format="json")
        assert respuesta.status_code == 201, respuesta.content
        assert Entrada.objects.get(slug="nueva").nodo == "cut"

    def test_editar_registra_antes_y_despues(self, como, editor, entrada):
        respuesta = como(editor).patch(
            "/api/v1/wiki/prueba", {"titulo": "Otro título"}, format="json"
        )
        assert respuesta.status_code == 200, respuesta.content
        registro = Bitacora.objects.get(accion="editar_entrada")
        assert registro.antes["titulo"] == "Prueba"
        assert registro.despues["titulo"] == "Otro título"

    def test_editar_sin_cambios_no_registra(self, como, editor, entrada):
        como(editor).patch("/api/v1/wiki/prueba", {"titulo": "Prueba"}, format="json")
        assert not Bitacora.objects.filter(accion="editar_entrada").exists()

    @pytest.mark.parametrize("campo", ["slug", "vigente", "inventado"])
    def test_editar_campo_no_editable(self, como, editor, entrada, campo):
        respuesta = como(editor).patch("/api/v1/wiki/prueba", {campo: "x"}, format="json")
        assert respuesta.status_code == 400
        assert respuesta.json()["error"]["codigo"] == "VALIDACION_FALLIDA"

    def test_lector_no_edita(self, como, lector, entrada):
        respuesta = como(lector).patch("/api/v1/wiki/prueba", {"titulo": "x"}, format="json")
        assert respuesta.status_code == 403


class TestVersiones:
    def test_editor_crea_borrador(self, como, editor, entrada):
        respuesta = como(editor).post(
            "/api/v1/wiki/prueba/versiones",
            {"markdown": "## Nuevo\n\nTexto nuevo.", "resumen": "Reescrita"},
            format="json",
        )
        assert respuesta.status_code == 201, respuesta.content
        cuerpo = respuesta.json()
        assert cuerpo["publicada"] is False
        assert cuerpo["vigente"] is False
        assert '<h2 id="nuevo">' in cuerpo["html"]
        assert Version.objects.get(pk=cuerpo["id"]).autor == editor

    def test_version_nueva_no_modifica_la_anterior(self, como, editor, entrada):
        anterior = entrada.vigente
        como(editor).post(
            "/api/v1/wiki/prueba/versiones",
            {"markdown": "Otro", "resumen": "Cambio"},
            format="json",
        )
        anterior.refresh_from_db()
        assert anterior.markdown == "## Hola\n\nUn párrafo."
        entrada.refresh_from_db()
        assert entrada.vigente_id == anterior.pk

    def test_borrador_no_se_ve_en_publico(self, como, editor, entrada):
        como(editor).post(
            "/api/v1/wiki/prueba/versiones",
            {"markdown": "Borrador secreto", "resumen": "Cambio"},
            format="json",
        )
        html = APIClient().get("/api/v1/wiki/prueba").json()["html"]
        assert "Borrador secreto" not in html

    def test_lector_no_crea_versiones(self, como, lector, entrada):
        respuesta = como(lector).post(
            "/api/v1/wiki/prueba/versiones", {"markdown": "x", "resumen": "x"}, format="json"
        )
        assert respuesta.status_code == 403

    def test_lector_ve_el_historial(self, como, lector, entrada):
        respuesta = como(lector).get("/api/v1/wiki/prueba/versiones")
        assert respuesta.status_code == 200
        assert [v["vigente"] for v in respuesta.json()] == [True]

    def test_historial_exige_sesion(self, entrada):
        assert APIClient().get("/api/v1/wiki/prueba/versiones").status_code == 401

    def test_contenido_inicial_sin_autor(self, como, lector):
        respuesta = como(lector).get("/api/v1/wiki/cut/versiones")
        assert respuesta.json()[0]["autor"] == "Contenido inicial"

    def test_lector_ve_una_version(self, como, lector, entrada):
        url = f"/api/v1/wiki/prueba/versiones/{entrada.vigente_id}"
        respuesta = como(lector).get(url)
        assert respuesta.status_code == 200
        assert respuesta.json()["markdown"] == "## Hola\n\nUn párrafo."

    def test_version_de_otra_entrada_es_404(self, como, lector, entrada):
        otra = crear_entrada("otra")
        url = f"/api/v1/wiki/prueba/versiones/{otra.vigente_id}"
        assert como(lector).get(url).status_code == 404


class TestPublicar:
    def _borrador(self, como, editor) -> int:
        respuesta = como(editor).post(
            "/api/v1/wiki/prueba/versiones",
            {"markdown": "## Publicada\n\nYa está.", "resumen": "Cambio"},
            format="json",
        )
        return respuesta.json()["id"]

    def test_publicar_cambia_la_vigente_y_registra(self, como, editor, entrada):
        anterior = entrada.vigente_id
        nueva = self._borrador(como, editor)
        respuesta = como(editor).post(f"/api/v1/wiki/prueba/versiones/{nueva}/publicar")
        assert respuesta.status_code == 200, respuesta.content
        assert respuesta.json()["vigente"] is True
        assert "Ya está." in APIClient().get("/api/v1/wiki/prueba").json()["html"]
        registro = Bitacora.objects.get(accion="publicar_entrada")
        assert registro.antes == {"version": anterior}
        assert registro.despues == {"version": nueva}
        assert registro.perfil == editor

    def test_volver_a_una_version_anterior(self, como, editor, entrada):
        anterior = entrada.vigente_id
        nueva = self._borrador(como, editor)
        como(editor).post(f"/api/v1/wiki/prueba/versiones/{nueva}/publicar")
        como(editor).post(f"/api/v1/wiki/prueba/versiones/{anterior}/publicar")
        entrada.refresh_from_db()
        assert entrada.vigente_id == anterior
        assert Bitacora.objects.filter(accion="publicar_entrada").count() == 2

    def test_publicar_la_vigente_no_registra(self, como, editor, entrada):
        url = f"/api/v1/wiki/prueba/versiones/{entrada.vigente_id}/publicar"
        assert como(editor).post(url).status_code == 200
        assert not Bitacora.objects.filter(accion="publicar_entrada").exists()

    def test_lector_no_publica(self, como, editor, lector, entrada):
        nueva = self._borrador(como, editor)
        url = f"/api/v1/wiki/prueba/versiones/{nueva}/publicar"
        assert como(lector).post(url).status_code == 403

    def test_publicar_en_entrada_sin_vigente(self, como, editor):
        entrada = crear_entrada("borrador", publicada=False)
        version = entrada.versiones.get()
        url = f"/api/v1/wiki/borrador/versiones/{version.pk}/publicar"
        assert como(editor).post(url).status_code == 200
        assert APIClient().get("/api/v1/wiki/borrador").status_code == 200
