# `core` — base compartida

Lee primero [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

Lo que comparten las demás aplicaciones. No tiene endpoints propios salvo el de salud.

**`core` no depende de ninguna otra aplicación del proyecto**: ninguna clave foránea ni importación hacia afuera. Es lo que permite construirla primero y probarla sola.

---

## Modelos

### `ModeloBase` (abstracto)

```python
class ModeloBase(models.Model):
    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
```

Todo modelo del proyecto hereda de acá. Nada de `id` propio: la clave es la de Django.

### `Municipio`

Dato de referencia territorial, no de dominio: lo usan `cuentas` (perfiles y réplica), `catalogo` (listados) y `servicios`. Vive acá, junto a `canonico`, para que `cuentas` no dependa de `catalogo`.

```python
class Municipio(ModeloBase):
    cut    = models.CharField(unique=True, max_length=5)   # canónico, con ceros
    nombre = models.CharField()
    # 346 comunas, 345 municipalidades. Carga inicial por migración de datos desde el CUT.
```

La carga inicial es una migración de datos, no un *script* suelto, y pasa cada código por `canonico`.

La región y la provincia **no** son tablas: se deducen del código (`municipio.region` es `cut[:2]`, `municipio.provincia` es `cut[:3]`). Guardarlas sería una segunda copia de lo que sirve `AdaptadorCUT` en vivo, y agregarlas después, si aparece un perfil con alcance regional, es una migración sin tocar `Municipio`.

### La foto del CUT

La migración no llama a la red: lee una **foto versionada** de la fuente, en `apps/core/datos/`.

| Archivo | Contenido |
|---|---|
| `regiones.json` · `provincias.json` · `comunas.json` | `{"fuente": url, "descargado_en": fecha, "datos": [...]}`, tal como los entregó la fuente |

- **De dónde sale.** De la API del CUT de SEM, hoy su ambiente de *staging* (`https://stag-api.sem2.gob.cl/api/utilitarios`), que es réplica de la real. Cuando haya acceso a la de producción, se regenera desde ahí.
- **Cómo se regenera.** `python manage.py descargar_cut`, que lee `CUT_API_URL` (o `--url`). Descarga los tres listados, los valida —lista no vacía, sin códigos repetidos, con `nombre`— y solo entonces reescribe los tres archivos. Se ejecuta a mano y el resultado se revisa en un commit, como cualquier cambio.
- **Por qué se versiona, si `insumos/` no se versiona.** `insumos/` es material de terceros que no es nuestro publicar. Esto es **dato abierto, sin datos personales**, y el catálogo tiene que poder decir de dónde salió cada municipio y en qué fecha. Es una excepción declarada, no un precedente: nada con datos de personas entra en `datos/`.
- **Los nombres van tal como vienen**, aunque la fuente escriba «Los Alamos» o «Los Angeles» sin tilde. El catálogo es copia fiel; corregir es pedirle a la fuente que corrija.
- Las tres fotos se cargan aunque hoy solo se use `comunas.json`: con las otras dos se prueba la jerarquía, y servirán de respuestas grabadas para las pruebas de `AdaptadorCUT`.

`Acceso` y `Bitacora` **no** viven acá: apuntan a `Perfil`, y eso haría depender `core` de `cuentas`. Están en [`../cuentas/INSTRUCCIONES.md`](../cuentas/INSTRUCCIONES.md) §5.

---

## Utilidades

### `canonico(codigo, nivel)`

El relleno del Código Único Territorial. Está acá porque lo usan `core.Municipio`, `integraciones` y `catalogo` y no puede estar duplicado.

```python
LARGO = {"region": 2, "provincia": 3, "comuna": 5}
# canonico(1101, "comuna") -> "01101"
```

Función pura, sin acceso a base de datos. Rechaza un código más largo que su nivel; no rechaza uno más corto, lo rellena. Su explicación para humanos vive en la entrada de wiki del CUT.

### Manejador de errores de DRF

El sobre único de la sección 6 del archivo raíz, en `errores.py`. Cualquier excepción no prevista sale como `ERROR_INTERNO` con mensaje genérico — **nunca** con la traza; la traza va al log.

| Excepción | Código |
|---|---|
| `ValidationError` | `VALIDACION_FALLIDA`, con `detalles` como lista de `{campo, mensaje}` |
| `NotFound`, `Http404` | `NO_ENCONTRADO` |
| `PermissionDenied` | `PERMISO_DENEGADO` |
| `NotAuthenticated`, `AuthenticationFailed` | `NO_AUTENTICADO` |
| Subclases de `ErrorNodo` | El `codigo`, `mensaje` y `status` que declare la subclase |

**`ErrorNodo` es la base de toda excepción propia del proyecto.** Las de `integraciones` (`FuenteNoDisponible`, `NoEncontrado`…) y la `CampoDeFicha` de `catalogo` heredan de ella y declaran su código; así `core` no importa nada de esas apps. Las rutas que no existen fuera de DRF responden el mismo sobre (`handler404` y `handler500`).

### Cabeceras de contexto

Un *middleware* que lee `X-Procedimiento` y `X-Id-Tramite` y los deja en el objeto de petición, para que las vistas no los parseen cada una. No valida que existan: eso lo decide cada endpoint.

Las dos cabeceras van en `CORS_ALLOW_HEADERS`, junto con las por defecto de `django-cors-headers`. Si no, el navegador las bloquea en la petición previa y el endpoint nunca las ve.

### `X-Robots-Tag`

Un *middleware* propio que agrega `X-Robots-Tag: noindex, nofollow` a toda respuesta cuando `NODO_OCULTO=1`. Django no trae un ajuste para esto. Va en el backend y no en el proxy para que el comportamiento no dependa de cómo informática configure lo que esté delante.

### `/api/v1/salud`

Endpoint sin autenticación que responde `{"estado": "ok", "version": "<versión del despliegue>"}`, con la versión desde `VERSION_DESPLIEGUE`. Sin detalles de infraestructura, sin estado de la base, sin nombres de servidores. Está exento de la redirección a HTTPS de `prod.py`, para que un chequeo interno por HTTP funcione.

---

## Pruebas mínimas

1. `canonico` rellena con ceros en los tres niveles y rechaza códigos demasiado largos.
2. El manejador de errores devuelve el sobre con `codigo`, `mensaje` y `detalles` para una validación fallida.
3. Una excepción no prevista no filtra la traza ni el mensaje original.
4. La migración de datos deja los 346 códigos de comuna en `Municipio`, en forma canónica, con ceros.
5. `/salud` responde sin token.
6. Con `NODO_OCULTO=1` toda respuesta lleva `X-Robots-Tag`; con `NODO_OCULTO=0`, ninguna.
7. Una petición previa de CORS con `X-Procedimiento` desde un origen permitido es aceptada.
8. La foto del CUT es coherente: 16 regiones, 56 provincias y 346 comunas; toda comuna cae en una provincia y toda provincia en una región, sin provincias ni regiones vacías.

## Qué no implementar

- Ninguna lógica de dominio. Si algo sabe qué es un permiso de circulación, no va acá. `Municipio` es la única excepción, y es dato de referencia.
- Ninguna clave foránea hacia otra aplicación del proyecto.
- Ninguna función de presentación.
- Ninguna tarea programada. La sincronización vive en `registro`.
