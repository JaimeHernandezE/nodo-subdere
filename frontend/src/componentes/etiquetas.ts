// Cómo se nombra y se pinta cada valor que viene del backend. Las clases son las de la maqueta.
import type { EstadoServicio, Nodo, Origen } from "../tipos";

export const ACCESO: Record<Nodo["acceso_tipo"], string> = {
  abierto: "Abierto",
  credencial: "Con credencial",
  "clave-unica": "Clave Única",
};

export const MADUREZ: Record<Nodo["madurez"], string> = {
  Deseable: "tag tag-mad",
  "En evaluación": "tag tag-eval",
  "En desarrollo": "tag tag-dev",
  Operativo: "tag tag-oper",
};

export const INTERCAMBIO: Record<string, string> = {
  consulta: "El municipio consulta",
  entrega: "El municipio entrega",
};

export const FORMATO: Record<string, string> = {
  "openapi-3.0": "OpenAPI 3.0",
  "openapi-3.1": "OpenAPI 3.1",
  descripcion: "Solo metadato",
};

export const COPIA: Record<string, { texto: string; clase: string }> = {
  exacta: { texto: "Copia exacta", clase: "tag tag-dev" },
  instantanea: { texto: "Instantánea", clase: "tag tag-eval" },
  reconstruccion: { texto: "Propuesta reconstruida", clase: "tag tag-mad" },
  "sin-copia": { texto: "Sin copia en el catálogo", clase: "tag tag-sin" },
};

export const ESTADO_SERVICIO: Record<EstadoServicio, { texto: string; clase: string }> = {
  disponible: { texto: "Disponible", clase: "tag" },
  en_construccion: { texto: "En construcción", clase: "tag tag-dev" },
  deseable: { texto: "Deseable", clase: "tag tag-mad" },
};

export const ORIGEN: Record<Origen, string> = {
  fuente: "En vivo",
  foto: "Copia guardada",
  muestra: "Datos de muestra",
};
