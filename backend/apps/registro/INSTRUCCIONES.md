# `registro` — fuentes, lecturas y sincronización

> **Construida.** Este archivo registra las decisiones y los límites de la aplicación; el código es la fuente de los detalles. Antes de cambiar algo de lo que dice acá, leer por qué está así. Contrato común en [`../../INSTRUCCIONES.md`](../../INSTRUCCIONES.md).

El [estándar de la ficha de servicio](../../../docs/estandar-ficha-de-servicio.md) define el archivo que esta aplicación lee y valida. **Ese documento es la fuente; este archivo dice cómo se implementa.** El camino completo está dibujado en [`esquemas-de-repositorios.html`](../../../docs/esquemas-de-repositorios.html), tercer esquema.

Esta aplicación es la razón por la que el catálogo no se escribe a mano.

Depende de `core`, `cuentas` y `catalogo`. Es **el único lugar del proyecto** que llama a `save(desde_sincronizacion=True)` y `delete(desde_sincronizacion=True)` sobre los modelos de `catalogo`.

## Dónde está cada cosa

| Pieza | Archivo |
|---|---|
| `Fuente`, `Lectura` y la regla de la dirección (`problema_de_url`) | `models.py` |
| `RepositorioNoDisponible` (interna: su mensaje es el motivo de la lectura), `FuenteDeNodoRetirado` y `FuenteInactiva` | `errores.py` |
| `LectorGitLab`, `LectorFalso` y el límite de 1 MB | `lectores.py` |
| Las ocho reglas, en orden, y `FichaInvalida` | `validacion.py` |
| La escritura sobre `catalogo` y la comparación por contenido (`instantanea`) | `proyeccion.py` |
| `sincronizar()`, el bloqueo de la fila y qué fuentes se leen | `sincronizacion.py` |
| El comando de la tarea programada | `management/commands/sincronizar_fuentes.py` |
| Endpoints | `api/v1/` |
| Admin para superusuarios locales | `admin.py` |
| Settings: `REGISTRO_GIT_API_URL`, `REGISTRO_GIT_TOKEN`, `REGISTRO_TIEMPO_ESPERA_SEGUNDOS`, `REGISTRO_DOMINIOS_NO_INSTITUCIONALES` | `config/settings/base.py` |

---

## 1. Modelos

```python
class Fuente(ModeloBase):
    tipo       = models.CharField(...)          # repositorio | carga_manual
    url        = models.URLField(blank=True)    # del proyecto en GitLab; vacía en una carga manual
    rama       = models.CharField(default="main")
    ruta_ficha = models.CharField(default="nodo/ficha.yaml")
    activa     = models.BooleanField(default=True)
    nodo_identificador = models.SlugField(blank=True)   # vacío hasta la primera lectura válida

class Lectura(SoloCrece):                       # de cuentas: no se edita ni se borra
    fuente    = models.ForeignKey(Fuente, related_name="lecturas", on_delete=models.PROTECT)
    perfil    = models.ForeignKey(Perfil, null=True)  # quién pidió leer; nulo si fue programada
    commit    = models.CharField(blank=True)    # la cabeza de la rama al leer
    contenido = models.TextField(blank=True)    # el YAML tal como se leyó
    valida    = models.BooleanField()
    motivo    = models.TextField(blank=True)
```

`nodo_identificador` dice qué nodo proyecta esta fuente. Se fija en la primera lectura válida y no cambia después: es el `id` de la ficha, que es inmutable. Es un identificador y no una clave foránea, por la misma razón que `catalogo.Alias.destino`. Con él, la validación 3 distingue «este `id` es de otra fuente» de «este `id` es el mío», y la sincronización sabe si el nodo está retirado sin leer el repositorio.

**Restricciones de `Fuente`:** `nodo_identificador` es único cuando no está vacío —dos fuentes no proyectan el mismo nodo—; `(url, rama, ruta_ficha)` es única; una fuente de tipo repositorio tiene `url`. El host de la `url` tiene que ser el de `REGISTRO_GIT_API_URL`: hay un solo GitLab y un solo token.

`Lectura` **solo crece**: hereda `SoloCrece` de `cuentas`, el mismo que protege `Acceso` y `Bitacora`. Guardar el YAML tal cual permite reconstruir la proyección si el modelo cambia, sin volver a pedirle nada al repositorio, y permite decir de qué *commit* salió cada ficha publicada.

**La carga manual queda para después.** Existe para la transición, cuando un responsable todavía no tiene repositorio: se sube el archivo, se valida igual, y el catálogo marca que esa ficha no tiene fuente verificable. **No es un atajo para editar a mano una ficha que sí tiene repositorio.** El modelo ya la admite —`tipo`, `url` vacía, `commit` vacío— y la sincronización se salta esas fuentes; falta el endpoint que reciba la ficha y, si la declara, el contrato.

**El traspaso de custodia es un cambio de `url`, no un servicio nuevo.** Cuando el dueño de una fuente aloje el contrato junto a su servicio, se cambia la dirección de la `Fuente` y el historial de lecturas muestra cuándo se movió. Funciona porque el identificador de la ficha es inmutable. Está en el [ADR de acceso directo](../../../docs/adr-2026-10-acceso-directo-primera-etapa.md) §6.

## 2. Lectura

Un cliente que lee un archivo de un repositorio por su API, con un token de **solo lectura**. El token entra por variable de entorno; su emisión, alcance y rotación son **HR-22**.

**Un solo token para todas las fuentes, no uno por repositorio.** El token identifica al nodo ante GitLab; lo que cambia de una fuente a otra es la dirección, no la credencial. Registrar una fuente nueva no toca la configuración: basta con que esa identidad tenga rol *Reporter* en el repositorio. Por eso `Fuente` no tiene campo de token, y ningún secreto se guarda en la base.

La identidad conviene que sea una **cuenta de servicio del nodo** —un usuario de GitLab sin persona detrás, con un token personal `read_api`— agregada como *Reporter* a los grupos donde viven los repositorios. Así un repositorio nuevo dentro de un grupo ya cubierto no requiere nada. Un *group access token* también sirve, pero alcanza solo a un grupo y sus subgrupos, y los repositorios pueden quedar repartidos cuando cada dueño aloje su contrato junto a su servicio (traspaso de custodia, §1).

Implementar detrás de una interfaz pequeña —leer la ficha, que devuelve el *commit* y el contenido, y leer un archivo en un *commit*— con una implementación para GitLab y otra falsa para las pruebas. Las pruebas **no** salen a la red.

**Cómo se lee en GitLab.** Está probado contra `gitlab.subdere.gob.cl` (16.11) y el repositorio `modernizacion/cut`, desde el contenedor de la API:

- `GET {REGISTRO_GIT_API_URL}/projects/{grupo%2Frepo}/repository/files/{ruta%2Fcodificada}?ref={rama}`, con el token en la cabecera `PRIVATE-TOKEN`. Una sola respuesta trae `content` en base64 y el *commit*: no hace falta clonar.
- **El *commit* que vale es `commit_id`, la cabeza de la rama al leer**, no `last_commit_id`, que es el último *commit* que tocó la ficha. Si el contrato cambió después que la ficha, leerlo en `last_commit_id` traería una versión vieja. `commit_id` es el que se guarda en `Lectura.commit` y en `Nodo.commit`.
- **La ficha se lee en la rama y el archivo de la especificación en ese `commit_id`**, con `ref={commit_id}`. Así los dos salen de la misma versión del repositorio aunque alguien haga *push* entremedio, que es lo que pide la validación 4.
- Los bytes llegan intactos: la huella del contrato leído coincide con la del archivo original. La validación 8 puede confiar en ella.
- **Límite de 1 MB por archivo.** Uno más grande se rechaza con motivo.
- El token necesita alcance `read_api` **y rol *Reporter*** en el proyecto. Con *Guest* GitLab responde `403 Forbidden` aunque el alcance sea correcto; sin token, `401` en la API y `404` en el archivo. **El motivo de la `Lectura` distingue esos casos y dice qué hacer**: ante un `403` o un `404`, dar rol *Reporter* a la cuenta del nodo en ese repositorio y revisar la rama y la ruta. Es el error más probable al dar de alta una fuente nueva. Una falla de red dice que GitLab no respondió.
- GitLab solo responde dentro de la red de SUBDERE o por VPN: el nombre resuelve a una IP privada. El servidor de la aplicación tiene que estar en esa red; es parte de **HR-20**.

## 3. Validación

En este orden, y la primera que falla detiene el resto:

1. El archivo es YAML válido y `ficha` es una versión conocida. Si no la conoce, **rechaza en vez de adivinar**.
2. Están todos los campos obligatorios, con su tipo, y los de lista cerrada traen un valor de la lista.
   - Las listas cerradas son las `TextChoices` de `catalogo.models` —`Clase`, `Intercambio`, `Madurez`, `Copia`, `TipoDeAcceso`, `Formato`, `NombreDeAmbiente`, `Datos`—. No se duplican acá.
   - `ambito` tiene que existir en `catalogo.Ambito`. `intercambio` se exige solo si `clase` es `intercambio`, y una plataforma no lo lleva.
   - `id` usa solo minúsculas, números y guiones: `SlugField` aceptaría mayúsculas y guion bajo.
   - **`version` tiene que venir como texto.** YAML lee `version: 1.10` como el número `1.1`; una versión numérica se rechaza pidiendo escribirla entre comillas. Lo mismo para `info.version` del contrato.
   - **Los largos y formatos los valida el propio modelo** con `clean_fields()` antes de guardar —`identificador` 100, `nombre` 200, `sigla` 30, `version` 50, la URL de un ambiente 500—, y cada error se traduce a un motivo. Una ficha demasiado larga deja un motivo, no un error 500.
3. `id` no está tomado por el nodo de otra fuente ni es el identificador de un `Alias`. Si la fuente ya tiene `nodo_identificador`, el `id` tiene que ser ese mismo: un `id` distinto es un servicio nuevo, no un renombre.
4. Si declara `especificacion.archivo`, existe en el mismo *commit* y se puede parsear, el `formato` es `openapi-3.0` u `openapi-3.1`, y el campo `openapi` del archivo calza con él (`3.0.x` con `openapi-3.0`, `3.1.x` con `openapi-3.1`). Sin archivo, el formato es `descripcion`. No se valida el contrato completo contra el esquema de OpenAPI.
5. Si hay archivo, `especificacion.version` coincide con el `info.version` del archivo. Atrapa el error más común: publicar una versión y declarar otra.
6. `responsable.correo` es institucional: **se rechazan los correos de proveedores públicos** —gmail, hotmail, outlook, yahoo y otros—, con la lista en `REGISTRO_DOMINIOS_NO_INSTITUCIONALES`. No se exige `.gob.cl`: muchos municipios usan dominios propios.
7. **La ficha no trae datos personales** más allá del contacto institucional. Sin excepciones: en este repositorio ya quedó versionado un archivo con nombre y RUT reales. Se rechaza una ficha que tenga, en cualquiera de sus textos, un RUN con dígito verificador válido (`core.run`) o un correo distinto del del responsable. El contrato no se revisa, para no rechazar ejemplos inventados.
8. **Una versión ya registrada no cambia.** Si el nodo ya tiene una `Especificacion` con esa `version`, la `huella` del archivo leído tiene que ser la misma. Si no, se rechaza nombrando la versión: ninguna versión se corrige. `catalogo` también lo impide en `save()`.

Cada falla produce una `Lectura` con `valida=False` y un `motivo` **en español y específico**: qué campo, qué se esperaba. Ese motivo lo va a leer la persona que escribió la ficha.

## 4. Sincronización

Comando de gestión `sincronizar_fuentes`, que corre por tarea programada, y el endpoint `POST /fuentes/{id}/sincronizar`, que usa el botón «resincronizar» de la administración. Los dos llaman a la misma función.

Para cada fuente activa de tipo repositorio **cuyo nodo no esté retirado**: lee, valida, proyecta sobre `catalogo.Nodo`, `catalogo.Especificacion` y `catalogo.Ambiente`, y crea la `Lectura`. La fila de la fuente se bloquea con `select_for_update` mientras tanto, para que el comando y el botón no proyecten a la vez.

La proyección escribe también en el nodo `leido_en` y `commit` de la lectura que la produjo. Así `catalogo` puede decir de cuándo es la ficha, y fechar un `410` de un nodo retirado, sin consultar esta aplicación.

La proyección guarda con `save(desde_sincronizacion=True)`, objeto por objeto, en los tres modelos, dentro de una transacción. No usa `update()`, `bulk_update()`, `bulk_create()` ni `delete()` sobre ellos: sus `QuerySet` los rechazan (ver `catalogo` §1).

- **Una especificación nueva se crea vigente** y la anterior deja de serlo, sin borrarse; primero se apaga la que regía, por la restricción de una sola vigente.
- **Si la ficha declara una versión que ya existe, con la misma huella, esa versión vuelve a regir.** Es volver atrás sin corregir nada.
- **Los ambientes que la ficha ya no declara** se borran con `delete(desde_sincronizacion=True)`.

**Cuando la lectura falla, no se borra ni se despublica nada.** Queda la `Lectura` inválida con su motivo, la proyección anterior sigue vigente, y la API informa de cuándo es la última lectura buena. Es el mismo patrón de degradación honesta de las pantallas de servicio.

**La proyección es idempotente, y se compara por contenido, no por *commit*.** Cualquier *push* —un README, por ejemplo— cambia la cabeza de la rama. Si los campos de ficha, los ambientes, la versión y la huella del contrato son los mismos, solo se actualizan `leido_en` y `commit` del nodo, sin entrada en `Bitacora`.

**Qué deja en `Bitacora`:**
- `sincronizar_nodo`, solo cuando la proyección cambió algo además de `leido_en` y `commit`, con el antes y el después de la ficha y la versión vigente. El perfil es quien pidió sincronizar desde la API; si fue la tarea programada, va sin perfil y con la nota `Sincronización programada: fuente {id}, commit {sha}`.
- `registrar_fuente` y `modificar_fuente`, desde los endpoints de §5.

Una ficha nueva entra como `oculto`. Publicarla es una decisión editorial de un curador; no exige pantalla, entrada de wiki ni servicio disponible (ver `catalogo` §4).

## 5. Endpoints

| Método y ruta | Quién | Qué hace |
|---|---|---|
| `GET /api/v1/fuentes` | lector | Lista, con su última lectura |
| `POST /api/v1/fuentes` | administrador | Registra una dirección. Lee y valida en el acto, y devuelve la fuente con el resultado. **La fuente se crea aunque la lectura falle** (`201`): la ficha puede no estar lista todavía, y se resincroniza después. Deja `Bitacora` |
| `PATCH /api/v1/fuentes/{id}` | administrador | Cambia dirección, rama, ruta o `activa`. Cambiar la dirección es el traspaso de custodia; `activa: false` es dar de baja la fuente, y no retira el nodo. Deja `Bitacora` |
| `POST /api/v1/fuentes/{id}/sincronizar` | curador | Vuelve a leer ahora. Si el nodo está retirado, `409` con código `FUENTE_DE_NODO_RETIRADO`; si la fuente está inactiva, `409 FUENTE_INACTIVA` |
| `GET /api/v1/fuentes/{id}/lecturas` | lector | El historial, con *commit*, fecha, validez y motivo |

`nodo_identificador` y `tipo` no se escriben por la API: el primero lo fija la primera lectura válida, y el segundo es `repositorio` mientras no exista la carga manual.

La respuesta de `GET /api/v1/nodos/{id}` ya trae `leido_en` y `commit`, porque la sincronización los escribe en el nodo (§4). El historial completo de lecturas, válidas e inválidas, está en `GET /api/v1/fuentes/{id}/lecturas`.

**Decisiones de implementación que no están en el estándar:**

- **Un campo que el estándar no define se rechaza**, nombrándolo. Atrapa errores de tipeo —`procedenica`— que de otro modo se perderían en silencio. Agregar un campo opcional al estándar obliga a enseñárselo a esta aplicación antes de usarlo en una ficha.
- **Una ficha rechazada por datos personales no se archiva**: la `Lectura` queda con `contenido` vacío, y el motivo nombra el campo pero no repite el dato. Guardarla sería versionar en la base lo que la regla 7 quiere impedir.
- **El RUN se busca con guion y dígito verificador** (`12.345.678-5`, `12345678-5`). Un número sin guion es ambiguo —teléfonos, folios— y daría falsos positivos.
- **Si la ficha es válida pero la proyección falla** en la base, queda una `Lectura` inválida con ese motivo y nada a medio escribir: la proyección corre en su propio punto de guardado.
- Registrar una fuente por el **admin** deja `Bitacora` con la nota del superusuario, pero no la lee: para eso están la API y el comando.

## 6. Lo que las pruebas garantizan

Ninguna prueba sale a la red: una fixture automática cierra `urllib.request.urlopen` y la sincronización usa `LectorFalso`. Las de `LectorGitLab` reemplazan `urlopen` por un GitLab falso que anota cada pedido.

1. Una ficha válida crea el nodo como `oculto` y su especificación vigente.
2. Una versión de estándar desconocida se rechaza con motivo, sin tocar la proyección.
3. Una versión declarada que no coincide con la del archivo se rechaza nombrando las dos.
4. Un `id` ya tomado, o que es un alias, se rechaza.
5. Un fallo de red deja `Lectura` inválida y **no** modifica el nodo publicado.
6. Sincronizar el mismo contenido dos veces no genera cambios ni entradas de bitácora, aunque cambie el *commit*: solo se actualizan `leido_en` y `commit`.
7. Cambiar la `url` de una fuente conserva el nodo y su identificador.
8. Ninguna prueba sale a la red.
9. La misma versión de especificación con otro contenido se rechaza nombrando la versión, sin tocar la proyección.
10. Una ficha sin archivo de especificación se proyecta como solo metadato, y una plataforma sin `intercambio` es válida.
11. Una fuente cuyo nodo está retirado no se lee.
12. La proyección deja en el nodo `leido_en` y `commit` de la lectura, y el contrato se lee en ese `commit`.
13. Un campo demasiado largo o una `version` numérica dejan un motivo, no un error.
14. Volver a una versión anterior idéntica la hace regir otra vez.
15. Un `403` de GitLab deja un motivo que pide el rol *Reporter*.
16. Un RUN válido en la ficha, o un correo de un proveedor público como responsable, la rechazan.

## 7. Qué no implementar

- Escritura hacia los repositorios. Solo lectura, siempre.
- Recepción de avisos desde los repositorios. El modelo es jalar, no recibir. Está decidido en el ADR de estructura.
- Edición del contenido de una ficha desde la administración.
- Borrado de lecturas, ni «limpieza» del historial.
- Validación completa del contrato contra el esquema de OpenAPI. Se comprueba que se puede leer, su versión de OpenAPI y su `info.version`.
- La carga manual, por ahora (§1).
