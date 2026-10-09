"""El catálogo es la proyección de las fichas: casi nada se edita acá.

Lo que viene de una ficha lo escribe solo la sincronización de `registro`, con
`save(desde_sincronizacion=True)`. Las personas administran tres campos editoriales del
nodo. Ver INSTRUCCIONES.md §1.
"""

import hashlib

from django.db import models
from django.db.models import Q

from apps.core.models import ModeloBase

from .errores import CampoDeFicha


class Clase(models.TextChoices):
    INTERCAMBIO = "intercambio", "Intercambio"
    PLATAFORMA = "plataforma", "Plataforma"


class Intercambio(models.TextChoices):
    CONSULTA = "consulta", "El municipio consulta"
    ENTREGA = "entrega", "El municipio entrega"


class Madurez(models.TextChoices):
    DESEABLE = "Deseable"
    EN_EVALUACION = "En evaluación"
    EN_DESARROLLO = "En desarrollo"
    OPERATIVO = "Operativo"


class Visibilidad(models.TextChoices):
    PUBLICADO = "publicado", "Publicado"
    OCULTO = "oculto", "Oculto"
    RETIRADO = "retirado", "Retirado"


class Copia(models.TextChoices):
    EXACTA = "exacta", "Copia exacta"
    INSTANTANEA = "instantanea", "Instantánea"
    RECONSTRUCCION = "reconstruccion", "Reconstrucción"
    SIN_COPIA = "sin-copia", "Sin copia"


class TipoDeAcceso(models.TextChoices):
    ABIERTO = "abierto", "Abierto"
    CREDENCIAL = "credencial", "Con credencial"
    CLAVE_UNICA = "clave-unica", "Con Clave Única"


class Formato(models.TextChoices):
    OPENAPI_30 = "openapi-3.0", "OpenAPI 3.0"
    OPENAPI_31 = "openapi-3.1", "OpenAPI 3.1"
    DESCRIPCION = "descripcion", "Solo metadato"


class NombreDeAmbiente(models.TextChoices):
    PRUEBAS = "pruebas", "Pruebas"
    PRODUCCION = "produccion", "Producción"


class Datos(models.TextChoices):
    INVENTADOS = "inventados", "Inventados"
    REALES = "reales", "Reales"


CAMPOS_EDITORIALES = ("visibilidad", "orden", "nota_editorial")

CAMPOS_DE_FICHA = (
    "identificador",
    "nombre",
    "sigla",
    "ambito",
    "clase",
    "intercambio",
    "funcion",
    "descripcion",
    "madurez",
    "instituciones",
    "responsable_organismo",
    "responsable_equipo",
    "responsable_correo",
    "origen_norma",
    "origen_nota",
    "procedencia_copia",
    "procedencia_fuente",
    "procedencia_detalle",
    "acceso_tipo",
    "acceso_detalle",
    "leido_en",
    "commit",
)


def _detalles(campos) -> list[dict]:
    return [{"campo": campo, "mensaje": "Viene de la ficha del servicio."} for campo in campos]


class Ambito(ModeloBase):
    nombre = models.CharField(max_length=50, unique=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "ámbito"
        verbose_name_plural = "ámbitos"

    def __str__(self) -> str:
        return self.nombre


class NodoQuerySet(models.QuerySet):
    def publicados(self):
        return self.filter(visibilidad=Visibilidad.PUBLICADO)

    def vigentes(self):
        return self.exclude(visibilidad=Visibilidad.RETIRADO)

    def _rechazar_campos_de_ficha(self, campos, metodo: str):
        opciones = self.model._meta
        columnas = {opciones.get_field(c).attname: c for c in CAMPOS_DE_FICHA}
        tocados = sorted({columnas.get(c, c) for c in campos} & set(CAMPOS_DE_FICHA))
        if tocados:
            raise CampoDeFicha(
                f"{metodo}() no puede escribir campos de ficha: {', '.join(tocados)}.",
                detalles=_detalles(tocados),
            )

    def update(self, **kwargs):
        self._rechazar_campos_de_ficha(kwargs, "update")
        return super().update(**kwargs)

    def bulk_update(self, objs, fields, batch_size=None):
        self._rechazar_campos_de_ficha(fields, "bulk_update")
        return super().bulk_update(objs, fields, batch_size=batch_size)

    def bulk_create(self, *args, **kwargs):
        raise CampoDeFicha("Un nodo nace de una ficha: lo crea la sincronización, uno por uno.")


class Nodo(ModeloBase):
    # De la ficha
    identificador = models.SlugField(max_length=100, unique=True, help_text="Inmutable.")
    nombre = models.CharField(max_length=200)
    sigla = models.CharField(max_length=30, blank=True)
    ambito = models.ForeignKey(Ambito, on_delete=models.PROTECT, related_name="nodos")
    clase = models.CharField(max_length=20, choices=Clase)
    intercambio = models.CharField(
        max_length=20, choices=Intercambio, blank=True, help_text="Vacío si es una plataforma."
    )
    funcion = models.TextField("función")
    descripcion = models.TextField("descripción")
    madurez = models.CharField(max_length=20, choices=Madurez)
    instituciones = models.JSONField(default=list, help_text="Lista de nombres, como en la ficha.")
    responsable_organismo = models.CharField(max_length=200)
    responsable_equipo = models.CharField(max_length=200, blank=True)
    responsable_correo = models.EmailField()
    origen_norma = models.TextField(blank=True)
    origen_nota = models.TextField(blank=True)
    procedencia_copia = models.CharField(max_length=20, choices=Copia, blank=True)
    procedencia_fuente = models.TextField(blank=True)
    procedencia_detalle = models.TextField(blank=True)
    acceso_tipo = models.CharField(max_length=20, choices=TipoDeAcceso, blank=True)
    acceso_detalle = models.TextField(blank=True)
    # De la lectura que produjo esta proyección
    leido_en = models.DateTimeField("leído en")
    commit = models.CharField(
        max_length=64, blank=True, help_text="Vacío: carga manual, sin fuente verificable."
    )
    # Editoriales
    visibilidad = models.CharField(max_length=20, choices=Visibilidad, default=Visibilidad.OCULTO)
    orden = models.PositiveSmallIntegerField(default=0)
    nota_editorial = models.TextField(blank=True)

    objects = NodoQuerySet.as_manager()

    class Meta:
        ordering = ["ambito__orden", "orden", "nombre"]
        verbose_name = "nodo"
        verbose_name_plural = "nodos"

    def __str__(self) -> str:
        return self.nombre

    def save(self, *args, desde_sincronizacion=False, **kwargs):
        if self._state.adding:
            if not desde_sincronizacion:
                raise CampoDeFicha(
                    "Un nodo nace de una ficha leída por la sincronización; no se crea a mano."
                )
        else:
            guardado = type(self).objects.filter(pk=self.pk).values(*CAMPOS_DE_FICHA).get()
            if guardado["identificador"] != self.identificador:
                raise CampoDeFicha(
                    "El identificador es inmutable: cambiarlo es un servicio nuevo, con un alias.",
                    detalles=_detalles(["identificador"]),
                )
            cambiados = [
                campo
                for campo in CAMPOS_DE_FICHA
                if guardado[campo] != getattr(self, self._meta.get_field(campo).attname)
            ]
            if cambiados and not desde_sincronizacion:
                raise CampoDeFicha(
                    f"Campos de ficha modificados a mano: {', '.join(cambiados)}.",
                    detalles=_detalles(cambiados),
                )
        super().save(*args, **kwargs)

    @property
    def especificacion_vigente(self) -> "Especificacion | None":
        return self.especificaciones.filter(vigente=True).first()

    def impedimento_para(self, visibilidad: str) -> str:
        """Por qué no puede pasar a `visibilidad`; vacío si puede."""
        if visibilidad == self.visibilidad:
            return ""
        if self.visibilidad == Visibilidad.RETIRADO and visibilidad != Visibilidad.OCULTO:
            return "Un nodo retirado solo vuelve a oculto: publicarlo otra vez pasa por revisarlo."
        if visibilidad == Visibilidad.PUBLICADO and self.especificacion_vigente is None:
            return "No se publica un nodo sin especificación vigente."
        return ""


class Alias(ModeloBase):
    """Identificadores antiguos que deben seguir resolviendo."""

    identificador = models.SlugField(max_length=100, unique=True)
    destino = models.SlugField(
        max_length=100, help_text="Identificador del nodo. No es clave foránea: es inmutable."
    )

    class Meta:
        ordering = ["identificador"]
        verbose_name = "alias"
        verbose_name_plural = "alias"
        constraints = [
            models.CheckConstraint(
                condition=~Q(identificador=models.F("destino")), name="alias_distinto_de_destino"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.identificador} → {self.destino}"


class SoloSincronizacionQuerySet(models.QuerySet):
    def _rechazar(self, metodo: str):
        raise CampoDeFicha(
            f"{self.model._meta.verbose_name} viene completo de la ficha: "
            f"{metodo}() no se usa, lo escribe solo la sincronización."
        )

    def update(self, **kwargs):
        self._rechazar("update")

    def bulk_update(self, objs, fields, batch_size=None):
        self._rechazar("bulk_update")

    def bulk_create(self, *args, **kwargs):
        self._rechazar("bulk_create")

    def delete(self):
        self._rechazar("delete")


class SoloSincronizacion(ModeloBase):
    """Modelos que vienen completos de la ficha: no se escriben fuera de la sincronización."""

    objects = SoloSincronizacionQuerySet.as_manager()

    class Meta:
        abstract = True

    def _exigir_sincronizacion(self, desde_sincronizacion: bool):
        if not desde_sincronizacion:
            raise CampoDeFicha(
                f"{self._meta.verbose_name} viene completo de la ficha: "
                "lo escribe solo la sincronización."
            )

    def save(self, *args, desde_sincronizacion=False, **kwargs):
        self._exigir_sincronizacion(desde_sincronizacion)
        super().save(*args, **kwargs)

    def delete(self, *args, desde_sincronizacion=False, **kwargs):
        self._exigir_sincronizacion(desde_sincronizacion)
        return super().delete(*args, **kwargs)


def huella(contenido: str) -> str:
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest() if contenido else ""


class Especificacion(SoloSincronizacion):
    """El contrato técnico. Ninguna versión se borra ni se corrige."""

    nodo = models.ForeignKey(Nodo, on_delete=models.PROTECT, related_name="especificaciones")
    version = models.CharField("versión", max_length=50)
    formato = models.CharField(max_length=20, choices=Formato)
    ruta = models.CharField(
        max_length=300, blank=True, help_text="Dentro del repositorio. Vacía: solo metadato."
    )
    contenido = models.TextField(blank=True, help_text="El archivo tal como se leyó.")
    huella = models.CharField(max_length=64, blank=True, help_text="sha256 del contenido.")
    publicada = models.DateField(null=True, blank=True)
    vigente = models.BooleanField(default=False)
    commit = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["nodo", "-creado_en"]
        verbose_name = "especificación"
        verbose_name_plural = "especificaciones"
        constraints = [
            models.UniqueConstraint(
                fields=["nodo", "version"], name="especificacion_version_unica"
            ),
            models.UniqueConstraint(
                fields=["nodo"], condition=Q(vigente=True), name="una_especificacion_vigente"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nodo_id} {self.version}"

    @property
    def tiene_archivo(self) -> bool:
        return bool(self.contenido)

    def save(self, *args, desde_sincronizacion=False, **kwargs):
        self._exigir_sincronizacion(desde_sincronizacion)
        self.huella = huella(self.contenido)
        if not self._state.adding:
            guardada = type(self).objects.filter(pk=self.pk).values("version", "huella").get()
            if (guardada["version"], guardada["huella"]) != (self.version, self.huella):
                raise CampoDeFicha(
                    "Una versión registrada no cambia: si el contrato cambió, es una versión nueva."
                )
        super().save(*args, desde_sincronizacion=True, **kwargs)


class Ambiente(SoloSincronizacion):
    nodo = models.ForeignKey(Nodo, on_delete=models.CASCADE, related_name="ambientes")
    nombre = models.CharField(max_length=20, choices=NombreDeAmbiente)
    base = models.URLField(max_length=500)
    datos = models.CharField(max_length=20, choices=Datos)

    class Meta:
        ordering = ["nodo", "nombre"]
        verbose_name = "ambiente"
        verbose_name_plural = "ambientes"
        constraints = [
            models.UniqueConstraint(fields=["nodo", "nombre"], name="ambiente_unico_por_nodo"),
        ]

    def __str__(self) -> str:
        return f"{self.nodo_id} {self.nombre}"
