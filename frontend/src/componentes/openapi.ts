// Lectura de una especificación OpenAPI 3.x para dibujarla en la ficha. Es el port de
// `prototipos/assets/openapi.js`: el catálogo no guarda operaciones, proyecta el contrato.
// Solo resuelve referencias internas (`#/…`); una especificación en varios archivos no se ensambla.

type Objeto = Record<string, unknown>;

export type Documento = Objeto & {
  info?: { title?: string; version?: string; description?: string };
  servers?: { url?: string }[];
  tags?: { name: string }[];
  paths?: Record<string, Record<string, unknown>>;
};

export type Parametro = { name: string; in: string; required?: boolean; schema?: unknown };

export type Respuesta = { codigo: string; descripcion: string; ejemplo: unknown };

export type Operacion = {
  metodo: string;
  ruta: string;
  resumen: string;
  descripcion: string;
  parametros: Parametro[];
  respuestas: Respuesta[];
};

export type Grupo = { tag: string; operaciones: Operacion[] };

const METODOS = ["get", "post", "put", "patch", "delete", "head", "options"];

function esObjeto(valor: unknown): valor is Objeto {
  return typeof valor === "object" && valor !== null;
}

/** Sigue un `$ref` interno. Un ciclo o un puntero roto devuelve un objeto vacío. */
export function deref(doc: Documento, nodo: unknown, visto = new Set<string>()): Objeto {
  if (!esObjeto(nodo)) return {};
  const ref = nodo.$ref;
  if (typeof ref !== "string") return nodo;
  if (visto.has(ref) || !ref.startsWith("#/")) return {};
  visto.add(ref);
  let destino: unknown = doc;
  for (const parte of ref.slice(2).split("/")) {
    const clave = parte.replace(/~1/g, "/").replace(/~0/g, "~");
    destino = esObjeto(destino) ? destino[clave] : undefined;
    if (destino === undefined) return {};
  }
  return deref(doc, destino, visto);
}

/** Un ejemplo derivado del propio esquema, cuando el contrato no trae uno. */
export function ejemplo(doc: Documento, esquema: unknown, profundidad = 0): unknown {
  if (profundidad > 8) return null;
  const s = deref(doc, esquema);
  if ("example" in s) return s.example;
  if (s.type === "array") return [ejemplo(doc, s.items, profundidad + 1)];
  if (esObjeto(s.properties)) {
    return Object.fromEntries(
      Object.entries(s.properties).map(([clave, valor]) => [clave, ejemplo(doc, valor, profundidad + 1)]),
    );
  }
  if (s.type === "integer" || s.type === "number") return 0;
  if (s.type === "boolean") return true;
  if (s.type === "string") return "";
  return null;
}

export function tipo(doc: Documento, esquema: unknown): string {
  const s = deref(doc, esquema);
  if (s.type === "array") return `lista de ${tipo(doc, s.items) || "objetos"}`;
  if (s.properties || s.type === "object") return "objeto";
  return typeof s.type === "string" ? s.type : "";
}

function respuestas(doc: Documento, op: Objeto): Respuesta[] {
  const todas = esObjeto(op.responses) ? op.responses : {};
  return Object.entries(todas).map(([codigo, valor]) => {
    const r = deref(doc, valor);
    const contenido = esObjeto(r.content) ? r.content : null;
    const media = contenido
      ? deref(doc, contenido["application/json"] ?? Object.values(contenido)[0])
      : null;
    const ej = !media ? null : media.example !== undefined ? media.example : ejemplo(doc, media.schema);
    return { codigo, descripcion: String(r.description ?? ""), ejemplo: ej };
  });
}

/** Las operaciones agrupadas según el orden de `tags` del documento. */
export function agrupar(doc: Documento): Grupo[] {
  const orden = (doc.tags ?? []).map((t) => t.name);
  const grupos = new Map<string, Operacion[]>();
  for (const [ruta, item] of Object.entries(doc.paths ?? {})) {
    for (const [metodo, valor] of Object.entries(item)) {
      if (!METODOS.includes(metodo) || !esObjeto(valor)) continue;
      const tags = Array.isArray(valor.tags) ? valor.tags : [];
      const tag = typeof tags[0] === "string" ? tags[0] : "Otras";
      if (!orden.includes(tag)) orden.push(tag);
      const parametros = (Array.isArray(valor.parameters) ? valor.parameters : []).map(
        (p) => deref(doc, p) as Parametro,
      );
      const lista = grupos.get(tag) ?? [];
      lista.push({
        metodo,
        ruta,
        resumen: String(valor.summary ?? ""),
        descripcion: String(valor.description ?? ""),
        parametros,
        respuestas: respuestas(doc, valor),
      });
      grupos.set(tag, lista);
    }
  }
  return orden.filter((t) => grupos.has(t)).map((t) => ({ tag: t, operaciones: grupos.get(t)! }));
}
