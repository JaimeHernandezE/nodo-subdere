# Nodo SUBDERE — maqueta del sitio

Maqueta estática para revisión, previa al desarrollo en Django + React.
Sin build, sin dependencias: vive en [`prototipos/`](../prototipos/). Se abre con doble clic o se publica tal cual.

## Páginas

| Archivo | Qué es |
|---|---|
| `prototipos/index.html` | Landing — qué es el nodo y para quién |
| `prototipos/que-es.html` | Descripción general: cómo funciona, alcance de la validación, los tres casos de municipio |
| `prototipos/catalogo.html` | **Servicios.** Las herramientas de uso humano construidas sobre las APIs. Conserva el nombre de archivo por los enlaces ya compartidos; en Django la ruta es `/servicios/` |
| `prototipos/apis.html` | **APIs.** Los doce intercambios del catálogo, con filtro por ámbito y buscador. Cada ficha dice si ya hay contrato publicado |
| `prototipos/servicio-cut.html` | Buscador de códigos territoriales |
| `prototipos/servicio-fiscalizacion.html` | Consulta de permiso de circulación por patente |
| `prototipos/wiki-fiscalizacion.html` | Entrada de wiki de los permisos de circulación |
| `prototipos/assets/fiscalizacion-demo.js` | Datos inventados de la pantalla de permisos. Se borra cuando el servicio sea alcanzable |
| `prototipos/wiki.html` | **Wiki.** Índice: cómo se usan las APIs, cómo se generan los códigos y en base a qué normas |
| `prototipos/wiki-cut.html` | Entrada de wiki de los Códigos Únicos Territoriales |
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

`prototipos/assets/data.js` es la maqueta del modelo. Los campos:

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
| `descargables` | lista | `{ archivo, que }` — solo demostración. Nombres y una línea de contenido. No son archivos reales ni se descargan |
| `dependencias` | lista | `{ nombre, id? }` — qué hay que tener implementado antes. `id` enlaza otra ficha; si falta, el módulo todavía no está en el catálogo |

**`clase` distingue dos figuras.** Un nodo `intercambio` es elegible (incluido el consumo por módulo cuando aplique). Un nodo `plataforma` es condición de otros: hoy, el core SGM. Sin ese campo, el core se leería como un módulo más.

Los dos campos que conviene no dejar para después son **`madurez`** y **`factibilidad`**: agregar una columna a un modelo que ya tiene datos y vistas siempre cuesta más que preverla. María José dejó esa evaluación explícitamente pendiente, y el catálogo es el lugar natural donde vive.

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
| `fiscalizacion` — Permisos de circulación por patente | Visible. Demostración |
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

Lo que se publica en el catálogo es **una propuesta de contrato reconstruida**, no la colección. Eso está dicho en tres lugares para que nadie lo confunda: en la descripción del propio archivo YAML, en el campo `espec.origen` del nodo y en la nota de la ficha. La comparación entre una y otra es el contenido de [`wiki-fiscalizacion.html`](../prototipos/wiki-fiscalizacion.html), y es también la agenda de la conversación con Servicios Municipales.

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
- La banda de «maqueta para revisión» pasó a gris neutro, para que el rojo signifique una sola cosa en el sitio.

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
| `apis.html` | Construir: los contratos publicados y cómo leer su estado |
| `catalogo.html` | Usar: las aplicaciones construidas sobre las APIs |
| `wiki.html` | Entender: cómo se usa cada intercambio y por qué está definido así |

Por eso la portada ya no tiene las tarjetas del mecanismo (formato publicado, revisión previa, comprobante, credencial) ni la sección «Cómo está armado»: lo primero está en `que-es.html` y lo segundo en «Cómo leer el estado» de `apis.html`. La sección «Lo que el nodo no es» pasó a «Lo que el municipio puede esperar», con cuatro tarjetas en redacción afirmativa.

`que-es.html` decía «el nodo conecta sistemas, no personas», lo que contradecía el catálogo de servicios. Quedó así: las entregas las hace el sistema del municipio, y las aplicaciones de servicios permiten probar algunas APIs desde una pantalla. No son un espejo de todo el catálogo de APIs, pero usan las mismas APIs publicadas, así que un sistema conectado obtiene los mismos resultados. No se destaca que el nodo no recibe planillas.

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

Hoy hay cuatro:

1. En la portada, tarjeta «SUBDERE se ocupa del resto del Estado»: cuánto se compromete del lado de SUBDERE hacia el resto del Estado.
2. En la portada, tarjeta «Abierto a cualquier proveedor»: si la zona de práctica queda totalmente abierta o pide algún registro, porque hará falta seguridad y control de uso para no saturar los servidores.
3. En `que-es.html`, sección «Qué revisa»: qué hace el nodo con lo que las municipalidades envían a otros organismos del Estado, que todavía no está levantado.
4. En `que-es.html`, sección «Por dónde pasa todo»: «servicio» nombra dos cosas —el sistema detrás de cada API y la pestaña «Servicios», que reúne aplicaciones—. Una opción es renombrar la pestaña a «Aplicaciones».

La primera y la tercera dependen del mismo levantamiento y se resuelven juntas.

`que-es.html` ya no trata la relación de SUBDERE con el resto del Estado: el párrafo que la justificaba se retiró y el tema quedó en la tarjeta de la portada.

La alternativa que estaba en el hero —la versión que partía por el problema— se incorporó como texto de la sección «Qué propone» de la portada.

## Para el QA

Tres preguntas que conviene hacer junto con el enlace, porque son las que definen lo que sigue:

1. ¿El catálogo es la pieza central del sitio, o es un anexo de la descripción del nodo?
2. ¿Qué le falta a la ficha de un nodo para que a una contraparte le sirva de verdad?
3. ¿El sitio es interno de SUBDERE o se abre a municipios y proveedores? Cambia el tono de todo el contenido y el nivel de terminación que necesita.
