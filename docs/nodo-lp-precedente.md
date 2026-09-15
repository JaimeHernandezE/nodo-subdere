# Nodo Laboral y Previsional — el precedente chileno en operación

**Fecha:** 15 de septiembre de 2026
**Para qué sirve este documento:** el Nodo L&P es el homólogo nacional más cercano al nodo SUBDERE y lleva casi un año operando. Acá está qué es, qué se puede copiar, qué no, y qué advertencias deja.

**Fuentes leídas.** Los cinco documentos que la Subsecretaría de Previsión Social publica en su página del Nodo L&P, en su texto extraído — no los diagramas ni las imágenes, que en la presentación de lanzamiento portan parte del contenido:

| Documento | Fecha |
|---|---|
| Presentación de lanzamiento — «Una estrategia de interoperabilidad para el Estado» | Diciembre 2025 |
| Tríptico «Entendiendo el Nodo Laboral y Previsional» | Diciembre 2025 |
| Presentación de la 1ª Mesa Técnica de Interoperabilidad | Enero 2026 |
| Presentación de la 2ª Mesa Técnica de Interoperabilidad | Abril 2026 |
| Minuta de la 3ª Mesa Técnica de Interoperabilidad | Julio 2026 |

---

## 1. Qué es

El Nodo Laboral y Previsional es la infraestructura sectorial de datos del Ministerio del Trabajo y Previsión Social. **Entró en operación el 26 de noviembre de 2025.**

Su definición propia, la que repiten en los tres documentos de difusión: *«el "punto de encuentro" digital del sector trabajo–previsión social, que ordena y conecta datos hoy dispersos, para que circulen una sola vez, con trazabilidad y reglas claras.»*

**Fundamento normativo.** Ley 21.180 y su principio «solo una vez», más las leyes 20.255, 20.403 y 21.735, que refuerzan el rol coordinador de la SPS y la obligación de interoperar con seguridad y protección de datos personales.

**Participantes.** Once organismos: SPS, IPS, SUSESO, DT, Superintendencia de Pensiones, ISL, SENCE, ChileValora, CAPREDENA, DIPRECA y SUBTRAB/BNE. La primera fase (2025) integró cuatro proveedores de datos —SUSESO, DT, IPS y SP— y la segunda (2026) incorpora a los siete restantes, cada uno con entre dos y siete conjuntos de datos.

**Artefacto central: la Ficha Única de Información Laboral y Previsional.** En vez de que cada organismo consulte y valide por su cuenta, el nodo consolida y la institución autorizada consume la ficha para tramitar. Los ejemplos que usan: el IPS evalúa el derecho a la PGU consumiendo cotizaciones de la SP, asignación familiar de SUSESO y finiquito electrónico de la DT.

**Dónde vive.** En la plataforma sectorial de la SPS, *«integrada de forma nativa a la Plataforma Integrada de Servicios Electrónicos del Estado (PISEE 2.0)»*. **No construyeron transporte propio.**

---

## 2. La diferencia que impide copiarlo tal cual

El flujo va al revés.

| | Nodo L&P | Nodo SUBDERE (diseño actual) |
|---|---|---|
| Quién inicia | La institución que necesita el dato | El municipio que debe entregar |
| Qué circula | Una consulta y su respuesta | Un reporte y su constancia |
| Modelo | Provisión / consumo | Envío / acuse |
| Artefacto | Ficha Única consolidada | Reporte en el estándar del destinatario |

El Nodo L&P resuelve que **el Estado deje de pedirle a la ciudadanía lo que ya tiene**. El nodo SUBDERE resuelve que **el municipio deje de entregar lo mismo muchas veces**. Son problemas hermanos, no el mismo problema.

Lo más cercano a nuestro caso dentro de su diseño es la **funcionalidad Pub/Sub** presentada en la 3ª mesa: generación, distribución y confirmación de eventos entre instituciones participantes, aplicada a los conjuntos de datos ya integrados. Ahí sí hay un emisor que empuja y un acuse de recibo.

**Conviene decir esto antes de que alguien proponga el Nodo L&P como plantilla.** Se copia su capa institucional entera; su modelo de intercambio, no.

---

## 3. Qué se copia

### 3.1 El modelo de operación en cuatro columnas

| Plataforma | Convenio de adhesión | Reglamentos | Herramientas |
|---|---|---|---|
| Nodo | Convenio de interoperabilidad | Reglas de uso | Repositorio digital |
| Ficha | Anexos técnicos | Instructivos | Paneles de control |
| Plataforma de gestión | | | Registros para control y auditoría |

Lo relevante es que **tres de las cuatro columnas no son software**. El nodo SUBDERE tiende a discutirse solo en la primera.

### 3.2 La gobernanza en cinco niveles

| Nivel | Roles |
|---|---|
| 1. Estratégico político | SPS; MINHAC/SGD |
| 2. Gobernanza sectorial | Comité Directivo SPS–OAE; Mesa Técnica de Interoperabilidad |
| 3. Operación del nodo y la ficha | Unidad IoP de la SPS; equipo TI del IPS; **operador técnico externo**; mesa de ayuda |
| 4. Nivel institucional | Responsables institucionales, técnicos de flujo, de seguridad; administradores funcionales de datos y de usuarios; equipos TI de cada organismo |
| 5. Encargados y auditoría | Auditoría interna, externa y sectorial coordinada por la SPS |

Dos cosas destacan. **El nivel 3 tiene operador técnico externo contratado**, con la rectoría en la SPS — es la separación entre quién decide la norma y quién opera la plataforma. Y **el nivel 4 exige que cada participante nombre roles formales**, lo que en la 3ª mesa seguía siendo un compromiso pendiente.

### 3.3 La Mesa Técnica como instancia permanente

Sesiona mensualmente y tiene rol, funciones y facultades escritas: revisar catálogos y cambios de conjuntos de datos, alinear agendas, priorizar mejoras y pruebas, seguir riesgos. Puede **proponer incorporar o eliminar conjuntos de datos** al administrador de la plataforma, y acordar priorización de mejoras no críticas. Sus evidencias esperadas son actas, acuerdos operativos, backlog priorizado y calendario de pruebas.

**El mecanismo de discrepancias es de dos pasos:** primero se busca acuerdo en la propia mesa; si persisten diferencias, la SPS como administrador de la plataforma resuelve **por resolución fundada**. Es una forma barata de tener vía de reclamo sin crear un tribunal, y resuelve un hueco que el ADR de portabilidad tenía abierto.

### 3.4 Graduación por campo, no por tamaño

La especificación de datos a consumir se hace bajo *«el principio de necesidad y proporcionalidad/minimización»*. La **parametrización** define qué atributos puede consumir cada institución según sus autorizaciones, y *«debe quedar formalizado en anexos técnicos ex-ante»*.

Es una tercera variable de proporcionalidad que no estaba en el ADR: no se acota la calidad de lo que el participante entrega, se acota el alcance de lo que puede pedir.

### 3.5 Transparencia operacional: el RDS

El **Repositorio Digital Sectorial** guarda la documentación del nodo. Detalle revelador de la 3ª mesa: *«todo incidente será guiado hasta su resolución por el Equipo IoP del Nodo, los tiempos de respuesta se irán registrando en los correspondientes tickets, que una vez cerrados serán subidos al RDS»*. Los tickets de soporte cerrados se publican.

### 3.6 Indicadores que miden uso, no cobertura

Desde la 2ª mesa usan el par **«consumo habilitado v/s consumo efectivo»**, más disponibilidad, latencia y desempeño. Es la distinción más útil de todo el corpus: habilitar a un participante no es que lo use.

En la 3ª mesa aparece el dato que la valida: el principal consumidor de información interoperada es **el portal MiChileAtiende**, no las instituciones. El valor se materializó donde hay volumen ciudadano, no donde estaba planificado.

---

## 4. Las advertencias

### 4.1 La parte técnica se resolvió antes que la institucional

Ocho meses después de entrar en operación, la minuta de julio de 2026 registra:

- Adhesiones formales pendientes de organismos de 2ª fase, con plazo *«antes de octubre de 2026»*.
- Planes de consumo sin enviar, comprometidos para el 31 de julio.
- La especificación de campos del conjunto LRE-DT incompleta para varios organismos.
- Responsables institucionales aún sin designar formalmente.
- Una **Mesa Jurídica** que a esa fecha todavía no se había calendarizado, convocada precisamente para destrabar las adhesiones.

La plataforma opera y el consumo crece. Lo que arrastra es la firma.

**Para el nodo SUBDERE:** si la presentación promete el nodo por su capacidad técnica, está prometiendo la parte fácil. Y nuestra escala es otra — 345 municipios y decenas de proveedores, contra once organismos del mismo ministerio.

### 4.2 La asistencia a la mesa es dispar

La minuta de la 3ª mesa lista sesenta y dos convocados con marca de asistencia. Varias instituciones tienen a todos sus representantes ausentes; otras asisten completas. Con once participantes la mesa funciona igual. Con un universo municipal, ese mismo patrón produce una gobernanza que decide sin los que después deben cumplir.

Vale la pena mirarlo antes de diseñar la instancia equivalente: **conviene que la mesa del nodo SUBDERE tenga representación delegada y quórum declarado**, no convocatoria abierta a todos.

### 4.3 El convenio de adhesión es exigible acá y es el camino crítico

Es la respuesta al reparo de que no se podrán exigir convenios. Sí se pueden —la SPS los exige, con documento de adhesión más anexos técnicos— y aun así, dentro de un mismo ministerio y con mandato legal expreso, tardan.

---

## 5. Lo que este precedente cambia en nuestros documentos

| Dónde | Qué cambia |
|---|---|
| ADR de portabilidad, §1.5 | Nueva sección con el precedente: PISEE en vez de transporte propio, instrumento documental, y las adhesiones como cuello de botella |
| ADR de portabilidad, §3.8 | La graduación por campo entra como tercera variable de corte para X-103 |
| ADR de portabilidad, consecuencias 14 y 15 | Medir conformidad ejercida y no solo declarada; tratar la capa jurídica como frente con calendario propio |
| ADR de portabilidad, X-106 y X-107 | Indicadores de conformidad ejercida; mecanismo de discrepancias de dos pasos |
| ADR del nodo | Pendiente de incorporar: gobernanza de cinco niveles, operador técnico externo, mesa técnica permanente con facultades escritas, RDS |
| Presentación al Subsecretario | Hay un nodo sectorial chileno operando desde noviembre de 2025. Deja de ser una propuesta sin antecedente nacional |
| Maqueta del sitio | Su página publica instituciones participantes y actas de las mesas con fecha. Son las dos secciones que el sitio del nodo SUBDERE no tiene |

---

## 6. Lo que falta revisar

- **Los diagramas de la presentación de lanzamiento.** El texto extraído pierde el esquema «situación actual v/s situación con Nodo L&P» y el modelo de operación, que están como imagen.
- **El Convenio Marco de Interoperabilidad y las Reglas de Uso.** Se mencionan en los cinco documentos y no están publicados en la página. Son la pieza que más nos serviría.
- **Los indicadores concretos de consumo.** Las minutas remiten a presentaciones adjuntas que no están en la carpeta.
- **Cómo se relaciona con el nodo de SUSESO** propiamente tal, si es una pieza distinta. SUSESO aparece acá como organismo proveedor de cuatro conjuntos de datos, no como operador de nodo.
