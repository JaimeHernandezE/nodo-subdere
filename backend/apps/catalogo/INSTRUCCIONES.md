# `catalogo` — ámbitos, nodos y especificaciones

Lee primero [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md). El modelo está definido campo por campo en [`../../../docs/estandar-ficha-de-servicio.md`](../../../docs/estandar-ficha-de-servicio.md) y en [`../../../docs/hoja-de-ruta.md`](../../../docs/hoja-de-ruta.md) §10. **Esos documentos son la fuente; este archivo dice cómo se implementa.**

Es el corazón. Lo que esta aplicación publica es lo que el mundo ve del nodo.

---

## 1. La idea central, y es contraintuitiva

`Nodo` **no se edita**: es la **proyección de la última lectura válida** de una ficha. Los campos que vienen de la ficha los escribe solo `registro` al sincronizar. Lo que esta aplicación administra son los campos editoriales.

| Campo | Lo escribe |
|---|---|
| `ambito`, `clase`, `funcion`, `descripcion`, `madurez`, `responsable`, `instituciones`, `intercambio` | Solo la sincronización |
| `visibilidad`, `orden`, `nota_editorial` | Solo una persona, desde la administración |

Se implementa en tres lugares, porque cada uno tapa una puerta distinta:

1. **`readonly_fields` en el admin.**
2. **`save()`** compara los campos de ficha con los guardados y levanta `CampoDeFicha` si cambió alguno, salvo que se llame como `nodo.save(desde_sincronizacion=True)`. Ese argumento lo usa **solo** `registro`; buscarlo en el código tiene que dar un único lugar.
3. **El `QuerySet` de `Nodo`** sobrescribe `update()` y `bulk_update()` para levantar `CampoDeFicha` si entre los campos hay alguno de ficha, porque esos métodos no pasan por `save()`.

No es paranoia: si alguien los edita, la siguiente sincronización le pasa por encima y el cambio se pierde sin aviso.

## 2. Modelos

```python
class Ambito(ModeloBase):
    nombre = models.CharField(unique=True)      # Transversal | SGM
    orden  = models.PositiveSmallIntegerField(default=0)

class Institucion(ModeloBase):
    nombre = models.CharField(unique=True)
    sigla  = models.CharField(blank=True)

class Nodo(ModeloBase):
    identificador = models.SlugField(unique=True)   # el id de la ficha. INMUTABLE
    nombre        = models.CharField()
    sigla         = models.CharField(blank=True)
    ambito        = models.ForeignKey(Ambito, on_delete=models.PROTECT)
    clase         = models.CharField(...)            # intercambio | plataforma
    intercambio   = models.CharField(...)            # consulta | entrega
    funcion       = models.TextField()
    descripcion   = models.TextField()
    madurez       = models.CharField(...)            # Deseable | En evaluación | En desarrollo | Operativo
    instituciones = models.ManyToManyField(Institucion, blank=True)
    responsable_organismo = models.CharField()
    responsable_equipo    = models.CharField(blank=True)
    responsable_correo    = models.EmailField()
    origen_norma  = models.TextField(blank=True)
    origen_nota   = models.TextField(blank=True)
    visibilidad   = models.CharField(default="oculto")   # publicado | oculto | retirado
    orden         = models.PositiveSmallIntegerField(default=0)
    nota_editorial = models.TextField(blank=True)

class Alias(ModeloBase):
    """Identificadores antiguos que deben seguir resolviendo."""
    identificador = models.SlugField(unique=True)
    nodo          = models.ForeignKey(Nodo, related_name="alias", on_delete=models.CASCADE)
    # Ya existe uno: division-territorial -> cut

class Especificacion(ModeloBase):
    nodo      = models.ForeignKey(Nodo, related_name="especificaciones", on_delete=models.CASCADE)
    version   = models.CharField()               # única por nodo
    archivo   = models.FileField(blank=True)
    formato   = models.CharField()               # openapi-3.0
    publicada = models.DateField(null=True)
    vigente   = models.BooleanField(default=False)
    origen_commit = models.CharField(blank=True)

class Ambiente(ModeloBase):
    nodo   = models.ForeignKey(Nodo, related_name="ambientes", on_delete=models.CASCADE)
    nombre = models.CharField()                  # pruebas | produccion
    base   = models.URLField()
    datos  = models.CharField(...)               # inventados | reales
```

`Municipio` no está acá: vive en `core`, porque `cuentas` lo necesita antes de que exista `catalogo`.

**Tres reglas que el modelo tiene que hacer evidentes:**

- **`identificador` es inmutable.** Cambiarlo es un servicio nuevo. Si hay que renombrar, se crea otro y se deja un `Alias`. Verificar en `save()`.
- **No existe campo `operaciones`.** Cuando hay archivo, las operaciones se renderizan desde el archivo; cuando solo hay metadato, no se transcriben a mano. La decisión está en el ADR del estándar legible por máquina.
- **No existe campo de observaciones ni de disponibilidad.** Las observaciones van en la wiki. La disponibilidad la mide el monitor (HR-09).

**`visibilidad` reemplaza el antiguo `oculto`**, con tres estados en vez de dos. `retirado` deja de leerse pero conserva su última lectura: el catálogo tiene que poder decir qué publicó y hasta cuándo.

## 3. Manager

```python
class NodoQuerySet(models.QuerySet):
    def publicados(self):  return self.filter(visibilidad="publicado")
    def vigentes(self):    return self.exclude(visibilidad="retirado")
```

Los endpoints públicos usan `publicados()` siempre. **Que sea explícito es a propósito**: un manager que filtre por defecto esconde el filtro y después alguien no entiende por qué le falta una fila en el admin.

`madurez` y `visibilidad` son ejes independientes. La madurez dice qué tan avanzado está el intercambio; la visibilidad, si se muestra. No confundirlos ni derivar uno del otro.

## 4. Endpoints

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/nodos` | público | Solo `publicados()`. Filtros por ámbito, madurez e intercambio |
| `GET /api/v1/nodos/{identificador}` | público | Resuelve también por `Alias`. Un nodo `oculto` responde por enlace directo, con `visibilidad` en la respuesta para que el frontend avise |
| `GET /api/v1/nodos/{identificador}/especificacion` | público | La vigente: metadatos y la URL del archivo |
| `PATCH /api/v1/nodos/{identificador}` | curador | Solo `visibilidad`, `orden` y `nota_editorial`. Cualquier otro campo da `400` con código `CAMPO_DE_FICHA`. Deja `Bitacora` |
| `GET /api/v1/ambitos` · `GET /api/v1/municipios` | público | Listados de apoyo. El de municipios lee `core.Municipio` |

Un `retirado` responde `410 Gone` con código `NODO_RETIRADO` y la fecha de su última lectura, no `404`. La diferencia importa: `404` dice «nunca existió».

## 5. Pruebas mínimas

1. Intentar escribir `funcion` por el `PATCH` da `400` con código `CAMPO_DE_FICHA`.
2. Intentar cambiar `identificador` levanta excepción en `save()`. Cambiar `funcion` con `save()` sin `desde_sincronizacion=True`, o con `Nodo.objects.update(funcion=...)`, levanta `CampoDeFicha`.
3. `GET /nodos` no devuelve ocultos ni retirados; `GET /nodos/{id}` de un oculto sí responde, con su `visibilidad`.
4. Un identificador antiguo con `Alias` resuelve al nodo nuevo.
5. Un nodo `retirado` responde `410` con la fecha de la última lectura.
6. Solo una `Especificacion` por nodo puede estar `vigente`.

## 6. Qué no implementar

- Formularios de creación de nodos. Un nodo nace de una ficha leída por `registro`.
- Validación del contenido de la especificación. Eso es de `registro`.
- Renderizado de la especificación. Eso es del frontend.
- Cualquier campo que describa el estado operacional del servicio.
