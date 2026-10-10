"""Admin de Django: solo superusuarios locales, para la puesta en marcha y emergencias.

Registrar una fuente desde acá no la lee: para eso está la API o `sincronizar_fuentes`.
"""

from django.contrib import admin
from django.forms.models import model_to_dict

from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.admin import SoloLectura

from .models import Fuente, Lectura

CAMPOS_EDITABLES = ["url", "rama", "ruta_ficha", "activa"]


@admin.register(Fuente)
class FuenteAdmin(admin.ModelAdmin):
    list_display = ["__str__", "url", "rama", "activa", "nodo_identificador"]
    list_filter = ["activa", "tipo"]
    search_fields = ["url", "nodo_identificador"]
    fields = ["tipo", *CAMPOS_EDITABLES, "nodo_identificador", "creado_en", "actualizado_en"]
    readonly_fields = ["tipo", "nodo_identificador", "creado_en", "actualizado_en"]

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        antes = model_to_dict(Fuente.objects.get(pk=obj.pk), CAMPOS_EDITABLES) if change else {}
        super().save_model(request, obj, form, change)
        registrar_bitacora(
            None,
            accion="modificar_fuente" if change else "registrar_fuente",
            objeto=f"registro.Fuente:{obj.pk}",
            antes=antes,
            despues=model_to_dict(obj, CAMPOS_EDITABLES),
            nota=f"Superusuario local desde el admin: {request.user.get_username()}",
        )


@admin.register(Lectura)
class LecturaAdmin(SoloLectura):
    list_display = ["creado_en", "fuente", "commit", "valida", "perfil"]
    list_filter = ["valida"]
    search_fields = ["fuente__url", "fuente__nodo_identificador", "commit"]
