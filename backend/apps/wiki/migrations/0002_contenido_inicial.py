"""Las 11 páginas de la maqueta, transcritas a Markdown en apps/wiki/contenido/."""

from pathlib import Path

from django.db import migrations
from django.utils import timezone

CONTENIDO = Path(__file__).resolve().parent.parent / "contenido"
RESUMEN = "Transcrita desde la maqueta"

# slug, título, descripción, sección, orden, nodo
ENTRADAS = [
    (
        "inicio",
        "Wiki",
        "Cómo se usan las APIs, cómo se generan los códigos y en base a qué normas. "
        "La documentación de trabajo del Nodo SUBDERE.",
        "",
        0,
        "",
    ),
    (
        "recorrido",
        "Cómo funciona un intercambio",
        "El recorrido de un intercambio en el Nodo SUBDERE: qué pasa cuando el municipio "
        "entrega un informe y cuando pregunta por un dato.",
        "usar_el_nodo",
        1,
        "",
    ),
    (
        "consumir",
        "Cómo se usa una API",
        "Cómo se entra, cómo probar antes de operar, cómo se versionan los contratos y qué "
        "hacer cuando algo falla al usar una API del catálogo.",
        "usar_el_nodo",
        2,
        "",
    ),
    (
        "conectar",
        "Conectar un sistema",
        "Qué necesita un municipio o un proveedor para conectar su sistema al Nodo SUBDERE: "
        "qué se puede hacer hoy, qué falta y cómo cambian las versiones.",
        "usar_el_nodo",
        3,
        "",
    ),
    (
        "ficha",
        "Cómo leer una ficha",
        "Qué quiere decir cada estado, indicador y etiqueta de las fichas del catálogo de "
        "APIs del Nodo SUBDERE.",
        "usar_el_nodo",
        4,
        "",
    ),
    (
        "cut",
        "Códigos Únicos Territoriales",
        "Cómo se compone el Código Único Territorial, qué norma lo fija, por qué comuna no "
        "es lo mismo que municipio, y qué revisar antes de usar la API.",
        "intercambios",
        0,
        "cut",
    ),
    (
        "permisos-de-circulacion",
        "Permisos de circulación",
        "Cómo se compone una patente, cómo se paga un permiso de circulación y qué cambió "
        "entre la colección de referencia y la propuesta de contrato.",
        "intercambios",
        0,
        "permisos-de-circulacion",
    ),
    (
        "codigos",
        "Índice de códigos",
        "Quién define cada código que se intercambia con los municipios, cómo se numera y "
        "qué entradas faltan por escribir.",
        "codigos",
        0,
        "",
    ),
    (
        "normas",
        "Normas",
        "Las normas que obligan lo que define el estándar del Nodo SUBDERE, con la "
        "advertencia de si se leyó el texto o solo una referencia.",
        "normas",
        0,
        "",
    ),
    (
        "glosario",
        "Glosario",
        "Los conceptos que el sitio del Nodo SUBDERE usa en más de una página, definidos "
        "una sola vez.",
        "referencia",
        1,
        "",
    ),
    (
        "decisiones",
        "Decisiones de arquitectura",
        "Las decisiones que dan forma al estándar del Nodo SUBDERE, escritas como notas "
        "fechadas con su contexto y sus consecuencias.",
        "referencia",
        2,
        "",
    ),
]


def cargar(apps, schema_editor):
    Entrada = apps.get_model("wiki", "Entrada")
    Version = apps.get_model("wiki", "Version")
    ahora = timezone.now()
    for slug, titulo, descripcion, seccion, orden, nodo in ENTRADAS:
        entrada = Entrada.objects.create(
            slug=slug,
            titulo=titulo,
            descripcion=descripcion,
            seccion=seccion,
            orden=orden,
            nodo=nodo,
        )
        version = Version.objects.create(
            entrada=entrada,
            markdown=(CONTENIDO / f"{slug}.md").read_text(encoding="utf-8"),
            resumen=RESUMEN,
            autor=None,
            publicada=True,
            publicada_en=ahora,
        )
        entrada.vigente = version
        entrada.save(update_fields=["vigente"])


def descargar(apps, schema_editor):
    Entrada = apps.get_model("wiki", "Entrada")
    Version = apps.get_model("wiki", "Version")
    slugs = [slug for slug, *_ in ENTRADAS]
    Entrada.objects.filter(slug__in=slugs).update(vigente=None)
    Version.objects.filter(entrada__slug__in=slugs).delete()
    Entrada.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [("wiki", "0001_initial")]

    operations = [migrations.RunPython(cargar, descargar)]
