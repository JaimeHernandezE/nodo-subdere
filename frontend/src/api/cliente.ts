// Cliente del backend. Todo pasa por acá: el navegador nunca llama a una fuente externa.

const BASE = (import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1").replace(/\/+$/, "");

/** Un error con el sobre del backend: `{error: {codigo, mensaje, detalles}}`. */
export class ErrorApi extends Error {
  constructor(
    readonly status: number,
    readonly codigo: string,
    mensaje: string,
    readonly detalles: { campo?: string; valor?: unknown; mensaje?: string }[] = [],
  ) {
    super(mensaje);
    this.name = "ErrorApi";
  }
}

export function esError(error: unknown, codigo: string): boolean {
  return error instanceof ErrorApi && error.codigo === codigo;
}

export function esEstado(error: unknown, status: number): boolean {
  return error instanceof ErrorApi && error.status === status;
}

// El token vive solo en memoria: ni localStorage ni cookies. Al recargar, se pierde.
let token: string | null = null;

export function fijarToken(nuevo: string | null) {
  token = nuevo;
}

export function hayToken(): boolean {
  return token !== null;
}

type Opciones = {
  params?: Record<string, string | number | undefined>;
  cabeceras?: Record<string, string>;
  texto?: boolean;
  signal?: AbortSignal;
};

export function url(ruta: string, params?: Opciones["params"]): string {
  const consulta = new URLSearchParams();
  for (const [clave, valor] of Object.entries(params ?? {})) {
    if (valor !== undefined && valor !== "") consulta.set(clave, String(valor));
  }
  const q = consulta.toString();
  return `${BASE}${ruta}${q ? `?${q}` : ""}`;
}

export async function pedir<T>(ruta: string, opciones: Opciones = {}): Promise<T> {
  const cabeceras: Record<string, string> = {
    Accept: opciones.texto ? "*/*" : "application/json",
    ...opciones.cabeceras,
  };
  if (token) cabeceras.Authorization = `Bearer ${token}`;

  let respuesta: Response;
  try {
    respuesta = await fetch(url(ruta, opciones.params), {
      headers: cabeceras,
      signal: opciones.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ErrorApi(0, "SIN_CONEXION", "No se pudo conectar con el nodo.");
  }

  if (!respuesta.ok) {
    let cuerpo: { error?: { codigo?: string; mensaje?: string; detalles?: ErrorApi["detalles"] } } = {};
    try {
      cuerpo = await respuesta.json();
    } catch {
      // Sin cuerpo JSON: queda el estado HTTP.
    }
    const error = cuerpo.error ?? {};
    throw new ErrorApi(
      respuesta.status,
      error.codigo ?? `HTTP_${respuesta.status}`,
      error.mensaje ?? `El nodo respondió ${respuesta.status}.`,
      error.detalles ?? [],
    );
  }

  return (opciones.texto ? await respuesta.text() : await respuesta.json()) as T;
}
