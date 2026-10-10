from django.apps import AppConfig


class RegistroConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.registro"
    label = "registro"
    verbose_name = "Registro: fuentes, lecturas y sincronización"
