# Backend — Nodo SUBDERE

API en Django que administra el catálogo de intercambios, el catálogo de servicios y la wiki, y que adapta hacia el frontend las APIs externas que esos servicios consumen.

El modelo de datos no se inventa acá: la maqueta de [`prototipos/`](../prototipos/) ya lo tiene definido en `assets/data.js`, y [`docs/maqueta.md`](../docs/maqueta.md) explica campo por campo qué significa cada uno y por qué. **Ese documento es la fuente; este README dice cómo se implementa.**

---

## Qué resuelve y qué no

| Resuelve | No resuelve |
|---|---|
| El contenido del sitio: nodos, especificaciones, servicios, entradas de wiki | La puerta de acceso, con credenciales y control de paso. Eso es la [plataforma de control](../docs/plataforma-control.md) y es otro sistema |
| La adaptación hacia APIs externas: normalizar respuestas, cachear, resolver CORS | Almacenar los datos de esos servicios. El backend consulta, no guarda una copia |
| La administración del catálogo por personas del equipo, vía el admin de Django | Autenticar municipios o proveedores |

La segunda columna importa tanto como la primera. Si este backend termina guardando una copia del CUT o de los permisos de circulación, deja de ser un catálogo y pasa a ser un registro paralelo — que es exactamente lo que el proyecto decidió no construir.

---

## Estructura

```
backend/
├── config/                  Proyecto Django: settings, urls, asgi, wsgi
│   └── settings/            base.py · dev.py · prod.py
├── apps/
│   ├── core/                Modelos abstractos y utilidades compartidas
│   ├── catalogo/            Ámbitos, instituciones, nodos y especificaciones
│   ├── servicios/           Las pantallas construidas sobre las APIs
│   ├── wiki/                Entradas de wiki y su relación con los nodos
│   └── integraciones/       Adaptadores a las APIs externas
├── tests/
├── manage.py
├── pyproject.toml
└── .env.example
```

Una app por dominio, no por capa. `catalogo` contiene sus modelos, sus serializadores, sus vistas y sus pruebas.

---

## Las apps

### `core`

Lo que comparten las demás. Modelos abstractos con marca de tiempo y slug, el *manager* que filtra lo oculto, y utilidades que no pertenecen a ningún dominio en particular.

Acá vive también el relleno canónico del Código Único Territorial —`1101` → `01101`—, porque lo usan `integraciones` y `catalogo` y no puede estar duplicado. Es una función pura de cinco líneas; su documentación está en [la entrada de wiki del CUT](../prototipos/wiki-cut.html).

### `catalogo`

El corazón. Los modelos y sus decisiones:

**`Nodo`** — un intercambio en el que participa el municipio. Campos según `docs/maqueta.md`: `ambito`, `clase` (*intercambio* o *plataforma*), `funcion`, `descripcion`, `instituciones`, `intercambio`, `madurez`, `factibilidad`, `origen`, `nota`.

**`oculto` es un campo del modelo, no una consulta.** Un nodo oculto existe y no aparece en los listados, pero su ficha sigue siendo alcanzable por enlace directo. Se implementa con un *manager* por defecto que filtra y un `todos` que no, de modo que ninguna vista tenga que acordarse:

```python
class NodoQuerySet(models.QuerySet):
    def visibles(self):
        return self.filter(oculto=False)

class Nodo(ModeloBase):
    objects = NodoQuerySet.as_manager()   # .visibles() explícito en los listados
```

No confundir `oculto` con `madurez`. La madurez dice qué tan avanzado está el intercambio; `oculto` dice si se muestra. Son ejes independientes.

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

`config/settings/` se divide en `base.py`, `dev.py` y `prod.py`. Ningún secreto en el repositorio: todo por variable de entorno, con `.env.example` como plantilla documentada.

> **Antecedente del proyecto.** En otro repositorio del equipo quedaron archivos `.env` versionados con contraseñas de base de datos. `.gitignore` debe excluir `.env` desde el primer commit, y conviene revisarlo antes de cada publicación.

### Migraciones

Se versionan siempre. Una migración que crea datos iniciales —los ámbitos, por ejemplo— va como migración de datos y no como *script* suelto.

---

## Cómo levantarlo

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env          # y completar
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

La API queda en `http://localhost:8000/api/v1/` y su documentación en `/api/v1/schema/swagger-ui/`.

---

## Qué falta decidir

- **Cómo se cargan las especificaciones.** ¿El equipo sube el archivo por el admin, o se sincroniza desde un repositorio de estándares? La segunda opción es más limpia y más trabajo.
- **Qué pasa cuando cambia una especificación vigente.** Versionar está definido; avisar a quien la consumía, no.
- **Si la wiki se administra en Django o en archivos.** Hoy la maqueta tiene las entradas como páginas. Un modelo con contenido en Markdown es más manejable para el equipo y menos revisable en *pull requests*.
- **El idioma de la API.** Los campos del modelo están en español; si algún día un tercero consume esta API, conviene haberlo decidido antes y no después.
