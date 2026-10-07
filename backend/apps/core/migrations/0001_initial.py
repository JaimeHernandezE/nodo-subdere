import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Municipio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "cut",
                    models.CharField(
                        max_length=5,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^\\d{5}$", "El código CUT de comuna tiene 5 dígitos."
                            )
                        ],
                        verbose_name="código CUT",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name": "municipio",
                "verbose_name_plural": "municipios",
                "ordering": ["cut"],
            },
        ),
    ]
