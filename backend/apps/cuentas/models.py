from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core import run
from apps.core.models import ModeloBase


class Rol(models.TextChoices):
    """Acumulativos: cada rol puede lo suyo y todo lo de los anteriores."""

    LECTOR = "lector", "Lector"
    EDITOR = "editor", "Editor"
    CURADOR = "curador", "Curador"
    ADMINISTRADOR = "administrador", "Administrador"


ORDEN_DE_ROLES = [Rol.LECTOR, Rol.EDITOR, Rol.CURADOR, Rol.ADMINISTRADOR]


class Perfil(ModeloBase):
    """Quién puede hacer qué en el nodo. La persona se identifica por el RUN, no por el `sub`."""

    run_numero = models.PositiveIntegerField("número del RUN")
    run_dv = models.CharField("dígito verificador", max_length=1)
    run_tipo = models.CharField("tipo de identificador", max_length=10, default="RUN")
    sub = models.CharField(
        max_length=255, blank=True, help_text="Subject del realm. Solo para depurar: no es llave."
    )
    nombre = models.CharField(max_length=200)
    rol = models.CharField(max_length=20, choices=Rol, default=Rol.LECTOR)
    municipio = models.ForeignKey(
        "core.Municipio",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="perfiles",
        help_text="Vacío: persona de SUBDERE.",
    )
    es_encargado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    # Lo que DRF y Django esperan de request.user.
    is_authenticated = True
    is_anonymous = False

    class Meta:
        ordering = ["nombre"]
        verbose_name = "perfil"
        verbose_name_plural = "perfiles"
        constraints = [
            models.UniqueConstraint(fields=["run_tipo", "run_numero"], name="perfil_run_unico"),
            models.UniqueConstraint(
                fields=["municipio"],
                condition=Q(es_encargado=True),
                name="un_encargado_por_municipio",
            ),
            models.CheckConstraint(
                condition=Q(es_encargado=False) | Q(municipio__isnull=False, activo=True),
                name="encargado_con_municipio_y_activo",
            ),
            models.CheckConstraint(
                condition=Q(run_dv__regex=r"^[0-9K]$"), name="perfil_run_dv_valido"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nombre} ({self.run})"

    @property
    def run(self) -> str:
        return run.formatear(self.run_numero, self.run_dv)

    def rol_al_menos(self, rol: str) -> bool:
        return ORDEN_DE_ROLES.index(self.rol) >= ORDEN_DE_ROLES.index(rol)

    @property
    def es_administrador(self) -> bool:
        return self.rol == Rol.ADMINISTRADOR

    def clean(self):
        try:
            run.validar(self.run_numero, self.run_dv)
        except ValueError as error:
            raise ValidationError({"run_dv": str(error)}) from error

    def save(self, *args, **kwargs):
        self.run_numero, self.run_dv = run.validar(self.run_numero, self.run_dv)
        self.run_tipo = self.run_tipo.strip().upper()
        if not self.activo or self.municipio_id is None:
            self.es_encargado = False
        super().save(*args, **kwargs)


class RegistroInmutable(Exception):
    """Se intentó modificar o borrar un registro que solo crece."""


class SoloCreceQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise RegistroInmutable(f"{self.model.__name__} solo crece: no admite update().")

    def delete(self):
        raise RegistroInmutable(f"{self.model.__name__} solo crece: no admite delete().")

    def bulk_update(self, objs, fields, batch_size=None):
        raise RegistroInmutable(f"{self.model.__name__} solo crece: no admite bulk_update().")


class SoloCrece(ModeloBase):
    objects = SoloCreceQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise RegistroInmutable(f"{type(self).__name__} solo crece: no se modifica.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RegistroInmutable(f"{type(self).__name__} solo crece: no se borra.")


class Acceso(SoloCrece):
    """Quién consultó datos de una persona. Nunca guarda la respuesta."""

    class Canal(models.TextChoices):
        API = "api"
        PANTALLA = "pantalla"

    class Resultado(models.TextChoices):
        ENCONTRADO = "encontrado"
        NO_ENCONTRADO = "no_encontrado"
        ERROR = "error"

    perfil = models.ForeignKey(Perfil, on_delete=models.PROTECT, related_name="accesos")
    canal = models.CharField(max_length=10, choices=Canal)
    nodo = models.CharField(max_length=100)
    operacion = models.CharField(max_length=100)
    parametros = models.JSONField(default=dict)
    procedimiento = models.CharField(max_length=200, blank=True)
    id_tramite = models.CharField(max_length=200, blank=True)
    resultado = models.CharField(max_length=20, choices=Resultado)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "acceso"
        verbose_name_plural = "accesos"

    def __str__(self) -> str:
        return f"{self.operacion} por {self.perfil_id} ({self.creado_en:%Y-%m-%d %H:%M})"


class Bitacora(SoloCrece):
    """Acciones editoriales. `perfil` nulo: la hizo la sincronización o un superusuario local."""

    perfil = models.ForeignKey(
        Perfil, null=True, blank=True, on_delete=models.PROTECT, related_name="bitacora"
    )
    accion = models.CharField(max_length=100)
    objeto = models.CharField(max_length=200)
    antes = models.JSONField(default=dict)
    despues = models.JSONField(default=dict)
    nota = models.TextField(blank=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "entrada de bitácora"
        verbose_name_plural = "bitácora"

    def __str__(self) -> str:
        return f"{self.accion} {self.objeto}"
