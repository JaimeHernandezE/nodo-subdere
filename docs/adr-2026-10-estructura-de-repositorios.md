# ADR 2026-10 — Estructura de repositorios del Nodo SUBDERE

**Estado:** propuesta
**Fecha:** 6 de octubre de 2026
**Ámbito:** Nodo SUBDERE · servicios del catálogo · publicación
**Relacionados:** [`adr-2026-09-estandar-legible-por-maquina.md`](adr-2026-09-estandar-legible-por-maquina.md), [`adr-2026-10-conector-municipal.md`](adr-2026-10-conector-municipal.md), [`estandar-ficha-de-servicio.md`](estandar-ficha-de-servicio.md), [`esquemas-de-repositorios.html`](esquemas-de-repositorios.html), [`hoja-de-ruta.md`](hoja-de-ruta.md) §§1, 3, 7, 9 y 10, [`plataforma-control.md`](plataforma-control.md)

> **Decisión.** Un repositorio por cosa con dueño: **uno para el Nodo SUBDERE** —la aplicación que administra y publica el catálogo, más la documentación base— y **uno por cada servicio**, que lleva adentro su propio estándar, lo administre nuestro equipo o no. La ficha de cada servicio es **un archivo versionado en el repositorio del servicio**, que la aplicación del nodo lee. Y **lo que publica los contratos a internet es la aplicación, no el repositorio.**

---

## 1. Contexto

El repositorio único de hoy contiene la aplicación, la documentación, la maqueta y, dentro de la maqueta, los contratos. Cuatro síntomas:

1. Los cuatro OpenAPI viven en `prototipos/estandares/`: el artefacto más durable de la estrategia está dentro de la carpeta que el propio README describe como desechable.
2. El *workflow* de GitHub Pages se dispara con cambios del backend, que no tienen nada que ver con el sitio estático.
3. El material recibido de terceros no tiene lugar, así que terminó en `docs/`. Por esa vía un archivo con nombre y RUT reales quedó versionado (`docs/fiscalizacion_stag.yml`).
4. Cómo se cargan las especificaciones quedó como pregunta abierta en `backend/README.md`, entre subirlas por el admin o sincronizarlas desde un repositorio.

Y hay dos restricciones de la casa que condicionan cualquier respuesta: el **GitLab institucional tiene Pages bloqueado**, y la publicación en GitHub existe hoy solo para exponer la maqueta.

Al mismo tiempo, el nodo va a albergar más de un servicio, con responsables distintos: la sección 7 de la hoja de ruta ya asigna el CUT al equipo SEM y los permisos de circulación a otro responsable.

## 2. Decisión

### 2.1 Los repositorios

| Repositorio | Qué contiene | Visibilidad |
|---|---|---|
| **`nodo-subdere`** | La aplicación: backend, frontend. La documentación base del nodo: hoja de ruta, ADR, registro de pendientes. Mientras dure, la maqueta | Interno |
| **`cut`** | El servicio de Códigos Únicos Territoriales, con su carpeta `nodo/` | Interno; su contrato lo publica la aplicación |
| **Un repositorio por servicio nuevo** | El servicio y su carpeta `nodo/` | Interno; su contrato lo publica la aplicación |
| **`conector-municipal`** | El conector de referencia del [ADR 2026-10](adr-2026-10-conector-municipal.md) | **Público, por diseño** |

El repositorio 1 es **el nodo**, no «la aplicación administradora». Por eso la documentación base vive ahí: la hoja de ruta y los ADR gobiernan el nodo completo, incluidos los servicios que viven en otros repositorios.

El conector es la excepción deliberada. Su razón de existir es que lo adopte un proveedor privado, y un proveedor no alcanza el GitLab interno de SUBDERE. Un conector que solo vive adentro no existe.

### 2.2 Lo que publica los contratos es la aplicación

El repositorio de un servicio es la **fuente** de su contrato. La **publicación** la hace la aplicación del nodo, que lee la ficha, resuelve la especificación que declara y la expone en el catálogo.

Esto tiene tres efectos que conviene nombrar:

- El contrato es alcanzable sin entrar al GitLab, que es la condición para que un proveedor pueda construir sin pedir permiso. Es el principio de que nadie tiene atajos, sostenido por la estructura y no por la buena voluntad.
- El repositorio del servicio puede ser interno sin que eso cierre el contrato.
- La aplicación del nodo deja de ser «el sitio» y pasa a ser **la pieza que no puede faltar**. Si está caída, no hay catálogo público.

### 2.3 La ficha se jala, no se empuja

La aplicación lee el archivo `nodo/ficha.yaml` del repositorio de cada servicio, con un token de solo lectura, y guarda el *commit* del que lo leyó. El formato está en [`estandar-ficha-de-servicio.md`](estandar-ficha-de-servicio.md).

Se descartó que cada servicio exponga su ficha como *endpoint*, por cuatro razones:

1. **La ficha tiene que existir antes que el servicio.** Hoy hay un intercambio visible sin servicio detrás y dos ocultos que no corren. El criterio de entrada al catálogo es contrato, pantalla y wiki, no servicio arriba. *Precisado el 10 de octubre de 2026:* basta la ficha; pantalla y wiki son vistas independientes y opcionales, y se muestran las que existan.
2. **El servicio puede estar en una red que la aplicación no alcanza.** El CUT responde hoy solo en la red SEM.
3. **La ficha es metadato de gobernanza** —responsable, ámbito, madurez—: cambia por decisión de una persona cada varios meses y conviene que pase por revisión y quede en el historial. Un *endpoint* cambia al desplegar, sin revisión y sin rastro.
4. **A un responsable se le puede pedir un archivo; un *endpoint* nuevo es pedirle código**, y el proyecto entero trata de bajar el costo de entrada.

Del modelo de *endpoint* se conserva una sola pieza: que el servicio informe **su versión en ejecución**, que ya quedó definido el 30 de septiembre de 2026. Así el catálogo puede mostrar que la ficha declara una versión y el servicio responde otra, que es la discrepancia que más confunde a un proveedor.

**La disponibilidad no va en la ficha.** La mide el monitor (HR-09). Una ficha que declara disponibilidad miente la primera vez que el servicio se cae.

### 2.4 Qué no entra a un repositorio

Cada repositorio tiene una carpeta `insumos/` **excluida del control de versiones**. Ahí va lo que nos pasan: yaml de referencia, planillas, borradores de terceros. Si no está en Git, no hay historial que limpiar después.

Los dos archivos que hoy están en `docs/` —`cut_stag.yaml` y `fiscalizacion_stag.yml`— se retiran del repositorio, y el segundo obliga además a revisar el historial, porque borrarlo del árbol de trabajo no lo saca de los *commits* anteriores.

### 2.5 La dirección del espejo

**El GitLab de SUBDERE es el origen. GitHub es espejo, y solo de lo que es público.** Hoy es al revés, según `CONTRIBUTING.md`. Invertirlo una vez cuesta un rato; invertirlo con cinco repositorios cuesta cinco veces ese rato, así que se invierte ahora.

La publicación de la maqueta en GitHub Pages **no se apaga en una fecha, se apaga en una condición**: cuando la aplicación del nodo sea alcanzable por la gente que necesita ver el sitio. Antes de eso, Pages es el único canal para mostrar algo, porque el GitLab institucional lo tiene bloqueado.

## 3. Cuándo nace un repositorio

| Gatillo | Qué se crea |
|---|---|
| Aparece un servicio con un responsable distinto | Un repositorio para ese servicio |
| Un tercero construye u opera un componente | Un repositorio propio: el límite del repositorio pasa a ser el límite del contrato, y así se puede entregar y auditar |
| Un componente tiene que ser adoptado desde fuera del Estado | Un repositorio público |

**Un repositorio de servicio puede llevar solo el contrato.** Cuando el servicio lo opera su dueño y no nosotros —el caso del CUT y de los permisos de circulación— el repositorio contiene únicamente la carpeta `nodo/`, y es custodia temporal hasta que el dueño de la fuente aloje el contrato junto al servicio. El traspaso es un cambio de dirección en el registro, no un servicio nuevo, porque el identificador de la ficha es inmutable. Está en el [ADR de acceso directo](adr-2026-10-acceso-directo-primera-etapa.md), §6.

No se parte preventivamente. Con un equipo chico, quince repositorios son peores que uno; lo que esta decisión fija es **dónde está el corte**, para que partir cueste poco cuando toque.

## 4. Consecuencias

1. **`estandares/` sale de `prototipos/`.** Mientras los servicios no tengan su repositorio, los contratos quedan en `estandares/` en la raíz, con su propio README y su `CODEOWNERS`. El *workflow* de Pages copia esa carpeta dentro de lo que publica, con lo que la maqueta sigue funcionando y se modela desde ya lo que hará el backend: sincronizar desde una fuente, no subir por el admin.
2. **El *workflow* de Pages se acota** a `prototipos/**` y `estandares/**`.
3. **El backend necesita un registro y una administración.** No existía en el diseño: está en `backend/README.md`, sección «Administración del catálogo».
4. **`CODEOWNERS` por área** en cada repositorio. Con eso, quién responde deja de ser una pregunta de organigrama (HR-04) y pasa a ser quién aprueba el *pull request*.
5. **Cada repositorio nuevo es otro espejo que mantener**, otro lugar donde se puede filtrar un secreto y otro `CODEOWNERS` que envejece. Conviene una línea base compartida: plantillas, *workflows* reutilizables y detección de secretos en todos.
6. **El repositorio no es el centro de información.** Sirve para lo que se revisa, se versiona y se difunde: estándares, decisiones, código. No para datos que cambian a diario, planillas, documentos que alguien edita en Word, ni nada con datos personales. El centro de información es la aplicación; el repositorio es la fuente.

## 5. Pendientes

| Id | Pendiente |
|---|---|
| **HR-20** | Dónde se despliega y se publica la aplicación del nodo, dado que el GitLab institucional tiene Pages bloqueado |
| **HR-22** | Token de lectura hacia los repositorios de servicio: quién lo emite, con qué alcance y cada cuánto se rota |
| **HR-23** | Qué se hace con los enlaces de GitHub Pages ya difundidos cuando se apague la publicación |
| **HR-25** | Río arriba del CUT: si el repositorio de su autor queda como fuente del código y cómo se le devuelven los cambios |

## Fuentes

- Estado actual del repositorio, verificado el 6 de octubre de 2026: `prototipos/estandares/` (cuatro OpenAPI), `docs/cut_stag.yaml`, `docs/fiscalizacion_stag.yml`, `.github/workflows/`, `.gitlab-ci.yml`, `CONTRIBUTING.md`.
- [`hoja-de-ruta.md`](hoja-de-ruta.md), §7 (responsables de contrato), §9 (componentes y estado), §10 (catálogo actual).
- [`adr-2026-09-estandar-legible-por-maquina.md`](adr-2026-09-estandar-legible-por-maquina.md), §3.3: SUBDERE publica el contrato de un tercero tal como lo entregó, y puede rechazar un registro pero no modificarlo.
- [`adr-2026-10-conector-municipal.md`](adr-2026-10-conector-municipal.md), §4: el conector es de código abierto y cualquier proveedor puede adoptarlo en las mismas condiciones.
