# Backend — Nodo SUBDERE

API en Django que administra el catálogo de intercambios, el catálogo de servicios y la wiki, y que adapta hacia el frontend las APIs externas que esos servicios consumen.

> **Para construir:** [`INSTRUCCIONES.md`](INSTRUCCIONES.md) tiene el contrato común y el orden de construcción, y cada `apps/<app>/INSTRUCCIONES.md` el detalle de su aplicación. Este README explica el diseño; esos archivos dicen qué escribir. **Si este README y esos archivos no coinciden, mandan ellos.**

El modelo de datos no se inventa acá: la maqueta de [`prototipos/`](../prototipos/) ya lo tiene definido en `assets/data.js`, y [`docs/maqueta.md`](../docs/maqueta.md) explica campo por campo qué significa cada uno y por qué. **Ese documento es la fuente; este README dice cómo se implementa.**

---

## Qué resuelve y qué no

| Resuelve | No resuelve |
|---|---|
| El contenido del sitio: nodos, especificaciones, servicios, entradas de wiki | La puerta de acceso, con credenciales y control de paso. Eso es la [plataforma de control](../docs/plataforma-control.md) y es otro sistema |
| La adaptación hacia APIs externas: normalizar respuestas, cachear, resolver CORS | Almacenar los datos de esos servicios. El backend consulta, no guarda una copia |
| La administración del catálogo por personas del equipo, vía la API y la interfaz en React. El admin de Django queda solo para superusuarios locales, en la puesta en marcha y emergencias | Autenticar municipios o proveedores |

La segunda columna importa tanto como la primera. Si este backend termina guardando una copia del CUT o de los permisos de circulación, deja de ser un catálogo y pasa a ser un registro paralelo — que es exactamente lo que el proyecto decidió no construir.

---

## Estructura

```
backend/
├── config/                  Proyecto Django: settings, urls, asgi, wsgi
│   └── settings/            base.py · local.py · prod.py
├── apps/
│   ├── core/                Modelos abstractos, Municipio y utilidades compartidas
│   ├── cuentas/             Keycloak, perfiles, roles, Acceso y Bitacora
│   ├── catalogo/            Ámbitos, instituciones, nodos y especificaciones
│   ├── registro/            Fuentes registradas y sus lecturas
│   ├── integraciones/       Adaptadores a las APIs externas
│   ├── servicios/           Las pantallas construidas sobre las APIs
│   └── wiki/                Entradas de wiki y su relación con los nodos
├── Dockerfile
├── entrypoint.sh            aplica migraciones y arranca
├── docker-compose.yml
├── docker-compose.prod.yml
├── manage.py
├── pyproject.toml           dependencias, ruff y pytest
└── .env.example
```

Una app por dominio, no por capa. `catalogo` contiene sus modelos, sus serializadores, sus vistas y sus pruebas, en `apps/catalogo/tests/`. Dentro de cada app, la API va en `api/v1/` y los archivos en snake_case; la estructura completa está en `INSTRUCCIONES.md` §2.ter. Las apps están listadas en el orden en que se construyen, y ninguna depende de una que esté más abajo (`INSTRUCCIONES.md` §7).

---

## Las apps

### `core`

Lo que comparten las demás, sin depender de ninguna. Modelos abstractos con marca de tiempo, el modelo `Municipio` como dato de referencia territorial, y utilidades que no pertenecen a ningún dominio en particular.

Acá vive también el relleno canónico del Código Único Territorial —`1101` → `01101`—, porque lo usan `integraciones` y `catalogo` y no puede estar duplicado. Es una función pura de cinco líneas; su documentación está en [la entrada de wiki del CUT](../prototipos/wiki-cut.html).

### `catalogo`

El corazón. Los modelos y sus decisiones:

**`Nodo`** — un intercambio en el que participa el municipio. Los campos están en [`apps/catalogo/INSTRUCCIONES.md`](apps/catalogo/INSTRUCCIONES.md) §2.

**`visibilidad` es un campo del modelo, no una consulta**, con tres estados: `publicado`, `oculto` y `retirado`. Un nodo oculto existe y no aparece en los listados, pero su ficha sigue siendo alcanzable por enlace directo. Los listados filtran de forma explícita, no con un *manager* que esconda el filtro:

```python
class NodoQuerySet(models.QuerySet):
    def publicados(self):
        return self.filter(visibilidad="publicado")

class Nodo(ModeloBase):
    objects = NodoQuerySet.as_manager()   # .publicados() explícito en los listados
```

No confundir `visibilidad` con `madurez`. La madurez dice qué tan avanzado está el intercambio; la visibilidad, si se muestra. Son ejes independientes.

**`Especificacion`** — el contrato técnico, **versionado aparte de la ficha**. Cada versión se registra y ninguna se corrige: si el contrato cambia, se crea una versión nueva y se marca cuál rige. El contrato puede cambiar sin que cambie la descripción del nodo, y al revés.

```python
class Especificacion(ModeloBase):
    nodo      = models.ForeignKey(Nodo, related_name="especificaciones", ...)
    version   = models.CharField(...)       # única por nodo
    archivo   = models.FileField(...)       # opcional: puede haber solo metadato
    formato   = models.CharField(...)
    validador = models.URLField(...)
    origen    = models.TextField(...)
    acceso    = models.TextField(...)
    vigente   = models.BooleanField(default=False)
```

**No hay un campo `operaciones`, y es deliberado.** Cuando la especificación tiene archivo, se renderiza desde el archivo; cuando solo hay metadato, no se transcriben operaciones a mano. La decisión completa está en [`adr-2026-09-estandar-legible-por-maquina.md`](../docs/adr-2026-09-estandar-legible-por-maquina.md).

**`archivo` opcional separa dos cosas que se confunden:** que un estándar esté publicado y que el servicio esté alcanzable. El catálogo de APIs lista los nodos con archivo; los que solo declaran metadato aparecen en el catálogo de servicios.

### `servicios`

Las pantallas construidas sobre una API del catálogo. `Servicio` apunta a un `Nodo` por clave foránea y tiene `url`, `tareas`, `estado` y `nota`.

Un servicio **no** es un nodo filtrado: es un consumidor de uno. Por eso es un modelo aparte y no una vista del mismo. El catálogo de APIs dice qué se puede consumir; el de servicios dice qué se puede usar hoy sin programar.

### `wiki`

Entradas de documentación, con su relación opcional a un nodo. La wiki contiene lo que el catálogo no debe contener: cómo se usa una API, cómo se generan los códigos, qué norma obliga cada cosa, y **las observaciones sobre un contrato**.

Esa última regla es importante y conviene que el modelo la haga evidente: el catálogo publica el contrato tal como se entregó, sin editarlo, porque su valor es ser copia fiel y auditable. La crítica vive en la wiki. Si alguna vez aparece un campo «observaciones» en `Especificacion`, esa separación se perdió.

### `integraciones`

Los adaptadores hacia APIs que no son nuestras: hoy el CUT y los permisos de circulación.

Cada adaptador hace tres cosas y ninguna más:

1. **Llama** a la API externa por su interfaz pública, la misma que usaría cualquier otro consumidor.
2. **Normaliza** lo que devuelve. El caso concreto: el CUT entrega los códigos como entero y acá se rellenan a su forma canónica.
3. **Cachea** por un tiempo corto y declarado, para no castigar al servicio de origen.

Lo que **no** hacen: guardar los datos en la base, enriquecerlos con información propia, ni exponer nada que la API de origen no exponga. Si un adaptador empieza a tener tablas, se convirtió en un registro paralelo.

Cada adaptador declara su URL base por variable de entorno y degrada con honestidad: si el servicio no responde, el frontend debe poder decirlo, no mostrar un vacío ambiguo.

---

## Administración del catálogo

El catálogo no se escribe a mano: se **sincroniza**. Cada servicio declara su ficha en su propio repositorio, según el [estándar de la ficha de servicio](../docs/estandar-ficha-de-servicio.md), y el backend la lee, la valida y la proyecta. Lo que se administra desde la aplicación es el **registro** —qué repositorios se leen y qué se publica— y los contenidos que son del nodo, sobre todo la wiki.

### `registro`

Dos modelos, y el segundo solo crece:

```python
class Fuente(ModeloBase):
    """Un repositorio registrado, o una carga manual de transición."""
    tipo        = models.CharField(...)      # repositorio | carga_manual
    url         = models.URLField(blank=True)
    rama        = models.CharField(default="main")
    ruta_ficha  = models.CharField(default="nodo/ficha.yaml")
    activa      = models.BooleanField(default=True)

class Lectura(ModeloBase):
    """Cada intento de leer una fuente. Nunca se edita ni se borra."""
    fuente     = models.ForeignKey(Fuente, related_name="lecturas", ...)
    commit     = models.CharField(blank=True)
    contenido  = models.TextField(blank=True)   # el YAML tal como se leyó
    valida     = models.BooleanField()
    motivo     = models.TextField(blank=True)   # por qué se rechazó
```

`Lectura` es un registro que solo crece porque el catálogo afirma ser copia fiel y auditable: tiene que poder decir de qué *commit* salió cada ficha publicada y en qué fecha se leyó. Guardar el YAML tal cual permite además reconstruir la proyección si el modelo cambia, sin volver a pedirle nada al repositorio.

**La carga manual existe solo para la transición**, cuando un responsable todavía no tiene repositorio: se sube el archivo, se valida igual, y el catálogo marca que esa ficha no tiene fuente verificable. No es un atajo para editar a mano una ficha que sí tiene repositorio.

### Lo que la sincronización escribe, y lo que no

`Nodo` pasa a ser la **proyección de la última lectura válida**, más los campos que son decisión del nodo:

| Campo | Lo escribe |
|---|---|
| `ambito`, `clase`, `funcion`, `descripcion`, `madurez`, `responsable`, `instituciones`, `intercambio` | Solo la sincronización |
| `visibilidad` (`publicado`, `oculto`, `retirado`), `orden`, `nota_editorial` | Solo una persona, desde la administración |

**Los campos que vienen de la ficha son de solo lectura.** No por estilo: si alguien los edita, la siguiente sincronización le pasa por encima y el cambio se pierde sin aviso. Se cierran tres puertas: `readonly_fields` en el admin, una verificación en `save()` que solo deja pasar a la sincronización, y un `QuerySet` que rechaza `update()` y `bulk_update()` sobre esos campos.

`retirado` deja de leer el repositorio pero conserva la última lectura, porque el catálogo tiene que poder decir qué publicó y hasta cuándo.

### La sincronización

Un comando de gestión, `sincronizar_fuentes`, que corre por tarea programada y también desde un botón «resincronizar» en la administración. Para cada fuente activa: lee la ficha, la valida, trae la especificación que declara, comprueba que parsea y que su `info.version` coincide con lo declarado, y proyecta.

Cuando la lectura falla, **no se borra ni se despublica nada**: queda una `Lectura` inválida con su motivo, la proyección anterior sigue vigente y el catálogo muestra de cuándo es la última lectura buena. Es el mismo patrón de degradación honesta de las pantallas de servicio.

### `cuentas` — quién administra

Autenticación a través de un **realm de Keycloak que federa Clave Única**, por OpenID Connect. El backend no habla con Clave Única: confía en el realm, valida el token contra su JWKS y no guarda sesión. El flujo de inicio lo hace el frontend, con Authorization Code y PKCE. Es el plano de personas que ya describe [`plataforma-control.md`](../docs/plataforma-control.md); el plano de sistemas, con credencial, es otra cosa y va por la puerta de acceso.

**Clave Única autentica, no autoriza.** Dice quién es la persona; qué puede hacer lo dice el nodo. Por eso hace falta una tabla propia:

```python
class Perfil(ModeloBase):
    sub    = models.CharField(unique=True)   # el subject del realm
    run    = models.CharField(unique=True)   # claim del realm, que lo trae de Clave Única
    nombre = models.CharField()
    rol    = models.CharField(...)           # lector | editor | curador | administrador
    municipio = models.ForeignKey("core.Municipio", null=True, blank=True, ...)
    activo = models.BooleanField(default=True)
```

| Rol | Puede |
|---|---|
| `lector` | Ver la administración, sin cambiar nada |
| `editor` | Escribir y publicar entradas de wiki |
| `curador` | Publicar, ocultar y retirar servicios; resincronizar |
| `administrador` | Registrar y dar de baja fuentes; administrar perfiles |

De cada persona se guarda el RUN y el nombre que entrega Clave Única, y nada más: es el mínimo para saber quién hizo cada cambio, y está ahí por eso. Una persona sin perfil activo se autentica y no entra: no se crean perfiles solos.

El superusuario local de Django se mantiene únicamente para la puesta en marcha y emergencias, documentado como tal y no para uso diario.

**Los usuarios municipales no los administramos nosotros.** Cada municipalidad designa un encargado que administra a su gente; el nodo mantiene una **réplica de ese registro, por municipio y solo para visualización**, siempre con la fecha en que el municipio la informó. La réplica no autoriza: quien autoriza es el perfil. Dónde administra el encargado sigue abierto (HR-27).

### `wiki` — el editor

Las entradas de wiki son contenido del nodo, no del servicio, así que sí se editan en la aplicación. Con historial:

```python
class Entrada(ModeloBase):
    slug   = models.SlugField(unique=True)
    titulo = models.CharField()
    nodo   = models.ForeignKey("catalogo.Nodo", null=True, blank=True, ...)
    vigente = models.ForeignKey("wiki.Version", null=True, ...)

class Version(ModeloBase):
    entrada   = models.ForeignKey(Entrada, related_name="versiones", ...)
    markdown  = models.TextField()
    autor     = models.ForeignKey("cuentas.Perfil", ...)
    publicada = models.BooleanField(default=False)
```

Markdown en la base de datos, con versiones que no se corrigen: una edición crea una versión nueva y se marca cuál rige. Eso resuelve la pregunta que estaba abierta entre base de datos y archivos del repositorio — con un editor en la aplicación, los archivos obligarían a darle permiso de escritura al repositorio, que es bastante más superficie por bastante menos utilidad.

**El Markdown se sanea al renderizar, siempre.** Es contenido que escriben personas y se muestra en un sitio público: nada de HTML crudo. La lista de etiquetas permitidas es parte del código, no configuración.

Acá viven también las observaciones sobre un contrato. El catálogo no tiene dónde escribirlas y eso es a propósito.

### `cuentas.Bitacora` y `cuentas.Acceso`

Toda acción editorial queda registrada en `Bitacora`: quién, qué objeto, qué cambió y cuándo. Publicar, ocultar, retirar, registrar una fuente, editar una entrada. Un catálogo que se presenta como auditable necesita poder mostrar su propia historia, no solo la de los contratos que publica.

Toda consulta que entrega datos de una persona queda en `Acceso`: quién consultó qué, para qué trámite y cuándo, sin la respuesta.

Los dos viven en `cuentas` porque responden «qué hizo este perfil», y porque así ninguna app depende de una que se construye después.

## Decisiones técnicas

| | |
|---|---|
| **Django** 5.x, **Python** 3.12 | |
| **Django REST Framework** | Para la API que consume el frontend |
| **PostgreSQL** | En desarrollo también, para no encontrarse diferencias tarde |
| **`drf-spectacular`** | La API del backend publica su propio OpenAPI. Un sitio que promueve contratos legibles por máquina no puede no tener el suyo |
| **`pytest` + `pytest-django`** | |
| **`ruff`** | Formato y linting |
| **Español en el dominio** | `Nodo`, `Especificacion`, `funcion`. El vocabulario del código es el mismo que el del sitio y el de los documentos. En inglés queda lo del framework |

### Configuración

`config/settings/` se divide en `base.py`, `local.py` y `prod.py`, con un archivo de variables por ambiente: `.env.local` y `.env.prod`. Ningún secreto en el repositorio: todo por variable de entorno, con `.env.example` como plantilla documentada. El detalle está en `INSTRUCCIONES.md` §2.bis.

> **Antecedente del proyecto.** En otro repositorio del equipo quedaron archivos `.env` versionados con contraseñas de base de datos. `.gitignore` debe excluir `.env` desde el primer commit, y conviene revisarlo antes de cada publicación.

### Migraciones

Se versionan siempre. Una migración que crea datos iniciales —los ámbitos, por ejemplo— va como migración de datos y no como *script* suelto.

---

## Cómo levantarlo

Con Docker Desktop, todo en contenedores:

```bash
cd backend
cp .env.example .env.local    # y completar: al menos SECRET_KEY
docker compose --env-file .env.local up
```

Las migraciones se aplican solas al arrancar, incluida la carga de los 346 municipios. Para el resto:

```bash
docker compose --env-file .env.local exec api pytest
docker compose --env-file .env.local exec api ruff check .
docker compose --env-file .env.local exec api python manage.py createsuperuser
```

O solo Postgres en Docker y Django en el equipo, con `DATABASE_URL` apuntando a `localhost:5432` y Python 3.12:

```bash
cd backend
docker compose --env-file .env.local up -d db
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python manage.py migrate
python manage.py runserver
```

En este segundo modo, `DJANGO_SETTINGS_MODULE` y las demás variables se cargan desde `.env.local` con `django-environ`.

La API queda en `http://localhost:8000/api/v1/`: `/api/v1/salud` responde sin token, y la documentación está en `/api/v1/schema/swagger-ui/`.

---

## Qué falta decidir

- **Cómo se cargan las especificaciones.** ¿El equipo sube el archivo por el admin, o se sincroniza desde un repositorio de estándares? La segunda opción es más limpia y más trabajo.
- **Qué pasa cuando cambia una especificación vigente.** Versionar está definido; avisar a quien la consumía, no.
- **El idioma de la API.** Los campos del modelo están en español; si algún día un tercero consume esta API, conviene haberlo decidido antes y no después.
