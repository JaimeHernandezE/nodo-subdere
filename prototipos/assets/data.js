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

   Campos opcionales, presentes solo cuando el nodo ya tiene contrato publicado:
     espec    { archivo?, formato, validador, registrada, origen, acceso, expuesto? }
     pruebas  texto

   descargables  lista de { archivo, que } — solo demostración; no son archivos reales
   dependencias lista de { nombre, id? } — qué hay que tener implementado antes.
                id apunta a otra ficha del catálogo; si falta, todavía no está publicado

   `espec.archivo` es opcional. Si existe, la ficha lo lee y lo renderiza.
   `espec.expuesto` distingue contrato registrado de servicio alcanzable.
   Si solo hay metadato (formato, origen, acceso), la ficha lo muestra sin
   transcribir operaciones. Ver docs/adr-2026-09-estandar-legible-por-maquina.md.

   Cuando faltan, la ficha muestra el bloque «Pendiente» correspondiente. */

const NODOS = [
  {
    id: "sgm-core",
    oculto: true,
    nombre: "Base común del SGM",
    ambito: "SGM",
    clase: "plataforma",
    funcion: "Lo que todo módulo del SGM necesita por debajo: quién es quién, qué puede hacer cada uno, y el registro de lo que se hizo.",
    descripcion: "No es un módulo que el municipio decida usar: es lo que está debajo de todos. Se ocupa de entrar con Clave Única, de saber qué puede hacer cada funcionario, de mantener separados los datos de cada municipio, de guardar los parámetros que fija la norma, de dejar registro de cada acto y de conectar con Mercado Público, la firma electrónica y los documentos. Un municipio que use solamente Adquisiciones igual está usando esto. No hay que confundirlo con la puerta de entrada del nodo, que es otra cosa: esta es la base del sistema, aquella controla quién llama.",
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
      origen: "Está descrito en la documentación de arquitectura del SGM, dentro del repositorio del proyecto. El catálogo no guarda una copia.",
      acceso: "Dos caminos: las personas entran con Clave Única y los sistemas con una credencial propia. Los dos pasan por la misma puerta."
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
    funcion: "Todo el ciclo de una compra municipal, desde que alguien la pide hasta que se paga.",
    descripcion: "Es el primer módulo del SGM que entra al catálogo. Cubre las modalidades de compra de la Ley 19.886 —Compra Ágil primero, y después Convenio Marco, Licitación Pública y Trato Directo—, todas descritas en el mismo lugar. La pantalla del propio SGM y el sistema de un municipio piden exactamente lo mismo y entran por la misma puerta: nadie tiene un camino privilegiado. Eso sí, «solo Adquisiciones» no viene solo: se apoya en la base común y necesita saber si hay presupuesto y cómo se contabiliza.",
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
      origen: "Copia armada a partir de la descripción del módulo de Adquisiciones (versión 0.1.0), que en la documentación del SGM está repartida en varios archivos. La fuente vigente está en sgm-docs/modulos/adquisiciones/openapi/adquisiciones.openapi.yaml, en el repositorio del SGM. Si esa descripción cambia, hay que volver a armar esta copia: el catálogo no la edita.",
      acceso: "Dos caminos: las personas entran con Clave Única desde la pantalla del SGM, y los sistemas con una credencial propia. Los dos pasan por la misma puerta, sin atajos."
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
    funcion: "Consultar el permiso de circulación de un vehículo a partir de su patente: el vehículo, los permisos pagados por año y la institución que los recaudó.",
    descripcion: "El permiso de circulación lo cobra cada municipio, pero quien necesita comprobarlo casi nunca es el municipio que lo cobró: es otro municipio, una policía en un control, o el propio dueño del vehículo. Hoy esa comprobación depende de a quién se le pregunte. Este intercambio la resuelve con una consulta por patente que devuelve el vehículo, sus permisos y quién los recaudó, identificando a la institución por su Código Único Territorial y no por el nombre escrito a mano.",
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
      formato: "OpenAPI 3.0.3 — propuesta de contrato, escrita para esta demostración",
      validador: "https://spec.openapis.org/oas/v3.0.3",
      registrada: "27 de septiembre de 2026",
      expuesto: false,
      origen: "La escribió el equipo del Nodo SUBDERE a partir de una colección de referencia de Servicios Municipales. No es el contrato publicado del servicio: es una propuesta de cómo se vería publicado. Las diferencias respecto de la colección de origen están en la wiki.",
      acceso: "Credencial de corta duración entregada por la puerta de acceso. A diferencia de los códigos territoriales, acá circulan datos de un vehículo y de su titular, así que la consulta queda registrada."
    },
    pruebas: "No hay ambiente de pruebas. La pantalla de demostración funciona con datos inventados que viven en el propio sitio, y se descarta apenas el servicio sea alcanzable."
  },
  {
    id: "cut",
    nombre: "Códigos Únicos Territoriales (CUT)",
    ambito: "Transversal",
    clase: "intercambio",
    funcion: "Regiones, provincias y comunas con su Código Único Territorial, para que todos los sistemas llamen igual a cada lugar.",
    descripcion: "Casi cualquier intercambio entre un municipio y una institución empieza por dejar claro de qué comuna se está hablando. Si cada sistema tiene su propia lista, con sus abreviaturas y sus nombres escritos a su manera, los datos no calzan aunque todo lo demás esté bien. Este nodo entrega la lista oficial vigente, con el código que le corresponde a cada lugar. Conviene que sea el primero justamente porque casi todos los demás lo necesitan.",
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
      origen: "Especificación de referencia entregada por Juan Helo, septiembre de 2026. Este archivo es una copia exacta, sin ningún cambio: el catálogo no la edita. Las observaciones sobre el contrato están en la wiki, no aquí.",
      acceso: "Sin credencial. Son datos públicos y solo se consultan, así que cualquiera puede construir y probar contra esto sin aceptar términos y condiciones."
    },
    pruebas: "Todavía no hay ambiente de pruebas abierto: el servicio responde solo dentro de la red de SEM. Exponerlo es el requisito para que un tercero pueda construir contra el estándar sin el Uso de Términos y Condiciones y sin datos reales, que es lo que este nodo debería demostrar antes que ningún otro.",
    descargables: [
      { archivo: "cut-operaciones.pdf", que: "Listado de ejemplo de las consultas: regiones, provincias y comunas, y qué devuelve cada una." },
      { archivo: "cut.openapi.yaml", que: "Descripción de ejemplo de esas consultas. Es la copia de la especificación de referencia, no un archivo nuevo." }
    ]
  },
];


/* ---------------------------------------------------------------------
   SERVICIOS — las herramientas de uso humano construidas sobre las APIs.

   Un servicio no es un intercambio: es una pantalla que consume uno o más
   nodos del catálogo de APIs y resuelve una tarea concreta sin programar.
   Se listan aparte porque responden a otra pregunta: el catálogo de APIs
   dice qué se puede consumir; este dice qué se puede usar hoy.

   Campos:
     id       slug de la URL
     nombre   cómo se llama la herramienta, no el nodo del que consume
     nodo     id del nodo de APIs sobre el que está construida
     url      página del servicio dentro de este sitio
     tareas   qué resuelve, en frases que el usuario reconozca
     estado   Disponible | En construcción | Deseable
     nota     advertencia destacada, opcional
   --------------------------------------------------------------------- */
const SERVICIOS = [
  {
    id: "consulta-permiso-circulacion",
    nombre: "Consulta de permiso de circulación",
    nodo: "fiscalizacion",
    url: "servicio-fiscalizacion.html",
    funcion: "Escribir una patente y ver si el vehículo tiene su permiso de circulación al día, en qué comuna se pagó y cuánto.",
    tareas: [
      "Comprobar si un vehículo tiene el permiso vigente",
      "Ver el historial de permisos por año y su institución recaudadora",
      "Consultar una patente provisoria de automotora"
    ],
    estado: "En construcción",
    nota: "Pantalla de demostración, con datos inventados."
  },
  {
    id: "buscador-cut",
    nombre: "Buscador de códigos territoriales",
    nodo: "cut",
    url: "servicio-cut.html",
    funcion: "Buscar el Código Único Territorial de una comuna, provincia o región, o averiguar a qué lugar corresponde un código.",
    tareas: [
      "Escribir el nombre de una comuna y obtener su código",
      "Escribir un código y ver a qué comuna, provincia y región corresponde",
      "Copiar el código en su forma canónica, con los ceros a la izquierda"
    ],
    estado: "En construcción",
    nota: "Consulta la API del CUT. Mientras el servicio no esté alcanzable desde fuera de la red de SUBDERE, la pantalla funciona con una muestra de demostración y lo dice en pantalla."
  }
];

const AMBITOS = ["SGM", "Transversal"];
