"""Un servicio es una pantalla construida sobre un nodo, no un nodo filtrado.

Lo mantiene un curador. `slug` y `nodo` no cambian: otro nodo es otro servicio.
Ver INSTRUCCIONES.md §2.
"""

from django.db import models

from apps.core.models import ModeloBase

CAMPOS_EDITABLES = ("nombre", "funcion", "descripcion", "tareas", "fuentes", "estado", "nota")


class Estado(models.TextChoices):
    DISPONIBLE = "disponible", "Disponible"
    EN_CONSTRUCCION = "en_construccion", "En construcción"
    DESEABLE = "deseable", "Deseable"


class Servicio(ModeloBase):
    nodo = models.ForeignKey("catalogo.Nodo", on_delete=models.PROTECT, related_name="servicios")
    slug = models.SlugField(max_length=100, unique=True, help_text="Inmutable.")
    nombre = models.CharField(max_length=200, help_text="La herramienta, no el nodo.")
    funcion = models.CharField("función", max_length=300, help_text="Una línea, para la tarjeta.")
    descripcion = models.TextField("descripción")
    tareas = models.JSONField(default=list, help_text="Lista de frases.")
    fuentes = models.JSONField(default=list, help_text="Lista de {dato, origen}.")
    estado = models.CharField(max_length=20, choices=Estado, default=Estado.EN_CONSTRUCCION)
    nota = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "servicio"
        verbose_name_plural = "servicios"

    def __str__(self) -> str:
        return self.nombre
