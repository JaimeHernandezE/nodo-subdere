from django.db import migrations

AMBITOS = [("SGM", 1), ("Transversal", 2)]
# El nodo ya pasó por un renombre, y el enlace antiguo había circulado.
ALIAS = [("division-territorial", "cut")]


def cargar(apps, schema_editor):
    Ambito = apps.get_model("catalogo", "Ambito")
    Alias = apps.get_model("catalogo", "Alias")
    for nombre, orden in AMBITOS:
        Ambito.objects.create(nombre=nombre, orden=orden)
    for identificador, destino in ALIAS:
        Alias.objects.create(identificador=identificador, destino=destino)


def descargar(apps, schema_editor):
    apps.get_model("catalogo", "Alias").objects.filter(
        identificador__in=[identificador for identificador, _ in ALIAS]
    ).delete()
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
