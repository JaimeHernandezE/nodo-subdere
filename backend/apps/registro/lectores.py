"""Leer archivos de un repositorio. Ver INSTRUCCIONES.md §2.

La interfaz es pequeña: leer la ficha en la rama de la fuente, que devuelve el *commit* y
el contenido, y leer un archivo en un *commit*. Hay una implementación para GitLab y una
falsa para las pruebas, que nunca salen a la red.
"""

import base64
import binascii
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from django.conf import settings

from .errores import RepositorioNoDisponible
from .models import Fuente

LIMITE_BYTES = 1024 * 1024


@dataclass(frozen=True)
class Leido:
    commit: str
    contenido: str


class Lector(Protocol):
    def leer_ficha(self, fuente: Fuente) -> Leido: ...

    def leer_archivo(self, fuente: Fuente, ruta: str, commit: str) -> str: ...


def _decodificar(crudo: bytes, ruta: str) -> str:
    if len(crudo) > LIMITE_BYTES:
        raise RepositorioNoDisponible(
            f"{ruta} pesa más de 1 MB: el nodo no lee archivos tan grandes."
        )
    try:
        return crudo.decode("utf-8")
    except UnicodeDecodeError:
        raise RepositorioNoDisponible(f"{ruta} no está codificado en UTF-8.") from None


class LectorGitLab:
    """La API v4 de GitLab, con el token del nodo en `PRIVATE-TOKEN`.

    Ninguna dirección lleva una barra codificada (`%2F`): el Apache delante de
    gitlab.subdere.gob.cl responde 404 a esas rutas. El proyecto se pide por su id, y las
    rutas, ramas y commits van en la consulta, donde la barra sí pasa.
    """

    def __init__(self, api_url: str | None = None, token: str | None = None, espera=None):
        self.api_url = (settings.REGISTRO_GIT_API_URL if api_url is None else api_url).rstrip("/")
        self.token = settings.REGISTRO_GIT_TOKEN if token is None else token
        self.espera = settings.REGISTRO_TIEMPO_ESPERA_SEGUNDOS if espera is None else espera
        self._ids: dict[str, int] = {}

    def leer_ficha(self, fuente: Fuente) -> Leido:
        ruta, rama = fuente.ruta_ficha, fuente.rama
        proyecto = self._id_proyecto(fuente, ruta, rama)
        commits = self._pedir(
            f"/projects/{proyecto}/repository/commits",
            {"ref_name": rama, "per_page": 1},
            fuente,
            ruta,
            rama,
        )
        if not isinstance(commits, list):
            raise RepositorioNoDisponible(f"GitLab respondió algo inesperado al pedir {ruta}.")
        if not commits:
            raise RepositorioNoDisponible(self._motivo_http(404, fuente, ruta, rama))
        commit = commits[0].get("id") if isinstance(commits[0], dict) else None
        if not isinstance(commit, str) or not commit:
            raise RepositorioNoDisponible("GitLab respondió sin el commit de la rama.")
        return Leido(commit=commit, contenido=self._leer(fuente, proyecto, ruta, commit, rama))

    def leer_archivo(self, fuente: Fuente, ruta: str, commit: str) -> str:
        proyecto = self._id_proyecto(fuente, ruta, commit)
        return self._leer(fuente, proyecto, ruta, commit, commit)

    def _id_proyecto(self, fuente: Fuente, ruta: str, ref: str) -> int:
        nombre = fuente.proyecto
        if nombre not in self._ids:
            encontrados = self._pedir(
                "/projects",
                {"search": nombre, "search_namespaces": "true", "simple": "true", "per_page": 100},
                fuente,
                ruta,
                ref,
            )
            if not isinstance(encontrados, list):
                raise RepositorioNoDisponible(
                    f"GitLab respondió algo inesperado al buscar {nombre}."
                )
            for proyecto in encontrados:
                if (
                    isinstance(proyecto, dict)
                    and str(proyecto.get("path_with_namespace", "")).lower() == nombre.lower()
                    and isinstance(proyecto.get("id"), int)
                ):
                    self._ids[nombre] = proyecto["id"]
                    break
            else:
                raise RepositorioNoDisponible(self._motivo_http(404, fuente, ruta, ref))
        return self._ids[nombre]

    def _leer(self, fuente: Fuente, proyecto: int, ruta: str, commit: str, ref: str) -> str:
        carpeta, _, nombre = ruta.rpartition("/")
        sha = None
        pagina = 1
        while sha is None:
            entradas = self._pedir(
                f"/projects/{proyecto}/repository/tree",
                {"path": carpeta, "ref": commit, "per_page": 100, "page": pagina},
                fuente,
                ruta,
                ref,
            )
            if not isinstance(entradas, list):
                raise RepositorioNoDisponible(f"GitLab respondió algo inesperado al pedir {ruta}.")
            for entrada in entradas:
                if (
                    isinstance(entrada, dict)
                    and entrada.get("name") == nombre
                    and entrada.get("type") == "blob"
                ):
                    sha = entrada.get("id")
                    break
            else:
                if len(entradas) < 100:
                    raise RepositorioNoDisponible(self._motivo_http(404, fuente, ruta, ref))
                pagina += 1
        if not isinstance(sha, str) or not sha:
            raise RepositorioNoDisponible(f"GitLab respondió algo inesperado al pedir {ruta}.")
        datos = self._pedir(f"/projects/{proyecto}/repository/blobs/{sha}", {}, fuente, ruta, ref)
        if not isinstance(datos, dict):
            raise RepositorioNoDisponible(f"GitLab respondió algo inesperado al pedir {ruta}.")
        return self._contenido(datos, ruta)

    def _pedir(self, camino: str, consulta: dict, fuente: Fuente, ruta: str, ref: str):
        if not self.api_url or not self.token:
            raise RepositorioNoDisponible(
                "La lectura de repositorios no está configurada en el nodo: "
                "faltan REGISTRO_GIT_API_URL o REGISTRO_GIT_TOKEN."
            )
        direccion = f"{self.api_url}{camino}"
        if consulta:
            direccion += f"?{urllib.parse.urlencode(consulta)}"
        pedido = urllib.request.Request(direccion, headers={"PRIVATE-TOKEN": self.token})
        try:
            with urllib.request.urlopen(pedido, timeout=self.espera) as respuesta:
                # base64 infla un tercio; el margen deja pasar el JSON que lo envuelve.
                crudo = respuesta.read(LIMITE_BYTES * 2)
        except urllib.error.HTTPError as error:
            raise RepositorioNoDisponible(
                self._motivo_http(error.code, fuente, ruta, ref)
            ) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise RepositorioNoDisponible(
                f"GitLab no respondió en {self.api_url}. El nodo solo lo alcanza dentro de la "
                "red de SUBDERE o por VPN."
            ) from None
        try:
            datos = json.loads(crudo)
        except ValueError:
            raise RepositorioNoDisponible(
                f"GitLab respondió algo que no se pudo leer al pedir {ruta}."
            ) from None
        return datos

    def _contenido(self, datos: dict, ruta: str) -> str:
        tamano = datos.get("size")
        if isinstance(tamano, int) and tamano > LIMITE_BYTES:
            raise RepositorioNoDisponible(
                f"{ruta} pesa más de 1 MB: el nodo no lee archivos tan grandes."
            )
        try:
            crudo = base64.b64decode(datos.get("content") or "", validate=True)
        except (binascii.Error, TypeError, ValueError):
            raise RepositorioNoDisponible(
                f"GitLab entregó {ruta} con un contenido ilegible."
            ) from None
        return _decodificar(crudo, ruta)

    @staticmethod
    def _motivo_http(codigo: int, fuente: Fuente, ruta: str, ref: str) -> str:
        if codigo == 401:
            return (
                "GitLab rechazó el token del nodo (401): falta, venció o fue revocado. "
                "Es la configuración del nodo, no del repositorio."
            )
        if codigo == 403:
            return (
                f"GitLab no deja leer {fuente.proyecto} (403). Hay que darle rol Reporter "
                "a la cuenta del nodo en ese repositorio o en su grupo."
            )
        if codigo == 404:
            return (
                f"GitLab no encontró {ruta} en «{ref}» de {fuente.proyecto} (404). Revisar la "
                "dirección, la rama y la ruta, y que la cuenta del nodo tenga rol Reporter en "
                "el repositorio: sin acceso, GitLab responde como si no existiera."
            )
        return f"GitLab respondió {codigo} al pedir {ruta}."


class LectorFalso:
    """Un repositorio en memoria, para las pruebas.

    `archivos` va de ruta a contenido; todos viven en un único `commit`. `falla`, si se
    da, es el motivo con que cualquier lectura termina en `RepositorioNoDisponible`.
    """

    def __init__(self, archivos: dict[str, str] | None = None, commit: str = "a" * 40):
        self.archivos = dict(archivos or {})
        self.commit = commit
        self.falla = ""
        self.pedidos: list[tuple[str, str]] = []

    def leer_ficha(self, fuente: Fuente) -> Leido:
        self.pedidos.append((fuente.rama, fuente.ruta_ficha))
        return Leido(commit=self.commit, contenido=self._leer(fuente, fuente.ruta_ficha))

    def leer_archivo(self, fuente: Fuente, ruta: str, commit: str) -> str:
        self.pedidos.append((commit, ruta))
        return self._leer(fuente, ruta)

    def _leer(self, fuente: Fuente, ruta: str) -> str:
        if self.falla:
            raise RepositorioNoDisponible(self.falla)
        if ruta not in self.archivos:
            raise RepositorioNoDisponible(f"GitLab no encontró {ruta} en {fuente.proyecto} (404).")
        return _decodificar(self.archivos[ruta].encode("utf-8"), ruta)
