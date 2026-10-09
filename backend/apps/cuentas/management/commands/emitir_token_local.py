from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core import run
from apps.cuentas import emisor_local
from apps.cuentas.models import Perfil


class Command(BaseCommand):
    help = (
        "Emite un access token del emisor local, para desarrollar sin Keycloak. "
        "Solo funciona con CUENTAS_EMISOR_LOCAL=1."
    )

    def add_arguments(self, parser):
        parser.add_argument("--run", required=True, help="RUN, con o sin puntos y guion.")
        parser.add_argument("--nombre", default="Persona de prueba")
        parser.add_argument("--minutos", type=int, default=60)

    def handle(self, *args, **opciones):
        if not settings.CUENTAS_EMISOR_LOCAL:
            raise CommandError("El emisor local no está activo (CUENTAS_EMISOR_LOCAL=1).")
        try:
            numero, dv = run.leer(opciones["run"])
        except ValueError as error:
            raise CommandError(str(error)) from error

        if not Perfil.objects.filter(run_tipo="RUN", run_numero=numero, activo=True).exists():
            self.stderr.write(
                "Aviso: no hay perfil activo para ese RUN; la API responderá SIN_PERFIL. "
                "Créalo desde el admin con un superusuario."
            )
        self.stdout.write(emisor_local.emitir(numero, dv, opciones["nombre"], opciones["minutos"]))
