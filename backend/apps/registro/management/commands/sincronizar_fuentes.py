from django.core.management.base import BaseCommand, CommandError

from apps.registro import sincronizacion
from apps.registro.models import Fuente


class Command(BaseCommand):
    help = (
        "Lee, valida y proyecta las fuentes activas de tipo repositorio cuyo nodo no está "
        "retirado. Lo corre la tarea programada. Una lectura que falla deja su motivo y no "
        "toca la proyección anterior."
    )

    def add_arguments(self, parser):
        parser.add_argument("--fuente", type=int, help="Solo esta fuente, por su id.")

    def handle(self, *args, fuente=None, **options):
        fuentes = sincronizacion.sincronizables()
        if fuente is not None:
            if not Fuente.objects.filter(pk=fuente).exists():
                raise CommandError(f"No existe la fuente {fuente}.")
            fuentes = fuentes.filter(pk=fuente)
            if not fuentes.exists():
                raise CommandError(f"La fuente {fuente} está inactiva o su nodo está retirado.")

        lector = sincronizacion.lector_por_defecto()
        validas = invalidas = 0
        for elegida in fuentes:
            lectura = sincronizacion.sincronizar(elegida, lector=lector)
            if lectura.valida:
                validas += 1
                self.stdout.write(f"{elegida}: válida, commit {lectura.commit[:8]}")
            else:
                invalidas += 1
                self.stdout.write(self.style.WARNING(f"{elegida}: {lectura.motivo}"))

        resumen = f"{validas} válidas, {invalidas} inválidas."
        self.stdout.write(self.style.SUCCESS(resumen) if not invalidas else resumen)
