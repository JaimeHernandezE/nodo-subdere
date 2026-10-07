from django.core.validators import RegexValidator
from django.db import models


class ModeloBase(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Municipio(ModeloBase):
    """Dato de referencia territorial: 346 comunas, cargadas desde la foto del CUT."""

    cut = models.CharField(
        "código CUT",
        max_length=5,
        unique=True,
        validators=[RegexValidator(r"^\d{5}$", "El código CUT de comuna tiene 5 dígitos.")],
    )
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ["cut"]
        verbose_name = "municipio"
        verbose_name_plural = "municipios"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.cut})"

    @property
    def region(self) -> str:
        return self.cut[:2]

    @property
    def provincia(self) -> str:
        return self.cut[:3]
