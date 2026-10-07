import json
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core.foto_cut import DIRECTORIO, LISTADOS

TIEMPO_DE_ESPERA = 15


class Command(BaseCommand):
    help = (
        "Descarga regiones, provincias y comunas desde CUT_API_URL y reescribe la foto "
        "versionada en apps/core/datos/. Se ejecuta a mano y el resultado se revisa en un "
        "commit; ninguna migración ni prueba llama a la red."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default=settings.CUT_API_URL,
            help="URL base de la API del CUT. Por defecto, CUT_API_URL.",
        )
        parser.add_argument("--destino", type=Path, default=DIRECTORIO)

    def handle(self, *args, url, destino, **options):
        if not url:
            raise CommandError("Falta la URL: definir CUT_API_URL o pasar --url.")

        destino.mkdir(parents=True, exist_ok=True)
        descargado_en = datetime.now(UTC).replace(microsecond=0).isoformat()
        fotos = {}

        for listado, campo_codigo in LISTADOS.items():
            fuente = f"{url.rstrip('/')}/{listado}"
            datos = self._descargar(fuente)
            self._validar(listado, campo_codigo, datos)
            fotos[listado] = {
                "fuente": fuente,
                "descargado_en": descargado_en,
                "datos": sorted(datos, key=lambda fila: fila[campo_codigo]),
            }

        # Se escribe solo si los tres listados se descargaron y validaron.
        for listado, foto in fotos.items():
            archivo = destino / f"{listado}.json"
            archivo.write_text(
                json.dumps(foto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            self.stdout.write(f"{archivo.name}: {len(foto['datos'])} registros")

        self.stdout.write(self.style.SUCCESS(f"Foto del CUT actualizada en {destino}"))

    def _descargar(self, fuente: str) -> list:
        peticion = urllib.request.Request(fuente, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(peticion, timeout=TIEMPO_DE_ESPERA) as respuesta:
                return json.load(respuesta)
        except (urllib.error.URLError, TimeoutError) as error:
            raise CommandError(f"No se pudo leer {fuente}: {error}") from error
        except json.JSONDecodeError as error:
            raise CommandError(f"{fuente} no devolvió JSON válido: {error}") from error

    def _validar(self, listado: str, campo_codigo: str, datos) -> None:
        if not isinstance(datos, list) or not datos:
            raise CommandError(f"{listado}: se esperaba una lista no vacía.")
        for fila in datos:
            if not isinstance(fila, dict) or campo_codigo not in fila or "nombre" not in fila:
                raise CommandError(f"{listado}: fila sin '{campo_codigo}' o 'nombre': {fila!r}")
        codigos = [fila[campo_codigo] for fila in datos]
        if len(codigos) != len(set(codigos)):
            raise CommandError(f"{listado}: hay códigos repetidos.")
