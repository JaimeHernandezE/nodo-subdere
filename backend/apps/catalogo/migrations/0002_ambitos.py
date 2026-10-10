from django.db import migrations

AMBITOS = [("SGM", 1), ("Transversal", 2)]


def cargar(apps, schema_editor):
    Ambito = apps.get_model("catalogo", "Ambito")
    for nombre, orden in AMBITOS:
        Ambito.objects.create(nombre=nombre, orden=orden)


def descargar(apps, schema_editor):
    apps.get_model("catalogo", "Ambito").objects.filter(
        nombre__in=[nombre for nombre, _ in AMBITOS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalogo", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(cargar, descargar),
    ]
