"""Entradas de la wiki y sus versiones en Markdown. Ver INSTRUCCIONES.md §1.

Una versión no se corrige: lo único que cambia es pasar de borrador a publicada.
El nodo se nombra por su identificador, no por clave foránea, para que el contenido
inicial pueda nombrarlo antes de que la sincronización lo cree.
"""

from django.db import models

from apps.core.models import ModeloBase

from .errores import VersionInmutable

CAMPOS_EDITABLES = ("titulo", "descripcion", "nodo", "seccion", "orden")
CONTENIDO_DE_VERSION = ("entrada", "markdown", "resumen", "autor")


class Seccion(models.TextChoices):
    """En el orden del menú de la wiki. La portada no tiene sección."""

    USAR_EL_NODO = "usar_el_nodo", "Usar el nodo"
    INTERCAMBIOS = "intercambios", "Intercambios"
    CODIGOS = "codigos", "Códigos y datos maestros"
    NORMAS = "normas", "Marco normativo"
    REFERENCIA = "referencia", "Referencia"


ORDEN_DE_SECCIONES = {"": 0} | {valor: i for i, valor in enumerate(Seccion.values, start=1)}


class Entrada(ModeloBase):
    slug = models.SlugField(max_length=100, unique=True, help_text="Inmutable.")
    titulo = models.CharField("título", max_length=200)
    descripcion = models.CharField("descripción", max_length=300, help_text="Para el índice.")
    nodo = models.SlugField(
        max_length=100, blank=True, help_text="Identificador del nodo. No es clave foránea."
    )
    seccion = models.CharField("sección", max_length=20, choices=Seccion, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)
    vigente = models.ForeignKey(
        "wiki.Version", null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["seccion", "orden", "titulo"]
        verbose_name = "entrada"
        verbose_name_plural = "entradas"

    def __str__(self) -> str:
        return self.titulo


class VersionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        if set(kwargs) & set(CONTENIDO_DE_VERSION):
            raise VersionInmutable()
        return super().update(**kwargs)

    def bulk_update(self, objs, fields, batch_size=None):
        if set(fields) & set(CONTENIDO_DE_VERSION):
            raise VersionInmutable()
        return super().bulk_update(objs, fields, batch_size=batch_size)

    def delete(self):
        raise VersionInmutable()


class Version(ModeloBase):
    entrada = models.ForeignKey(Entrada, related_name="versiones", on_delete=models.PROTECT)
    markdown = models.TextField()
    resumen = models.CharField(max_length=300, help_text="Qué cambió, para el historial.")
    autor = models.ForeignKey(
        "cuentas.Perfil",
        null=True,
        blank=True,
        related_name="versiones_wiki",
        on_delete=models.PROTECT,
        help_text="Nulo: contenido inicial, transcrito desde la maqueta.",
    )
    publicada = models.BooleanField(default=False)
    publicada_en = models.DateTimeField(null=True, blank=True)

    objects = VersionQuerySet.as_manager()

    class Meta:
        ordering = ["entrada", "-creado_en", "-id"]
        verbose_name = "versión"
        verbose_name_plural = "versiones"

    def __str__(self) -> str:
        return f"{self.entrada_id} v{self.pk}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            guardada = (
                type(self)
                .objects.filter(pk=self.pk)
                .values("entrada_id", "markdown", "resumen", "autor_id", "publicada")
                .get()
            )
            actual = {
                "entrada_id": self.entrada_id,
                "markdown": self.markdown,
                "resumen": self.resumen,
                "autor_id": self.autor_id,
            }
            if any(guardada[campo] != valor for campo, valor in actual.items()):
                raise VersionInmutable()
            if guardada["publicada"] and not self.publicada:
                raise VersionInmutable("Una versión publicada no vuelve a borrador.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise VersionInmutable()
