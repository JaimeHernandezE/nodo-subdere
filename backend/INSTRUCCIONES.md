# Instrucciones de construcción — backend del Nodo SUBDERE

Este archivo es el contrato común de todas las aplicaciones. Cada `apps/<app>/INSTRUCCIONES.md` supone lo que está acá y no lo repite. Si algo de acá se contradice con un archivo de app o con [`README.md`](README.md), manda este. El README explica el diseño; si quedó atrasado respecto de estos archivos, se corrige el README.

**Para quien construya con asistencia de IA:** lee este archivo y el de la app antes de escribir código. Lo que no está acá no es libertad creativa: es una pregunta. Las preguntas abiertas están marcadas con `HR-nn` o `X-nn` y viven en [`../docs/hoja-de-ruta.md`](../docs/hoja-de-ruta.md), Parte III.

---

## 1. Qué estamos construyendo

La aplicación del Nodo SUBDERE: el sistema que **administra y publica** el catálogo de intercambios del dominio municipal, sirve las vistas de uso humano de esos servicios, y aloja la wiki.

**No** es la puerta de acceso, **no** es un registro de datos municipales y **no** transporta datos entre órganos. Los límites completos están en [`README.md`](README.md) y en [`../docs/hoja-de-ruta.md`](../docs/hoja-de-ruta.md) §4.

Objetivo inmediato: **una primera versión en producción, oculta por informática.** Oculta significa no alcanzable desde internet todavía; no significa insegura. Se construye como si fuera pública desde el primer commit.

## 2. Decisiones ya tomadas, que no se rediscuten al construir

| | |
|---|---|
| Python 3.12 · Django 5.x · Django REST Framework | |
| PostgreSQL | También en desarrollo, para no encontrarse diferencias tarde |
| `drf-spectacular` | La API publica su propio OpenAPI. Un sitio que promueve contratos legibles por máquina no puede no tener el suyo |
| `pytest` + `pytest-django` · `ruff` | Las pruebas viven dentro de cada app, en `apps/<app>/tests/`, salvo que Banco de Proyectos las ordene de otra forma (§2.ter) |
| `django-environ` | Lee las variables de entorno y `DATABASE_URL`. Una sola biblioteca para las dos cosas |
| `django-cors-headers` | El frontend corre en otro origen. Orígenes y cabeceras permitidas por variable de entorno |
| `PyJWT` + `cryptography` | Validación del token del realm (§3) |
| `gunicorn` | Servidor de producción. `runserver` solo en local |
| **Español en el dominio** | `Nodo`, `Especificacion`, `funcion`, `visibilidad`. En inglés queda solo lo del framework |
| Sin secretos en el repositorio | Todo por variable de entorno, con `.env.example` documentado. `.env` excluido desde el primer commit |
| Docker Desktop en local, un archivo por ambiente | Detalle en §2.bis |
| `insumos/` fuera del control de versiones | Ahí va material recibido de terceros. Nunca se versiona |

**Un detalle de arquitectura que cambia cómo se escribe todo:** en esta primera versión **no hay gateway delante**. El backend es su propio *resource server*: valida los token él mismo. La puerta de acceso se licita y se construye aparte, y cuando exista se pone delante **sin cambiar las aplicaciones**. Por eso nada depende de cabeceras que inyecte un intermediario.

## 2.bis Ambientes: un archivo por ambiente

Desarrollo en local con **Docker Desktop**. La regla es que **cada ambiente tenga su archivo**, y que el nombre del ambiente aparezca en los tres lugares a la vez: el módulo de configuración, el archivo de variables y, si hace falta, la composición de contenedores.

```
backend/
├── Dockerfile
├── docker-compose.yml          desarrollo: base de datos y api
├── docker-compose.prod.yml     sobrescribe lo que cambia en producción
├── .env.example                plantilla documentada  → SÍ se versiona
├── .env.local                  desarrollo             → NO se versiona
├── .env.prod                   producción             → NO se versiona
└── config/settings/
    ├── base.py                 lo común
    ├── local.py                desarrollo
    └── prod.py                 producción
```

- `DJANGO_SETTINGS_MODULE` sale del archivo de variables, no del código. En local, `config.settings.local`.
- **Cuidado con `--env-file`: no le pasa variables al contenedor.** Solo reemplaza las `${VARIABLE}` dentro del propio YAML. Para que Django las reciba, el servicio `api` declara `env_file: ${ARCHIVO_ENV}` en `docker-compose.yml`, y cada archivo de variables dice su propio nombre en `ARCHIVO_ENV`. Así `--env-file` elige el ambiente una sola vez y `docker-compose.prod.yml` no repite nada de eso. Los comandos quedan así:

```bash
# local
docker compose --env-file .env.local up

# producción oculta
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d
```

- `docker-compose.prod.yml` cambia el comando de `api` a `gunicorn`. `runserver` solo corre en local.
- **Solo ambientes que existen.** Hoy son dos: local y la producción oculta. Cuando aparezca un ambiente de desarrollo compartido, se agrega su par de archivos; no se dejan vacíos esperando.
- `.gitignore` ya excluye `.env` y `.env.*`, con `.env.example` como única excepción. **Revisar que siga así antes de cada publicación**: en otro repositorio del equipo quedaron archivos `.env` versionados con contraseñas de base de datos.
- Dos formas de correr en local, y el `.env.local` debe decir cuál se está usando: todo en contenedores, y entonces la base es `db:5432`; o solo Postgres en Docker y Django en el equipo, y entonces es `localhost:5432`.
- `prod.py` no es `local.py` con `DEBUG=False`. Tiene `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` desde el ambiente, los `SECURE_*` activos, y la cabecera `X-Robots-Tag: noindex` mientras el sitio esté oculto. Django no trae un ajuste para esa cabecera: la pone un *middleware* de `core`, controlado por la variable `NODO_OCULTO`.

## 2.ter De dónde se copian las convenciones

**El orden de carpetas y la autenticación no se inventan acá.** El proyecto **Banco de Proyectos** —Django y React, del mismo equipo— ya tiene las dos cosas resueltas y en uso. Al construir, conviene abrirlo al lado y seguirlo:

| Qué se copia de Banco de Proyectos | Por qué |
|---|---|
| **El orden de carpetas dentro de cada app** y la convención de nombres de archivo | Es el que el equipo ya lee sin pensar. Los nombres de archivo que aparecen en estos documentos son la lista de piezas, no una imposición: si Banco de Proyectos las ordena de otra forma, manda Banco de Proyectos |
| **El bloqueo de quien se autentica y no está habilitado** | Es exactamente nuestro `403` con código `SIN_PERFIL`. Está probado en producción y no hay razón para rehacerlo |
| La configuración de `ruff`, `pytest` y el `Dockerfile`, si sirven tal cual | |

**Lo que hay que mirar con cuidado antes de copiar: el camino de Clave Única.** Banco de Proyectos se integra con Clave Única, y acá la decisión es pasar por un **realm de Keycloak que la federa**. No es lo mismo, y conviene no mezclar las dos cosas sin decidirlo:

- Se mantiene **Keycloak**, porque es la pieza de identidad que ya está en la nota de la plataforma de control, porque deja un solo lugar donde poner después el control de paso, y porque el día que haya perfiles municipales el realm es donde viven.
- De Banco de Proyectos se porta la **capa de autorización** —la tabla de habilitados y el bloqueo— que es independiente de por dónde venga la autenticación.
- Si al abrirlo resulta que su integración es directa contra Clave Única y portarla a Keycloak cuesta más de lo que parece, es una decisión que vale conversar antes de escribir código, no después. Queda anotada en **HR-21**.

## 3. Autenticación: Keycloak delante de Clave Única

Hay un *realm* de Keycloak al que el equipo tiene acceso, y ese realm federa Clave Única. El backend **no habla con Clave Única**: confía en el realm.

- El frontend hace el flujo **Authorization Code + PKCE** contra el realm, como cliente público. El backend no guarda sesión.
- El frontend manda el *access token* en `Authorization: Bearer <token>`.
- El backend valida el token con el **JWKS del realm**, verificando firma, `iss`, `aud` y expiración. Implementar como clase de autenticación de DRF en `apps/cuentas`. Dependencia: `PyJWT` con `cryptography`. No usar bibliotecas que agreguen sesiones o vistas de login al backend.
- El JWKS va en el caché de Django y se vuelve a pedir una sola vez ante un `kid` desconocido, para soportar la rotación de claves del realm. Detalle en `apps/cuentas/INSTRUCCIONES.md` §2.
- El `sub` del token identifica a la persona. El RUN viene como *claim* del realm.

**Keycloak autentica; el nodo autoriza.** Lo que la persona puede hacer lo dice el perfil en nuestra base, no el token. Detalle en `apps/cuentas/INSTRUCCIONES.md`.

El admin de Django queda **solo para superusuarios locales**, para la puesta en marcha y emergencias. La administración real va por la API y la interfaz en React, porque necesita identidad de Keycloak, perfiles y bitácora.

## 4. Reglas invariantes

Estas salen de decisiones escritas en `../docs/`. Romper una es un cambio de decisión, no un detalle de implementación.

1. **Nadie tiene atajos.** Toda pantalla, incluidas las nuestras, consume la misma interfaz pública que usaría un municipio o un proveedor. Si una vista llega a datos que la API no expone, el catálogo deja de describir lo que se puede construir. **La única excepción declarada es el admin de Django** (§3): existe para la puesta en marcha y emergencias, solo para superusuarios locales, y no se construye ninguna funcionalidad que dependa de él.
2. **La crítica va en la wiki, no en el catálogo.** No existe campo de observaciones en el catálogo ni en la especificación. Si aparece, se perdió la separación.
3. **Los campos que vienen de una ficha son de solo lectura.** Se escriben solo por sincronización. Hay tres puertas y se cierran las tres: `readonly_fields` en el admin, verificación en `save()`, y un `QuerySet` que rechaza `update()` y `bulk_update()` sobre esos campos, porque esos métodos no pasan por `save()`. La sincronización se identifica con un argumento explícito. Detalle en `apps/catalogo/INSTRUCCIONES.md` §1.
4. **El backend no guarda los datos de los servicios externos.** Consulta, normaliza y cachea por un tiempo corto y declarado. Si a un adaptador le aparecen tablas, se convirtió en un registro paralelo.
5. **Ninguna versión se corrige.** Especificaciones, fichas y entradas de wiki se versionan; una corrección es una versión nueva.
6. **Degradación honesta.** Si una fuente no responde, no se despublica ni se vacía nada: se muestra el último dato bueno diciendo de cuándo es.
7. **Sin datos personales fuera de lo declarado.** Solo el RUN y el nombre de quien administra, y lo que un servicio externo devuelva en el momento de una consulta, que no se persiste.

## 5. Trazabilidad y registro de accesos: un solo modelo

Toda consulta que entregue **datos de una persona** —por API o por pantalla— deja un registro en `cuentas.Acceso`. Es a la vez el registro de accesos de las vistas humanas (HR-28) y el antecedente de los metadatos del artículo 9 del Decreto N° 12, para que migrar a la Red sea configuración.

Las consultas a datos abiertos sin datos personales, como el CUT, no se registran. Y en producción, toda consulta que se registra exige perfil activo: no hay accesos anónimos a datos de personas.

Lo que **no** se acepta de la petición, porque se deduce del token: quién es la persona y a qué municipio pertenece. Lo que **sí** viene en la petición: `X-Procedimiento` (para qué trámite) y, cuando corresponda, `X-Id-Tramite`.

Nunca se guarda el contenido de la respuesta, solo qué se consultó.

## 6. Errores

Un solo sobre, resuelto en un manejador de excepciones de DRF en `apps/core`:

```json
{"error": {"codigo": "PATENTE_INVALIDA", "mensaje": "La patente no tiene un formato válido.", "detalles": []}}
```

Códigos en MAYÚSCULA_CON_GUION_BAJO, mensajes en español y para humanos. El formato de error de PISEE no está documentado (X-121): por eso esto vive en un solo lugar y cambiarlo es un módulo.

## 7. Orden de construcción

Cada app se documenta y después se construye. No empezar la siguiente sin que las pruebas de la anterior pasen.

| # | App | Depende de |
|---|---|---|
| 1 | `core` | — |
| 2 | `cuentas` | core |
| 3 | `catalogo` | core, cuentas |
| 4 | `registro` | core, cuentas, catalogo |
| 5 | `integraciones` | core, cuentas |
| 6 | `servicios` | core, cuentas, catalogo, integraciones |
| 7 | `wiki` | core, cuentas, catalogo |

**Ninguna app apunta a una que esté más abajo en la tabla**, ni por clave foránea ni por importación. Por eso `Municipio` vive en `core` y `Acceso` y `Bitacora` en `cuentas`: si estuvieran en `catalogo` y en `core`, `core` dependería de `cuentas` y `cuentas` de `catalogo`, y el paso 1 no se podría probar solo. Si al construir aparece la necesidad de apuntar hacia abajo, es una pregunta, no un `ForeignKey` en texto.

El frontend puede empezar en paralelo desde el paso 3, contra el OpenAPI del backend.

## 8. La primera versión en producción

Oculta por informática, y aun así:

- `DEBUG=False`, `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` por variable de entorno, `SECURE_*` activos.
- Sin registro público de usuarios. Un perfil se crea a mano o por réplica; nadie entra por tener Clave Única.
- Los endpoints públicos del catálogo existen y devuelven **solo** lo que está `publicado`.
- `X-Robots-Tag: noindex` mientras esté oculta (`NODO_OCULTO=1`), y quitarlo es una decisión consciente.
- Ningún dato real de un vecino en la base. Los ambientes con datos sintéticos lo declaran en su ficha.

**No apoyarse en que está oculta para postergar nada de lo anterior.** Se publica cuando informática lo decida, y ese día no debería haber lista de pendientes de seguridad.
