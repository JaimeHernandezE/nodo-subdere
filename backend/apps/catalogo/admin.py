"""Admin de Django: solo superusuarios locales, para la puesta en marcha y emergencias.

De un nodo se editan solo los campos editoriales. Lo que viene de la ficha se ve y no
se toca: la siguiente sincronización le pasaría por encima.
"""

from django import forms
from django.contrib import admin

from apps.cuentas.actuaciones import registrar_bitacora
from apps.cuentas.admin import SoloLectura

from .models import (
    CAMPOS_DE_FICHA,
    CAMPOS_EDITORIALES,
    Alias,
    Ambiente,
    Ambito,
    Especificacion,
    Nodo,
)


class NodoForm(forms.ModelForm):
    class Meta:
        model = Nodo
        fields = list(CAMPOS_EDITORIALES)

    def clean_visibilidad(self):
        visibilidad = self.cleaned_data["visibilidad"]
        if impedimento := self.instance.impedimento_para(visibilidad):
            raise forms.ValidationError(impedimento)
        return visibilidad


class EspecificacionEnLinea(admin.TabularInline):
    model = Especificacion
    fields = ["version", "formato", "ruta", "publicada", "vigente", "commit", "huella"]
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class AmbienteEnLinea(admin.TabularInline):
    model = Ambiente
    fields = ["nombre", "base", "datos"]
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Nodo)
class NodoAdmin(admin.ModelAdmin):
    form = NodoForm
    list_display = ["nombre", "identificador", "ambito", "madurez", "visibilidad", "leido_en"]
    list_filter = ["visibilidad", "ambito", "clase", "madurez"]
    search_fields = ["identificador", "nombre", "sigla"]
    readonly_fields = [*CAMPOS_DE_FICHA, "creado_en", "actualizado_en"]
    inlines = [EspecificacionEnLinea, AmbienteEnLinea]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        antes = {campo: form.initial.get(campo) for campo in CAMPOS_EDITORIALES}
        super().save_model(request, obj, form, change)
        despues = {campo: getattr(obj, campo) for campo in CAMPOS_EDITORIALES}
        if antes != despues:
            registrar_bitacora(
                None,
                accion="editar_nodo",
                objeto=f"catalogo.Nodo:{obj.identificador}",
                antes=antes,
                despues=despues,
                nota=f"Superusuario local desde el admin: {request.user.get_username()}",
            )


@admin.register(Especificacion)
class EspecificacionAdmin(SoloLectura):
    list_display = ["nodo", "version", "formato", "vigente", "publicada", "commit"]
    list_filter = ["formato", "vigente"]


@admin.register(Ambiente)
class AmbienteAdmin(SoloLectura):
    list_display = ["nodo", "nombre", "base", "datos"]


@admin.register(Ambito)
class AmbitoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "orden"]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Alias)
class AliasAdmin(admin.ModelAdmin):
    list_display = ["identificador", "destino"]
    search_fields = ["identificador", "destino"]
