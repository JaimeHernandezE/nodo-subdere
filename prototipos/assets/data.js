/* Datos semilla del catálogo.

   Trece nodos vienen del mapeo de interoperabilidad del JPL, María José Besa,
   8 de septiembre de 2026, tras la reunión con el Juzgado de Policía Local de
   Lo Barnechea. Los tres últimos de esa lista los agregó Allison Díaz.

   División territorial no viene de ahí: es el prototipo basado en el repositorio
   «utilitarios» del equipo SEM, y el único con implementación existente.

   Dos nodos más, ámbito SGM, se agregaron el 15 de septiembre de 2026:
     sgm-core        — la base común del SGM (clase plataforma: está siempre, no se elige)
     adquisiciones   — primer módulo de negocio; instantánea OpenAPI 0.1.0 en estandares/

   Estándares de Gobierno Digital (nodos-gobierno) se retiró el 16 de septiembre
   de 2026: es condición de capa, no un intercambio. Ver docs/maqueta.md.

   Este archivo es la maqueta del modelo de datos del catálogo. Cada campo de aquí
   debería existir como campo del modelo en Django.

   Campos:
     clase    intercambio | plataforma
              plataforma = condición de otros; no se elige por módulo
     oculto   true = el nodo existe en el modelo pero no aparece en los
              listados. Su ficha sigue siendo alcanzable por enlace directo.
              Se usa para lo que está en preparación y todavía no se muestra.
     actualizado  fecha ISO (AAAA-MM-DD) del último cambio de la ficha. No es
              la fecha de registro del contrato (espec.registrada).
     acceso_tipo  abierto | credencial | clave-unica — resumen del modo de
              acceso, para el badge. El detalle sigue en espec.acceso.
     sandbox  { script } — la ficha tiene un ambiente de pruebas que ejecuta el
              contrato con datos ficticios. `script` registra los datos y el
              responder con Sandbox.registra(id, …); ver assets/sandbox.js.
              Requiere espec.archivo: las operaciones salen del contrato.
     monitoreo    { salud?, alcance } — de dónde sale la disponibilidad.
              alcance  publico | interno
              salud    URL que responde si el servicio está arriba. Solo se
                       anota si existe; el catálogo no la inventa. Se sondea
                       desde el navegador únicamente si alcance = publico.
              Sin este campo, la ficha dice «Sin monitoreo».
              La fuente principal es estado/status.json, que genera un
              monitor externo; ver estado/status.example.json.
     wiki     dirección de la entrada del intercambio en la wiki. El índice
              wiki-intercambios.html se arma con este campo; un nodo visible
              sin él aparece como «Entrada pendiente».

   Campos opcionales, presentes solo cuando el nodo ya tiene contrato publicado:
     espec    { archivo?, formato, validador, registrada, procedencia, acceso, expuesto? }
     pruebas  texto

   espec.procedencia — de dónde viene el contrato y cuánto se le puede creer:
     responsable    quién responde por el contrato
     fuente         dónde está la versión que rige
     copia          exacta | instantanea | reconstruccion | sin-copia
                    qué relación tiene lo que muestra el catálogo con la fuente
     detalle        una frase que precisa `copia`
     observaciones  { texto, url }? — dónde están las diferencias y las preguntas
                    abiertas. Van en la wiki, no en el contrato.

   descargables  lista de { archivo, que, url?, generar? }
                url      el archivo existe y se descarga desde ahí
                generar  "sandbox" = se arma en el navegador con los datos de prueba
                Sin url ni generar, la ficha lo lista como ejemplo, sin descarga.
   dependencias lista de { nombre, id? } — qué hay que tener implementado antes.
                id apunta a otra ficha del catálogo; si falta, todavía no está publicado

   `espec.archivo` es opcional. Si existe, la ficha lo lee y lo renderiza.
   `espec.expuesto` distingue contrato registrado de servicio alcanzable.
   Si solo hay metadato (formato, procedencia, acceso), la ficha lo muestra sin
   transcribir operaciones. Ver docs/adr-2026-09-estandar-legible-por-maquina.md.

   Cuando faltan, la ficha muestra el bloque «Pendiente» correspondiente.

   Los textos (descripcion, nota, espec.acceso, procedencia.detalle, pruebas) pueden
   enlazar un término del glosario con [[id]] o [[id|texto]]. Ver TERMINOS
   al final del archivo. */

const NODOS = [
  {
    id: "sgm-core",
    oculto: true,
    nombre: "Base común del SGM",
    ambito: "SGM",
    clase: "plataforma",
    actualizado: "2026-09-15",
    acceso_tipo: "clave-unica",
    funcion: "Lo que todo módulo del SGM necesita por debajo: quién es quién, qué puede hacer cada uno, y el registro de lo que se hizo.",
    descripcion: "No es un módulo que el municipio decida usar: es lo que está debajo de todos. Se ocupa de entrar con Clave Única, de saber qué puede hacer cada funcionario, de mantener separados los datos de cada municipio, de guardar los parámetros que fija la norma, de dejar registro de cada acto y de conectar con Mercado Público, la firma electrónica y los documentos. Un municipio que use solamente Adquisiciones igual está usando esto. No hay que confundirlo con la [[puerta-de-acceso|puerta de entrada del nodo]], que es otra cosa: esta es la base del sistema, aquella controla quién llama.",
    instituciones: ["SUBDERE — SGM", "Municipios", "Proveedores de sistemas de gestión municipal"],
    intercambio: "Transversal",
    madurez: "En desarrollo",
    factibilidad: "Alta",
    origen: "Documentación de arquitectura del SGM",
    nota: "Está siempre: no es algo que se active. Quien use cualquier módulo del SGM está usando esto. Lo que entrega está descrito en borrador, todavía no en su forma final, y el servicio no corre en ninguna parte. Publicar la descripción no significa que se pueda usar.",
    espec: {
      formato: "Descripción funcional; la versión técnica final está pendiente",
      validador: "https://spec.openapis.org/oas/v3.1.0",
      registrada: "15 de septiembre de 2026",
      procedencia: {
        responsable: "SUBDERE — SGM",
        fuente: "Documentación de arquitectura del SGM, en el repositorio del proyecto",
        copia: "sin-copia",
        detalle: "El catálogo no guarda una copia: la descripción se consulta en su fuente."
      },
      acceso: "Dos caminos: las personas entran con Clave Única y los sistemas con una credencial propia. Los dos pasan por la [[puerta-de-acceso|misma puerta]]."
    },
    pruebas: "Todavía no hay ambiente de pruebas. El sandbox previsto es el de SGM (sandbox-desarrolladores.md en el corpus de licitación).",
    descargables: [
      { archivo: "sgm-base-comun-operaciones.pdf", que: "Listado de ejemplo de lo que cubre la base: quién entra, qué puede hacer cada uno y qué queda registrado." },
      { archivo: "sgm-base-comun.openapi.yaml", que: "Contrato de ejemplo, en el formato que lee una máquina. No es el servicio." }
    ]
  },
  {
    id: "adquisiciones",
    oculto: true,
    nombre: "Adquisiciones",
    ambito: "SGM",
    clase: "intercambio",
    actualizado: "2026-09-16",
    acceso_tipo: "clave-unica",
    funcion: "Todo el ciclo de una compra municipal, desde que alguien la pide hasta que se paga.",
    descripcion: "Es el primer módulo del SGM que entra al catálogo. Cubre las modalidades de compra de la Ley 19.886 —Compra Ágil primero, y después Convenio Marco, Licitación Pública y Trato Directo—, todas descritas en el mismo lugar. La pantalla del propio SGM y el sistema de un municipio piden exactamente lo mismo y entran por la [[puerta-de-acceso|misma puerta]]: nadie tiene un camino privilegiado. Eso sí, «solo Adquisiciones» no viene solo: se apoya en la base común y necesita saber si hay presupuesto y cómo se contabiliza.",
    instituciones: ["SUBDERE — SGM", "Municipios", "Proveedores de sistemas de gestión municipal", "ChileCompra / Mercado Público"],
    intercambio: "El municipio consulta",
    madurez: "En desarrollo",
    factibilidad: "Alta",
    origen: "Documentación del módulo de Adquisiciones del SGM",
    nota: "Ya está escrito qué entrega, pero el servicio todavía no corre en ninguna parte. Lo que se muestra acá es una copia tomada el 16 de septiembre de 2026 (versión 0.1.0) para poder leerla; la descripción vigente sigue en la documentación del SGM.",
    dependencias: [
      { nombre: "Base común del SGM", id: "sgm-core" },
      { nombre: "Presupuestos" },
      { nombre: "Contabilidad" }
    ],
    espec: {
      archivo: "estandares/adquisiciones.openapi.yaml",
      formato: "OpenAPI 3.1 — el formato estándar para describir un servicio web",
      validador: "https://spec.openapis.org/oas/v3.1.0",
      registrada: "16 de septiembre de 2026",
      expuesto: false,
      procedencia: {
        responsable: "SUBDERE — SGM",
        fuente: "sgm-docs/modulos/adquisiciones/openapi/adquisiciones.openapi.yaml, en el repositorio del SGM",
        copia: "instantanea",
        detalle: "Armada con la versión 0.1.0, que en la documentación del SGM está repartida en varios archivos. Si la fuente cambia, hay que volver a armarla: el catálogo no la edita."
      },
      acceso: "Dos caminos: las personas entran con Clave Única desde la pantalla del SGM, y los sistemas con una credencial propia. Los dos pasan por la [[puerta-de-acceso|misma puerta]], sin atajos."
    },
    pruebas: "Todavía no hay ambiente de pruebas. El sandbox previsto es el de SGM (sandbox-desarrolladores.md), con el mismo contrato que en producción.",
    descargables: [
      { archivo: "adquisiciones-operaciones.pdf", que: "Listado de ejemplo de todas las operaciones: qué se puede pedir y para qué sirve cada una, agrupadas por parte del módulo." },
      { archivo: "adquisiciones.openapi.yaml", que: "La descripción técnica de ejemplo, la misma que la ficha muestra más arriba. Sirve para construir contra ella, no para leerla seguido." },
      { archivo: "adquisiciones-casos-de-practica.md", que: "Casos de ejemplo con datos inventados, para practicar antes de usar datos de un municipio." }
    ]
  },
  {
    id: "fiscalizacion",
    nombre: "Permisos de circulación por patente",
    ambito: "Transversal",
    clase: "intercambio",
    actualizado: "2026-09-27",
    acceso_tipo: "credencial",
    wiki: "wiki-fiscalizacion.html",
    sandbox: { script: "assets/fiscalizacion-demo.js" },
    funcion: "Consultar el permiso de circulación de un vehículo a partir de su patente: el vehículo, los permisos pagados por año y la institución que los recaudó.",
    descripcion: "El permiso de circulación lo cobra cada municipio, pero quien necesita comprobarlo casi nunca es el municipio que lo cobró: es otro municipio, un control policial, o el propio dueño del vehículo. Este intercambio la resuelve con una consulta por patente que devuelve el vehículo, sus permisos y quién los recaudó, identificando a la institución por su Código Único Territorial.",
    instituciones: [
      "SUBDERE — SEM",
      "Municipios",
      "Instituciones que fiscalizan en vía pública"
    ],
    intercambio: "El municipio consulta",
    madurez: "En evaluación",
    factibilidad: "Media",
    origen: "Colección de referencia del equipo de Servicios Municipales de SUBDERE, septiembre de 2026",
    nota: "Demostración. La especificación que se publica acá es una propuesta reconstruida para mostrar qué forma tendría este intercambio como estándar, no el contrato del servicio. No hay compromiso de disponibilidad ni de contenido, y los datos de la pantalla son inventados.",
    espec: {
      archivo: "estandares/fiscalizacion.openapi.yaml",
      formato: "OpenAPI 3.0.3 — propuesta de contrato",
      validador: "https://spec.openapis.org/oas/v3.0.3",
      registrada: "27 de septiembre de 2026",
      expuesto: false,
      procedencia: {
        responsable: "Equipo del Nodo SUBDERE, mientras Servicios Municipales no publique el contrato",
        fuente: "Colección de referencia del equipo de Servicios Municipales de SUBDERE, septiembre de 2026",
        copia: "reconstruccion",
        detalle: "Propuesta de cómo se vería el contrato publicado, escrita a partir de la colección. No es la colección ni el contrato del servicio.",
        observaciones: { texto: "Diferencias con la colección y preguntas para el equipo que opera el servicio", url: "wiki-fiscalizacion.html" }
      },
      acceso: "Credencial de corta duración entregada por la [[puerta-de-acceso]]. A diferencia de los códigos territoriales, acá circulan datos de un vehículo y de su titular, así que la consulta queda registrada."
    },
    pruebas: "Las tres operaciones responden aquí mismo, con un conjunto fijo de vehículos ficticios. Las validaciones y los errores son los del contrato: una patente mal escrita devuelve 400, una que no existe devuelve 404 y una consulta sin credencial devuelve 401. La credencial de prueba viene puesta.",
    descargables: [
      { archivo: "fiscalizacion.openapi.yaml", url: "estandares/fiscalizacion.openapi.yaml",
        que: "El contrato en el formato que lee una máquina. Se importa tal cual en Postman, Insomnia o un generador de clientes." },
      { archivo: "fiscalizacion.datos-prueba.json", generar: "sandbox",
        que: "Todos los vehículos y permisos del ambiente de pruebas, para montar un simulador propio o escribir pruebas automáticas." }
    ]
  },
  {
    id: "cut",
    nombre: "Códigos Únicos Territoriales (CUT)",
    ambito: "Transversal",
    clase: "intercambio",
    actualizado: "2026-09-15",
    acceso_tipo: "abierto",
    wiki: "wiki-cut.html",
    monitoreo: { alcance: "interno" },
    funcion: "Regiones, provincias y comunas con su Código Único Territorial, para que todos los sistemas llamen igual a cada lugar.",
    descripcion: "Casi cualquier intercambio entre un municipio y una institución empieza por dejar claro de qué comuna se está hablando. Si cada sistema tiene su propia lista, con sus abreviaturas y sus nombres escritos a su manera, los datos no calzan aunque todo lo demás esté bien. Este nodo entrega la lista oficial vigente, con el código que le corresponde a cada lugar.",
    instituciones: ["SUBDERE — SEM", "Municipios", "Proveedores de sistemas de gestión municipal"],
    intercambio: "El municipio consulta",
    madurez: "En desarrollo",
    factibilidad: "Alta",
    origen: "Un servicio que ya construyó el equipo SEM de SUBDERE",
    nota: "Es el único del catálogo que además de estar escrito ya funciona. Pero funciona solo dentro de la red de SUBDERE: desde fuera todavía no se puede usar, y nadie se ha comprometido a mantenerlo andando. Lo que se publica acá es qué entrega, no una promesa de que esté disponible.",
    espec: {
      archivo: "estandares/cut.openapi.yaml",
      expuesto: true,
      formato: "OpenAPI 3.0.3 — el formato estándar para describir un servicio web",
      validador: "https://spec.openapis.org/oas/v3.0.3",
      registrada: "15 de septiembre de 2026",
      procedencia: {
        responsable: "SUBDERE — SEM",
        fuente: "Especificación de referencia entregada por Juan Helo, septiembre de 2026",
        copia: "exacta",
        detalle: "Sin ningún cambio: el catálogo no la edita.",
        observaciones: { texto: "Observaciones sobre el contrato", url: "wiki-cut.html" }
      },
      acceso: "Sin credencial. Son datos públicos y solo se consultan, así que cualquiera puede construir y probar contra esto sin aceptar términos y condiciones."
    },
    sandbox: { script: "assets/cut-demo.js" },
    pruebas: "Todas las operaciones responden aquí mismo, sin credencial, con un extracto del catálogo: tres regiones completas (Tarapacá, Maule y Ñuble) con sus provincias y comunas. Los códigos son los oficiales; lo que no está en el extracto responde 404. El servicio real sigue respondiendo solo dentro de la red de SEM.",
    descargables: [
      { archivo: "cut.openapi.yaml", url: "estandares/cut.openapi.yaml", que: "El contrato en el formato que lee una máquina. Es la copia exacta de la especificación de referencia." },
      { archivo: "cut.datos-prueba.json", generar: "sandbox", que: "Las regiones, provincias y comunas del ambiente de pruebas, para montar un simulador propio o escribir pruebas automáticas." },
      { archivo: "cut-operaciones.pdf", que: "Listado de ejemplo de las consultas: regiones, provincias y comunas, y qué devuelve cada una." }
    ]
  },
];


/* ---------------------------------------------------------------------
   SERVICIOS — las herramientas de uso humano construidas sobre las APIs.

   Un servicio no es un intercambio: es una pantalla que consume uno o más
   nodos del catálogo de APIs y resuelve una tarea concreta sin programar.
   Se listan aparte porque responden a otra pregunta: el catálogo de APIs
   dice qué se puede consumir; este dice qué se puede usar hoy.

   Campos (la plantilla de la página los pinta con assets/servicio.js;
   el detalle de cada sección está en docs/plantillas.md):
     id             slug; la página lo declara en <main data-servicio="…">
     nombre         cómo se llama la herramienta, no el nodo del que consume
     nodo           id del nodo de APIs sobre el que está construida
     url            página del servicio dentro de este sitio
     funcion        una línea, para la tarjeta del catálogo
     descripcion    párrafo de entrada de la página
     tareas         qué resuelve, en frases que el usuario reconozca
     estado         Disponible | En construcción | Deseable
     actualizado    fecha ISO de la última revisión de la ficha
     fuentes_intro  frase antes de la tabla de fuentes, opcional
     fuentes        [{ dato, origen }] — qué institución genera cada dato
     wiki           { texto, url }? — entrada de la wiki. Si falta, se usa
                    procedencia.observaciones del nodo
     nota           advertencia destacada bajo la descripción, opcional.
                    Lo que depende de la conexión (datos de prueba o en
                    vivo) lo dice la propia pantalla, no este campo.
   --------------------------------------------------------------------- */
const SERVICIOS = [
  {
    id: "consulta-permiso-circulacion",
    nombre: "Consulta de permiso de circulación",
    nodo: "fiscalizacion",
    url: "servicio-fiscalizacion.html",
    funcion: "Escribir una patente y ver si el vehículo tiene su permiso de circulación al día, en qué comuna se pagó y cuánto.",
    descripcion: "Escriba la patente de un vehículo para ver si su permiso de circulación está vigente, en qué comuna se pagó y cuánto. Sirve también para patentes provisorias de automotora.",
    tareas: [
      "Comprobar si un vehículo tiene el permiso vigente",
      "Ver el historial de permisos por año y su institución recaudadora",
      "Consultar una patente provisoria de automotora"
    ],
    estado: "En construcción",
    actualizado: "2026-09-29",
    fuentes_intro: "La pantalla reúne en una sola consulta información que nace en instituciones distintas.",
    fuentes: [
      { dato: "La patente y los datos del vehículo", origen: "Registro Civil, que asigna la patente e inscribe el vehículo" },
      { dato: "El permiso de circulación y sus pagos", origen: "La municipalidad que lo cobró, que puede cambiar de un año a otro" },
      { dato: "Los permisos de una patente provisoria", origen: "La municipalidad que los emitió a la automotora" },
      { dato: "La consulta que junta todo lo anterior", origen: "Servicio del equipo de Servicios Municipales de SUBDERE" }
    ],
    wiki: { texto: "Permisos de circulación", url: "wiki-fiscalizacion.html" }
  },
  {
    id: "buscador-cut",
    nombre: "Buscador de códigos territoriales",
    nodo: "cut",
    url: "servicio-cut.html",
    funcion: "Buscar el Código Único Territorial de una comuna, provincia o región, o averiguar a qué lugar corresponde un código.",
    descripcion: "Escriba el nombre de una comuna, provincia o región para obtener su Código Único Territorial. O escriba un código para ver a qué lugar corresponde. Funciona en las dos direcciones con el mismo campo.",
    tareas: [
      "Escribir el nombre de una comuna y obtener su código",
      "Escribir un código y ver a qué comuna, provincia y región corresponde",
      "Copiar el código en su forma canónica, con los ceros a la izquierda"
    ],
    estado: "En construcción",
    actualizado: "2026-09-29",
    fuentes_intro: "La lista es una sola y oficial mantenida por SUBDERE.",
    fuentes: [
      { dato: "Los códigos y los nombres de regiones, provincias y comunas", origen: "SUBDERE, que mantiene el Código Único Territorial (versión 2018)" },
      { dato: "La consulta que los entrega", origen: "Servicio del equipo SEM de SUBDERE" }
    ],
    wiki: { texto: "Códigos Únicos Territoriales", url: "wiki-cut.html" }
  }
];

const AMBITOS = ["SGM", "Transversal"];


/* ---------------------------------------------------------------------
   TERMINOS — conceptos del sitio que tienen definición en el glosario
   de la wiki (wiki-glosario.html#<id>).

   En los textos de NODOS se marcan así:
     [[id]]              muestra `nombre` y lo enlaza a su definición
     [[id|texto]]        muestra `texto` y lo enlaza a su definición
   Solo la primera mención de cada campo. Lo resuelve assets/terminos.js.

   Campos:
     nombre       cómo se escribe el término en minúscula, dentro de una frase
     provisional  true = el nombre todavía no está definido
     alias        otros nombres con que se le conoce
     wiki         dirección de la entrada del glosario
   Al definir el nombre basta con cambiarlo aquí y en el glosario.
   --------------------------------------------------------------------- */
const TERMINOS = {
  "api": {
    nombre: "API",
    wiki: "wiki-glosario.html#api"
  },
  "aplicacion": {
    nombre: "aplicación",
    wiki: "wiki-glosario.html#aplicacion"
  },
  "clave-unica": {
    nombre: "Clave Única",
    wiki: "wiki-glosario.html#clave-unica"
  },
  "comprobante": {
    nombre: "comprobante",
    wiki: "wiki-glosario.html#comprobante"
  },
  "credencial": {
    nombre: "credencial",
    wiki: "wiki-glosario.html#credencial"
  },
  "estandar": {
    nombre: "estándar",
    alias: ["contrato", "especificación"],
    wiki: "wiki-glosario.html#estandar"
  },
  "nodo": {
    nombre: "nodo",
    wiki: "wiki-glosario.html#nodo"
  },
  "procedencia": {
    nombre: "procedencia",
    wiki: "wiki-glosario.html#procedencia"
  },
  "puerta-de-acceso": {
    nombre: "puerta de acceso",
    provisional: true,
    alias: ["Plataforma de Control"],
    wiki: "wiki-glosario.html#puerta-de-acceso"
  },
  "servicio": {
    nombre: "servicio",
    wiki: "wiki-glosario.html#servicio"
  },
  "sgm": {
    nombre: "SGM",
    alias: ["Sistema de Gestión Municipal"],
    wiki: "wiki-glosario.html#sgm"
  },
  "terminos-y-condiciones": {
    nombre: "Términos y Condiciones",
    alias: ["Uso de Términos y Condiciones"],
    wiki: "wiki-glosario.html#terminos-y-condiciones"
  },
  "zona-de-practica": {
    nombre: "zona de práctica",
    alias: ["sandbox"],
    wiki: "wiki-glosario.html#zona-de-practica"
  }
};
