# `cuentas` — identidad, perfiles y registro de actuaciones

Lee primero [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

Resuelve quién es la persona, qué puede hacer y qué hizo. **Keycloak autentica; esta aplicación autoriza y registra.**

Depende solo de `core`. Ninguna clave foránea hacia `catalogo` ni hacia otra aplicación posterior.

---

## 1. Qué resuelve y qué no

| Resuelve | No resuelve |
|---|---|
| Validar el token del realm de Keycloak y resolver el perfil | Autenticar. Eso lo hace el realm, que federa Clave Única |
| Qué puede hacer cada persona en el nodo | Administrar los usuarios de un municipio. Eso lo hace su encargado |
| Mantener una réplica del registro de cada municipio, para visualización | Ser la fuente de verdad de ese registro. La fuente es del municipio |

## 2. Autenticación

Clase de autenticación de DRF que valida el *access token*: firma contra el JWKS del realm, `iss`, `aud`, expiración. Dependencia: `PyJWT` con `cryptography`.

El JWKS se guarda en el caché de Django (`django.core.cache`), por `KEYCLOAK_JWKS_CACHE_SEGUNDOS`. Con varios procesos de `gunicorn` y caché en memoria, cada proceso pide el JWKS una vez por ventana: es aceptable, y no justifica Redis por sí solo. Ante un `kid` desconocido se vuelve a pedir el JWKS **una vez**; si el `kid` sigue sin aparecer, `401`. Así una rotación de claves en el realm no deja a nadie afuera, y un token inventado no provoca una descarga por petición.

Del token se toman el `sub`, el RUN y el nombre. **Nada más.** No se copian *claims* del realm a nuestra base «por si acaso».

Si el token es válido pero no hay perfil activo, la respuesta es `403` con código `SIN_PERFIL`, no `401`. La distinción importa: la persona se autenticó bien, simplemente no tiene nada que hacer acá.

## 3. Modelos

```python
class Perfil(ModeloBase):
    sub      = models.CharField(unique=True)        # el subject del realm
    run      = models.CharField(unique=True)
    nombre   = models.CharField()
    rol      = models.CharField(...)                # lector | editor | curador | administrador
    municipio = models.ForeignKey("core.Municipio", null=True, blank=True, on_delete=models.PROTECT)
    activo   = models.BooleanField(default=True)
```

| Rol | Puede |
|---|---|
| `lector` | Ver la administración, sin cambiar nada |
| `editor` | Escribir y publicar entradas de wiki |
| `curador` | Publicar, ocultar y retirar servicios; resincronizar fuentes |
| `administrador` | Registrar y dar de baja fuentes; administrar perfiles |

`municipio` nulo significa persona de SUBDERE. Con municipio, es funcionaria o funcionario municipal y solo ve lo de su municipio en las vistas de uso humano.

**Los permisos se expresan como permisos de DRF por rol, no con `if` repartidos en las vistas.** Una clase por rol, y las vistas la declaran.

## 4. El encargado municipal y la réplica

Cada municipalidad designa un **encargado**. Él administra a su gente; nosotros **no**. Lo que mantenemos es una **réplica del registro interno de cada municipio, para visualización**: saber quién está habilitado, por municipio, sin ser la autoridad sobre esa lista.

```python
class EncargadoMunicipal(ModeloBase):
    municipio = models.ForeignKey("core.Municipio", on_delete=models.PROTECT)
    nombre    = models.CharField()
    correo    = models.EmailField()          # institucional
    vigente   = models.BooleanField(default=True)

class PersonaReplicada(ModeloBase):
    municipio   = models.ForeignKey("core.Municipio", on_delete=models.PROTECT)
    nombre      = models.CharField()
    run         = models.CharField()
    cargo       = models.CharField(blank=True)
    habilitado  = models.BooleanField(default=True)
    informado_en = models.DateField()        # cuándo nos lo informó el municipio
    origen      = models.CharField(...)       # carga_manual | realm
```

Reglas:

- **`PersonaReplicada` es para visualización, no para autorizar.** Quien autoriza es `Perfil`. Si alguna vez una vista consulta `PersonaReplicada` para decidir un permiso, se rompió la separación y la réplica pasó a ser fuente de verdad sin que nadie lo decidiera.
- La réplica se muestra siempre **con la fecha en que el municipio la informó**. Una lista sin fecha miente.
- `run` acá es dato personal con una finalidad acotada: saber a quién habilitó cada municipio. No se usa para nada más y no se expone en endpoints públicos.
- **Dónde administra el encargado es HR-27**: en la consola del realm, o en una pantalla nuestra que escriba en el realm. Mientras no se decida, la réplica entra por carga manual y `origen` lo registra.

## 5. Registro de actuaciones: `Acceso` y `Bitacora`

Viven acá porque los dos responden «qué hizo este perfil», y porque así ni `core` depende de `cuentas` ni `cuentas` depende de `catalogo`. Las demás aplicaciones escriben en ellos a través de dos funciones de este módulo, `registrar_acceso(...)` y `registrar_bitacora(...)`, no creando los objetos directamente.

### `Acceso`

El registro de quién consultó qué. Es el único lugar donde esto se guarda.

```python
class Acceso(ModeloBase):
    perfil        = models.ForeignKey(Perfil, null=True, on_delete=models.PROTECT)
    canal         = models.CharField(...)      # api | pantalla
    nodo          = models.CharField()         # identificador del nodo; es inmutable, no hace falta clave foránea
    operacion     = models.CharField(...)      # p. ej. consultar_permiso_por_patente
    parametros    = models.JSONField(default=dict)   # qué se consultó, sin la respuesta
    procedimiento = models.CharField(blank=True)     # de la cabecera X-Procedimiento
    id_tramite    = models.CharField(blank=True)
    resultado     = models.CharField(...)      # encontrado | no_encontrado | error
```

Reglas:

- **Qué se registra.** Toda consulta que entregue **datos de una persona** —hoy, los permisos de circulación—. Las consultas a datos abiertos sin datos personales, como el CUT, no escriben `Acceso`: registrarlas no protege a nadie y llena la tabla de ruido.
- **Solo crece.** Sin `update` ni `delete`; no se expone en el admin con permiso de edición.
- **Nunca guarda la respuesta.** `parametros` lleva lo justo para saber qué se preguntó: una patente. Si alguna vez hace falta guardar más, es una decisión de datos personales, no de implementación.
- `perfil` es nulo solo cuando la consulta es anónima contra un ambiente con datos sintéticos. En producción toda consulta que escribe `Acceso` exige perfil activo.
- Cuánto tiempo se conserva y quién lo revisa es **HR-28**. Hasta que se resuelva, no se borra nada.

### `Bitacora`

Las acciones editoriales: publicar, ocultar, retirar, registrar una fuente, editar una entrada de wiki, crear o modificar un perfil.

```python
class Bitacora(ModeloBase):
    perfil  = models.ForeignKey(Perfil, null=True, on_delete=models.PROTECT)
    accion  = models.CharField(...)
    objeto  = models.CharField(...)        # "catalogo.Nodo:cut"
    antes   = models.JSONField(default=dict)
    despues = models.JSONField(default=dict)
    nota    = models.TextField(blank=True)
```

Solo crece, igual que `Acceso`. `perfil` es nulo cuando la acción la hace la sincronización o un superusuario local desde el admin; en ese caso `nota` dice cuál de los dos. Un catálogo que se presenta como auditable necesita poder mostrar su propia historia, no solo la de los contratos que publica.

**Cómo se garantiza que solo crecen:** `save()` levanta excepción si el objeto ya tiene clave primaria, `delete()` levanta excepción siempre, y el *manager* devuelve un `QuerySet` cuyos `update()`, `delete()` y `bulk_update()` también la levantan. El admin los muestra en solo lectura.

## 6. Endpoints

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/yo` | autenticado | Devuelve el perfil propio: nombre, rol, municipio. Es lo que el frontend llama al entrar |
| `GET /api/v1/perfiles` | administrador | Lista y filtra |
| `POST /api/v1/perfiles` · `PATCH /api/v1/perfiles/{id}` | administrador | Crear y modificar. Deja `Bitacora` |
| `GET /api/v1/municipios/{cut}/personas` | lector de SUBDERE, o perfil de ese municipio | La réplica, con su fecha de informe |

No hay endpoint de alta propia. No hay recuperación de contraseña: no guardamos contraseñas.

## 7. Pruebas mínimas

1. Un token con firma inválida, `aud` equivocado o expirado da `401`.
2. Un token válido sin perfil activo da `403` con código `SIN_PERFIL`.
3. Un `curador` no puede crear perfiles; un `administrador` sí.
4. Un perfil con municipio no ve la réplica de otro municipio.
5. Crear o modificar un perfil escribe en `Bitacora` con el antes y el después.
6. El JWKS se refresca ante un `kid` desconocido, una sola vez, y no en cada petición.
7. `Acceso` y `Bitacora` no se pueden modificar ni borrar: ni por `save()`, ni por `delete()`, ni por `update()` sobre un `QuerySet`.

## 8. Qué no implementar

- Vistas de login, logout ni registro en el backend. El flujo es del frontend contra el realm.
- Sesiones de Django para la API.
- Sincronización automática con el realm. Hasta HR-27, la réplica entra a mano.
- Ningún permiso basado en el correo o en el dominio del correo.
