# Nodo SUBDERE — maqueta del sitio

Maqueta estática para revisión, previa al desarrollo en Django + React.
Sin build, sin dependencias: vive en [`prototipos/`](../prototipos/). Se abre con doble clic o se publica tal cual.

## Páginas

| Archivo | Qué es |
|---|---|
| `prototipos/index.html` | Landing — qué es el nodo y para quién |
| `prototipos/que-es.html` | Descripción general: cómo funciona, alcance de la validación, los tres casos de municipio |
| `prototipos/catalogo.html` | **Servicios.** Las herramientas de uso humano construidas sobre las APIs. Conserva el nombre de archivo por los enlaces ya compartidos; en Django la ruta es `/servicios/` |
| `prototipos/apis.html` | **APIs.** Los intercambios visibles del catálogo, agrupados por ámbito y con buscador, y una tarjeta de ejemplo anotada que explica cada parte |
| `prototipos/servicio-cut.html` | Buscador de códigos territoriales |
| `prototipos/servicio-fiscalizacion.html` | Consulta de permiso de circulación por patente |
| `prototipos/wiki-fiscalizacion.html` | Entrada de wiki de los permisos de circulación |
| `prototipos/assets/fiscalizacion-demo.js` | Datos ficticios y casos de prueba de permisos de circulación. Los usan el ambiente de pruebas de la ficha y la aplicación de consulta |
| `prototipos/assets/cut-demo.js` | Extracto del catálogo CUT (Tarapacá, Maule y Ñuble completas, con códigos oficiales) y casos de prueba del ambiente de pruebas de su ficha |
| `prototipos/assets/servicio.js` | Plantilla de la página de un servicio: arma cabecera, fuentes y panel lateral desde `SERVICIOS`. Ver [`plantillas.md`](plantillas.md) |
| `prototipos/assets/sandbox.js` | Motor del ambiente de pruebas de una ficha: ejecuta el contrato OpenAPI contra datos ficticios |
| `prototipos/wiki.html` | **Wiki.** Portada: qué es la wiki, a quién está dirigida y cómo está ordenada |
| `prototipos/wiki-recorrido.html` | Wiki · Cómo funciona un intercambio: entregar y preguntar, los cuatro pasos de una entrega, qué se revisa y la puerta |
| `prototipos/wiki-consumir.html` | Wiki · Cómo se usa una API del catálogo |
| `prototipos/wiki-conectar.html` | Wiki · Conectar un sistema: los tres casos, el paso a paso, práctica y operación, versiones |
| `prototipos/wiki-ficha.html` | Wiki · Cómo leer una ficha: disponibilidad, procedencia y acceso |
| `prototipos/wiki-intercambios.html` | Wiki · Índice de entradas, generado desde `NODOS` con buscador |
| `prototipos/wiki-cut.html` | Entrada de wiki de los Códigos Únicos Territoriales |
| `prototipos/wiki-codigos.html` | Wiki · Índice de códigos y datos maestros |
| `prototipos/wiki-normas.html` | Wiki · Marco normativo |
| `prototipos/wiki-glosario.html` | Wiki · Glosario de términos del sitio |
| `prototipos/wiki-decisiones.html` | Wiki · Decisiones de arquitectura |
| `prototipos/assets/wiki-nav.js` | Barra lateral común de la wiki (`WIKI_NAV`) e índice «En esta página». Ver «La wiki, ordenada como WikiGuías» |
| `prototipos/assets/pie.js` | Pie común de todas las páginas. Cada página deja `<footer id="pie"></footer>` y carga el script justo después; `data-nota` reemplaza la segunda línea cuando la página necesita citar su fuente |
| `prototipos/nodo.html?id=<slug>` | Ficha de un nodo. Una sola plantilla sirve a todos |
| `prototipos/participar.html` | Cómo participar y qué está definido y qué no |
| `prototipos/404.html` | Página de error. Usa rutas absolutas `/nodo-subdere/…` porque se sirve desde cualquier URL — **por eso se ve sin estilos si se abre con doble clic**, y bien una vez publicada |
| `prototipos/assets/data.js` | **Los datos y el modelo.** Cada campo de aquí debería existir en el modelo Django |
| `prototipos/estandares/` | Las especificaciones registradas localmente: copia del CUT, propuesta de permisos de circulación e instantánea ensamblada de Adquisiciones |
| `prototipos/_to_delete/` | Archivos retirados, a la espera de borrarse del repositorio |
| `prototipos/assets/openapi.js` | Renderiza una especificación OpenAPI en la ficha. Nada de lo que se ve ahí está transcrito |
| `prototipos/assets/js-yaml.min.js` | Lector de YAML, incluido para no depender de la red |
| `prototipos/assets/styles.css` | Estilos, con la paleta del proyecto en variables CSS |
| `prototipos/assets/favicon.svg` | Ícono del sitio |
| `prototipos/assets/og.png` | Imagen de previsualización cuando se comparte el enlace |

Las rutas son todas relativas —salvo las de `404.html`, por lo dicho arriba—, así que el sitio funciona igual en un subdirectorio que en la raíz. Cómo publicarlo está en el [README del repositorio](../README.md).

El catálogo guarda el filtro y la búsqueda en la dirección, así que `catalogo.html?ambito=SGM` se puede compartir tal cual.

## El modelo del catálogo

`prototipos/assets/data.js` es la maqueta del modelo. Cómo usan estos campos las plantillas de API y de servicio, y qué edita el mantenedor, está en [`plantillas.md`](plantillas.md). Los campos:

| Campo | Tipo | Nota |
|---|---|---|
| `id` | slug | Clave de la URL de la ficha |
| `nombre` | texto | |
| `ambito` | opción | **SGM** · Transversal. La lista se recortó con el catálogo; vuelve a crecer con él |
| `clase` | opción | **intercambio** (módulo o canal de datos) · **plataforma** (condición de otros; no se elige por módulo) |
| `funcion` | texto corto | Una línea, aparece en la tarjeta del catálogo |
| `descripcion` | texto largo | Cuerpo de la ficha |
| `instituciones` | lista | Relación en Django, no texto libre |
| `intercambio` | opción | Bidireccional · El municipio entrega · El municipio consulta · Transversal |
| `madurez` | opción | Deseable · En evaluación · En desarrollo · Operativo |
| `factibilidad` | opción | Por evaluar · Alta · Media · Baja |
| `origen` | texto | De dónde salió el nodo, para poder auditar el catálogo |
| `nota` | texto | Advertencia destacada en la ficha, opcional |
| `oculto` | booleano | `true` = existe en el modelo y no se lista. Ver más abajo |
| `descargables` | lista | `{ archivo, que, url?, generar? }`. Con `url` el archivo existe y se descarga; con `generar: "sandbox"` se arma en el navegador con los datos de prueba. Sin ninguno de los dos, se lista como ejemplo |
| `sandbox` | objeto | `{ script }`. La ficha tiene un ambiente de pruebas; `script` registra los datos y el responder. Requiere `espec.archivo` |
| `espec.procedencia` | objeto | `{ responsable, fuente, copia, detalle, observaciones? }`. Reemplaza al texto libre `espec.origen`. `copia` es `exacta`, `instantanea`, `reconstruccion` o `sin-copia`, y dice qué relación tiene lo que muestra el catálogo con la fuente oficial. `observaciones` es `{ texto, url }` y apunta a la wiki, donde van las diferencias y las preguntas abiertas |
| `dependencias` | lista | `{ nombre, id? }` — qué hay que tener implementado antes. `id` enlaza otra ficha; si falta, el módulo todavía no está en el catálogo |
| `wiki` | ruta | Entrada del intercambio en la wiki (`wiki-cut.html`). Con ella se arma `wiki-intercambios.html`; un nodo visible sin este campo aparece como «Entrada pendiente» |

**`clase` distingue dos figuras.** Un nodo `intercambio` es elegible (incluido el consumo por módulo cuando aplique). Un nodo `plataforma` es condición de otros: hoy, el core SGM. Sin ese campo, el core se leería como un módulo más.

Los dos campos que conviene no dejar para después son **`madurez`** y **`factibilidad`**: agregar una columna a un modelo que ya tiene datos y vistas siempre cuesta más que preverla. María José dejó esa evaluación explícitamente pendiente, y el catálogo es el lugar natural donde vive. Desde el 30 de septiembre de 2026 siguen en el modelo, pero el sitio no los muestra (ver «Lo publicado funciona»).

### El contrato técnico, cuando existe

Dos campos más, opcionales. Un nodo que no los trae muestra el bloque «Pendiente» correspondiente en su ficha.

| Campo | Tipo | Nota |
|---|---|---|
| `espec` | objeto | `{ archivo?, formato, validador, registrada, origen, acceso, expuesto? }` — `archivo` es opcional. `expuesto` distingue contrato registrado de servicio alcanzable |
| `pruebas` | texto | Estado del ambiente de pruebas |

**Hay estándar ≠ hay servicio alcanzable.** La ficha los separa con `espec.expuesto`. `cut` tiene archivo local (copia) y servicio existente (en red SEM). `fiscalizacion` tiene archivo local, que es una propuesta escrita para la demostración, sin servicio detrás. `adquisiciones` tiene archivo local que es una instantánea ensamblada del OpenAPI seccionado del corpus SGM (versión 0.1.0, 16 de septiembre de 2026); el servicio no está expuesto. `sgm-core` declara metadato de contrato sin archivo local.

**No hay un campo `operaciones`, y es deliberado.** Cuando hay `espec.archivo`, la ficha lo lee y lo renderiza. Cuando solo hay metadato, no se transcriben operaciones. La decisión está en [`adr-2026-09-estandar-legible-por-maquina.md`](adr-2026-09-estandar-legible-por-maquina.md).

En el modelo Django, `espec` es un documento versionado —cada versión se registra, ninguna se corrige— y **se versiona aparte de la ficha**: el contrato puede cambiar sin que cambie la descripción del nodo, y al revés.

Las especificaciones registradas localmente viven en [`prototipos/estandares/`](../prototipos/estandares/). El renderizador es [`prototipos/assets/openapi.js`](../prototipos/assets/openapi.js), y [`js-yaml.min.js`](../prototipos/assets/js-yaml.min.js) viene junto para no depender de la red. Límite de la maqueta: solo resuelve `$ref` internos (`#/…`); no ensambla specs seccionadas en varios archivos. Por eso Adquisiciones se publica ya ensamblada: la fuente viva sigue seccionada en el corpus SGM y esta copia no se edita aquí.

**Una consecuencia práctica:** la ficha de un nodo con `espec.archivo` **no funciona abriendo el archivo con doble clic**, porque el navegador no permite que una página local lea otro archivo del disco. La página lo explica cuando ocurre. Para verla hay que servir la carpeta.

## Datos

El catálogo tiene **dos intercambios visibles**: los Códigos Únicos Territoriales y los permisos de circulación. La decisión es de la jefatura, del 26 de septiembre de 2026, y el criterio es preferir una entrada completa —contrato publicado, pantalla que lo usa, entrada de wiki— antes que una lista larga de intenciones.

| Nodo | Estado en el catálogo |
|---|---|
| `cut` — Códigos Únicos Territoriales | Visible |
| `fiscalizacion` — Permisos de circulación por patente | Visible. Con ambiente de pruebas y aplicación vinculada |
| `sgm-core` — Base común del SGM | **Oculto.** Sigue en el modelo; su ficha se alcanza por enlace directo |
| `adquisiciones` | **Oculto**, en las mismas condiciones |

Se retiraron del archivo los nueve nodos que venían del mapeo de interoperabilidad del Juzgado de Policía Local de Lo Barnechea y del levantamiento municipal: `pagos-tesoreria`, `indice-expedientes`, `notificador-electronico`, `dom`, `nodos-gobierno`, `correos`, `inspeccion-municipal`, `direcciones-municipales` y `entre-juzgados`.

**Salen del catálogo, no del levantamiento.** Siguen siendo intercambios reales que alguien necesita, y el trabajo de María José Besa y Allison Díaz que los identificó no se pierde: está en el mapeo original. Lo que cambió es el umbral para aparecer acá. Cuando uno de ellos tenga contrato publicado, vuelve.

`nodos-gobierno` (Estándares de Gobierno Digital) es la excepción: ya se había retirado el 16 de septiembre de 2026 por otra razón, y esa no cambia aunque el umbral baje. Es condición de capa —Clave Única, FirmaGob, la plataforma de interoperabilidad del Estado—, no un intercambio que el municipio active. Sigue siendo restricción sobre el resto; no es ficha del catálogo.

### El campo `oculto`

`oculto: true` significa que el nodo existe en el modelo y no aparece en los listados, pero su ficha sigue siendo alcanzable por enlace directo. La ficha lo dice en un aviso: está en preparación y puede cambiar antes de publicarse.

Es distinto de borrarlo y distinto de un estado de madurez. La madurez describe **qué tan avanzado está el intercambio**; `oculto` describe **si se muestra**. Un nodo puede estar en desarrollo y ser visible, como el CUT, o estar en desarrollo y no mostrarse todavía, como los dos del SGM. En Django es un campo booleano del modelo con un `manager` por defecto que filtra, no una consulta que cada vista tenga que recordar.

**Consecuencia para la vista de APIs:** se retiraron los filtros por ámbito. Con un intercambio visible no ordenan nada, y volverán cuando la lista lo justifique. El buscador se mantiene.

## La navegación, y por qué se separó en tres

La jefatura pidió distinguir tres usos que antes estaban mezclados en una sola página. La barra superior los refleja:

| Entrada | Para qué se entra | Archivo |
|---|---|---|
| **APIs** | Construir contra un contrato publicado: formato, validador, versión, acceso | `apis.html` |
| **Servicios** | Buscar qué intercambios existen, leerlos en lenguaje común, filtrar por ámbito | `catalogo.html` |
| **Wiki** | Entender cómo se usa, cómo se generan los códigos y qué norma obliga qué | `wiki.html` |

La distinción entre Servicios y APIs **no es cosmética y se ve en los datos**: Servicios lista los doce intercambios del catálogo, incluidos los nueve que están solo en estado deseable; APIs lista únicamente los tres que tienen `espec`, o sea contrato publicado. Si la única diferencia fuera el tono del texto, no justificaría dos páginas.

Desde el 28 de septiembre de 2026, APIs y Servicios son pestañas independientes en la barra, en el mismo orden que las presenta el hero de la portada. Antes compartían un desplegable «Catálogos». Con eso la barra quedó solo con enlaces, y `assets/nav.js` —que cerraba el desplegable— pasó a `_to_delete/`. La ficha de un nodo (`nodo.html`) cuelga de APIs.

**Se retiró la página de comentarios.** Las preguntas para el QA que vivían ahí están más abajo, en este mismo documento, que es donde corresponde: son una pauta de trabajo del equipo, no contenido de un sitio público.

## El CUT como caso completo

Los **Códigos Únicos Territoriales** son el primer intercambio con las tres vistas escritas, y sirve de molde para los que vengan.

| Vista | Dónde | Qué responde |
|---|---|---|
| APIs | [`apis.html`](../prototipos/apis.html) → [`nodo.html?id=cut`](../prototipos/nodo.html?id=cut) | Qué entrega, con quién conversa, en qué estado está, y la especificación renderizada operación por operación |
| Servicios | [`servicio-cut.html`](../prototipos/servicio-cut.html) | Buscar el código de una comuna, o el lugar de un código, sin programar |
| Wiki | [`wiki-cut.html`](../prototipos/wiki-cut.html) | Cómo se compone el código, qué decreto lo fija, comuna versus municipio, y las observaciones al contrato |

El nodo se llamaba «División Político-Administrativa» y pasó a llamarse por su nombre propio. El id cambió de `division-territorial` a `cut`, y `nodo.html` mantiene un alias para que los enlaces ya compartidos sigan funcionando; en Django eso es una redirección permanente, no un diccionario.

**La especificación** es `cut_stag.yaml`, la versión de referencia que entregó Juan Helo en septiembre de 2026, copiada sin cambios a [`prototipos/estandares/cut.openapi.yaml`](../prototipos/estandares/cut.openapi.yaml). Once operaciones, todas de consulta, y solo referencias internas: el renderizador la lee entera sin ensamblar nada.

### Qué es un servicio y qué es una API

Los dos catálogos responden preguntas distintas, y la distinción define qué va en cada uno.

**APIs** es el catálogo de intercambios: los doce nodos, con su ficha, su estado y —cuando existe— su contrato renderizado operación por operación. Es la vista para quien va a construir, y mantiene la misma presentación de tarjetas con filtro por ámbito y buscador que tenía desde el principio.

**Servicios** es el catálogo de pantallas construidas sobre esas APIs, que resuelven una tarea sin programar. Un servicio no es un intercambio: es un consumidor de uno. Por eso `SERVICIOS` es un arreglo aparte en `data.js`, con sus propios campos —`nodo`, `url`, `tareas`, `estado`—, y no una vista filtrada de `NODOS`.

La regla que ordena la relación: **el servicio no tiene atajos.** Consume la interfaz pública, la misma que usaría el sistema de un municipio o de un proveedor. Si una pantalla de SUBDERE pudiera llegar a datos que la interfaz no expone, el catálogo de APIs dejaría de describir lo que de verdad se puede construir. Es la regla de 6.2 de la minuta, aplicada al propio sitio.

### El buscador de códigos territoriales

Es el primer servicio y el molde de los que vengan. Resuelve las dos direcciones con un solo campo: nombre → código, y código → lugar. Detecta si lo escrito son dígitos o letras y actúa en consecuencia; dos dígitos se leen como región, tres como provincia y cinco como comuna.

Tres decisiones que conviene conservar al llevarlo a Django:

- **No tiene lista propia.** Consulta `GET /regiones`, `/provincias` y `/comunas` al abrir, y arma el índice en el cliente. La jerarquía se reconstruye con el propio código —el de una comuna empieza por el de su provincia— en vez de pedir un campo padre que la API no entrega. Es la propiedad que hace útil al CUT, usada como corresponde.
- **Muestra el código en su forma canónica.** La API los entrega como entero, así que Iquique llega como `1101`; la pantalla lo rellena a `01101`. Es la observación 01 de [la entrada de wiki del CUT](../prototipos/wiki-cut.html), y la pantalla la corrige a la vista en lugar de esconderla. Si el contrato se arregla, este relleno sobra y se borra.
- **Degrada con honestidad.** Cuando el servicio no está alcanzable, funciona con cinco comunas de demostración —las únicas que aparecen en los documentos de SUBDERE que se revisaron— y lo dice en pantalla con el número real del catálogo, 346. Para apuntarlo a otro servidor se agrega `?api=http://localhost:8000` a la dirección, sin tocar el archivo.

**Hay un segundo archivo en `docs/`**, `fiscalizacion_stag.yml`, que todavía no se incorporó al catálogo.

## Los permisos de circulación: una demostración, y qué cuidado tuvo

Se agregó como segundo caso completo el 27 de septiembre de 2026, para conversarlo con la Secretaría de Gobierno Digital. **Es una demostración y el sitio lo dice en cada pantalla:** no pasa por control de calidad, no hay compromiso de disponibilidad y los datos son inventados.

El insumo fue `fiscalizacion_stag.yml`, una colección de consultas del equipo de Servicios Municipales exportada a OpenAPI. No es un contrato: las patentes van dentro de la ruta —cuatro direcciones fijas, una por vehículo consultado—, no hay parámetros, no hay errores declarados, no hay autenticación, hay dos envoltorios de respuesta distintos y el servidor de pruebas quedó escrito adentro.

Lo que se publica en el catálogo es **una propuesta de contrato reconstruida**, no la colección. Eso está dicho en la descripción del propio archivo YAML, en la procedencia del nodo (`espec.procedencia.copia: "reconstruccion"`) y en la nota de la ficha, que es la única advertencia de demostración que se mantiene (ver «Ambiente de pruebas y aplicación vinculada»). La comparación entre una y otra es el contenido de [`wiki-fiscalizacion.html`](../prototipos/wiki-fiscalizacion.html), y es también la agenda de la conversación con Servicios Municipales.

### El dato personal que no viajó

La colección de referencia traía, en uno de sus ejemplos de respuesta, el nombre y el RUT del representante de una automotora, además del RUT, la razón social y la dirección de la empresa. Otros registros del mismo archivo sí estaban anonimizados, lo que sugiere una limpieza a medio hacer.

**Nada de eso entró al prototipo.** Todos los ejemplos del contrato publicado y todos los datos de la pantalla son inventados, y el modelo se cambió además en el fondo: la respuesta de un permiso provisional entrega la persona jurídica titular y no los datos de su representante, porque para comprobar un permiso no hace falta saber quién firma por la empresa.

Queda una recomendación que excede al prototipo: **`docs/fiscalizacion_stag.yml` no debería estar en un repositorio que se publica**, y borrar el archivo no basta si ya se subió, porque el historial lo conserva.

### Por qué esta demostración vale como argumento

El permiso de circulación identifica a la institución recaudadora. En la colección de referencia venía como texto libre —`NUNOA`, `SAN FELIPE`, `LA REINA`—, sin acentos ni código. En la propuesta viaja como objeto con su Código Único Territorial.

Es el primer intercambio del catálogo que consume un estándar publicado por otro intercambio del catálogo. Eso es lo que convierte una lista de servicios en un estándar, y es más fácil de mostrar que de explicar.

## Identidad gráfica

El sitio sigue el **Kit Gráfico de Gobierno de Chile** (lineamientos del 11 de marzo de 2026) y el logotipo institucional de la Subsecretaría. Todo está en variables CSS al inicio de [`styles.css`](../prototipos/assets/styles.css), así que cambiar la paleta es editar un bloque.

| Token | Valor | Origen |
|---|---|---|
| `--navy` | `#25306B` | Color base, Pantone 2756C |
| `--azul` | `#006BB9` | Color base, Pantone 2175C. Botón primario y enlaces |
| `--rojo` | `#FF1D3D` | Color base, Pantone 1788c. Solo como marca gráfica |
| `--grey` | `#EDF0F5` | Color base, Pantone 663C. Fondo de secciones |

El hero usa el gradiente oficial `#25306B → #006BB9`, con el azul empujado al extremo derecho para que el texto quede siempre sobre el navy.

**Dos ajustes de accesibilidad**, porque los colores de marca están pensados para impreso:

- El rojo `#FF1D3D` sobre blanco da 3,8:1 y no alcanza el mínimo para texto pequeño. Los números de las tarjetas usan `--rojo-tx` (`#D6102B`, 5,3:1). El rojo pleno se reserva para elementos gráficos —el subrayado de la página actual, el borde de los avisos— donde el mínimo no aplica.
- La banda gris de avisos (`.alerta`) es neutra, para que el rojo signifique una sola cosa en el sitio. Desde el 29 de septiembre de 2026 ya no se usa para decir «maqueta para revisión» (ver «Marcas de maqueta, badges y disponibilidad»).

Todos los pares de color del sitio se verificaron contra el mínimo 4,5:1 de la W3C, que es lo que exigen las *Recomendaciones e indicaciones para sitios web institucionales*.

**Tipografía.** El kit define gobCL para titulares y Museo Sans para cuerpo. Museo Sans es comercial: el sitio la reemplaza por una pila de sistema. gobCL está declarada con `@font-face` y se activa dejando los `.woff2` en `prototipos/assets/fonts/` —ver el README de esa carpeta—. Sin los archivos el sitio no se rompe: cae en la pila de respaldo.

**Logotipo.** La versión monocromo blanca va en el pie de todas las páginas, a 88 px de alto, que es donde el nombre completo de la Subsecretaría todavía se lee. En la barra superior se mantiene la marca tipográfica, porque el logotipo es un bloque casi cuadrado y a 44 px su texto sería ilegible. El archivo es [`assets/logo-subdere-blanco.png`](../prototipos/assets/logo-subdere-blanco.png), recortado y reducido desde el original del kit: 17 kB, bajo el límite de 100 kB que recomienda la guía.

## Qué describe el sitio, y qué no

**Decisión de la reunión del 23 de septiembre de 2026.** La arquitectura quedó definida por la jefatura de la División: SUBDERE se conecta con el resto del Estado por sus nodos de la Red de Interoperabilidad o por los convenios que ya tiene vigentes, y expone a los municipios los servicios resultantes mediante interfaces programables, con una capa de identidad y una de control de paso. El sitio se escribe sobre esa definición.

Consecuencia editorial, y es la regla que conviene mantener: **el sitio describe el lado municipal y no declara una topología de transporte.** Lo que el municipio obtiene —estándares publicados, validación antes de enviar, comprobante, una credencial— es exacto y útil sin que la portada afirme por dónde viaja después la información. Mientras menos declare el sitio sobre el lado de SUBDERE hacia el resto del Estado, menos queda comprometido por escrito antes de que la jefatura lo resuelva.

Por eso se retiraron dos promesas de la portada anterior:

- **«Una sola puerta entre el municipio y el Estado»** y **«el nodo la reparte a cada destino»**. El reenvío a terceros dejó de enunciarse como característica. Desde el 28 de septiembre de 2026, `que-es.html` tampoco describe qué hace el nodo con lo que el municipio envía a otros organismos: las filas «Le da el formato» y «Prepara el documento» se retiraron porque ese levantamiento todavía no está hecho. Lo que sí se afirma, en primera persona, es que **la información que SUBDERE recopila de las municipalidades queda estandarizada en el nodo**.
- **«Un solo registro, no uno por plataforma»**, que describía un padrón de funcionarios administrado por SUBDERE. Quedó como **«una credencial del municipio»**, que es la capa de identidad de la puerta y no un registro paralelo.

El nombre del proyecto se define en el título del hero: **«Nodo SUBDERE, la plataforma de encuentro municipal»**, porque «Nodo SUBDERE» por sí solo se lee como una red aparte. El párrafo que lo acompaña se ordena por las tres piezas del sitio —catálogo de APIs, catálogo de servicios y wiki—, y la relación con el resto del Estado quedó en la tarjeta «SUBDERE se ocupa del resto del Estado». Esa tarjeta ya no se defiende de parecer una red paralela: presenta la interoperabilidad con el Estado como algo que SUBDERE le resuelve al municipio. Es una excepción consciente a la regla de arriba y queda marcada como redacción pendiente hasta que la jefatura la confirme. Hasta el 28 de septiembre de 2026 esa función la cumplía una sección aparte, «Un catálogo, una puerta y un compromiso de operación», que se retiró porque su tercer punto no decía nada concreto y lo demás repetía la tarjeta.

**El comprobante no se presenta como algo que hoy falta.** El municipio ya recibe comprobantes de lo que entrega; lo que no tiene es uno con la misma forma para todos los intercambios y que diga contra qué versión de la regla se revisó el envío. El sitio no afirma que el municipio «no tiene cómo comprobar» lo que mandó.

El nombre se mantiene por continuidad con lo ya conversado con el equipo y con la Secretaría de Gobierno Digital. La separación en tres sitios que pidió la jefatura —catálogo, servicios y wiki— queda para cuando el contenido de cada uno justifique su propia navegación.

## Tono y reparto de contenido

**Tono afirmativo.** Los encabezados dicen qué propone o qué aporta la plataforma, no qué «hoy no pasa». Se escriben desde quien la usa —el municipio, un proveedor, una institución que recibe información— y no desde el proceso interno de SUBDERE.

**Cada página tiene un alcance y no invade el de las otras:**

| Página | Qué cuenta |
|---|---|
| `index.html` | Global. El hero, «Qué propone» (una forma común de pedir y entregar información), las tres piezas con su enlace y lo que el municipio puede esperar |
| `que-es.html` | Cómo funciona el intercambio que sostiene las tres piezas: publicar, revisar, autorizar, comprobante, la puerta y el paso de práctica a operación |
| `apis.html` | Construir: los contratos publicados, y qué dice cada parte de la tarjeta. El detalle de procedencia y acceso está en `wiki-ficha.html` |
| `catalogo.html` | Usar: las aplicaciones construidas sobre las APIs |
| `wiki.html` | Entender: cómo se usa cada intercambio y por qué está definido así |

Por eso la portada ya no tiene las tarjetas del mecanismo (formato publicado, revisión previa, comprobante, credencial) ni la sección «Cómo está armado»: lo primero está en `que-es.html` y lo segundo en [`wiki-ficha.html`](../prototipos/wiki-ficha.html). Hasta el 29 de septiembre de 2026 las tablas de madurez y disponibilidad estaban en la sección «Cómo leer el estado» de `apis.html`. Desde el 30 de septiembre esa sección es «Cómo leer una tarjeta» (ver «Lo publicado funciona»). `que-es.html` conserva su explicación completa y enlaza a `wiki-recorrido.html` y `wiki-conectar.html` con «Más detalle en la wiki». La sección «Lo que el nodo no es» pasó a «Lo que el municipio puede esperar», con cuatro tarjetas en redacción afirmativa.

`que-es.html` decía «el nodo conecta sistemas, no personas», lo que contradecía el catálogo de servicios. Quedó así: las entregas las hace el sistema del municipio, y las aplicaciones de servicios permiten probar algunas APIs desde una pantalla. No son un espejo de todo el catálogo de APIs, pero usan las mismas APIs publicadas, así que un sistema conectado obtiene los mismos resultados. No se destaca que el nodo no recibe planillas.

## Marcas de maqueta, badges y disponibilidad

**29 de septiembre de 2026.** El sitio se escribe como versión definitiva, así que se retiraron las marcas de maqueta, que solo le servían al equipo:

- La banda «Maqueta para revisión» salió de todas las páginas. Quedó solo el aviso de `wiki-fiscalizacion.html`, que explica que el contrato comentado es una propuesta. El aviso «Estado de la ficha» de `nodo.html` se retiró el 30 de septiembre de 2026 (ver «Lo publicado funciona»).
- El pie dice «Última actualización» en vez de «Maqueta de trabajo». La fecha por omisión y el texto del pie viven en [`assets/pie.js`](../prototipos/assets/pie.js); en `apis.html` se reemplaza por la más reciente de los campos `actualizado` de los nodos visibles.

**Tarjetas de `apis.html`.** Desde el 30 de septiembre de 2026, cada tarjeta muestra:

- El nombre y qué entrega.
- El contrato (`OpenAPI 3.0.3` o `Sin contrato`).
- El modo de acceso (`Abierto`, `Con credencial`, `Clave Única`).
- `Se puede probar` cuando la ficha tiene ambiente de pruebas.
- La fecha de la última actualización de la ficha.
- La disponibilidad.

Los campos nuevos (`actualizado`, `acceso_tipo`, `sandbox`, `monitoreo`) están documentados en la cabecera de [`data.js`](../prototipos/assets/data.js).

**Disponibilidad.** Nunca se escribe a mano. La página lee `prototipos/estado/status.json`, que debe publicar un monitor externo (Upptime, Uptime Kuma u otro) con la forma de [`estado/status.example.json`](../prototipos/estado/status.example.json). Si ese archivo no existe, sondea desde el navegador los nodos que declaran `monitoreo.salud` con `alcance: "publico"`. Los demás se muestran como «Solo red interna» o «Sin monitoreo». Hoy no hay monitor ni endpoint público de salud: CUT aparece como «Solo red interna» y Permisos de circulación como «Sin monitoreo». Elegir y configurar el monitor queda pendiente.

## Lo publicado funciona

**30 de septiembre de 2026.** Criterio del equipo: **no se publica un contrato sin servicio disponible.** La maqueta asume que todo intercambio visible está publicado y funcionando, así que el sitio dejó de mostrar etapas y dejó de distinguir contrato publicado de servicio disponible. La distancia con el estado real (el CUT responde solo en la red SEM y los permisos de circulación no tienen servicio) está en [`hoja-de-ruta.md`](hoja-de-ruta.md), §10 y Etapa 1.

- **Tarjeta de `apis.html`.** Sin la etiqueta de etapa y sin la fila de ámbito, «Base» e instituciones; el buscador sigue encontrando por institución. La sección «Cómo leer el estado» pasó a «Cómo leer una tarjeta»: una tarjeta de ejemplo con cinco partes numeradas (nombre, qué entrega, contrato/acceso/pruebas, fecha de actualización y disponibilidad) y una lista que explica cada una. Estilos `.anatomia` y `.anota` en `styles.css`.
- **Ficha (`nodo.html`).** Salieron el aviso «Estado de la ficha» y su lógica, y las filas «En qué estado está» y «¿Es viable?» del panel lateral. Los campos `madurez` y `factibilidad` siguen en el modelo, pero ninguna página los muestra.
- **`wiki-ficha.html`.** Salió la sección de etapas; la página responde tres preguntas: si está funcionando ahora, de dónde sale el contrato y cómo se entra.
- **Versionado informado por la API.** Cada API publicada informa, dentro de su propio contrato, su versión, su fecha de publicación y el plazo de gracia vigente. Lo dicen `wiki-consumir.html` y `wiki-conectar.html` (sección de versiones y caso C). Cuánto dura el plazo sigue pendiente (X-109).

## Ambiente de pruebas y aplicación vinculada

**29 de septiembre de 2026.** Quienes revisan el sitio ya saben que los datos son ficticios. Por eso la ficha de Permisos de circulación conserva una sola advertencia, la nota «Demostración» bajo «Para qué sirve», y en lugar de las demás ofrece herramientas que funcionan con esos datos.

- **Probar la API.** Es una consola dentro de la ficha. Se elige una operación, se completan los parámetros y se envía; muestra la petición HTTP y la respuesta con su código y su cuerpo JSON. Todo lo que no depende de los datos lo decide el contrato: sin credencial la respuesta es 401, una patente que no calza con el `pattern` da 400, y los cuerpos de error son los ejemplos del YAML. Los parámetros de consulta se validan antes de enviar, porque el contrato no define un error para ellos. El motor está en [`sandbox.js`](../prototipos/assets/sandbox.js) y sirve para cualquier nodo: basta con declarar `sandbox.script` y registrar un `responder` que busque en los datos.
- **Casos de prueba.** Son diez, y cada uno ejercita una situación distinta: vigente en dos cuotas, cambio de comuna, filtro `desde_anio`, formato antiguo, vencido, anulado, lista vacía, provisoria, 404, 400 y 401. Para el caso «anulado» se agregó el vehículo `FGHJ27`, que usa el estado `ANULADO` que el contrato ya declaraba.
- **Botón por operación.** Cada operación de «Qué se le puede pedir» tiene un botón «Probar esta operación» que la carga en la consola.
- **Descargables reales.** El YAML del contrato se descarga desde su archivo. Los datos de prueba se arman como JSON en el navegador, a partir del mismo objeto que usa la consola.
- **Aplicaciones que la usan.** Es una sección nueva de la ficha, justo después de «Para qué sirve». Lista los servicios de `SERVICIOS` cuyo `nodo` es el de la ficha y lleva a cada aplicación. Si no hay ninguno, la sección no aparece.
- **La aplicación de consulta** dejó la banda «Demostración». Ahora dice que responde con los datos de prueba y enlaza al ambiente de pruebas de la API.

El renderizador de contratos (`openapi.js`) mostraba siempre el ejemplo derivado del esquema, aunque la respuesta trajera uno propio. Por eso el 400 aparecía con `NO_ENCONTRADO`. Ahora usa primero el ejemplo de la respuesta.

**CUT.** La ficha del CUT tiene el mismo ambiente de pruebas, con [`cut-demo.js`](../prototipos/assets/cut-demo.js). Sus datos no son ficticios sino un extracto del catálogo oficial: tres regiones completas, Tarapacá, Maule (la del ejemplo del contrato) y Ñuble (la más nueva, con códigos de cinco dígitos). Lo que no está en el extracto responde 404. El contrato del CUT no pide credencial ni define una respuesta 400, así que la consola no muestra credencial y un código no numérico se detiene en el formulario en vez de enviarse. El motor aplica esa regla a cualquier contrato: un parámetro de ruta mal formado solo se envía si el contrato dice qué responde. El error 404 usa `{ "error": "No encontrada" }`, tomado de la descripción de esa respuesta, porque el contrato no trae un ejemplo. El campo opcional `abreviatura` no se incluye: el catálogo no tiene la lista oficial.

La versión del contrato de permisos de circulación pasó de `0.1.0-demo` a `0.1.0`, y su descripción ya no advierte que es una demostración: dice que es una propuesta de contrato con ejemplos ficticios.

## Glosario y términos enlazados

**29 de septiembre de 2026.** Los conceptos que el sitio usa en más de una página se definen una sola vez, en el glosario de la wiki, `wiki-glosario.html` (hasta el mismo día era una sección de `wiki.html`). Cada entrada tiene su ancla (`wiki-glosario.html#<id>`). La primera mención del término en cada bloque de texto enlaza ahí, con subrayado punteado (clase `termino`) para que no se confunda con un enlace de navegación.

- **En las páginas HTML** el enlace se escribe a mano: `<a class="termino" href="wiki-glosario.html#puerta-de-acceso">…</a>`.
- **En los textos de [`data.js`](../prototipos/assets/data.js)** se usa el marcado `[[id]]` o `[[id|texto visible]]`. Lo resuelve [`assets/terminos.js`](../prototipos/assets/terminos.js) contra el diccionario `TERMINOS`, al final de `data.js`. La ficha lo aplica a `descripcion`, `nota`, `espec.acceso`, `espec.procedencia.detalle` y `pruebas`; el catálogo lo quita en los tooltips. El texto se escapa antes de enlazar, así que `data.js` sigue sin poder inyectar HTML.

Hay trece términos, en orden alfabético. Desde el 30 de septiembre de 2026 la página abre con un buscador, que busca en el término y en su definición sin distinguir tildes, y cada término es una entrada desplegable; un enlace a `wiki-glosario.html#<id>` abre la entrada. Los términos: API, aplicación, Clave Única, comprobante, credencial, estándar (también contrato o especificación), nodo (dos sentidos), procedencia, puerta de acceso, servicio (dos sentidos, con la discusión sobre renombrar la pestaña), SGM, Términos y Condiciones (por definir) y zona de práctica (también *sandbox*; no existe todavía, y no es lo mismo que el ambiente de pruebas de las fichas). Todos están en `TERMINOS`, así que cualquiera se puede marcar en `data.js`.

Uno solo tiene **nombre provisional**, **puerta de acceso**: también se le dice Plataforma de Control (ver [`plataforma-control.md`](plataforma-control.md)). Cuando se defina el nombre, hay que cambiarlo en tres lugares:

- En `TERMINOS`. Los textos de `data.js` que usan `[[puerta-de-acceso]]` sin texto propio se actualizan solos.
- En la entrada del glosario.
- En los enlaces escritos a mano, que hoy están en `que-es.html`, `participar.html` y en casi todas las páginas de la wiki. Para ubicarlos: `grep -rn 'puerta-de-acceso' prototipos/`.

## La wiki, ordenada como WikiGuías

**29 de septiembre de 2026.** La wiki dejó de ser una sola página con secciones y copia el orden de [WikiGuías](https://wikiguias.digital.gob.cl/), la plataforma de guías técnicas de la Secretaría de Gobierno Digital:

- **Portada de bienvenida.** `wiki.html` dice qué es la wiki, a quién está dirigida, cómo está ordenada y dónde pedir ayuda.
- **Una página por enlace.** Cada sección de la antigua `wiki.html` pasó a su propia página: `wiki-consumir.html`, `wiki-codigos.html`, `wiki-normas.html`, `wiki-glosario.html` y `wiki-decisiones.html`. Después se sumaron `wiki-recorrido.html`, `wiki-conectar.html` y `wiki-ficha.html`, con contenido que antes solo estaba en `que-es.html`, `participar.html` y `apis.html`, y el índice `wiki-intercambios.html`.
- **Barra lateral izquierda común** en las doce páginas de la wiki, con el mismo modelo que la de WikiGuías: encabezados de grupo, enlaces y divisores. Los grupos son Usar el nodo (recorrido, cómo se usa una API, conectar un sistema, cómo leer una ficha), Intercambios, Códigos y datos maestros, Marco normativo y Referencia. El menú es la lista `WIKI_NAV` de [`assets/wiki-nav.js`](../prototipos/assets/wiki-nav.js). En pantallas angostas se pliega en «Menú de la wiki».
- **«En esta página»** a la derecha, armado con los `h2` de cada página. Solo aparece en pantallas anchas y cuando la página tiene más de un `h2`.

No se copiaron los tags ni los botones de compartir e imprimir: todavía no hay contenido que los justifique, y el sitio no lleva dependencias.

**El menú lateral solo lleva secciones fijas.** El catálogo de APIs y el de aplicaciones pueden crecer sin límite, así que las entradas de intercambio no se listan en la barra: van en [`wiki-intercambios.html`](../prototipos/wiki-intercambios.html), un índice que se arma solo desde `NODOS`. Muestra los nodos no ocultos agrupados por `AMBITOS`; cada tarjeta enlaza la entrada (campo `wiki`), la ficha y las aplicaciones de `SERVICIOS` que usan ese nodo, y tiene un buscador que ignora tildes. Un nodo visible sin `wiki` aparece con la etiqueta «Entrada pendiente». La base común del SGM y Adquisiciones, que están ocultas, no aparecen.

Las entradas declaran a qué sección del menú pertenecen con `<main class="wiki-main" data-wiki-seccion="wiki-intercambios.html">`, para que la barra marque «Índice de entradas» aunque la entrada no esté en ella. Su miga es `Wiki / Intercambios / <nombre>`. **Para agregar una entrada** basta crear la página y poner su ruta en el campo `wiki` del nodo; no se toca `WIKI_NAV`.

Cada página nueva de la wiki necesita, además del contenido, el marco `wiki-layout` (`<aside id="wiki-nav">`, `<main class="wiki-main">`, `<nav id="wiki-toc">`) y cargar `assets/wiki-nav.js` al final, además del pie común (`<footer id="pie">` seguido de `assets/pie.js`). `wiki-consumir.html` sirve de molde para una página de sección y `wiki-cut.html` para una entrada.

### El tono de la wiki

**29 de septiembre de 2026.** Toda la wiki se reescribió con el tono de la presentación «Gobierno Digital · Tres meses de gestión»: lenguaje llano, centrado en quien lee, sin perder precisión. Las reglas:

- **El título dice el beneficio, no el mecanismo.** Cada bloque sigue la misma forma: una etiqueta corta en mayúsculas, el título, una frase que explica y, si hace falta, una lista breve y una línea de cierre.
- **El término técnico se traduce en la misma frase** la primera vez que aparece. Los que se repiten van al glosario.
- **Palabras de todos los días.** «Pedir» en vez de «consumir», «dirección» en vez de *endpoint* o URI, «revisar» en vez de «validar contra el esquema».
- **Primera persona plural para lo que hace SUBDERE** («publicamos», «revisamos», «avisamos») y «tú» para el lector, en todo el sitio: «busca», «revisa», «si tu sistema cumple», «te avisamos». Se tutea solo cuando la frase le habla al lector; «su» sigue valiendo para terceros («el municipio y su sistema»).
- **Las advertencias son cortas y dicen de quién depende** lo que falta.
- **El detalle técnico se conserva, pero va después**: en tablas, en bloques de código o en un párrafo «Para quien programa» (clase `para-tecnico`). Las observaciones a los contratos del CUT y de permisos de circulación van en dos capas: primero el problema en palabras simples y después el detalle técnico.
- **No cambian** los datos, las normas, los ejemplos, las marcas de pendiente ni lo que dice sobre qué se leyó y qué no.

Antes y después:

| Antes | Después |
|---|---|
| «Cómo se generan los Códigos Únicos Territoriales» | «Que todos los sistemas llamen igual a cada comuna» |
| «Los códigos están declarados como número entero» | «Los códigos pueden perder el cero inicial», y debajo: «Para quien programa: los identificadores están declarados como `integer`» |
| «En base a qué se define lo que se define» | «Detrás de cada exigencia, una ley que la respalda» |
| «Qué revisar antes de consumir la API» | «Qué revisar antes de usar la API» |

Para revisar que no se cuele jerga: `grep -rniE "endpoint|payload|consumir|schema|request" prototipos/wiki*.html`. Lo que aparezca solo puede estar en un bloque «Para quien programa» o en un nombre de archivo.

## Redacciones alternativas en discusión

El sitio está pensado como **definitivo y público**, pero en esta etapa se usa para conversarlo con el equipo. Cuando hay una redacción que todavía no está zanjada, la alternativa va **en la propia página**, entre paréntesis y en cursiva, con la clase `alt`:

```html
<p class="alt">(Versión alternativa en discusión: «…»)</p>
```

Deliberadamente **no** va en un recuadro de advertencia: un bloque amarillo ensucia la percepción de la página y hace que el lector lo lea como un problema en vez de como una opción sobre la mesa.

**Todas se retiran antes de publicar.** Para encontrarlas:

```bash
grep -rn 'class="alt"' prototipos/
```

Hoy hay cinco:

1. En la portada, tarjeta «SUBDERE se ocupa del resto del Estado»: cuánto se compromete del lado de SUBDERE hacia el resto del Estado.
2. En la portada, tarjeta «Abierto a cualquier proveedor»: si la zona de práctica queda totalmente abierta o pide algún registro, porque hará falta seguridad y control de uso para no saturar los servidores.
3. En `que-es.html`, sección «Qué revisa»: qué hace el nodo con lo que las municipalidades envían a otros organismos del Estado, que todavía no está levantado.
4. En `que-es.html`, sección «Por dónde pasa todo»: «servicio» nombra dos cosas —el sistema detrás de cada API y la pestaña «Servicios», que reúne aplicaciones—. Una opción es renombrar la pestaña a «Aplicaciones».
5. En `que-es.html`, caso C de «Casos»: cómo se avisa a las entidades conectadas cuando cambia un estándar y cuánto dura el período de gracia de la versión anterior. El compromiso de avisar con antelación y dar un período de gracia es nuevo: la nota de arquitectura del estándar legible por máquina solo dice que cada versión queda registrada y no se corrige.
La primera y la tercera dependen del mismo levantamiento y se resuelven juntas. La tarjeta «Recibo información de municipios» de `participar.html` depende de ese mismo levantamiento y lo marca como pendiente.

**29 de septiembre de 2026.** Salió la alternativa de `participar.html`, tarjeta «Quiero usar el nodo», sobre mencionar el uso de partes del SGM sin el sistema completo: se quitó junto con la mención a Adquisiciones, que está oculto en el catálogo. La página se reescribió con el tono de la wiki; la tabla de práctica y operación quedó solo en `que-es.html` y `wiki-conectar.html`, y el canal de contacto figura como pendiente.

`que-es.html` ya no trata la relación de SUBDERE con el resto del Estado: el párrafo que la justificaba se retiró y el tema quedó en la tarjeta de la portada.

La alternativa que estaba en el hero —la versión que partía por el problema— se incorporó como texto de la sección «Qué propone» de la portada.

## El sitio en React: lo que cambia respecto de la maqueta

**10 de octubre de 2026.** La primera etapa del [frontend](../frontend/) traduce el sitio público a React contra el backend. El contenido y los estilos son los de la maqueta (`maqueta.css` es una copia de `styles.css`); estos son los cambios deliberados:

- **Sin ambiente de pruebas ni disponibilidad.** La consola «Probar la API», los casos de prueba, el botón «Probar esta operación», los descargables generados en el navegador y la columna de disponibilidad (`status.json` o sondeo desde el navegador) no se portaron. La ficha conserva «Dónde practicar», que lista los ambientes que declara el nodo o lo marca como pendiente. Vuelven cuando exista la zona de práctica del backend y un monitor.
- **Tarjeta de `apis.html`.** «Cómo leer una tarjeta» pasó de cinco partes a cuatro: nombre, qué entrega, madurez y acceso, y la fecha, que ahora es la última vez que el catálogo leyó la ficha. Sin monitor ni ambiente de pruebas, «Se puede probar» y la disponibilidad dirían algo que nadie comprueba; la madurez sí la declara la ficha y el backend la entrega.
- **Ficha.** Sin «Depende de» ni «Descargables»: el modelo del backend no los tiene. El archivo de la especificación se enlaza desde «Qué entrega, y en qué forma».
- **Índice de intercambios de la wiki.** `wiki-intercambios.html` es ahora la sección `#intercambios` de la portada `/wiki`, sin agrupar por ámbito. La dirección vieja redirige ahí.
- **Pie.** Sin fecha de «Última actualización» y sin logotipo: el archivo del logo no está en el repositorio del frontend y la fecha la escribía `pie.js` a mano.
- **Cómo participar.** La fila de la zona de práctica perdió la frase sobre el ambiente de pruebas dentro del navegador.
- **Menú de sesión.** Es lo único nuevo en la barra: «Entrar» sin sesión, y con sesión un `<details>` con nombre, rol, municipio y «Salir». La consulta de permisos de circulación exige sesión, pide el trámite que la motiva y avisa que queda registrada.
- **Foco visible** en enlaces, botones y campos, con `:focus-visible` en `sitio.css`.

## Para el QA

Tres preguntas que conviene hacer junto con el enlace, porque son las que definen lo que sigue:

1. ¿El catálogo es la pieza central del sitio, o es un anexo de la descripción del nodo?
2. ¿Qué le falta a la ficha de un nodo para que a una contraparte le sirva de verdad?
3. ¿El sitio es interno de SUBDERE o se abre a municipios y proveedores? Cambia el tono de todo el contenido y el nivel de terminación que necesita.
