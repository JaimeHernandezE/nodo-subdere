"""Admin de Django: solo superusuarios locales, para la puesta en marcha y emergencias.

Las versiones se ven y no se tocan: se escriben y publican por la API, que deja autor
y bitácora.
"""

from django.contrib import admin

from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.admin import SoloLectura

from .models import CAMPOS_EDITABLES, Entrada, Version


class VersionEnLinea(admin.TabularInline):
    model = Version
    fields = ["id", "resumen", "autor", "publicada", "publicada_en", "creado_en"]
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = ["titulo", "slug", "seccion", "orden", "nodo", "vigente"]
    list_filter = ["seccion"]
    search_fields = ["slug", "titulo", "nodo"]
    readonly_fields = ["slug", "vigente", "creado_en", "actualizado_en"]
    inlines = [VersionEnLinea]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        antes = {campo: form.initial.get(campo) for campo in CAMPOS_EDITABLES}
        super().save_model(request, obj, form, change)
        despues = {campo: getattr(obj, campo) for campo in CAMPOS_EDITABLES}
        if antes != despues:
            registrar_bitacora(
                None,
                accion="editar_entrada",
                objeto=f"wiki.Entrada:{obj.slug}",
                antes=antes,
                despues=despues,
                nota=f"Superusuario local desde el admin: {request.user.get_username()}",
            )


@admin.register(Version)
class VersionAdmin(SoloLectura):
    list_display = ["entrada", "id", "resumen", "autor", "publicada", "creado_en"]
    list_filter = ["publicada"]
