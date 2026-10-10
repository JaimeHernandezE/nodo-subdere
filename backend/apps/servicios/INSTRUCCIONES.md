# `servicios` — las pantallas de uso humano

> **Construida.** Este archivo registra las decisiones y los límites de la aplicación; el código es la fuente de los detalles. Antes de cambiar algo de lo que dice acá, leer por qué está así. Contrato común en [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

Un **servicio** es una pantalla construida sobre una API del catálogo, para resolver una tarea sin programar. Es el catálogo de «Servicios» del sitio, distinto del de «APIs».

**Un servicio no es un nodo filtrado: es un consumidor de uno.** Por eso es un modelo aparte y no una vista del mismo. El catálogo de APIs dice qué se puede consumir; el de servicios, qué se puede usar hoy sin escribir código.

Depende de `core`, `cuentas`, `catalogo` e `integraciones`.

## Dónde está cada cosa

| Pieza | Archivo |
|---|---|
| `Servicio`, `Estado` y `CAMPOS_EDITABLES` | `models.py` |
| `ProcedimientoRequerido` | `errores.py` |
| Catálogo de servicios: listar, ver, crear y editar | `api/v1/servicios_view.py`, `api/v1/servicio_serializer.py` |
| Buscador del CUT, por nombre y por código | `api/v1/cut_view.py`, `api/v1/cut_serializer.py` |
| Permisos de circulación por patente | `api/v1/permisos_view.py`, `api/v1/permisos_serializer.py` |
| El sobre `{origen, obtenido_en, datos}` y cómo se juntan dos respuestas | `api/v1/respuesta_serializer.py` |
| Rutas, con las de datos antes de `<slug>` | `api/v1/routers.py` |
| Admin para superusuarios locales | `admin.py` |

---

## 1. Por qué esta aplicación es la menos riesgosa, y la más delicada

La menos riesgosa en lo normativo: una persona que se autentica y consulta por pantalla es canal de plataforma de trámite, no interoperabilidad. No depende de HR-26 y puede ir a producción.

La más delicada en datos personales: las pantallas muestran patente y titular. Que un funcionario del municipio A consulte un vehículo del municipio B **tiene que quedar registrado**. Eso es `cuentas.Acceso`, con `canal="pantalla"`, y es obligatorio en todo endpoint que entregue datos de una persona.

**El `Acceso` no lo escribe esta aplicación: lo escribe el adaptador.** `AdaptadorPermisos` exige un `Contexto` —el perfil, el canal y la petición— y registra cada consulta él mismo, también cuando responde desde el caché. Los endpoints de acá solo arman ese contexto. Así ninguna vista nueva puede olvidarse del registro (ver `integraciones` §3).

## 2. Modelos

```python
class Servicio(ModeloBase):
    nodo        = models.ForeignKey("catalogo.Nodo", related_name="servicios", on_delete=models.PROTECT)
    slug        = models.SlugField(unique=True)        # inmutable
    nombre      = models.CharField(max_length=200)     # la herramienta, no el nodo
    funcion     = models.CharField(max_length=300)     # una línea, para la tarjeta
    descripcion = models.TextField()                   # el párrafo de entrada de la pantalla
    tareas      = models.JSONField(default=list)       # ["Buscar el código de una comuna", ...]
    fuentes     = models.JSONField(default=list)       # [{"dato": ..., "origen": ...}]
    estado      = models.CharField(...)                # disponible | en_construccion | deseable
    nota        = models.TextField(blank=True)
```

Los campos son los que pinta la maqueta (`prototipos/assets/data.js`, `SERVICIOS`). La fecha de revisión es `actualizado_en`. El enlace a la wiki no se guarda: la pantalla lo pide a `GET /wiki?nodo=`.

`estado` describe la pantalla, no la fuente: `disponible`, `en_construccion` o `deseable` (pensada, sin construir). La disponibilidad de la fuente la mide el monitor (HR-09) y la frescura del dato la informa el adaptador.

**Los servicios los mantiene un curador por la API**, con `Bitácora`, y el admin queda para la puesta en marcha. No hay migración de datos: el nodo sobre el que se construye lo crea la sincronización de `registro`. `slug` y `nodo` no cambian después de creado: otro nodo es otro servicio.

El nodo de los permisos de circulación se identifica como **`permisos-de-circulacion`**: es el `nodo` que el adaptador escribe en cada `Acceso`, y la ficha real tiene que usar ese identificador. La maqueta lo llamaba `fiscalizacion`.

## 3. Endpoints

Dos familias, y conviene no mezclarlas.

**El catálogo de servicios**, de lectura pública:

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/servicios` | público | Los servicios de nodos `publicados()`. Con `?nodo={identificador}` —o un alias—, solo los construidos sobre ese nodo: es lo que pide la ficha del nodo, porque `catalogo` no consulta esta aplicación. Un nodo oculto, solo con sesión; uno retirado, lista vacía |
| `POST /api/v1/servicios` | curador | Crea un servicio sobre un nodo vigente |
| `GET /api/v1/servicios/{slug}` | público | Uno, con sus tareas y su estado. Si su nodo no está publicado, `404` sin sesión |
| `PATCH /api/v1/servicios/{slug}` | curador | Edita todo menos `slug` y `nodo` |

**Las consultas que entregan datos**, una por tarea:

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/servicios/cut/buscar?q=` | público | Busca por nombre de región, provincia o comuna; al menos dos caracteres |
| `GET /api/v1/servicios/cut/codigo/{codigo}` | público | El camino inverso: código a unidad territorial |
| `GET /api/v1/servicios/permisos/{patente}` | perfil activo | El vehículo y sus permisos de circulación, con `?desde_anio=` opcional. Una patente provisoria trae los permisos provisionales |

Las rutas de datos van antes de `servicios/{slug}` y tienen más de un segmento, así que no chocan con ningún slug.

El CUT es público porque es dato abierto, y no escribe `Acceso`: no entrega datos de nadie. Los permisos de circulación **no**: sin sesión dan `401`, con sesión y sin perfil activo `403 SIN_PERFIL`, exigen la cabecera `X-Procedimiento` y el adaptador escribe `cuentas.Acceso`, uno por operación consultada a la fuente. Sin esa cabecera, `400` con código `PROCEDIMIENTO_REQUERIDO` — para que nadie consulte «porque sí». La cabecera y la patente se revisan antes de llamar al adaptador.

**`PR` y cuatro dígitos se consulta como provisoria.** El patrón calza también con la forma antigua de dos letras y cuatro dígitos (`integraciones` §2); la pantalla de la maqueta las trata como provisorias de automotora, y así queda. Las demás patentes consultan el vehículo y, si existe, sus permisos: un vehículo inexistente da `404` sin consultar los permisos.

Un perfil con municipio ve lo que su trámite necesita; **que haya o no restricción por municipio en los permisos de circulación es una pregunta para jurídica**, no una decisión de implementación. Hasta que se responda, se registra todo acceso y no se restringe por municipio, y la pantalla dice que la consulta queda registrada.

## 4. Degradación honesta

La decide el adaptador, y cada respuesta trae su `origen` —`fuente`, `foto` o `muestra`— y su fecha (`integraciones` §5). Esta aplicación lo pasa tal cual a la pantalla, en un sobre común:

```json
{"origen": "foto", "obtenido_en": "2026-10-09T12:00:00-03:00", "datos": ...}
```

Cuando una respuesta junta dos consultas —el vehículo y sus permisos—, se informa lo menos fresco: el peor origen (`muestra`, luego `foto`, luego `fuente`) y la fecha más antigua.

- **CUT:** si la fuente no responde, se entrega la foto versionada, con su fecha. Es dato real y abierto.
- **Permisos:** si la fuente está configurada y no responde, `503 FUENTE_NO_DISPONIBLE`, y la pantalla lo dice. **Nunca** datos inventados sobre una patente que puede existir. La muestra sintética aparece solo en un ambiente sin fuente configurada, marcada en cada respuesta.
- Nunca una pantalla en blanco, nunca datos de muestra sin aviso.

Una pantalla que se queda en blanco no se puede mostrar en una reunión; una que finge datos sin avisar es peor.

## 5. Pruebas mínimas

1. `GET /servicios` no devuelve servicios de nodos ocultos.
2. Consultar un permiso sin sesión da `401`; sin perfil activo, `403`; sin `X-Procedimiento`, `400`.
3. Cada consulta de permisos deja en `cuentas.Acceso` el perfil, la patente y el procedimiento, y **sin** la respuesta. Lo escribe el adaptador; acá se prueba que el endpoint le pasa el contexto.
4. Con la fuente del CUT caída, la respuesta trae la foto y el campo que lo declara; con la de permisos caída, `503`.
5. El buscador del CUT funciona en los dos sentidos y devuelve códigos canónicos.
6. Una patente mal formada se rechaza antes de llamar a la fuente.

## 6. Qué no implementar

- Ninguna pantalla que llegue a datos que la API no exponga. Nadie tiene atajos, y eso incluye a estas vistas.
- Ninguna consulta masiva, exportación ni descarga de listados de personas.
- Ningún almacenamiento de las respuestas.
- Ninguna búsqueda por nombre de persona o por RUT. La entrada es la patente.
