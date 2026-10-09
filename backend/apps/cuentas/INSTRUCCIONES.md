# `cuentas` — identidad, perfiles y registro de actuaciones

> **Construida.** Este archivo registra las decisiones y los límites de la aplicación; el código es la fuente de los detalles. Antes de cambiar algo de lo que dice acá, leer por qué está así. Contrato común en [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

Resuelve quién es la persona, qué puede hacer y qué hizo. **Keycloak autentica; esta aplicación autoriza y registra.**

Depende solo de `core`. Ninguna clave foránea hacia `catalogo` ni hacia otra aplicación posterior.

## Dónde está cada cosa

| Pieza | Archivo |
|---|---|
| `Perfil`, `Rol`, `Acceso`, `Bitacora` y el `QuerySet` que solo crece | `models.py` |
| Validación del token y resolución del perfil; `AutenticacionOpcional` para rutas públicas | `autenticacion.py` |
| Emisor de tokens para desarrollo local | `emisor_local.py` · `management/commands/emitir_token_local.py` |
| `RolMinimo`, `GestionaEquipo`, `VeEquipo` | `permisos.py` |
| `registrar_acceso` y `registrar_bitacora` | `actuaciones.py` |
| `SinPerfil`, `RealmNoDisponible`, `PerfilExistente` | `errores.py` |
| Endpoints | `api/v1/` |
| Admin para superusuarios locales | `admin.py` |

---

## 1. Qué resuelve y qué no

| Resuelve | No resuelve |
|---|---|
| Validar el token del realm de Keycloak y resolver el perfil | Autenticar. Eso lo hace el realm, que federa Clave Única |
| Qué puede hacer cada persona en el nodo | Crear usuarios en el realm. Quien tenga Clave Única ya puede autenticarse; entrar depende del perfil |
| Los equipos de cada municipio: quién está habilitado, y quién lo administra | Decidir a quién habilita un municipio. Eso lo decide su encargado |

## 2. Autenticación

Clase de autenticación de DRF que valida el *access token*: firma contra el JWKS del realm, `iss`, `aud`, expiración. Dependencia: `PyJWT` con `cryptography`.

El JWKS se guarda en el caché de Django (`django.core.cache`), por `KEYCLOAK_JWKS_CACHE_SEGUNDOS`. Con varios procesos de `gunicorn` y caché en memoria, cada proceso pide el JWKS una vez por ventana: es aceptable, y no justifica Redis por sí solo. Ante un `kid` desconocido se vuelve a pedir el JWKS **una vez**, y a lo más una vez por minuto; si el `kid` sigue sin aparecer, `401`. Así una rotación de claves en el realm no deja a nadie afuera, y un token inventado no provoca una descarga por petición. Un token cuyo `iss` no es el del realm se rechaza sin descargar nada.

Si el JWKS no se puede descargar, la respuesta es `503` con código `REALM_NO_DISPONIBLE`, no `401`: la persona no hizo nada mal.

`KEYCLOAK_JWKS_URL` vacío significa `<KEYCLOAK_ISSUER>/protocol/openid-connect/certs`, la ruta estándar de Keycloak.

**Las rutas públicas autentican de forma opcional**, con `AutenticacionOpcional`. Un token ausente, vencido, inválido o sin perfil, o el realm caído, dejan la petición como anónima en vez de responder `401`, `403` o `503`: nadie se queda sin ver lo público por traer un token que no sirve. Un token válido identifica al perfil, que es lo que permite a `catalogo` mostrar un nodo oculto. Es la misma clase con `opcional=True` y no una subclase, porque el esquema OpenAPI nombra el mecanismo por su clase.

### La persona se identifica por el RUN, no por el `sub`

Del token se toman el *claim* `RolUnico` y el nombre. **Nada más.** No se copian *claims* del realm a nuestra base «por si acaso».

`RolUnico` llega como lo entrega Clave Única: `{"numero": 12345678, "DV": "5", "tipo": "RUN"}`. Se valida con `core.run.validar` y el perfil se busca por `(run_tipo, run_numero)`. Si no trae `tipo` —el realm de Banco de Proyectos no lo trae—, se asume `RUN`.

El nombre sale de `name` (texto, o `{"nombres": [...], "apellidos": [...]}` como lo entrega Clave Única), o si no de `firstName` y `lastName`, que es como lo mapea el realm de Banco de Proyectos, o de `given_name` y `family_name`. Cuál usa nuestro realm se fija en HR-21; el código acepta los tres para no depender de eso.

El `sub` **no** es la llave. La guía de integración de Clave Única lo dice explícitamente: viene porque OpenID Connect lo exige, y el identificador de la persona es el RUN. Además, con Keycloak en medio el `sub` del token es el del realm, no el de Clave Única: si se recrea el usuario en el realm o se cambia de realm, cambia. Se guarda solo como referencia para depurar.

### Sin perfil

Si el token es válido pero no hay perfil activo para ese RUN, la respuesta es `403` con código `SIN_PERFIL`, no `401`. La distinción importa: la persona se autenticó bien, simplemente no tiene nada que hacer acá. Un token válido sin `RolUnico`, o con un dígito verificador que no corresponde, también da `SIN_PERFIL`, y deja una advertencia en el log: es un realm mal configurado, no una persona que se equivocó.

En cada ingreso con perfil, `sub` y `nombre` se actualizan con lo que trae el token. El nombre que se escribió al crear el perfil es provisional.

### Si Clave Única no responde

El respaldo vive **en el realm, no en el backend**: credenciales locales de Keycloak con segundo factor, para una lista corta de administradores, con el atributo `RolUnico` cargado en el mismo formato. Para el backend es el mismo emisor, el mismo token y el mismo camino. Una segunda puerta en el backend sería la que buscaría un atacante, y duplicaría el código que más importa que esté bien. La configuración del realm es parte de HR-21.

### Desarrollo local: emisor propio

En local no hace falta Keycloak. Con `CUENTAS_EMISOR_LOCAL=1`, la clase de autenticación acepta además tokens con `iss` `nodo-local`, firmados con una clave que genera `python manage.py emitir_token_local --run 12345678-5 [--nombre ...]` la primera vez y guarda en `backend/.local/`, que git y Docker ignoran. Después de verificar la firma, el camino es **exactamente el mismo**: `RolUnico`, búsqueda del perfil, `SIN_PERFIL`. Las pruebas usan el mismo mecanismo.

- Solo `local.py` lee la variable; las pruebas la activan con el *fixture* `settings`. **`prod.py` se niega a arrancar si la variable está presente**, con cualquier valor.
- El comando se niega a correr si el emisor local no está activo.
- El emisor no crea perfiles. El primero se crea desde el admin con un superusuario, igual que en producción.

## 3. Perfiles y roles

```python
class Perfil(ModeloBase):
    run_numero = models.PositiveIntegerField()      # tal como lo entrega Clave Única
    run_dv     = models.CharField(max_length=1)     # "0"-"9" o "K"
    run_tipo   = models.CharField(default="RUN")
    sub        = models.CharField(blank=True)       # referencia para depurar; no es llave
    nombre     = models.CharField()
    rol        = models.CharField(...)              # lector | editor | curador | administrador
    municipio  = models.ForeignKey("core.Municipio", null=True, blank=True, on_delete=models.PROTECT)
    es_encargado = models.BooleanField(default=False)
    activo     = models.BooleanField(default=True)

    @property
    def run(self) -> str:                           # "12345678-5", con core.run.formatear
        ...
```

- **La llave es `(run_tipo, run_numero)`**, con restricción única en la base. El dígito verificador no es parte de la llave: se deduce del número, y `save()` verifica que corresponda.
- `run` es una **propiedad calculada**, no una columna: una copia en texto es una copia que se puede desincronizar.
- **El RUN se normaliza al entrar**: con `core.run.validar` cuando viene del token y con `core.run.leer` cuando lo escribe una persona en un formulario. Ninguna vista compara RUN quitando puntos al vuelo.
- `municipio` nulo significa persona de SUBDERE. Con municipio, es funcionaria o funcionario municipal y solo ve lo de su municipio en las vistas de uso humano.

Los roles son **acumulativos**: cada uno puede lo suyo y todo lo de los anteriores.

| Rol | Además de lo anterior, puede |
|---|---|
| `lector` | Ver la administración, sin cambiar nada |
| `editor` | Escribir y publicar entradas de wiki |
| `curador` | Publicar, ocultar y retirar servicios; resincronizar fuentes |
| `administrador` | Registrar y dar de baja fuentes; administrar perfiles de cualquier municipio y de SUBDERE; designar encargados |

**Los permisos se expresan como permisos de DRF, no con `if` repartidos en las vistas.** Una clase `RolMinimo` que recibe el rol exigido y compara por orden, y una clase `GestionaEquipo` para lo de la sección 4. Las vistas las declaran.

## 4. Equipos municipales y su encargado

Cada municipalidad tiene un **encargado**, que arma y administra su equipo en el nodo. Los administradores de SUBDERE pueden hacer lo mismo en cualquier municipio. El encargado es quien lo hace en el día a día; el administrador existe para que el municipio nunca quede sin control: si el encargado renuncia o pierde el acceso, un administrador designa a otro.

El equipo de un municipio son **los perfiles con ese municipio**. No hay tabla aparte ni réplica: el nodo es la fuente de verdad de quién está habilitado en él.

Reglas:

- **Un encargado vigente por municipio**, como máximo. Restricción en la base: única sobre `municipio` cuando `es_encargado` es verdadero. Un encargado tiene siempre municipio y está activo; desactivarlo le quita la marca en la misma operación.
- **Solo un administrador designa o reemplaza al encargado.** Al designar a otro, el anterior pierde la marca y queda como perfil común de su municipio, activo o no según decida el administrador.
- **El encargado puede, solo en su municipio:** crear perfiles, desactivarlos y reactivarlos. Los perfiles que crea son siempre `lector` y sin `es_encargado`: los roles superiores actúan sobre el catálogo nacional, no sobre el municipio.
- **El encargado no puede:** tocar perfiles de otro municipio ni de SUBDERE, cambiar el rol de nadie, nombrar a otro encargado ni modificar su propio perfil. Lo último evita que un encargado se deje a sí mismo fuera sin que nadie lo note.
- **Un RUN, un perfil.** Si el encargado intenta crear un perfil para un RUN que ya existe en otro municipio, la respuesta es `409` con código `PERFIL_EXISTENTE`, sin revelar a qué municipio pertenece. Moverlo es tarea de un administrador.
- **Los perfiles no se borran, se desactivan.** `Acceso` y `Bitacora` los referencian con `PROTECT`.
- Todo cambio de perfil, incluida la designación de encargado, deja `Bitacora` con el antes y el después.
- **El RUN de un integrante del equipo lo ven solo quienes lo administran**: el encargado de ese municipio y los administradores. Es dato personal con una finalidad acotada, y un lector no la necesita.

## 5. Registro de actuaciones: `Acceso` y `Bitacora`

Viven acá porque los dos responden «qué hizo este perfil», y porque así ni `core` depende de `cuentas` ni `cuentas` depende de `catalogo`. Las demás aplicaciones escriben en ellos a través de dos funciones de este módulo, `registrar_acceso(...)` y `registrar_bitacora(...)`, no creando los objetos directamente.

### `Acceso`

El registro de quién consultó qué. Es el único lugar donde esto se guarda.

```python
class Acceso(ModeloBase):
    perfil        = models.ForeignKey(Perfil, on_delete=models.PROTECT)
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
- **Nunca hay consultas anónimas a datos de personas**, en ningún ambiente, tampoco con datos sintéticos. Por eso `perfil` no admite nulo. Si un ambiente de demostración necesita mostrar la consulta, se le crea un perfil.
- **Solo crece.** Sin `update` ni `delete`; no se expone en el admin con permiso de edición.
- **Nunca guarda la respuesta.** `parametros` lleva lo justo para saber qué se preguntó: una patente. Si alguna vez hace falta guardar más, es una decisión de datos personales, no de implementación.
- Cuánto tiempo se conserva y quién lo revisa es **HR-28**. Hasta que se resuelva, no se borra nada.

### `Bitacora`

Las acciones editoriales: publicar, ocultar, retirar, registrar una fuente, editar una entrada de wiki, crear o modificar un perfil, designar un encargado.

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
| `GET /api/v1/yo` | autenticado | Devuelve el perfil propio: nombre, rol, municipio y si es encargado. Es lo que el frontend llama al entrar |
| `GET /api/v1/perfiles` | administrador, o encargado | Lista y filtra. El encargado solo recibe los de su municipio |
| `POST /api/v1/perfiles` · `PATCH /api/v1/perfiles/{id}` | administrador, o encargado con las restricciones de §4 | Crear, modificar, desactivar y reactivar. El RUN entra como texto y se lee con `core.run.leer`. Deja `Bitacora` |
| `PUT /api/v1/municipios/{cut}/encargado` | administrador | Designa o reemplaza al encargado. Deja `Bitacora` |
| `GET /api/v1/municipios/{cut}/equipo` | cualquier perfil de SUBDERE, o perfil de ese municipio | El equipo: nombre, rol, si es encargado, activo. El RUN, solo para quien lo administra |

No hay endpoint de alta propia. No hay recuperación de contraseña: no guardamos contraseñas. No hay `DELETE` de perfiles.

Lo que un encargado no puede hacer responde `403 PERMISO_DENEGADO`; un perfil de otro municipio no existe para él, y responde `404`. Los listados todavía no se paginan: con perfiles por municipio es razonable, y se agrega cuando haga falta sin cambiar el contrato de cada elemento.

**El primer administrador** se crea desde el admin de Django, con un superusuario local. Es la puesta en marcha que prevé `../../INSTRUCCIONES.md` §3, y la única manera de crear un perfil sin otro perfil. Queda en `Bitacora` sin perfil y con la nota de qué superusuario lo hizo.

## 7. Lo que las pruebas garantizan

En `tests/`. Si una de estas deja de cumplirse, se rompió una decisión de arriba:

1. Un token con firma inválida, `aud` o `iss` equivocado, expirado o sin `exp` da `401`. Si el realm no responde, `503 REALM_NO_DISPONIBLE`.
2. Un token válido sin perfil activo da `403` con código `SIN_PERFIL`; también uno sin `RolUnico` o con un dígito verificador que no corresponde.
3. El perfil se encuentra por el RUN aunque el `sub` del token haya cambiado, y en ese ingreso se actualiza el `sub`.
4. No se pueden crear dos perfiles con el mismo RUN, aunque se escriba con y sin puntos.
5. Los roles son acumulativos: un `curador` puede lo de un `editor`, pero no crear perfiles; un `administrador` sí.
6. Un encargado crea un `lector` en su municipio; no puede crearlo en otro, ni con otro rol, ni marcarlo como encargado, ni modificarse a sí mismo. Un RUN existente en otro municipio da `409 PERFIL_EXISTENTE`.
7. No puede haber dos encargados vigentes en un municipio; designar a uno nuevo le quita la marca al anterior.
8. Un perfil con municipio no ve el equipo de otro municipio; un lector de SUBDERE ve el equipo sin RUN.
9. Crear o modificar un perfil y designar un encargado escriben en `Bitacora` con el antes y el después.
10. El JWKS se refresca ante un `kid` desconocido, una sola vez, y no en cada petición.
11. `Acceso` y `Bitacora` no se pueden modificar ni borrar: ni por `save()`, ni por `delete()`, ni por `update()` sobre un `QuerySet`.
12. Con `CUENTAS_EMISOR_LOCAL` desactivado, un token del emisor local da `401`; y `prod.py` no arranca si la variable está presente.

## 8. Qué no implementar

- Vistas de login, logout ni registro en el backend. El flujo es del frontend contra el realm.
- Sesiones de Django para la API.
- Escrituras en el realm. Los perfiles viven en nuestra base; el realm solo autentica.
- Un segundo camino de autenticación en producción. El respaldo vive en el realm (§2).
- Ningún permiso basado en el correo o en el dominio del correo.
- Ninguna comparación de RUN sobre texto sin normalizar.
