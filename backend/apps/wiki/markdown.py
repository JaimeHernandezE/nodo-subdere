"""Markdown a HTML saneado. El único lugar donde se audita qué llega al sitio público.

La lista blanca es código, no configuración (HR-24). Ver INSTRUCCIONES.md §2.
"""

import re
import unicodedata

import nh3
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.container import container_plugin

# Los componentes de la maqueta. Un contenedor con otro nombre no genera nada.
CONTENEDORES = frozenset({"aviso", "tarjetas", "tarjeta", "tecnico"})

ETIQUETAS = frozenset(
    {
        "p", "br", "hr",
        "h2", "h3", "h4",
        "ul", "ol", "li",
        "table", "thead", "tbody", "tr", "th", "td",
        "pre", "code",
        "a", "strong", "em", "blockquote",
        "div",
    }
)  # fmt: skip
ATRIBUTOS = {
    "a": {"href", "title"},
    "h2": {"id"},
    "h3": {"id"},
    "h4": {"id"},
    "th": {"style"},
    "td": {"style"},
}
CLASES = {"div": set(CONTENEDORES)}
ESQUEMAS = frozenset({"http", "https", "mailto"})
# Las tablas alinean columnas con `style`; solo eso.
PROPIEDADES_DE_ESTILO = frozenset({"text-align"})


def slug(texto: str) -> str:
    """El mismo que `wiki-nav.js` de la maqueta: sin tildes, en minúsculas y con guiones."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", texto.lower()) if not unicodedata.combining(c)
    )
    return re.sub(r"[^a-z0-9]+", "-", sin_tildes).strip("-")


def _motor() -> MarkdownIt:
    motor = MarkdownIt("commonmark", {"html": False}).enable("table")
    for nombre in sorted(CONTENEDORES):
        container_plugin(motor, nombre)
    anchors_plugin(motor, min_level=2, max_level=4, slug_func=slug)
    return motor


_MOTOR = _motor()


def renderizar(texto: str) -> str:
    return nh3.clean(
        _MOTOR.render(texto),
        tags=set(ETIQUETAS),
        attributes={etiqueta: set(nombres) for etiqueta, nombres in ATRIBUTOS.items()},
        allowed_classes={etiqueta: set(clases) for etiqueta, clases in CLASES.items()},
        url_schemes=set(ESQUEMAS),
        filter_style_properties=set(PROPIEDADES_DE_ESTILO),
        link_rel="noopener noreferrer",
    )
