# `wiki` — entradas, versiones y editor

Lee primero [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

La wiki contiene lo que el catálogo no debe contener: cómo se usa una API, de dónde viene cada dato, qué norma obliga cada cosa, y **las observaciones sobre un contrato**.

Esa última es la regla que hace existir esta aplicación. El catálogo publica cada contrato tal como se entregó, sin editarlo, porque su valor es ser copia fiel. La crítica vive acá. **Si alguna vez aparece un campo de observaciones en `catalogo`, esta separación se perdió.**

---

## 1. Modelos

```python
class Entrada(ModeloBase):
    slug    = models.SlugField(unique=True)
    titulo  = models.CharField()
    nodo    = models.ForeignKey("catalogo.Nodo", null=True, blank=True,
                                related_name="entradas_wiki", on_delete=models.SET_NULL)
    seccion = models.CharField(blank=True)       # para ordenar el índice
    orden   = models.PositiveSmallIntegerField(default=0)
    vigente = models.ForeignKey("wiki.Version", null=True, blank=True,
                                related_name="+", on_delete=models.SET_NULL)

class Version(ModeloBase):
    entrada   = models.ForeignKey(Entrada, related_name="versiones", on_delete=models.CASCADE)
    markdown  = models.TextField()
    resumen   = models.CharField(blank=True)     # qué cambió, para el historial
    autor     = models.ForeignKey("cuentas.Perfil", null=True, on_delete=models.PROTECT)
    publicada = models.BooleanField(default=False)
```

**Markdown en la base de datos, con versiones que no se corrigen.** Una edición crea una `Version` nueva y se marca cuál rige. Eso resolvió la pregunta que estaba abierta entre base de datos y archivos del repositorio: con un editor en la aplicación, los archivos obligarían a darle permiso de escritura al repositorio, que es bastante más superficie por bastante menos utilidad.

El contenido se guarda como Markdown, **no** como HTML. Nunca se guarda HTML generado.

## 2. Saneamiento

**El Markdown se sanea al renderizar, siempre.** Es contenido que escriben personas y se muestra en un sitio público.

- Renderizar en el backend y devolver HTML saneado, o devolver el Markdown y renderizar en el frontend: **se elige una y se documenta**. Recomendación: sanear y renderizar en el backend, porque así hay un solo lugar donde auditar.
- Biblioteca de saneamiento con lista blanca, no lista negra.
- **La lista de etiquetas y atributos permitidos es parte del código, no configuración** — HR-24. Sin `script`, sin `style`, sin `iframe`, sin atributos `on*`, sin `javascript:` en los enlaces.
- Hay una prueba por cada vector que se intente bloquear. Si no hay prueba, no está bloqueado.

## 3. Endpoints

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/wiki` | público | Índice: secciones y entradas con versión publicada. Con `?nodo={identificador}`, solo las asociadas a ese nodo |
| `GET /api/v1/wiki/{slug}` | público | La versión vigente y publicada. Si no hay, `404` |
| `GET /api/v1/wiki/{slug}/versiones` | lector | El historial, con autor, fecha y resumen |
| `POST /api/v1/wiki/{slug}/versiones` | editor | Crea una versión nueva, en borrador |
| `POST /api/v1/wiki/{slug}/versiones/{id}/publicar` | editor | La marca vigente. Deja `Bitacora` |

El público nunca ve borradores. Un `GET` público de una entrada sin versión publicada responde `404`, no una página vacía.

Las entradas asociadas a un nodo se enlazan desde su ficha, pero **la respuesta del nodo no las incluye**: `catalogo` se construye antes y no consulta esta aplicación. El frontend las pide con `GET /api/v1/wiki?nodo={identificador}`. Un nodo sin entrada publicada recibe una lista vacía, y la ficha simplemente no enlaza a la wiki: la entrada es una vista opcional del nodo, no una deuda.

## 4. Contenido inicial

La maqueta ya tiene las entradas escritas en `prototipos/wiki-*.html`. **Migrarlas como contenido, no copiar su HTML**: se transcriben a Markdown en una migración de datos, con autor nulo y un resumen que diga que vienen de la maqueta. Las dos que importan primero son la del CUT y la de los permisos de circulación.

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
