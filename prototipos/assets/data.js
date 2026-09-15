/* Datos semilla del catálogo.

   Trece nodos vienen del mapeo de interoperabilidad del JPL, María José Besa,
   8 de septiembre de 2026, tras la reunión con el Juzgado de Policía Local de
   Lo Barnechea. Los tres últimos de esa lista los agregó Allison Díaz.

   El primero —división territorial— no viene de ahí: es el prototipo basado en
   el repositorio «utilitarios» del equipo SEM, y el único con implementación
   existente. Por eso trae tres campos que los demás no tienen.

   Este archivo es la maqueta del modelo de datos del catálogo. Cada campo de aquí
   debería existir como campo del modelo en Django.

   Campos opcionales, presentes solo cuando el nodo ya tiene contrato publicado:
     espec    { archivo, formato, validador, registrada, origen, acceso }
     pruebas  texto

   `espec.archivo` apunta a la especificación legible por máquina del nodo. La ficha
   la lee y la renderiza: no hay operaciones transcritas en este archivo, a propósito.
   Ver docs/adr-2026-09-estandar-legible-por-maquina.md.

   Cuando faltan, la ficha muestra el bloque «Pendiente» correspondiente. */

const NODOS = [
  {
    id: "division-territorial",
    nombre: "División Político-Administrativa",
    ambito: "Transversal",
    funcion: "Consulta de regiones, provincias y comunas con su código oficial, para que todos los sistemas nombren el territorio igual.",
    descripcion: "Casi cualquier intercambio entre un municipio y una institución empieza por establecer de qué comuna se habla. Si cada sistema mantiene su propia lista —con sus abreviaturas, sus códigos y sus nombres escritos a su manera—, los datos no cruzan aunque el formato sea correcto. Este nodo entrega la división político-administrativa vigente con su código único territorial, y conviene que sea el primero precisamente porque casi todos los demás dependen de él.",
    instituciones: ["SUBDERE — SEM", "Municipios", "Proveedores de sistemas de gestión municipal"],
    intercambio: "El municipio consulta",
    madurez: "En desarrollo",
    factibilidad: "Alta",
    origen: "Repositorio «utilitarios», equipo SEM de SUBDERE",
    nota: "Es el único nodo del catálogo con implementación existente, y por eso el único cuya ficha publica un estándar en vez de un pendiente. Hoy opera dentro de la infraestructura de SEM y todavía no está expuesto como nodo: no hay acceso desde fuera de esa red ni nivel de servicio comprometido. Lo que se publica acá es su contrato técnico, no una promesa de disponibilidad.",
    espec: {
      archivo: "estandares/division-territorial.openapi.yaml",
      formato: "OpenAPI 3.0.3",
      validador: "https://spec.openapis.org/oas/v3.0.3",
      registrada: "15 de septiembre de 2026",
      origen: "Publicada por el equipo SEM en el repositorio «utilitarios». Este archivo es una copia sin modificar; el catálogo no lo edita.",
      acceso: "Sin credencial. Los datos son públicos y de solo lectura, así que este nodo pertenece al plano abierto: se construye y se prueba contra él sin convenio."
    },
    pruebas: "Todavía no hay ambiente de pruebas abierto: el servicio responde solo dentro de la red de SEM. Exponerlo es el requisito para que un tercero pueda construir contra el estándar sin convenio y sin datos reales, que es lo que este nodo debería demostrar antes que ningún otro."
  },
  {
    id: "pagos-tesoreria",
    nombre: "Pagos y Tesorería Municipal",
    ambito: "Pagos",
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
    funcion: "Carpeta digital por ROL, con documentos firmados e identificador único nacional.",
    descripcion: "Establece un identificador numérico único a nivel nacional, con formato conocido y trazable, que permite seguir una causa a lo largo de su recorrido y entre instituciones. Sin un identificador común, cada institución vuelve a nombrar el mismo expediente a su manera.",
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
    id: "nodos-gobierno",
    nombre: "Estándares de Gobierno Digital",
    ambito: "Transversal",
    funcion: "Clave Única, FirmaGob y la plataforma de interoperabilidad del Estado.",
    descripcion: "No es un intercambio de datos sino el conjunto de estándares de transformación digital sobre los que se apoyan los demás: autenticación, firma electrónica, y el canal por el que el Estado conversa consigo mismo.",
    instituciones: ["Secretaría de Gobierno Digital"],
    intercambio: "Transversal",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Mapeo JPL",
    nota: "Condición de los demás más que nodo propio: lo que aquí se defina restringe a todo el resto del catálogo."
  },
  {
    id: "correos",
    nombre: "Correos de Chile",
    ambito: "Transversal",
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

const AMBITOS = ["Transversal", "Juzgado de Policía Local", "Pagos", "Municipal"];
