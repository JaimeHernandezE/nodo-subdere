from django.db import migrations

from apps.core import foto_cut
from apps.core.cut import canonico


def cargar(apps, schema_editor):
    Municipio = apps.get_model("core", "Municipio")
    comunas = foto_cut.leer("comunas")["datos"]
    Municipio.objects.bulk_create(
        Municipio(cut=canonico(comuna["comuna_id"], "comuna"), nombre=comuna["nombre"])
        for comuna in comunas
    )


def descargar(apps, schema_editor):
    apps.get_model("core", "Municipio").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(cargar, descargar),
    ]
