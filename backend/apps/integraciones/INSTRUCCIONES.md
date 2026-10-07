# `integraciones` — adaptadores a las fuentes externas

Lee primero [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md). La decisión de la primera etapa está en el [ADR de acceso directo](../../../docs/adr-2026-10-acceso-directo-primera-etapa.md).

Los adaptadores hacia APIs que no son nuestras. Hoy dos: el **CUT** y los **permisos de circulación**, los dos en su fuente en SEM.

---

## 1. Cada adaptador hace tres cosas y ninguna más

1. **Llama** a la API de origen por su interfaz pública, la misma que usaría cualquier otro consumidor.
2. **Normaliza** lo que devuelve. El caso concreto: el CUT entrega los códigos como entero y acá se rellenan a su forma canónica con `core.canonico`.
3. **Cachea** por un tiempo corto y declarado, para no castigar al servicio de origen.

**Lo que no hacen:** guardar los datos en la base, enriquecerlos con información propia, ni exponer nada que la API de origen no exponga. **Si a un adaptador le aparecen tablas, se convirtió en un registro paralelo** — que es exactamente lo que el proyecto decidió no construir.

El caché es de memoria o Redis, nunca tablas del modelo. Y su duración se declara en la ficha del servicio, no se esconde en el código.

## 2. Forma de un adaptador

Una clase por fuente, con una interfaz chica y tipada. Sin estado entre llamadas, salvo el caché.

```python
class AdaptadorCUT:
    def regiones(self) -> list[Region]: ...
    def provincias(self, region: str | None = None) -> list[Provincia]: ...
    def comunas(self, provincia: str | None = None) -> list[Comuna]: ...
    def por_codigo(self, codigo: str) -> Region | Provincia | Comuna | None: ...

class AdaptadorPermisos:
    def por_patente(self, patente: str) -> Permiso | None: ...
```

Devuelven objetos propios (`dataclass`), **no** el JSON crudo del origen. Así un cambio de forma en el origen se absorbe en un lugar.

La URL base y el tiempo de caché de cada adaptador entran por variable de entorno, una por ambiente. Las credenciales, si llegan a existir, también: **nunca en el código ni en el repositorio.**

## 3. Reglas que vienen de la disciplina de contrato de PISEE

Están en el ADR de acceso directo §3, y se construyen desde ya para que migrar a la Red sea configuración:

- **Consulta y respuesta sincrónica.** Nada asincrónico, nada de webhooks. PISEE no los tiene.
- **Un identificador de trámite por transacción**, con idempotencia: un reintento no cuenta dos veces.
- **Un límite de tamaño de respuesta declarado** en el contrato. Rechazar lo que lo exceda con un código propio en vez de descubrirlo en producción (X-122).
- **Los metadatos de identidad y trazabilidad viajan igual por el camino directo.** El adaptador recibe el contexto —quién pregunta, por qué procedimiento— y, cuando entrega datos de una persona, lo registra con `cuentas.registrar_acceso`. Quién es la persona **no** se acepta como parámetro: se deduce del token.

## 4. Errores

Excepciones propias, que `core` traduce al sobre único:

| Excepción | Código |
|---|---|
| `FuenteNoDisponible` | `FUENTE_NO_DISPONIBLE` |
| `ParametroInvalido` | depende: `PATENTE_INVALIDA`, `CODIGO_INVALIDO` |
| `NoEncontrado` | `NO_ENCONTRADO` |
| `NoAutorizado` | `NO_AUTORIZADO` |

Distinguir **fuente caída** de **dato no encontrado** es obligatorio: son cosas distintas para quien consulta, y confundirlas es el error más común de un adaptador.

Tiempo de espera corto y explícito, con un reintento como máximo. Un adaptador que se cuelga, cuelga la pantalla.

## 5. Datos de muestra

Mientras la fuente no esté alcanzable, cada adaptador tiene un modo de muestra con **datos sintéticos de verdad**: patentes inventadas que pasen la validación de formato, RUT que no correspondan a nadie. **No datos reales con los nombres borrados.**

Los datos de muestra viven en archivos aparte y claramente nombrados, para poder borrarlos de una vez cuando las fuentes estén arriba. Y cuando un adaptador responde en modo muestra, **lo dice en la respuesta** con un campo explícito, para que la pantalla lo muestre y la ficha lo declare.

## 6. Pruebas mínimas

1. Ninguna prueba sale a la red: los adaptadores se prueban contra respuestas grabadas.
2. El CUT normaliza `1101` a `01101` en los tres niveles.
3. Una patente con formato inválido falla **antes** de llamar a la fuente.
4. Fuente caída da `FUENTE_NO_DISPONIBLE`; patente inexistente da `NO_ENCONTRADO`. No se confunden.
5. El caché evita la segunda llamada dentro de su ventana, y la hace al expirar.
6. Cada consulta que entrega datos de una persona escribe exactamente un `cuentas.Acceso`. Las consultas al CUT no escriben ninguno.
7. El modo muestra marca sus respuestas.

## 7. Qué no implementar

- Ningún modelo de Django. Esta aplicación **no tiene migraciones**.
- Ninguna agregación, estadística ni informe sobre los datos del origen.
- Ninguna consulta a la fuente que la pantalla no necesite.
- Ninguna copia de la respuesta más allá del caché declarado.
