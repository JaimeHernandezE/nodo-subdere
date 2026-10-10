import pytest

from apps.wiki.markdown import renderizar, slug


class TestSaneamiento:
    """Cada vector, por separado: lo que no está en la lista blanca no llega al sitio."""

    def test_script_queda_como_texto(self):
        html = renderizar("<script>alert(1)</script>")
        assert "<script" not in html
        assert "&lt;script&gt;" in html

    def test_html_en_linea_queda_como_texto(self):
        html = renderizar('Hola <img src=x onerror="alert(1)"> mundo')
        assert "<img" not in html

    @pytest.mark.parametrize(
        "destino",
        ["javascript:alert(1)", "JAVASCRIPT:alert(1)", "data:text/html;base64,PHNjcmlwdD4="],
    )
    def test_enlace_con_esquema_peligroso_no_es_enlace(self, destino):
        html = renderizar(f"[pinchar]({destino})")
        assert "href" not in html

    def test_enlace_con_entidades_no_cuela_javascript(self):
        html = renderizar("[pinchar](&#106;avascript:alert(1))")
        assert "href" not in html

    def test_imagen_no_se_publica(self):
        assert "<img" not in renderizar("![x](https://ejemplo.cl/x.png)")

    def test_enlace_externo_lleva_rel(self):
        html = renderizar("[sitio](https://ejemplo.cl)")
        assert 'href="https://ejemplo.cl"' in html
        assert 'rel="noopener noreferrer"' in html

    def test_estilo_de_tabla_solo_alinea(self):
        html = renderizar("| a |\n|--:|\n| 1 |")
        assert "text-align:right" in html.replace(" ", "")

    def test_contenedor_desconocido_queda_como_texto(self):
        html = renderizar("::: peligro\nHola\n:::")
        assert "<div" not in html
        assert "peligro" in html

    @pytest.mark.parametrize("nombre", ["aviso", "tecnico", "tarjeta"])
    def test_contenedor_conocido(self, nombre):
        assert f'<div class="{nombre}">' in renderizar(f"::: {nombre}\nHola\n:::")

    def test_contenedores_anidados(self):
        texto = ":::: tarjetas\n::: tarjeta\nUna\n:::\n::: tarjeta\nOtra\n:::\n::::"
        html = renderizar(texto)
        assert html.count('<div class="tarjeta">') == 2
        assert html.index('<div class="tarjetas">') < html.index('<div class="tarjeta">')
        assert ":::" not in html


class TestTitulos:
    def test_titulos_llevan_id(self):
        html = renderizar("## Cómo se compone el código\n\n### Año 2018")
        assert 'id="como-se-compone-el-codigo"' in html
        assert 'id="ano-2018"' in html

    def test_h1_no_lleva_id(self):
        assert "id=" not in renderizar("# Título")

    def test_slug_como_la_maqueta(self):
        assert slug("  ¿Qué es un CUT?  ") == "que-es-un-cut"
