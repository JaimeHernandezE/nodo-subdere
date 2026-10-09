from django.apps import AppConfig


class CuentasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cuentas"
    label = "cuentas"
    verbose_name = "Identidad, perfiles y registro de actuaciones"

    def ready(self):
        from . import esquema  # noqa: F401
