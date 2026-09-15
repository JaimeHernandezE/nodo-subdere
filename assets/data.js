/* Datos semilla del catálogo.
   Fuente: Mapeo de nodos de interoperabilidad del JPL, María José Besa, 8 de septiembre de 2026,
   tras la reunión con el Juzgado de Policía Local de Lo Barnechea.
   Los tres últimos fueron agregados por Allison Díaz.

   Este archivo es la maqueta del modelo de datos del catálogo. Cada campo de aquí
   debería existir como campo del modelo en Django. */

const NODOS = [
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
    ambito: "Justicia local",
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
    id: "registro-civil",
    nombre: "Registro Civil",
    ambito: "Identidad",
    funcion: "Consulta automatizada de patentes y del registro de multas no pagadas para identificar infractores.",
    descripcion: "Permite al tribunal resolver la identidad y el domicilio del infractor sin oficios ni esperas: datos personales, domicilio, estado civil, y la consulta al registro de deudores de pensiones de alimentos. Hoy buena parte de esto se resuelve por vías manuales.",
    instituciones: ["Servicio de Registro Civil e Identificación"],
    intercambio: "El municipio consulta",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Mapeo JPL",
    nota: ""
  },
  {
    id: "mtt",
    nombre: "Transportes",
    ambito: "Justicia local",
    funcion: "Recepción de lotes de partes empadronados y envío de morosos al registro nacional.",
    descripcion: "Recibe en lote las infracciones cursadas por fiscalización de transportes, en vez de digitarlas una por una, y devuelve al registro nacional de multas no pagadas a quienes quedan en mora.",
    instituciones: ["Ministerio de Transportes y Telecomunicaciones", "Servicio de Registro Civil e Identificación"],
    intercambio: "Bidireccional",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Mapeo JPL",
    nota: ""
  },
  {
    id: "mop",
    nombre: "Obras Públicas — multas TAG",
    ambito: "Justicia local",
    funcion: "Recepción de lotes de multas de autopistas y tramitación masiva de causas.",
    descripcion: "Habilita la tramitación masiva de causas y notificaciones asociadas a multas de autopistas concesionadas, que hoy llegan en volúmenes que el tribunal no puede procesar de a una. Devuelve los morosos al registro nacional.",
    instituciones: ["Ministerio de Obras Públicas", "Servicio de Registro Civil e Identificación"],
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
    id: "carabineros-gendarmeria",
    nombre: "Carabineros y Gendarmería",
    ambito: "Justicia local",
    funcion: "Partes, órdenes de búsqueda y arresto, y coordinación de sanciones.",
    descripcion: "Canal para la recepción de partes y para las medidas de apercibimiento, órdenes de búsqueda y arresto, y la coordinación de sanciones que hoy se tramitan por oficio.",
    instituciones: ["Carabineros de Chile", "Gendarmería de Chile"],
    intercambio: "Bidireccional",
    madurez: "Deseable",
    factibilidad: "Por evaluar",
    origen: "Mapeo JPL",
    nota: ""
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
    ambito: "Justicia local",
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

const AMBITOS = ["Justicia local", "Pagos", "Identidad", "Municipal", "Transversal"];
