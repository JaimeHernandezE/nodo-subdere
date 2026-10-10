# `integraciones` — adaptadores a las fuentes externas

> **Construida.** Este archivo registra las decisiones y los límites de la aplicación; el código es la fuente de los detalles. Antes de cambiar algo de lo que dice acá, leer por qué está así. Contrato común en [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

La decisión de la primera etapa está en el [ADR de acceso directo](../../../docs/adr-2026-10-acceso-directo-primera-etapa.md).

Los adaptadores hacia APIs que no son nuestras. Hoy dos: el **CUT** y los **permisos de circulación**, los dos en su fuente en SEM.

Depende de `core` y `cuentas`. **No tiene modelos, migraciones ni endpoints propios**: es una biblioteca que usa `servicios`, que es quien expone las consultas.

## Dónde está cada cosa

| Pieza | Archivo |
|---|---|
| `AdaptadorCUT`, `Region`, `Provincia`, `Comuna` y la caída a la foto | `cut.py` |
| `AdaptadorPermisos`, `Contexto`, las dataclasses del contrato y el registro de accesos | `permisos.py` |
| La muestra sintética de permisos | `muestras/permisos.json` |
| La única salida HTTP: tiempo de espera, reintento, límite de 1 MB, mapeo de errores | `cliente.py` |
| `Respuesta` y `Origen` (`fuente`, `foto`, `muestra`) | `respuesta.py` |
| Normalizar y validar patentes | `patente.py` |
| `FuenteNoDisponible`, `ParametroInvalido`, `NoEncontrado`, `RespuestaDemasiadoGrande` | `errores.py` |
| Settings: `CUT_API_URL`, `CUT_CACHE_SEGUNDOS`, `PERMISOS_CIRCULACION_API_URL`, `PERMISOS_CIRCULACION_CACHE_SEGUNDOS`, `INTEGRACIONES_TIEMPO_ESPERA_SEGUNDOS`, `CACHES` | `config/settings/base.py` |

---

## 1. Cada adaptador hace tres cosas y ninguna más

1. **Llama** a la API de origen por su interfaz pública, la misma que usaría cualquier otro consumidor.
2. **Normaliza** lo que devuelve. El caso concreto: el CUT entrega los códigos como entero y acá se rellenan a su forma canónica con `core.cut.canonico`.
3. **Cachea** por un tiempo corto y declarado, para no castigar al servicio de origen.

**Lo que no hacen:** guardar los datos en la base, enriquecerlos con información propia, ni exponer nada que la API de origen no exponga. **Si a un adaptador le aparecen tablas, se convirtió en un registro paralelo** — que es exactamente lo que el proyecto decidió no construir.

El caché es el de Django (`LocMemCache`, uno por proceso), nunca tablas del modelo. Si el nodo llega a correr en varias instancias, se cambia a Redis en `CACHES`, sin tocar los adaptadores. **La duración es del nodo que consume, no del servicio**: se declara por variable de entorno (`CUT_CACHE_SEGUNDOS`, `PERMISOS_CIRCULACION_CACHE_SEGUNDOS`), no en la ficha, que es del dueño del servicio y no tiene ese campo. Lo que sí viaja es **de dónde y de cuándo es cada respuesta** (§2).

## 2. Forma de un adaptador

Una clase por fuente, con una interfaz chica y tipada. Sin estado entre llamadas, salvo el caché.

```python
class AdaptadorCUT:
    def regiones(self) -> Respuesta[list[Region]]: ...
    def provincias(self, region: str | None = None) -> Respuesta[list[Provincia]]: ...
    def comunas(self, provincia: str | None = None) -> Respuesta[list[Comuna]]: ...
    def por_codigo(self, codigo: str) -> Respuesta[Region | Provincia | Comuna]: ...
    def buscar(self, texto: str) -> Respuesta[list[Region | Provincia | Comuna]]: ...

class AdaptadorPermisos:
    def vehiculo(self, patente: str, contexto: Contexto) -> Respuesta[Vehiculo]: ...
    def permisos(self, patente: str, contexto: Contexto, desde_anio: int | None = None) -> Respuesta[list[Permiso]]: ...
    def provisionales(self, patente: str, contexto: Contexto) -> Respuesta[list[PermisoProvisional]]: ...
```

La interfaz de permisos sigue las tres operaciones del contrato propuesto, [`fiscalizacion.openapi.yaml`](../../../prototipos/estandares/fiscalizacion.openapi.yaml): el vehículo, sus permisos y los permisos provisionales. **`PR` y cuatro dígitos calza con los dos patrones del contrato**: es una provisoria y también la forma antigua de dos letras y cuatro dígitos. El contrato no lo resuelve; el adaptador expone las dos operaciones y `servicios` decide cuál consulta: la trata como provisoria (`servicios` §3). Es una observación para la wiki del contrato.

Los nombres de las operaciones en `Acceso` son `consultar_vehiculo`, `consultar_permisos` y `consultar_permisos_provisionales`, con `nodo="permisos-de-circulacion"`. Una patente mal formada no deja acceso: se rechaza antes de llegar a datos de nadie.

Devuelven objetos propios (`dataclass`), **no** el JSON crudo del origen. Así un cambio de forma en el origen se absorbe en un lugar. Todos van envueltos en `Respuesta`, con `datos`, `origen` —`fuente`, `foto` o `muestra`— y `obtenido_en`. Ese es el campo explícito con que la pantalla avisa que no está viendo la fuente en vivo.

**Jerarquía del CUT.** La fuente entrega cada nivel con su código y su nombre, nada más. La jerarquía sale del código canónico: la provincia `011` es de la región `01`, la comuna `01101` es de la provincia `011`. `por_codigo` decide el nivel por el largo: uno o dos dígitos es región, tres es provincia, cuatro o cinco es comuna. `buscar` compara sin tildes ni mayúsculas: «nunoa» encuentra «Ñuñoa».

La URL base y el tiempo de caché de cada adaptador entran por variable de entorno, una por ambiente. Las credenciales, si llegan a existir, también: **nunca en el código ni en el repositorio.**

## 3. Reglas que vienen de la disciplina de contrato de PISEE

Están en el ADR de acceso directo §3, y se construyen desde ya para que migrar a la Red sea configuración:

- **Consulta y respuesta sincrónica.** Nada asincrónico, nada de webhooks. PISEE no los tiene.
- **Un identificador de trámite por transacción.** Viaja hacia la fuente en `X-Id-Tramite`, junto con `X-Procedimiento`, y queda en `Acceso`. **Las consultas no se deduplican por él**: cada lectura de datos de una persona es un acceso, también un reintento. Es lo más conservador para auditar. La idempotencia se aplica cuando haya operaciones que escriben.
- **Un límite de tamaño de respuesta**: 1 MB, en el código. Lo que lo exceda se rechaza con `RESPUESTA_DEMASIADO_GRANDE` en vez de descubrirlo en producción. Declararlo en los contratos es X-122.
- **Los metadatos de identidad y trazabilidad viajan igual por el camino directo.** El adaptador de permisos **exige** un `Contexto` —quién pregunta, por qué canal, la petición con su procedimiento y trámite— y **él mismo** registra cada consulta con `cuentas.registrar_acceso`: también cuando la respuesta sale del caché, cuando la patente no existe y cuando la fuente falla. Así ningún llamador, presente o futuro, puede entregar datos de una persona sin dejar registro. Quién es la persona **no** se acepta como parámetro: se deduce del token. Su identidad queda en `Acceso` y no viaja a SEM: en la primera etapa fuente y consumidor son el mismo órgano.

## 4. Errores

Excepciones propias, que heredan de `ErrorNodo` y `core` traduce al sobre único:

| Excepción | Estado | Código |
|---|---|---|
| `FuenteNoDisponible` | 503 | `FUENTE_NO_DISPONIBLE` |
| `ParametroInvalido` | 400 | `PATENTE_INVALIDA` o `CODIGO_INVALIDO` |
| `NoEncontrado` | 404 | `NO_ENCONTRADO` |
| `RespuestaDemasiadoGrande` | 502 | `RESPUESTA_DEMASIADO_GRANDE` |

Distinguir **fuente caída** de **dato no encontrado** es obligatorio: son cosas distintas para quien consulta, y confundirlas es el error más común de un adaptador. Un `404` de la fuente es `NoEncontrado`; la red, un `5xx`, un `401` o un `403` son `FuenteNoDisponible`.

**No hay `NO_AUTORIZADO`.** Que la fuente rechace la credencial del nodo es un problema de configuración del nodo, no de quien consulta: se informa como fuente no disponible y queda en el log. La autenticación de la persona ya la cubren `NO_AUTENTICADO` y `PERMISO_DENEGADO` de `core`.

Tiempo de espera corto y explícito (`INTEGRACIONES_TIEMPO_ESPERA_SEGUNDOS`), con un reintento como máximo, y solo ante una falla de red o un `5xx`. Un adaptador que se cuelga, cuelga la pantalla.

## 5. Cuando la fuente no está

Cada adaptador degrada distinto, porque sus datos no pesan lo mismo:

| | Sin URL configurada | Fuente caída |
|---|---|---|
| **CUT** | La foto versionada de `core` (`apps/core/datos/`), con `origen="foto"` y la fecha de `descargado_en` | Igual: la foto, diciéndolo |
| **Permisos** | La muestra sintética, con `origen="muestra"` | `503 FUENTE_NO_DISPONIBLE` |

- **El CUT cae a la foto** porque es dato real, abierto y fechado: mostrarlo con su fecha es honesto. **La caída se recuerda un minuto** (`RESPALDO_SEGUNDOS`), y vale para los tres listados: sin eso, con la fuente caída cada consulta esperaría el tiempo de espera y su reintento antes de caer, y la pantalla se colgaría igual. Comprobado el 10 de octubre de 2026, con el *staging* de SEM respondiendo `504` a los 30 segundos.
- **Permisos nunca cae a la muestra cuando hay fuente.** Mostrar datos inventados sobre una patente que sí existe es peor que decir que la fuente no responde. La muestra existe solo para un ambiente sin fuente, y lo dice en cada respuesta.

La muestra son **datos sintéticos de verdad**: patentes inventadas que pasan la validación de formato y RUT de empresa ficticios. **No datos reales con los nombres borrados.** Vive en `muestras/`, aparte, para poder borrarla de una vez cuando la fuente esté arriba.

## 6. Lo que las pruebas garantizan

Una fixture automática cierra `urllib.request.urlopen` y vacía el caché antes de cada prueba; las que necesitan una fuente la reemplazan por una falsa que anota cada pedido. El vencimiento del caché se prueba adelantando el reloj, no esperando.

1. Ninguna prueba sale a la red: los adaptadores se prueban contra respuestas grabadas —la foto de `core` para el CUT, los ejemplos del contrato para permisos—.
2. El CUT normaliza `1101` a `01101` en los tres niveles, y `buscar` encuentra sin tildes.
3. Una patente o un código con formato inválido fallan **antes** de llamar a la fuente.
4. Fuente de permisos caída da `FUENTE_NO_DISPONIBLE`; patente inexistente da `NO_ENCONTRADO`. No se confunden.
5. Fuente del CUT caída responde la foto, marcada.
6. El caché evita la segunda llamada dentro de su ventana, y la hace al expirar.
7. Cada consulta de permisos escribe exactamente un `cuentas.Acceso`, también desde el caché y cuando no encuentra nada. Las consultas al CUT no escriben ninguno.
8. Sin URL, permisos responde la muestra, marcada; sus patentes pasan el formato.
9. Una respuesta de más de 1 MB da `RESPUESTA_DEMASIADO_GRANDE`; un `401` de la fuente, `FUENTE_NO_DISPONIBLE`.

## 7. Qué no implementar

- Ningún modelo de Django. Esta aplicación **no tiene migraciones**.
- Ninguna agregación, estadística ni informe sobre los datos del origen.
- Ninguna consulta a la fuente que la pantalla no necesite.
- Ninguna copia de la respuesta más allá del caché declarado.
- Ningún respaldo con datos inventados cuando la fuente de permisos está configurada y cae.
