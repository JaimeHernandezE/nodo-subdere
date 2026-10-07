# `servicios` — las pantallas de uso humano

Lee primero [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

Un **servicio** es una pantalla construida sobre una API del catálogo, para resolver una tarea sin programar. Es el catálogo de «Servicios» del sitio, distinto del de «APIs».

**Un servicio no es un nodo filtrado: es un consumidor de uno.** Por eso es un modelo aparte y no una vista del mismo. El catálogo de APIs dice qué se puede consumir; el de servicios, qué se puede usar hoy sin escribir código.

---

## 1. Por qué esta aplicación es la menos riesgosa, y la más delicada

La menos riesgosa en lo normativo: una persona que se autentica y consulta por pantalla es canal de plataforma de trámite, no interoperabilidad. No depende de HR-26 y puede ir a producción.

La más delicada en datos personales: las pantallas muestran patente y titular. Que un funcionario del municipio A consulte un vehículo del municipio B **tiene que quedar registrado**. Eso es `cuentas.Acceso`, con `canal="pantalla"`, y es obligatorio en todo endpoint que entregue datos de una persona.

## 2. Modelos

```python
class Servicio(ModeloBase):
    nodo    = models.ForeignKey("catalogo.Nodo", related_name="servicios", on_delete=models.PROTECT)
    slug    = models.SlugField(unique=True)
    nombre  = models.CharField()
    tareas  = models.JSONField(default=list)     # "Buscar el código de una comuna"
    estado  = models.CharField(...)              # disponible | en_desarrollo | sin_servicio
    nota    = models.TextField(blank=True)
```

`estado` describe la pantalla, no la fuente. La disponibilidad de la fuente la mide el monitor (HR-09) y la frescura del dato la informa el adaptador.

## 3. Endpoints

Dos familias, y conviene no mezclarlas.

**El catálogo de servicios**, público:

| Método y ruta | Qué hace |
|---|---|
| `GET /api/v1/servicios` | Los servicios de nodos `publicados()` |
| `GET /api/v1/servicios/{slug}` | Uno, con sus tareas y su estado |

**Las consultas que entregan datos**, autenticadas, una por tarea:

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/servicios/cut/buscar?q=` | público | Busca por nombre de región, provincia o comuna |
| `GET /api/v1/servicios/cut/codigo/{codigo}` | público | El camino inverso: código a unidad territorial |
| `GET /api/v1/servicios/permisos/{patente}` | autenticado con perfil | El permiso de circulación de una patente |

El CUT es público porque es dato abierto, y no escribe `Acceso`: no entrega datos de nadie. Los permisos de circulación **no**: requieren perfil activo, exigen la cabecera `X-Procedimiento` y escriben `cuentas.Acceso`. Sin esa cabecera, `400` con código `PROCEDIMIENTO_REQUERIDO` — para que nadie consulte «porque sí».

Un perfil con municipio ve lo que su trámite necesita; **que haya o no restricción por municipio en los permisos de circulación es una pregunta para jurídica**, no una decisión de implementación. Hasta que se responda, se registra todo acceso y no se restringe por municipio, y la pantalla dice que la consulta queda registrada.

## 4. Degradación honesta

Es el patrón que la maqueta ya resolvió y hay que portarlo, no reinventarlo:

- Se intenta la fuente. Si responde, se entrega el dato.
- Si no responde, se entrega la **muestra sintética, diciéndolo en la respuesta** con un campo explícito, para que la pantalla lo muestre en pantalla.
- Nunca una pantalla en blanco, nunca datos de muestra sin aviso.

Una pantalla que se queda en blanco no se puede mostrar en una reunión; una que finge datos sin avisar es peor.

## 5. Pruebas mínimas

1. `GET /servicios` no devuelve servicios de nodos ocultos.
2. Consultar un permiso sin perfil activo da `403`; sin `X-Procedimiento` da `400`.
3. Cada consulta exitosa de permisos escribe exactamente un `cuentas.Acceso` con el perfil, la patente y el procedimiento, y **sin** la respuesta.
4. Con la fuente caída, la respuesta trae datos de muestra y el campo que lo declara.
5. El buscador del CUT funciona en los dos sentidos y devuelve códigos canónicos.
6. Una patente mal formada se rechaza antes de llamar a la fuente.

## 6. Qué no implementar

- Ninguna pantalla que llegue a datos que la API no exponga. Nadie tiene atajos, y eso incluye a estas vistas.
- Ninguna consulta masiva, exportación ni descarga de listados de personas.
- Ningún almacenamiento de las respuestas.
- Ninguna búsqueda por nombre de persona o por RUT. La entrada es la patente.
