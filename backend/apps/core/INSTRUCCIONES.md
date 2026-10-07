# `core` — base compartida

> **Construida.** Este archivo registra las decisiones y los límites de la aplicación; el código es la fuente de los detalles. Antes de cambiar algo de lo que dice acá, leer por qué está así. Contrato común en [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

Lo que comparten las demás aplicaciones. No tiene endpoints propios salvo el de salud.

**`core` no depende de ninguna otra aplicación del proyecto**: ninguna clave foránea ni importación hacia afuera. Es lo que permite construirla primero y probarla sola, y es la regla que más fácil se rompe por comodidad.

## Dónde está cada cosa

| Pieza | Archivo |
|---|---|
| `ModeloBase` (abstracto) y `Municipio` | `models.py` |
| `canonico(codigo, nivel)` | `cut.py` |
| Lectura de la foto del CUT | `foto_cut.py` · datos en `datos/` |
| `ErrorNodo` y el manejador de errores de DRF | `errores.py` |
| Cabeceras de contexto y `X-Robots-Tag` | `middleware.py` |
| `GET /api/v1/salud` | `api/v1/salud_view.py` |
| Regenerar la foto del CUT | `management/commands/descargar_cut.py` |
| Carga de los 346 municipios | `migrations/0002_cargar_municipios.py` |

---

## Decisiones

### `ModeloBase`

Todo modelo del proyecto hereda de él: `creado_en` y `actualizado_en`. Nada de `id` propio: la clave es la de Django.

### `Municipio` vive acá

Es dato de referencia territorial, no de dominio: lo usan `cuentas` (perfiles y réplica), `catalogo` (listados) y `servicios`. Si viviera en `catalogo`, `cuentas` dependería de una app que se construye después (`../../INSTRUCCIONES.md` §7).

Por la misma razón `Acceso` y `Bitacora` **no** viven acá: apuntan a `Perfil`, y eso haría depender `core` de `cuentas`. Están en [`../cuentas/INSTRUCCIONES.md`](../cuentas/INSTRUCCIONES.md) §5.

### Región y provincia no son tablas

Se deducen del código: `municipio.region` es `cut[:2]`, `municipio.provincia` es `cut[:3]`. Guardarlas sería una segunda copia de lo que sirve `AdaptadorCUT` en vivo, y tarde o temprano las dos se separan. Si aparece un perfil con alcance regional, agregarlas es una migración que no toca `Municipio`.

### La foto del CUT

La migración de carga **no llama a la red**: lee una foto versionada de la fuente, en `datos/` —`regiones.json`, `provincias.json` y `comunas.json`, cada una con `fuente`, `descargado_en` y los `datos` tal como llegaron—.

- **De dónde sale.** De la API del CUT de SEM, hoy su ambiente de *staging* (`https://stag-api.sem2.gob.cl/api/utilitarios`), que es réplica de la real. Cuando haya acceso a la de producción, se regenera desde ahí.
- **Cómo se regenera.** `python manage.py descargar_cut`, que lee `CUT_API_URL` (o `--url`). Solo reescribe si los tres listados se descargan y validan. Se ejecuta a mano y el resultado se revisa en un commit. Si cambian los códigos, hace falta además una migración de datos nueva: la `0002` ya corrió y no se edita.
- **Por qué se versiona, si `insumos/` no.** `insumos/` es material de terceros que no es nuestro publicar. Esto es **dato abierto, sin datos personales**, y el catálogo tiene que poder decir de dónde salió cada municipio y en qué fecha. Es una excepción declarada, no un precedente: nada con datos de personas entra en `datos/`.
- **Los nombres van tal como vienen**, aunque la fuente escriba «Los Alamos» o «Los Angeles» sin tilde. El catálogo es copia fiel; corregir es pedirle a la fuente que corrija.
- Se guardan los tres listados aunque solo se cargue `comunas.json`: con los otros dos se prueba la jerarquía, y servirán de respuestas grabadas para las pruebas de `AdaptadorCUT`.

### `canonico`

El relleno del Código Único Territorial (`1101` → `"01101"`). Está acá porque lo usan `Municipio`, `integraciones` y `catalogo`, y **no puede estar duplicado**: ninguna otra app rellena códigos por su cuenta. Función pura, sin base de datos. Rechaza un código más largo que su nivel; uno más corto lo rellena. Su explicación para humanos vive en la entrada de wiki del CUT.

### Errores: `ErrorNodo` y el sobre único

Toda respuesta de error sale con el sobre de `../../INSTRUCCIONES.md` §6. El manejador traduce las excepciones de DRF (`VALIDACION_FALLIDA`, `NO_ENCONTRADO`, `PERMISO_DENEGADO`, `NO_AUTENTICADO`…) y cualquier excepción no prevista sale como `ERROR_INTERNO` con mensaje genérico — **nunca** con la traza ni el mensaje original; la traza va al log. Las rutas inexistentes fuera de DRF responden el mismo sobre (`handler404`, `handler500`).

**Contrato con las demás apps:** toda excepción propia del proyecto hereda de `ErrorNodo` y declara su `codigo`, `mensaje` y `status`. Las de `integraciones` (`FuenteNoDisponible`, `NoEncontrado`…) y la `CampoDeFicha` de `catalogo` siguen esa forma. Así `core` traduce excepciones que no conoce, sin importar nada de esas apps.

### Cabeceras de contexto

El *middleware* deja `X-Procedimiento` y `X-Id-Tramite` en `request.procedimiento` y `request.id_tramite`, como cadena vacía si no vienen. **No valida que existan**: eso lo decide cada endpoint. Las dos cabeceras están en `CORS_ALLOW_HEADERS`; si se quitan, el navegador las bloquea en la petición previa y el endpoint nunca las ve.

### `X-Robots-Tag`

Se agrega a toda respuesta mientras `NODO_OCULTO=1`. Va en el backend y no en el proxy para que no dependa de cómo informática configure lo que esté delante. Quitarlo es una decisión consciente, no un ajuste.

### `/api/v1/salud`

Responde `{"estado": "ok", "version": ...}` sin token, con la versión desde `VERSION_DESPLIEGUE`. **Sin detalles de infraestructura, sin estado de la base, sin nombres de servidores**: es público y no le dice nada a quien sondea. Está exento de la redirección a HTTPS de `prod.py` para que un chequeo interno por HTTP funcione.

---

## Lo que las pruebas garantizan

En `tests/`. Si una de estas deja de cumplirse, se rompió una decisión de arriba:

1. `canonico` rellena en los tres niveles y rechaza códigos demasiado largos o que no son dígitos.
2. El manejador devuelve el sobre con `codigo`, `mensaje` y `detalles`, y una excepción no prevista no filtra la traza ni el mensaje original.
3. La migración deja los 346 municipios en forma canónica.
4. La foto del CUT es coherente: 16 regiones, 56 provincias y 346 comunas, sin huérfanos ni vacíos.
5. `/salud` responde sin token, y el esquema OpenAPI es público.
6. `X-Robots-Tag` aparece con `NODO_OCULTO=1` y con `0` no.
7. Una petición previa de CORS con `X-Procedimiento` desde un origen permitido es aceptada.
8. Swagger se sirve sin depender de un CDN.

## Qué no implementar

- Ninguna lógica de dominio. Si algo sabe qué es un permiso de circulación, no va acá. `Municipio` es la única excepción, y es dato de referencia.
- Ninguna clave foránea ni importación hacia otra aplicación del proyecto.
- Ninguna función de presentación.
- Ninguna tarea programada. La sincronización vive en `registro`.
- Ninguna tabla de regiones o provincias sin un caso que la necesite (ver arriba).
