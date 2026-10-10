import urllib.parse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.models import ModeloBase
from apps.cuentas.models import Perfil, SoloCrece


class TipoDeFuente(models.TextChoices):
    REPOSITORIO = "repositorio", "Repositorio"
    CARGA_MANUAL = "carga_manual", "Carga manual"


def problema_de_url(url: str) -> str:
    """Por qué `url` no sirve como dirección de un proyecto de GitLab; vacío si sirve."""
    partes = urllib.parse.urlsplit(url)
    if partes.scheme != "https" or not partes.hostname:
        return "Debe ser la dirección https del proyecto en GitLab."
    if partes.query or partes.fragment:
        return "Debe ser la dirección del proyecto, sin parámetros."
    if partes.path.strip("/").removesuffix(".git").count("/") < 1:
        return "Debe incluir el grupo y el proyecto, p. ej. https://host/grupo/proyecto."
    gitlab = urllib.parse.urlsplit(settings.REGISTRO_GIT_API_URL).hostname
    if gitlab and partes.hostname != gitlab:
        return f"El nodo lee un solo GitLab: la dirección tiene que estar en {gitlab}."
    return ""


class Fuente(ModeloBase):
    """Un repositorio registrado, o una carga manual de transición."""

    tipo = models.CharField(max_length=20, choices=TipoDeFuente, default=TipoDeFuente.REPOSITORIO)
    url = models.URLField(max_length=500, blank=True, help_text="Dirección del proyecto en GitLab.")
    rama = models.CharField(max_length=200, default="main")
    ruta_ficha = models.CharField(max_length=300, default="nodo/ficha.yaml")
    activa = models.BooleanField(default=True)
    nodo_identificador = models.SlugField(
        max_length=100,
        blank=True,
        help_text="Lo fija la primera lectura válida y no cambia después.",
    )

    class Meta:
        ordering = ["nodo_identificador", "url"]
        verbose_name = "fuente"
        verbose_name_plural = "fuentes"
        constraints = [
            models.UniqueConstraint(
                fields=["nodo_identificador"],
                condition=~Q(nodo_identificador=""),
                name="una_fuente_por_nodo",
            ),
            models.UniqueConstraint(
                fields=["url", "rama", "ruta_ficha"], name="fuente_direccion_unica"
            ),
            models.CheckConstraint(
                condition=~Q(tipo=TipoDeFuente.REPOSITORIO) | ~Q(url=""),
                name="repositorio_con_url",
            ),
        ]

    def __str__(self) -> str:
        return self.nodo_identificador or self.url or f"Fuente {self.pk}"

    @property
    def proyecto(self) -> str:
        """`grupo/proyecto`, como lo nombra la API de GitLab."""
        return urllib.parse.urlsplit(self.url).path.strip("/").removesuffix(".git")

    @property
    def ultima_lectura(self) -> "Lectura | None":
        return self.lecturas.order_by("-creado_en", "-pk").first()

    def clean(self):
        if self.tipo == TipoDeFuente.REPOSITORIO and (problema := problema_de_url(self.url)):
            raise ValidationError({"url": problema})


class Lectura(SoloCrece):
    """Cada intento de leer una fuente. Nunca se edita ni se borra."""

    fuente = models.ForeignKey(Fuente, on_delete=models.PROTECT, related_name="lecturas")
    perfil = models.ForeignKey(
        Perfil,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="lecturas",
        help_text="Quién pidió leer. Vacío: la tarea programada.",
    )
    commit = models.CharField(max_length=64, blank=True)
    contenido = models.TextField(blank=True, help_text="El YAML tal como se leyó.")
    valida = models.BooleanField()
    motivo = models.TextField(blank=True)

    class Meta:
        ordering = ["-creado_en", "-pk"]
        verbose_name = "lectura"
        verbose_name_plural = "lecturas"

    def __str__(self) -> str:
        estado = "válida" if self.valida else "inválida"
        return f"{self.fuente} {self.commit[:8]} {estado}"
