"""Admin de Django: solo superusuarios locales, para la puesta en marcha y emergencias.

Es por donde se crea el primer administrador. Todo cambio de perfil queda en la bitácora
con la nota de qué superusuario lo hizo.
"""

from django import forms
from django.contrib import admin

from apps.core import run

from .actuaciones import registrar_bitacora
from .api.v1.serializers import instantanea
from .models import Acceso, Bitacora, Perfil


class PerfilForm(forms.ModelForm):
    run_texto = forms.CharField(label="RUN", help_text="Con o sin puntos y guion.")

    class Meta:
        model = Perfil
        fields = ["run_texto", "nombre", "rol", "municipio", "es_encargado", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["run_texto"].initial = self.instance.run
            self.fields["run_texto"].disabled = True

    def clean_run_texto(self):
        if self.instance.pk:
            return self.instance.run_numero, self.instance.run_dv
        try:
            return run.leer(self.cleaned_data["run_texto"])
        except ValueError as error:
            raise forms.ValidationError("El RUN no es válido.") from error

    def clean(self):
        datos = super().clean()
        if not self.instance.pk and "run_texto" in datos:
            self.instance.run_numero, self.instance.run_dv = datos["run_texto"]
        return datos


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    form = PerfilForm
    list_display = ["nombre", "run", "rol", "municipio", "es_encargado", "activo"]
    list_filter = ["rol", "es_encargado", "activo"]
    search_fields = ["nombre", "run_numero", "municipio__nombre", "municipio__cut"]
    autocomplete_fields = ["municipio"]
    readonly_fields = ["sub", "creado_en", "actualizado_en"]

    def save_model(self, request, obj, form, change):
        antes = instantanea(Perfil.objects.get(pk=obj.pk)) if change else {}
        super().save_model(request, obj, form, change)
        registrar_bitacora(
            None,
            accion="modificar_perfil" if change else "crear_perfil",
            objeto=f"cuentas.Perfil:{obj.pk}",
            antes=antes,
            despues=instantanea(obj),
            nota=f"Superusuario local desde el admin: {request.user.get_username()}",
        )

    def has_delete_permission(self, request, obj=None):
        return False


class SoloLectura(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Acceso)
class AccesoAdmin(SoloLectura):
    list_display = ["creado_en", "perfil", "canal", "nodo", "operacion", "resultado"]
    list_filter = ["canal", "nodo", "resultado"]


@admin.register(Bitacora)
class BitacoraAdmin(SoloLectura):
    list_display = ["creado_en", "perfil", "accion", "objeto"]
    list_filter = ["accion"]
