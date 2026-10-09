# ADR 2026-10 — Primera etapa: acceso directo a la fuente, con el contrato en forma PISEE

**Estado:** propuesta
**Fecha:** 7 de octubre de 2026
**Ámbito:** Nodo SUBDERE · CUT · permisos de circulación · puerta de acceso
**Relacionados:** [`adr-2026-10-estructura-de-repositorios.md`](adr-2026-10-estructura-de-repositorios.md), [`estandar-ficha-de-servicio.md`](estandar-ficha-de-servicio.md), [`plataforma-control.md`](plataforma-control.md), [`hoja-de-ruta.md`](hoja-de-ruta.md) §4.1 y §4.2, [`esquemas-de-intercambio.html`](esquemas-de-intercambio.html)

> **Decisión.** En la primera etapa, el CUT y los permisos de circulación se consumen **directamente desde su fuente en SEM**, a través de la puerta de acceso de SUBDERE y sin nodo de la Red. La vista de uso humano se autentica con **Clave Única** sobre un sistema de perfiles propio. Las APIs se publican con **datos sintéticos declarados en la ficha**. Y todo se construye con la **disciplina de contrato de PISEE**, de modo que migrar a la Red sea configuración y no reescritura.

---

## 1. Por qué se puede, caso por caso

No es una excepción que haya que justificar: cada pieza de la primera etapa cae en un canal que la propia norma deja fuera del concepto de interoperabilidad.

| Pieza | Por qué queda fuera de la Red |
|---|---|
| **CUT** | Es dato abierto. El artículo 19 del Decreto N° 12 dispone que los datos abiertos «serán directamente consumidos por los órganos de la Administración del Estado, no siendo parte del concepto de interoperabilidad de esta norma». Es la única excepción explícita del decreto y nos cubre completa |
| **Permisos de circulación, consumido por un sistema de SUBDERE** | La fuente es SEM, una plataforma de SUBDERE, y el consumidor también. Es un intercambio dentro de un mismo órgano |
| **Las vistas de uso humano** | Una persona que se autentica y consulta por pantalla es el canal de plataforma de trámite, no interoperabilidad. Es lo que hace MiChileAtiende para el Nodo Laboral y Previsional, su mayor consumidor según la 3ª Mesa Técnica |
| **La zona de práctica y los ambientes con datos sintéticos** | No involucran datos reales ni a otro órgano |

> **Cómo se leyeron las fuentes.** El Decreto N° 12 de 2023 se leyó directo del texto actualizado de la Biblioteca del Congreso, en su versión al 24 de diciembre de 2025. La conclusión de que un consumidor municipal cambia el encuadre es nuestra, no del texto: queda para el equipo jurídico.

## 2. El borde que esta decisión no cubre

**Un sistema municipal consumiendo máquina a máquina, para un trámite municipal.** Ahí son dos órganos y la pregunta vuelve, con el horizonte del artículo segundo transitorio: desde el 31 de diciembre de 2026 la Red es la única vía de interoperabilidad entre órganos.

El borde no está entre el CUT y los permisos de circulación, ni entre una tecnología y otra: está en **quién consume**. Mientras los consumidores sean de la casa o personas por pantalla, la primera etapa es libre.

## 3. Qué se copia de PISEE, y qué no

El principio es **copiar la disciplina de contrato, no el transporte.** Replicar TLS mutuo, firma de mensajes o tokens de un módulo central sería construir transporte propio: trabajo que se bota el día que aparezca el nodo, y exactamente lo que el Nodo Laboral y Previsional evitó al integrarse de forma nativa a PISEE 2.0.

**Se adopta desde ya:**

1. **Los metadatos de trazabilidad del artículo 9** como campos de primera clase en cada petición: órgano requirente, funcionario responsable, procedimiento y fecha. Viajan también por el camino directo. Es lo que hace que la migración sea configuración.
2. **El nombre del servicio tal como aparecería en el Catálogo de Servicios**, registrado en la ficha. Es el valor que un municipio escribiría en la configuración de su nodo.
3. **Consulta y respuesta sincrónica.** PISEE, como X-Road, no tiene mensajería asincrónica. Si hiciera falta algo asincrónico, se declara como extensión local que no sobrevive a la migración.
4. **Un identificador de trámite por transacción, con idempotencia.** Un reintento no duplica la entrega, y es la unidad con que la Red cuenta transacciones.
5. **Un límite de tamaño de mensaje declarado en el contrato.** PISEE separa el mensaje normal del envío de archivos grandes y su umbral no está documentado (X-122). Declarar un límite propio ahora es más barato que descubrirlo después.
6. **Los códigos del Estado**, partiendo por el propio CUT, en vez de catálogos paralelos.

**No se adopta:** TLS mutuo, firma de mensajes, tokens del módulo central, ni el formato de error de PISEE, que no está documentado (X-121). Los errores se normalizan en un solo lugar, para que cambiar de formato sea un módulo.

## 4. La vista de uso humano

Clave Única autentica, **no autoriza**. Que la persona sea funcionaria del municipio de Marchigüe y pueda ver lo de Marchigüe lo dice el sistema de perfiles del nodo, no Clave Única.

Dos requisitos que se modelan desde el principio porque después son una migración:

- **Administración delegada.** Si SUBDERE da de alta a los funcionarios uno por uno, no escala a 345 municipios. Hace falta un rol de administrador por municipio que dé de alta a los suyos (HR-27). **Resuelto el 7 de octubre de 2026:** cada municipio tiene un encargado que arma su equipo en el nodo, y los administradores de SUBDERE pueden hacer lo mismo y reemplazar al encargado. Detalle en `backend/apps/cuentas/INSTRUCCIONES.md` §4.
- **Registro de accesos.** Las vistas muestran datos personales: patente y titular. Que un funcionario del municipio A consulte un vehículo del municipio B tiene que quedar registrado — quién consultó qué y cuándo. Es el equivalente humano de la trazabilidad del artículo 9 (HR-28).

## 5. Datos sintéticos

Las APIs se publican con datos sintéticos mientras no haya datos reales detrás, y **la ficha lo declara**: el campo `ambientes[].datos` del [estándar de la ficha](estandar-ficha-de-servicio.md) toma los valores `inventados` o `reales`. Así la premisa «lo publicado funciona» sigue siendo cierta sin que nadie se confunda.

Sintéticos de verdad: patentes inventadas que pasen la validación de formato y RUT que no correspondan a nadie. **No datos reales con los nombres borrados**, que es el atajo habitual y el modo de falla habitual. En este repositorio ya quedó versionado un archivo con nombre y RUT reales.

## 6. Los repositorios de estos dos servicios

Juan Helo entrega las APIs y queda como dueño de la fuente. Eso cambia lo que contienen sus repositorios respecto del caso general del [ADR de estructura](adr-2026-10-estructura-de-repositorios.md): **no llevan el servicio, llevan solo el contrato.**

| Etapa | Dónde vive el contrato | Dónde corre el servicio |
|---|---|---|
| **Ahora** | Un repositorio nuestro por servicio, con solo la carpeta `nodo/`: la ficha y el yaml del estándar | En la fuente, operada por su dueño |
| **Cuando se pruebe que funciona** | Se le pide al dueño de la fuente que aloje el contrato junto al servicio, y que lo complete con la información definitiva | En la fuente |

El traspaso es **un cambio de dirección en el registro, no un servicio nuevo**: el identificador de la ficha es inmutable, así que la fuente apunta a otro repositorio y el historial de lecturas queda mostrando cuándo se movió la custodia. Esa es la razón por la que el identificador no se corrige nunca (HR-25).

## 7. Consecuencias

1. **La Etapa 1 deja de depender de la Secretaría de Gobierno Digital.** Avanza completa —puerta, perfiles, vistas humanas, APIs publicadas con datos sintéticos— mientras HR-26 sigue abierto. La pregunta del nodo pasa a la Etapa 2, cuando aparezca el primer sistema municipal consumiendo máquina a máquina.
2. **La puerta de acceso queda en la ruta crítica**, y por razones propias: es donde se resuelve la identidad, los permisos por municipio y el registro. Se necesitaba igual en cualquier escenario.
3. **SUBDERE pasa a ser el primer consumidor serio de las APIs de SEM.** Vamos a encontrar sus huecos, y documentarlos produce el contrato que hoy no existe.
4. **Los contratos publicados son portables.** Si mañana hay que mover la salida a la Red, cambia por dónde sale el mensaje, no su forma ni sus campos.
5. **Nada de esto se declara en el sitio como compromiso institucional.** El catálogo sigue publicando lo que existe, con su estado real.

## 8. Pendientes

| Id | Pendiente |
|---|---|
| **HR-27** | Administración delegada de perfiles: quién da de alta a los funcionarios de cada municipio. **Resuelto** (§4) |
| **HR-28** | Registro de accesos de las vistas de uso humano: qué se guarda, por cuánto tiempo y quién lo revisa |
| **HR-25** | Traspaso de la custodia del contrato al dueño de la fuente, y en qué momento se pide |
| **HR-26** | Sigue abierto, pero fuera de la ruta crítica de la Etapa 1 |
| **X-122** | Límite de tamaño de mensaje, para declarar uno propio que sea portable |

## Fuentes

- Decreto N° 12, de 2023, del Ministerio Secretaría General de la Presidencia, Norma Técnica de Interoperabilidad, artículos 9 y 19 y artículo segundo transitorio. Texto actualizado al 24 de diciembre de 2025: <https://www.bcn.cl/leychile/Navegar?idNorma=1195125>.
- Decreto N° 876, de 2025, del Ministerio de Hacienda, que modifica el anterior. Publicado el 24 de diciembre de 2025, CVE 2743271.
- [`nodo-lp-precedente.md`](nodo-lp-precedente.md): la plataforma del Nodo Laboral y Previsional está integrada de forma nativa a PISEE 2.0 y no construyó transporte propio; su mayor consumidor es un portal de atención a personas.
