/* Datos semilla del catálogo.

   Trece nodos vienen del mapeo de interoperabilidad del JPL, María José Besa,
   8 de septiembre de 2026, tras la reunión con el Juzgado de Policía Local de
   Lo Barnechea. Los tres últimos de esa lista los agregó Allison Díaz.

   División territorial no viene de ahí: es el prototipo basado en el repositorio
   «utilitarios» del equipo SEM, y el único con implementación existente.

   Dos nodos más, ámbito SGM, se agregaron el 15 de septiembre de 2026:
     sgm-core        — la base común del SGM (clase plataforma: está siempre, no se elige)
     adquisiciones   — primer módulo de negocio con OpenAPI de piloto

   Estándares de Gobierno Digital (nodos-gobierno) se retiró el 16 de septiembre
   de 2026: es condición de capa, no un intercambio. Ver docs/maqueta.md.

   Este archivo es la maqueta del modelo de datos del catálogo. Cada campo de aquí
   debería existir como campo del modelo en Django.

   Campos:
     clase    intercambio | plataforma
              plataforma = condición de otros; no se elige por módulo

   Campos opcionales, presentes solo cuando el nodo ya tiene contrato publicado:
     espec    { archivo?, formato, validador, registrada, origen, acceso }
     pruebas  texto

   `espec.archivo` es opcional. Si existe, la ficha lo lee y lo renderiza.
   Si solo hay metadato (formato, origen, acceso), la ficha lo muestra sin
   transcribir operaciones. Ver docs/adr-2026-09-estandar-legible-por-maquina.md.

   Cuando faltan, la ficha muestra el bloque «Pendiente» correspondiente. */

const NODOS = [
  {
    id: "sgm-core",
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
    pruebas: "Todavía no hay ambiente de pruebas. El sandbox previsto es el de SGM (sandbox-desarrolladores.md en el corpus de licitación)."
  },
  {
    id: "adquisiciones",
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
    nota: "Ya está escrito qué entrega, pero el servicio todavía no corre en ninguna parte. Depende de la base común del SGM y de que existan presupuestos y contabilidad. La descripción vive en la documentación del SGM, repartida en varios archivos; el catálogo no la copia, a propósito.",
    espec: {
      formato: "OpenAPI 3.1 — el formato estándar para describir un servicio web",
      validador: "https://spec.openapis.org/oas/v3.1.0",
      registrada: "15 de septiembre de 2026",
      origen: "Está descrito en la documentación del módulo de Adquisiciones, repartido en varios archivos dentro del repositorio del proyecto. El catálogo no guarda una copia.",
      acceso: "Dos caminos: las personas entran con Clave Única desde la pantalla del SGM, y los sistemas con una credencial propia. Los dos pasan por la misma puerta, sin atajos."
    },
    pruebas: "Todavía no hay ambiente de pruebas. El sandbox previsto es el de SGM (sandbox-desarrolladores.md), con el mismo contrato que en producción."
  },
  {
    id: "division-territorial",
    nombre: "División Político-Administrativa",
    ambito: "Transversal",
    clase: "intercambio",
    funcion: "Regiones, provincias y comunas con su código oficial, para que todos los sistemas llamen igual a cada lugar.",
    descripcion: "Casi cualquier intercambio entre un municipio y una institución empieza por dejar claro de qué comuna se está hablando. Si cada sistema tiene su propia lista, con sus abreviaturas y sus nombres escritos a su manera, los datos no calzan aunque todo lo demás esté bien. Este nodo entrega la lista oficial vigente, con el código que le corresponde a cada lugar. Conviene que sea el primero justamente porque casi todos los demás lo necesitan.",
    instituciones: ["SUBDERE — SEM", "Municipios", "Proveedores de sistemas de gestión municipal"],
    intercambio: "El municipio consulta",
    madurez: "En desarrollo",
    factibilidad: "Alta",
    origen: "Un servicio que ya construyó el equipo SEM de SUBDERE",
    nota: "Es el único del catálogo que además de estar escrito ya funciona. Pero funciona solo dentro de la red de SUBDERE: desde fuera todavía no se puede usar, y nadie se ha comprometido a mantenerlo andando. Lo que se publica acá es qué entrega, no una promesa de que esté disponible.",
    espec: {
      archivo: "estandares/division-territorial.openapi.yaml",
      formato: "OpenAPI 3.0.3 — el formato estándar para describir un servicio web",
      validador: "https://spec.openapis.org/oas/v3.0.3",
      registrada: "15 de septiembre de 2026",
      origen: "La publicó el equipo SEM de SUBDERE. Este archivo es una copia exacta, sin ningún cambio: el catálogo no la edita.",
      acceso: "Sin credencial. Son datos públicos y solo se consultan, así que cualquiera puede construir y probar contra esto sin firmar nada."
    },
    pruebas: "Todavía no hay ambiente de pruebas abierto: el servicio responde solo dentro de la red de SEM. Exponerlo es el requisito para que un tercero pueda construir contra el estándar sin convenio y sin datos reales, que es lo que este nodo debería demostrar antes que ningún otro."
  },
  {
    id: "pagos-tesoreria",
    nombre: "Pagos y Tesorería Municipal",
    ambito: "Pagos",
    clase: "intercambio",
    funcion: "Que la sentencia, la multa y su estado de pago fluyan hacia la contabilidad del municipio.",
    descripcion: "Conecta la resolución del tribunal con el registro contable municipal, de modo que la multa cursada y su estado de pago lleguen al sistema de gestión sin transcripción. Para los municipios que no tienen sistema de gestión, opera con un mecanismo alternativo de comunicación, de manera que ninguno queda fuera por no tener con qué conectarse.",
    instituciones: ["SUBDERE — SGM", "Tesorería General de la República", "Proveedores de sistemas de gestión municipal"],
    intercambio: "Bidireccional",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Mapeo JPL",
    nota: "Desemboca en la contabilidad del sistema de gestión municipal: es uno de los dos nodos que apuntan de vuelta al propio SGM."
  },
  {
    id: "indice-expedientes",
    nombre: "Índice de Expedientes",
    ambito: "Juzgado de Policía Local",
    clase: "intercambio",
    funcion: "Carpeta digital por ROL, con documentos firmados e identificador único nacional.",
    descripcion: "Le da a cada causa un número único en todo el país, con un formato conocido, para poder seguirla a lo largo de su recorrido y entre instituciones. Sin ese número común, cada institución vuelve a bautizar el mismo expediente a su manera y después nadie sabe que son el mismo.",
    instituciones: ["Poder Judicial", "Corte Suprema"],
    intercambio: "Bidireccional",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Mapeo JPL",
    nota: ""
  },
  {
    id: "notificador-electronico",
    nombre: "Notificador Electrónico",
    ambito: "Transversal",
    clase: "intercambio",
    funcion: "Notificación al domicilio digital único, con firma del Estado.",
    descripcion: "Reemplaza la notificación física por la entrega al domicilio digital único de la persona. Es el nodo que más depende de una definición externa: habilita una norma miscelánea que está pendiente en la ley de reajuste.",
    instituciones: ["Secretaría de Gobierno Digital", "FirmaGob", "Domicilio Digital Único"],
    intercambio: "El municipio entrega",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Mapeo JPL",
    nota: "Su factibilidad no es técnica: depende de que se apruebe la norma que lo habilita."
  },
  {
    id: "dom",
    nombre: "Dirección de Obras Municipales",
    ambito: "Municipal",
    clase: "intercambio",
    funcion: "Recepción final de obras, emplazamiento y permisos de edificación.",
    descripcion: "Intercambio con la Dirección de Obras del propio municipio para resolver antecedentes de emplazamiento, permisos de edificación y recepción final que el tribunal necesita en sus causas.",
    instituciones: ["Dirección de Obras Municipales"],
    intercambio: "El municipio consulta",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Mapeo JPL",
    nota: "Es el segundo nodo que apunta de vuelta al propio municipio: la DOM es un módulo municipal más, no una institución externa."
  },
  {
    id: "correos",
    nombre: "Correos de Chile",
    ambito: "Transversal",
    clase: "intercambio",
    funcion: "Envío de archivos para cartas certificadas.",
    descripcion: "Convenio de envío de archivos para la emisión de cartas certificadas, que es hoy el canal formal de notificación mientras el domicilio digital único no esté disponible.",
    instituciones: ["Correos de Chile"],
    intercambio: "El municipio entrega",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Mapeo JPL",
    nota: ""
  },
  {
    id: "inspeccion-municipal",
    nombre: "Inspección Municipal",
    ambito: "Municipal",
    clase: "intercambio",
    funcion: "Origen masivo de las infracciones municipales que llegan al tribunal.",
    descripcion: "La inspección municipal es donde se generan en volumen las infracciones que después tramita el tribunal. Conectarla evita que el parte se digite dos veces: una al cursarlo y otra al ingresarlo a la causa.",
    instituciones: ["Municipalidad — Inspección"],
    intercambio: "El municipio entrega",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Agregado por Allison Díaz",
    nota: ""
  },
  {
    id: "direcciones-municipales",
    nombre: "Direcciones municipales que remiten infracciones",
    ambito: "Municipal",
    clase: "intercambio",
    funcion: "Canalizar hacia el tribunal las infracciones que originan otras direcciones del municipio.",
    descripcion: "Además de inspección, varias direcciones municipales remiten infracciones al tribunal. El mapeo propone canalizarlas a través de la inspección de cada municipalidad en vez de abrir un canal por dirección.",
    instituciones: ["Municipalidad — direcciones varias"],
    intercambio: "El municipio entrega",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Agregado por Allison Díaz",
    nota: ""
  },
  {
    id: "entre-juzgados",
    nombre: "Interoperabilidad entre Juzgados de Policía Local",
    ambito: "Juzgado de Policía Local",
    clase: "intercambio",
    funcion: "Tramitación electrónica de exhortos y diligencias entre tribunales.",
    descripcion: "Permite que dos juzgados de policía local se envíen exhortos y otras diligencias por vía electrónica, evitando el intercambio físico de documentos entre comunas.",
    instituciones: ["Juzgados de Policía Local"],
    intercambio: "Bidireccional",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Agregado por Allison Díaz",
    nota: ""
  }
];

const AMBITOS = ["SGM", "Transversal", "Juzgado de Policía Local", "Pagos", "Municipal"];
