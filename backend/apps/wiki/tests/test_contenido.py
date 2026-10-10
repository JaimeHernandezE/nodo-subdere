"""El contenido inicial: las 11 páginas de la maqueta, transcritas por la migración 0002."""

import re

import pytest

from apps.wiki.api.v1.entradas_view import html_de
from apps.wiki.models import Entrada

pytestmark = pytest.mark.django_db

SLUGS = {
    "inicio",
    "recorrido",
    "consumir",
    "conectar",
    "ficha",
    "cut",
    "permisos-de-circulacion",
    "codigos",
    "normas",
    "glosario",
    "decisiones",
}
ENLACE_INTERNO = re.compile(r'href="/wiki(?:/([a-z0-9-]+))?(?:#([a-z0-9-]+))?"')
RUTAS_DEL_SITIO = re.compile(
    r'href="/(?:que-es|apis(?:/[a-z0-9-]+)?|servicios(?:/[a-z0-9-]+)?|participar)?"'
)
SECCIONES_DEL_INDICE = {"usar-el-nodo", "intercambios", "codigos", "normas", "referencia"}


def _publicadas() -> dict[str, Entrada]:
    return {e.slug: e for e in Entrada.objects.select_related("vigente")}


def test_estan_las_once_publicadas():
    entradas = _publicadas()
    assert set(entradas) == SLUGS
    assert all(e.vigente and e.vigente.publicada for e in entradas.values())
    assert all(e.vigente.autor_id is None for e in entradas.values())


@pytest.mark.parametrize("slug", sorted(SLUGS))
def test_el_markdown_no_trae_html(slug):
    markdown = Entrada.objects.get(slug=slug).vigente.markdown
    assert not re.search(r"<\s*/?\s*[a-zA-Z][^>]*>", markdown)


@pytest.mark.parametrize("slug", sorted(SLUGS))
def test_no_quedan_contenedores_sin_cerrar(slug):
    html = html_de(Entrada.objects.get(slug=slug).vigente)
    assert ":::" not in html


def test_enlaces_internos_resuelven():
    entradas = _publicadas()
    ids = {
        slug: set(re.findall(r'<h[2-4] id="([^"]+)"', html_de(e.vigente)))
        for slug, e in entradas.items()
    }
    revisados = 0
    for origen, entrada in entradas.items():
        for destino, ancla in ENLACE_INTERNO.findall(html_de(entrada.vigente)):
            revisados += 1
            if not destino:
                assert ancla in SECCIONES_DEL_INDICE | {""}, (origen, ancla)
                continue
            assert destino in entradas, (origen, destino)
            if ancla:
                assert ancla in ids[destino], (origen, destino, ancla)
    assert revisados > 20


def test_no_quedan_enlaces_a_la_maqueta():
    for slug, entrada in _publicadas().items():
        assert ".html" not in entrada.vigente.markdown, slug


def test_enlaces_al_resto_del_sitio_son_rutas_conocidas():
    for slug, entrada in _publicadas().items():
        for href in re.findall(r'href="(/[^"]*)"', html_de(entrada.vigente)):
            if href.startswith("/wiki"):
                continue
            assert RUTAS_DEL_SITIO.fullmatch(f'href="{href}"'), (slug, href)
