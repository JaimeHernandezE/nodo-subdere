"""Admin de Django: solo superusuarios locales, para la puesta en marcha y emergencias.

El curador mantiene los servicios por la API. Desde acá, `slug` y `nodo` se fijan al
crear y después solo se ven.
"""

from django.contrib import admin

from apps.cuentas.actuaciones import registrar_bitacora

from .models import CAMPOS_EDITABLES, Servicio


def _editables(servicio: Servicio) -> dict:
    return {campo: getattr(servicio, campo) for campo in CAMPOS_EDITABLES}


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ["nombre", "slug", "nodo", "estado", "actualizado_en"]
    list_filter = ["estado", "nodo"]
    search_fields = ["slug", "nombre"]

    def get_readonly_fields(self, request, obj=None):
        return ["slug", "nodo"] if obj else []

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        antes = {campo: form.initial.get(campo) for campo in CAMPOS_EDITABLES} if change else None
        super().save_model(request, obj, form, change)
        despues = _editables(obj)
        if antes != despues:
            registrar_bitacora(
                None,
                accion="editar_servicio" if change else "crear_servicio",
                objeto=f"servicios.Servicio:{obj.slug}",
                antes=antes,
                despues=despues,
                nota=f"Superusuario local desde el admin: {request.user.get_username()}",
            )
