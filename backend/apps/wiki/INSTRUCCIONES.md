# `wiki` — entradas, versiones y editor

> **Construida.** Este archivo registra las decisiones y los límites de la aplicación; el código es la fuente de los detalles. Antes de cambiar algo de lo que dice acá, leer por qué está así. Contrato común en [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

La wiki contiene lo que el catálogo no debe contener: cómo se usa una API, de dónde viene cada dato, qué norma obliga cada cosa, y **las observaciones sobre un contrato**.

Esa última es la regla que hace existir esta aplicación. El catálogo publica cada contrato tal como se entregó, sin editarlo, porque su valor es ser copia fiel. La crítica vive acá. **Si alguna vez aparece un campo de observaciones en `catalogo`, esta separación se perdió.**

Depende de `core`, `cuentas` y `catalogo`.

## Dónde está cada cosa

| Pieza | Archivo |
|---|---|
| `Entrada`, `Version` inmutable, `Seccion` y `CAMPOS_EDITABLES` | `models.py` |
| `VersionInmutable` | `errores.py` |
| Markdown a HTML: contenedores, `id` de los títulos y lista blanca | `markdown.py` |
| Índice, entrada, crear y editar entradas | `api/v1/entradas_view.py`, `api/v1/entrada_serializer.py` |
| Historial, versiones y publicar | `api/v1/versiones_view.py`, `api/v1/version_serializer.py` |
| Las once páginas transcritas desde la maqueta | `contenido/*.md`, cargadas por `migrations/0002_contenido_inicial.py` |
| Admin para superusuarios locales | `admin.py` |

---

## 1. Modelos

```python
class Entrada(ModeloBase):
    slug        = models.SlugField(unique=True)            # inmutable
    titulo      = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=300)         # una línea, para el índice
    nodo        = models.SlugField(blank=True)             # identificador del nodo; no es clave foránea
    seccion     = models.CharField(choices=Seccion, blank=True)  # vacía: la portada
    orden       = models.PositiveSmallIntegerField(default=0)
    vigente     = models.ForeignKey("wiki.Version", null=True, blank=True,
                                    related_name="+", on_delete=models.SET_NULL)

class Version(ModeloBase):
    entrada      = models.ForeignKey(Entrada, related_name="versiones", on_delete=models.PROTECT)
    markdown     = models.TextField()
    resumen      = models.CharField(max_length=300)        # qué cambió, para el historial
    autor        = models.ForeignKey("cuentas.Perfil", null=True, on_delete=models.PROTECT)
    publicada    = models.BooleanField(default=False)
    publicada_en = models.DateTimeField(null=True)
```

Las secciones son las del menú de la maqueta (`WIKI_NAV`), en su orden: `usar_el_nodo`, `intercambios`, `codigos`, `normas` y `referencia`.

**El nodo se guarda por su identificador, no por clave foránea**, como `catalogo.Alias.destino`: el identificador es inmutable, y así el contenido inicial puede nombrar su nodo antes de que la sincronización de `registro` lo cree. Al crear o editar por la API se valida contra el catálogo, y un alias se guarda como el identificador vigente.

**Markdown en la base de datos, con versiones que no se corrigen.** Una edición crea una `Version` nueva y se marca cuál rige. Lo único que cambia de una versión es pasar de borrador a publicada; no se borra. Eso resolvió la pregunta que estaba abierta entre base de datos y archivos del repositorio: con un editor en la aplicación, los archivos obligarían a darle permiso de escritura al repositorio, que es bastante más superficie por bastante menos utilidad.

El contenido se guarda como Markdown, **no** como HTML. Nunca se guarda HTML generado.

## 2. Saneamiento

**El Markdown se renderiza y se sanea en el backend, siempre, al responder.** Es contenido que escriben personas y se muestra en un sitio público, y así hay un solo lugar donde auditar.

- Markdown CommonMark con tablas. **El HTML escrito dentro del Markdown no se interpreta**: sale como texto.
- Los componentes de la maqueta son **contenedores**, no HTML:

  ```markdown
  ::: aviso
  **Los ceros a la izquierda son parte del código.**
  :::
  ```

  Hay cuatro: `aviso`, `tarjetas` (el grupo), `tarjeta` y `tecnico` (el bloque «Para quien programa»). Cada uno es un `div` con esa clase. Un contenedor con otro nombre no genera nada. **Un contenedor se cierra con la primera marca igual o más larga que la suya**, así que el de afuera lleva más dos puntos que los de adentro: `:::::` tarjetas, `::::` tarjeta, `:::` aviso o técnico.
- Los títulos `h2` a `h4` llevan `id`, con el mismo slug que la maqueta (sin tildes, separado por guiones): sirven al índice «En esta página» y a las anclas del glosario. Un término del glosario es un enlace común a `/wiki/glosario#termino`.
- Después, nh3 con **lista blanca** de etiquetas, atributos, clases y esquemas de enlace. **La lista es parte del código, no configuración** — HR-24. Sin `script`, sin `style`, sin `iframe`, sin atributos `on*`, sin `javascript:` ni `data:` en los enlaces.
- Hay una prueba por cada vector que se intente bloquear. Si no hay prueba, no está bloqueado.

## 3. Endpoints

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/wiki` | público | Índice: entradas con versión publicada, por sección y orden. Con `?nodo={identificador}` —o un alias—, solo las de ese nodo. Con sesión, `?estado=todas` incluye las que no tienen versión publicada |
| `POST /api/v1/wiki` | editor | Crea una entrada, sin versiones. Deja `Bitacora` |
| `GET /api/v1/wiki/{slug}` | público | La versión vigente, como HTML saneado. Si no hay, `404` |
| `PATCH /api/v1/wiki/{slug}` | editor | Edita título, descripción, nodo, sección y orden. El `slug` no cambia. Deja `Bitacora` |
| `GET /api/v1/wiki/{slug}/versiones` | lector | El historial, con autor, fecha y resumen |
| `GET /api/v1/wiki/{slug}/versiones/{id}` | lector | Una versión con su Markdown y su HTML: la vista previa del editor |
| `POST /api/v1/wiki/{slug}/versiones` | editor | Crea una versión nueva, en borrador |
| `POST /api/v1/wiki/{slug}/versiones/{id}/publicar` | editor | La marca vigente. Deja `Bitacora` con la anterior y la nueva. Publicar una versión antigua es volver atrás |

El público nunca ve borradores ni autores. Un `GET` público de una entrada sin versión publicada responde `404`, no una página vacía.

**La entrada de un nodo oculto se ve solo con sesión**, como el nodo. Si el nodo está retirado, la entrada se sigue leyendo: es parte de su historia. Si todavía no se sincronizó, también: el contenido es nuestro.

Las entradas asociadas a un nodo se enlazan desde su ficha, pero **la respuesta del nodo no las incluye**: `catalogo` se construye antes y no consulta esta aplicación. El frontend las pide con `GET /api/v1/wiki?nodo={identificador}`. Un nodo sin entrada publicada recibe una lista vacía, y la ficha simplemente no enlaza a la wiki: la entrada es una vista opcional del nodo, no una deuda.

## 4. Contenido inicial

La maqueta tiene las entradas escritas en `prototipos/wiki-*.html`. **Se migraron como contenido, no como HTML**: cada una está transcrita a Markdown en `contenido/`, y la migración `0002_contenido_inicial` la carga como versión 1, publicada, con autor nulo y el resumen «Transcrita desde la maqueta». Son once: la portada (`inicio`) y las diez páginas de contenido. `wiki-intercambios.html` no se migró: es el índice que entrega `GET /wiki`.

Los enlaces internos apuntan a las rutas del frontend: `/wiki` (la portada con el índice), `/wiki/{slug}`, `/apis/{id}` y `/servicios/{slug}`. Un ancla es el `id` que sale del texto del título: las dos que la maqueta tenía escritas a mano (`#versiones` en conectar y `#procedencia` en ficha) se reemplazaron por las del título. Una prueba revisa que cada enlace `/wiki/...#ancla` del contenido inicial llegue a una entrada y a un título que existen.

Los `.md` de `contenido/` son la fuente de la migración, no de la wiki: **editarlos no cambia nada en una base ya migrada**. Una corrección posterior es una versión nueva, por la API.

El tono de la wiki está definido en [`../../../docs/maqueta.md`](../../../docs/maqueta.md). No es decorativo: es lo que hace que estas páginas se puedan leer.

## 5. Pruebas mínimas

1. Una edición crea una versión nueva y no modifica la anterior.
2. El público no ve borradores; una entrada sin versión publicada da `404`.
3. Un `lector` no puede crear versiones; un `editor` sí.
4. Publicar deja `Bitacora` con la versión anterior y la nueva.
5. Una batería de entradas con `script`, `iframe`, `onerror` y enlaces `javascript:` sale saneada, con una prueba por caso.
6. Las entradas migradas de la maqueta quedan como Markdown, sin HTML residual.

## 6. Qué no implementar

- Edición colaborativa en vivo, comentarios ni discusiones.
- Subida de archivos o imágenes en esta versión. Si hace falta, es otra decisión, con su propio análisis de qué se puede subir.
- Borrado de versiones.
- Cualquier campo de observaciones en `catalogo` para «acercar» la crítica al contrato.
