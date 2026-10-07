# `registro` — fuentes, lecturas y sincronización

Lee primero [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md) y el [estándar de la ficha de servicio](../../../docs/estandar-ficha-de-servicio.md), que define el archivo que esta aplicación lee y valida. El camino completo está dibujado en [`esquemas-de-repositorios.html`](../../../docs/esquemas-de-repositorios.html), tercer esquema.

Esta aplicación es la razón por la que el catálogo no se escribe a mano.

---

## 1. Modelos

```python
class Fuente(ModeloBase):
    tipo       = models.CharField(...)          # repositorio | carga_manual
    url        = models.URLField(blank=True)
    rama       = models.CharField(default="main")
    ruta_ficha = models.CharField(default="nodo/ficha.yaml")
    activa     = models.BooleanField(default=True)

class Lectura(ModeloBase):
    fuente    = models.ForeignKey(Fuente, related_name="lecturas", on_delete=models.PROTECT)
    commit    = models.CharField(blank=True)
    contenido = models.TextField(blank=True)    # el YAML tal como se leyó
    valida    = models.BooleanField()
    motivo    = models.TextField(blank=True)
```

`Lectura` **solo crece**: no se edita ni se borra. Guardar el YAML tal cual permite reconstruir la proyección si el modelo cambia, sin volver a pedirle nada al repositorio, y permite decir de qué *commit* salió cada ficha publicada.

**La carga manual existe solo para la transición**, cuando un responsable todavía no tiene repositorio. Se sube el archivo, se valida igual, y el catálogo marca que esa ficha no tiene fuente verificable. **No es un atajo para editar a mano una ficha que sí tiene repositorio.**

**El traspaso de custodia es un cambio de `url`, no un servicio nuevo.** Cuando el dueño de una fuente aloje el contrato junto a su servicio, se cambia la dirección de la `Fuente` y el historial de lecturas muestra cuándo se movió. Funciona porque el identificador de la ficha es inmutable. Está en el [ADR de acceso directo](../../../docs/adr-2026-10-acceso-directo-primera-etapa.md) §6.

## 2. Lectura

Un cliente que lee un archivo de un repositorio por su API, con un token de **solo lectura**. El token entra por variable de entorno; su emisión, alcance y rotación son **HR-22**.

Implementar detrás de una interfaz pequeña —`leer(fuente) -> (commit, contenido)`— con una implementación para GitLab y otra falsa para las pruebas. Las pruebas **no** salen a la red.

## 3. Validación

En este orden, y la primera que falla detiene el resto:

1. El archivo es YAML válido y `ficha` es una versión conocida. Si no la conoce, **rechaza en vez de adivinar**.
2. Están todos los campos obligatorios, y los de lista cerrada traen un valor de la lista.
3. `id` no está tomado por otro nodo ni por un `Alias`.
4. `especificacion.archivo` existe en el mismo *commit* y se puede parsear.
5. `especificacion.version` coincide con el `info.version` del archivo. Atrapa el error más común: publicar una versión y declarar otra.
6. `responsable.correo` es institucional.
7. **La ficha no trae datos personales** más allá del contacto institucional. Sin excepciones: en este repositorio ya quedó versionado un archivo con nombre y RUT reales.

Cada falla produce una `Lectura` con `valida=False` y un `motivo` **en español y específico**: qué campo, qué se esperaba. Ese motivo lo va a leer la persona que escribió la ficha.

## 4. Sincronización

Comando de gestión `sincronizar_fuentes`, que corre por tarea programada y también desde el botón «resincronizar» de la administración.

Para cada fuente activa: lee, valida, proyecta sobre `catalogo.Nodo` y `catalogo.Especificacion`, y crea la `Lectura`.

La proyección guarda con `nodo.save(desde_sincronizacion=True)`, objeto por objeto. Es el único lugar del proyecto que usa ese argumento, y no se usa `update()` ni `bulk_update()` sobre campos de ficha: el `QuerySet` de `Nodo` los rechaza (ver `catalogo` §1).

**Cuando la lectura falla, no se borra ni se despublica nada.** Queda la `Lectura` inválida con su motivo, la proyección anterior sigue vigente, y la API informa de cuándo es la última lectura buena. Es el mismo patrón de degradación honesta de las pantallas de servicio.

La proyección es **idempotente**: sincronizar dos veces el mismo *commit* no cambia nada ni genera ruido en `Bitacora`.

Una ficha nueva entra como `oculto`. Publicarla es una decisión editorial de un curador, cuando el servicio cumple el criterio de entrada: contrato, pantalla, entrada de wiki y servicio disponible.

## 5. Endpoints

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/fuentes` | lector | Lista, con su última lectura |
| `POST /api/v1/fuentes` | administrador | Registra una dirección. Lee y valida en el acto, y devuelve el resultado |
| `PATCH /api/v1/fuentes/{id}` | administrador | Cambia dirección, rama o ruta. Es el traspaso de custodia. Deja `Bitacora` |
| `POST /api/v1/fuentes/{id}/sincronizar` | curador | Vuelve a leer ahora |
| `GET /api/v1/fuentes/{id}/lecturas` | lector | El historial, con *commit*, fecha, validez y motivo |

En la respuesta de `GET /api/v1/nodos/{id}` el frontend necesita saber de cuándo es la ficha: incluir `leida_en` y `commit` de la última lectura válida.

## 6. Pruebas mínimas

1. Una ficha válida crea el nodo como `oculto` y su especificación vigente.
2. Una versión de estándar desconocida se rechaza con motivo, sin tocar la proyección.
3. Una versión declarada que no coincide con la del archivo se rechaza nombrando las dos.
4. Un `id` ya tomado se rechaza.
5. Un fallo de red deja `Lectura` inválida y **no** modifica el nodo publicado.
6. Sincronizar el mismo *commit* dos veces no genera cambios ni entradas de bitácora.
7. Cambiar la `url` de una fuente conserva el nodo y su identificador.
8. Ninguna prueba sale a la red.

## 7. Qué no implementar

- Escritura hacia los repositorios. Solo lectura, siempre.
- Recepción de avisos desde los repositorios. El modelo es jalar, no recibir. Está decidido en el ADR de estructura.
- Edición del contenido de una ficha desde la administración.
- Borrado de lecturas, ni «limpieza» del historial.
