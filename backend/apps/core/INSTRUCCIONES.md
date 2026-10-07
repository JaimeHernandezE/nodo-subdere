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

El sobre único de la sección 6 del archivo raíz. Traduce `ValidationError`, `NotFound`, `PermissionDenied` y las excepciones propias de `integraciones` a códigos en MAYÚSCULA. Cualquier excepción no prevista sale como `ERROR_INTERNO` con mensaje genérico — **nunca** con la traza.

### Cabeceras de contexto

Un *middleware* que lee `X-Procedimiento` y `X-Id-Tramite` y los deja en el objeto de petición, para que las vistas no los parseen cada una. No valida que existan: eso lo decide cada endpoint.

Las dos cabeceras van en `CORS_ALLOW_HEADERS`, junto con las por defecto de `django-cors-headers`. Si no, el navegador las bloquea en la petición previa y el endpoint nunca las ve.

### `X-Robots-Tag`

Un *middleware* propio que agrega `X-Robots-Tag: noindex, nofollow` a toda respuesta cuando `NODO_OCULTO=1`. Django no trae un ajuste para esto. Va en el backend y no en el proxy para que el comportamiento no dependa de cómo informática configure lo que esté delante.

### `/salud`

Endpoint sin autenticación que responde `{"estado": "ok", "version": "<versión del despliegue>"}`. Sin detalles de infraestructura, sin estado de la base, sin nombres de servidores.

---

## Pruebas mínimas

1. `canonico` rellena con ceros en los tres niveles y rechaza códigos demasiado largos.
2. El manejador de errores devuelve el sobre con `codigo`, `mensaje` y `detalles` para una validación fallida.
3. Una excepción no prevista no filtra la traza ni el mensaje original.
4. La migración de datos deja los 346 códigos de comuna en `Municipio`, en forma canónica, con ceros.
5. `/salud` responde sin token.
6. Con `NODO_OCULTO=1` toda respuesta lleva `X-Robots-Tag`; con `NODO_OCULTO=0`, ninguna.
7. Una petición previa de CORS con `X-Procedimiento` desde un origen permitido es aceptada.

## Qué no implementar

- Ninguna lógica de dominio. Si algo sabe qué es un permiso de circulación, no va acá. `Municipio` es la única excepción, y es dato de referencia.
- Ninguna clave foránea hacia otra aplicación del proyecto.
- Ninguna función de presentación.
- Ninguna tarea programada. La sincronización vive en `registro`.
