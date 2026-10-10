# `catalogo` — ámbitos, nodos y especificaciones

> **Construida.** Este archivo registra las decisiones y los límites de la aplicación; el código es la fuente de los detalles. Antes de cambiar algo de lo que dice acá, leer por qué está así. Contrato común en [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

Los campos que vienen de una ficha están definidos en [`../../../docs/estandar-ficha-de-servicio.md`](../../../docs/estandar-ficha-de-servicio.md). **Ese documento es la fuente; este archivo dice cómo se implementa.**

Es el corazón. Lo que esta aplicación publica es lo que el mundo ve del nodo.

Depende de `core` y `cuentas`. **No consulta `registro`, `servicios` ni `wiki`**, que se construyen después: lo que el catálogo necesita saber de una lectura lo escribe la sincronización en el propio nodo, y lo que necesita la ficha de la wiki o de los servicios lo junta el frontend.

## Dónde está cada cosa

| Pieza | Archivo |
|---|---|
| `Ambito`, `Nodo`, `Alias`, `Especificacion`, `Ambiente`, las listas cerradas, `CAMPOS_DE_FICHA` y las tres puertas | `models.py` |
| `CampoDeFicha` y `NodoRetirado` | `errores.py` |
| Los ámbitos `SGM` y `Transversal` | `migrations/0002_ambitos.py` |
| Resolución de un identificador, con alias y reglas de visibilidad | `resolver_nodo` en `api/v1/nodos_view.py` |
| Endpoints | `api/v1/` |
| Admin para superusuarios locales | `admin.py` |

---

## 1. La idea central, y es contraintuitiva

`Nodo` **no se edita**: es la **proyección de la última lectura válida** de una ficha. Todo lo que viene de la ficha lo escribe solo `registro` al sincronizar. Lo que esta aplicación administra son tres campos editoriales.

| Campos | Los escribe |
|---|---|
| `identificador`, `nombre`, `sigla`, `ambito`, `clase`, `intercambio`, `funcion`, `descripcion`, `madurez`, `instituciones`, `responsable_*`, `origen_*`, `procedencia_*`, `acceso_*`, `leido_en`, `commit` | Solo la sincronización |
| `visibilidad`, `orden`, `nota_editorial` | Solo una persona, desde la administración |
| `Especificacion` y `Ambiente`, completos | Solo la sincronización |

La lista de campos de ficha vive en el código como una constante, `CAMPOS_DE_FICHA`, y las tres protecciones la leen de ahí. Un campo de ficha nuevo que no se agregue a la constante queda editable a mano: la prueba 2 lo detecta comparando la constante con los campos del modelo.

Se implementa en tres lugares, porque cada uno tapa una puerta distinta:

1. **`readonly_fields` en el admin.**
2. **`save()`** compara los campos de ficha con los guardados y levanta `CampoDeFicha` si cambió alguno, salvo que se llame como `nodo.save(desde_sincronizacion=True)`. Ese argumento lo usa **solo** `registro`; buscarlo en el código tiene que dar un único lugar.
3. **El `QuerySet` de `Nodo`** sobrescribe `update()` y `bulk_update()` para levantar `CampoDeFicha` si entre los campos hay alguno de ficha, porque esos métodos no pasan por `save()`.

**`Especificacion` y `Ambiente` se protegen enteros**, no campo por campo: vienen completos de la ficha. `save()` y `delete()` exigen `desde_sincronizacion=True`, y su `QuerySet` rechaza `update()`, `bulk_update()`, `bulk_create()` y `delete()`.

**Un nodo tampoco se crea a mano**: crear también exige `desde_sincronizacion=True`, y `bulk_create()` se rechaza, porque se saltaría `save()`. La sincronización crea y guarda los nodos de a uno.

No es paranoia: si alguien los edita, la siguiente sincronización le pasa por encima y el cambio se pierde sin aviso.

**Por qué no hay relaciones muchos a muchos con datos de ficha.** `instituciones.set(...)` no pasa por `save()` ni por `update()`: se escaparía de las tres puertas. Las instituciones son una lista de textos (`JSONField`), tal como vienen en la ficha.

## 2. Modelos

```python
class Ambito(ModeloBase):
    nombre = models.CharField(unique=True)       # Transversal | SGM
    orden  = models.PositiveSmallIntegerField(default=0)

class Nodo(ModeloBase):
    # De la ficha
    identificador = models.SlugField(unique=True)   # el id de la ficha. INMUTABLE
    nombre        = models.CharField()
    sigla         = models.CharField(blank=True)
    ambito        = models.ForeignKey(Ambito, on_delete=models.PROTECT)
    clase         = models.CharField(...)            # intercambio | plataforma
    intercambio   = models.CharField(blank=True)     # consulta | entrega; vacío si clase = plataforma
    funcion       = models.TextField()
    descripcion   = models.TextField()
    madurez       = models.CharField(...)            # Deseable | En evaluación | En desarrollo | Operativo
    instituciones = models.JSONField(default=list)   # lista de nombres, como en la ficha
    responsable_organismo = models.CharField()
    responsable_equipo    = models.CharField(blank=True)
    responsable_correo    = models.EmailField()
    origen_norma  = models.TextField(blank=True)
    origen_nota   = models.TextField(blank=True)
    procedencia_copia   = models.CharField(blank=True)   # exacta | instantanea | reconstruccion | sin-copia
    procedencia_fuente  = models.TextField(blank=True)
    procedencia_detalle = models.TextField(blank=True)
    acceso_tipo    = models.CharField(blank=True)        # abierto | credencial | clave-unica
    acceso_detalle = models.TextField(blank=True)
    # De la lectura que produjo esta proyección
    leido_en = models.DateTimeField()
    commit   = models.CharField(blank=True)          # vacío: carga manual, sin fuente verificable
    # Editoriales
    visibilidad    = models.CharField(default="oculto")   # publicado | oculto | retirado
    orden          = models.PositiveSmallIntegerField(default=0)
    nota_editorial = models.TextField(blank=True)

class Alias(ModeloBase):
    """Identificadores antiguos que deben seguir resolviendo."""
    identificador = models.SlugField(unique=True)
    destino       = models.SlugField()           # identificador del nodo; no es clave foránea

class Especificacion(ModeloBase):
    nodo      = models.ForeignKey(Nodo, related_name="especificaciones", on_delete=models.PROTECT)
    version   = models.CharField()               # única por nodo
    formato   = models.CharField()               # openapi-3.0 | openapi-3.1 | descripcion
    ruta      = models.CharField(blank=True)     # dentro del repositorio; vacía si solo hay metadato
    contenido = models.TextField(blank=True)     # el archivo tal como se leyó
    huella    = models.CharField(blank=True)     # sha256 de `contenido`
    publicada = models.DateField(null=True)
    vigente   = models.BooleanField(default=False)
    commit    = models.CharField(blank=True)

class Ambiente(ModeloBase):
    nodo   = models.ForeignKey(Nodo, related_name="ambientes", on_delete=models.CASCADE)
    nombre = models.CharField()                  # pruebas | produccion; único por nodo
    base   = models.URLField()
    datos  = models.CharField(...)               # inventados | reales
```

`Municipio` no está acá: vive en `core`, porque `cuentas` lo necesita antes de que exista `catalogo`.

**Reglas que el modelo tiene que hacer evidentes:**

- **`identificador` es inmutable.** Cambiarlo es un servicio nuevo. Si hay que renombrar, se crea otro y se deja un `Alias`. Verificar en `save()`, incluso con `desde_sincronizacion=True`.
- **`Alias.destino` es un identificador, no una clave foránea.** El identificador es inmutable, igual que en `cuentas.Acceso.nodo`, y así un alias puede existir antes de que la sincronización cree su nodo. **El catálogo parte sin alias**: `cut` se llama así desde la primera lectura. El renombre `division-territorial` → `cut` ocurrió en la maqueta, y esa dirección vieja la redirige el frontend (ver `frontend/INSTRUCCIONES.md`). Un alias se crea cuando un nodo real se renombre.
- **Un solo `Especificacion` vigente por nodo** (restricción única condicional), y `(nodo, version)` único. Ninguna versión se borra ni se corrige: la `huella` permite a `registro` rechazar una lectura que trae la misma versión con otro contenido. **El modelo también lo impide**: `save()` calcula la huella y, sobre una versión ya guardada, rechaza otro contenido u otra versión **incluso desde la sincronización**. Lo único que la sincronización cambia de una versión registrada es cuál rige.
- **El archivo de la especificación se guarda como texto, no como `FileField`.** Viene de un repositorio, no de una subida, y guardarlo como texto evita tener que servir archivos subidos en producción. Sin archivo, el nodo publica solo metadato: `formato = descripcion`, `ruta` y `contenido` vacíos, y la ficha lo dice. No se transcriben operaciones a mano.
- **No existe campo `operaciones`.** Cuando hay archivo, las operaciones se renderizan desde el archivo. La decisión está en el ADR del estándar legible por máquina.
- **No existe campo de observaciones ni de disponibilidad.** Las observaciones van en la wiki. La disponibilidad la mide el monitor (HR-09).

**`visibilidad` reemplaza el antiguo `oculto`**, con tres estados en vez de dos. `retirado` deja de leerse pero conserva su última lectura: el catálogo tiene que poder decir qué publicó y hasta cuándo.

**`Ambito` se carga por migración de datos**, con `Transversal` y `SGM`. La ficha lo nombra, y un ámbito que no existe lo rechaza `registro` al validar.

## 3. Manager

```python
class NodoQuerySet(models.QuerySet):
    def publicados(self):  return self.filter(visibilidad="publicado")
    def vigentes(self):    return self.exclude(visibilidad="retirado")
```

Los endpoints públicos usan `publicados()` siempre. **Que sea explícito es a propósito**: un manager que filtre por defecto esconde el filtro y después alguien no entiende por qué le falta una fila en el admin.

`madurez` y `visibilidad` son ejes independientes. La madurez dice qué tan avanzado está el intercambio; la visibilidad, si se muestra. No confundirlos ni derivar uno del otro.

## 4. Visibilidad

- Un curador puede mover un nodo entre los tres estados, con una excepción: **de `retirado` solo se sale a `oculto`**. Volver a publicar algo retirado pasa primero por revisarlo.
- **Publicar exige una especificación vigente**, que puede ser solo metadato. Toda ficha válida la trae, así que en la práctica exige que el nodo venga de una lectura buena. **No exige pantalla, entrada de wiki ni servicio disponible**: las tres vistas de un nodo —su contrato acá, sus pantallas en `servicios` y su entrada en `wiki`— son independientes, y un nodo puede publicarse con una sola. Cada una se publica en su aplicación, y el frontend muestra las que existan.
- `registro` no lee las fuentes de nodos retirados. Al salir de `retirado`, la siguiente sincronización vuelve a leerlas.

## 5. Endpoints

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/nodos` | público | Solo `publicados()`. Filtros por ámbito, clase, madurez e intercambio |
| `GET /api/v1/nodos?visibilidad=publicado\|oculto\|retirado\|todas` | lector | Filtra por esa visibilidad, o trae todas. Es lo que usa la pantalla de visibilidad. Otro valor da `400` |
| `GET /api/v1/nodos/{identificador}` | público si está publicado; lector si está oculto | Resuelve también por `Alias`, y responde con el `identificador` vigente. Incluye `visibilidad`, para que el frontend avise cuando no está publicado, y `leido_en` y `commit` |
| `GET /api/v1/nodos/{identificador}/especificacion` | ídem | La vigente: metadatos y, si tiene archivo, la URL del archivo |
| `GET /api/v1/nodos/{identificador}/especificacion/archivo` | ídem | El archivo tal como se leyó, con su tipo de contenido. `404` si el nodo solo publica metadato |
| `PATCH /api/v1/nodos/{identificador}` | curador | Solo `visibilidad`, `orden` y `nota_editorial`. Deja `Bitacora` |
| `GET /api/v1/ambitos` · `GET /api/v1/municipios` | público | Listados de apoyo. El de municipios lee `core.Municipio` |

**Errores del `PATCH`:** un campo de ficha da `400` con código `CAMPO_DE_FICHA`, también si se usa el nombre agrupado con que lo muestra la respuesta (`responsable`, `especificacion`, `ambientes`...); un campo que no existe, `400 VALIDACION_FALLIDA`; publicar sin especificación vigente o salir de `retirado` a otro estado que no sea `oculto`, `400 VALIDACION_FALLIDA` con el detalle. El `PATCH` alcanza también a un nodo retirado: es la única manera de sacarlo de ese estado. Deja `Bitacora` con acción `editar_nodo` y los tres campos editoriales antes y después, solo si algo cambió.

**La ficha se responde agrupada como en el estándar**: `responsable`, `origen`, `procedencia` y `acceso` son objetos, y los tres últimos son `null` si la ficha no los declara. Trae `ambientes` y la `especificacion` vigente, con la URL del archivo.

**El archivo de la especificación** se responde byte por byte, con `application/yaml` o, si la ruta termina en `.json`, `application/json`, y un `ETag` con la huella. Los errores de esa ruta salen siempre en el sobre JSON, aunque la petición pida YAML.

**Un nodo `oculto` no es público, ni por enlace directo.** Toda ficha nueva entra oculta, y los repositorios de origen están en el GitLab privado de SUBDERE: un contrato en preparación no puede quedar a la vista de quien adivine su identificador. Sin sesión, un oculto responde `404`, igual que uno que no existe, para no confirmar que está ahí. Con cualquier perfil responde, con su `visibilidad`, y así se puede revisar antes de publicar.

**Un `retirado` responde `410 Gone`** con código `NODO_RETIRADO` y su `leido_en` en los detalles —`{"campo": "leido_en", "valor": "<fecha ISO>"}`—, en el nodo y en su especificación. No `404`: `404` dice «nunca existió».

**Las rutas públicas autentican de forma opcional**, con `cuentas.autenticacion.AutenticacionOpcional`. Un token válido identifica al perfil, que es lo que permite ver un oculto. Un token ausente, vencido, inválido o sin perfil deja la petición como anónima, sin `401`: un token vencido no puede dejar a alguien sin ver el catálogo publicado. La excepción es `GET /nodos` con `?visibilidad=`, que exige sesión: sin ella, `401`. Ámbitos y municipios no autentican.

Los listados no se paginan todavía: son decenas de nodos y 346 comunas.

La respuesta del nodo **no** incluye su entrada de wiki ni sus servicios. Los pide el frontend a esas aplicaciones, filtrando por el identificador del nodo.

## 6. Lo que las pruebas garantizan

En `tests/`. Si una de estas deja de cumplirse, se rompió una decisión de arriba:

1. Intentar escribir `funcion` por el `PATCH` da `400` con código `CAMPO_DE_FICHA`.
2. Cambiar `identificador` levanta excepción en `save()`, incluso desde la sincronización. Cambiar `funcion` con `save()` sin `desde_sincronizacion=True`, o con `Nodo.objects.update(funcion=...)`, levanta `CampoDeFicha`. `CAMPOS_DE_FICHA` cubre todos los campos del modelo salvo los editoriales y los de `ModeloBase`.
3. `Especificacion` y `Ambiente` no se crean, modifican ni borran sin `desde_sincronizacion=True`, ni por `save()` ni por `QuerySet`.
4. `GET /nodos` no devuelve ocultos ni retirados. `GET /nodos/{id}` de un oculto, su especificación y su archivo dan `404` sin sesión, también por `Alias`; con un perfil responden, con su `visibilidad`. `?visibilidad=todas` sin sesión da `401`.
5. Un identificador antiguo con `Alias` resuelve al nodo nuevo y responde con el identificador vigente.
6. Un nodo `retirado` responde `410` con la fecha de la última lectura, también en su especificación.
7. Solo una `Especificacion` por nodo puede estar `vigente`.
8. No se publica un nodo sin especificación vigente, y de `retirado` solo se pasa a `oculto`.
9. Un nodo con solo metadato responde `404` en el archivo, y uno con archivo lo devuelve tal como se guardó.
10. Un token vencido no impide leer un nodo publicado, y tampoco da acceso a uno oculto. Un token sin perfil, tampoco.
11. Una versión registrada no cambia de contenido, ni desde la sincronización, y un nodo no se crea a mano.
12. Editar un nodo deja `Bitacora` solo si algo cambió; un lector no edita, y sin sesión es `401`.

Además, `core` comprueba que el esquema OpenAPI completo se genera sin advertencias y es válido.

## 7. Qué no implementar

- Formularios de creación de nodos. Un nodo nace de una ficha leída por `registro`.
- Validación del contenido de la especificación. Eso es de `registro`.
- Renderizado de la especificación. Eso es del frontend.
- Cualquier campo que describa el estado operacional del servicio.
- Consultas a `registro`, `servicios` o `wiki` desde esta aplicación.
- **Lo que la maqueta muestra y el estándar de la ficha todavía no tiene**, y por qué:
  - **Monitoreo y disponibilidad:** los mide el monitor (HR-09), no la ficha.
  - **Sandbox:** depende de la zona de práctica del nodo.
  - **Dependencias y descargables:** quedan para una versión posterior del estándar, como campos opcionales.
  - **Factibilidad:** era una estimación interna del levantamiento, no un hecho del servicio.
  - **La nota de advertencia** de la maqueta («Demostración... datos inventados») no se pierde: es `nota_editorial`.
