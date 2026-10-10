import { render } from "@testing-library/react";
import { MemoryRouter, useLocation } from "react-router";
import { vi } from "vitest";

import { fijarToken } from "../api/cliente";
import { crearClienteDeConsultas, Proveedores, RutasDelSitio } from "../app/App";
import type { Entrada, EntradaResumen, Nodo, NodoResumen } from "../tipos";

type Respuesta = { status?: number; json?: unknown; texto?: string };
type Manejador = (url: URL, init: RequestInit | undefined) => Respuesta;
/** Ruta del backend (sin `/api/v1`) a su respuesta. Lo que no está, responde 404. */
export type Backend = Record<string, Respuesta | Manejador>;

export function simularBackend(backend: Backend) {
  const fetch = vi.fn(async (entrada: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(entrada));
    const ruta = url.pathname.replace(/^\/api\/v1/, "");
    const definida = backend[ruta];
    const r: Respuesta =
      typeof definida === "function"
        ? definida(url, init)
        : (definida ?? { status: 404, json: { error: { codigo: "NO_ENCONTRADO", mensaje: "No existe." } } });
    const cuerpo = r.texto ?? JSON.stringify(r.json ?? null);
    return new Response(cuerpo, {
      status: r.status ?? 200,
      headers: { "Content-Type": r.texto !== undefined ? "application/yaml" : "application/json" },
    });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

let ubicacion = "";
function Ubicacion() {
  const l = useLocation();
  ubicacion = `${l.pathname}${l.search}${l.hash}`;
  return null;
}
export const ubicacionActual = () => ubicacion;

export function renderizar(ruta: string, backend: Backend = {}) {
  fijarToken(null);
  const fetch = simularBackend({ ...PUBLICO, ...backend });
  const cliente = crearClienteDeConsultas();
  cliente.setDefaultOptions({ queries: { ...cliente.getDefaultOptions().queries, retry: false } });
  const resultado = render(
    <MemoryRouter initialEntries={[ruta]}>
      <Proveedores cliente={cliente}>
        <RutasDelSitio />
        <Ubicacion />
      </Proveedores>
    </MemoryRouter>,
  );
  return { ...resultado, fetch };
}

export const NODO_RESUMEN: NodoResumen = {
  identificador: "cut",
  nombre: "Códigos Únicos Territoriales",
  sigla: "CUT",
  ambito: "Territorio",
  clase: "intercambio",
  intercambio: "consulta",
  funcion: "El código de cada región, provincia y comuna.",
  madurez: "En desarrollo",
  acceso_tipo: "abierto",
  visibilidad: "publicado",
  orden: 1,
  leido_en: "2026-10-01T12:00:00Z",
};

export const NODO: Nodo = {
  ...NODO_RESUMEN,
  descripcion: "Para que todos los sistemas llamen igual a cada comuna.",
  instituciones: ["SUBDERE", "INE"],
  responsable: { organismo: "SUBDERE", equipo: "División de Municipalidades", correo: "nodo@subdere.gov.cl" },
  origen: null,
  procedencia: null,
  acceso: null,
  ambientes: [],
  especificacion: {
    version: "1.0.0",
    formato: "openapi-3.0",
    ruta: "especificacion/openapi.yaml",
    huella: "abc",
    publicada: "2026-09-01",
    commit: "abc123",
    archivo: "https://git.example/cut/openapi.yaml",
  },
  nota_editorial: "",
  commit: "abc123",
};

export const ENTRADA_INICIO: Entrada = {
  slug: "inicio",
  titulo: "Wiki",
  descripcion: "La documentación de trabajo.",
  seccion: "" as Entrada["seccion"],
  orden: 0,
  nodo: "",
  publicada: true,
  publicada_en: "2026-10-01T12:00:00Z",
  version: 1,
  html: '<h2 id="la-wiki">La wiki</h2><p>Hola.</p>',
};

export const ENTRADAS: EntradaResumen[] = [
  { ...ENTRADA_INICIO },
  {
    slug: "glosario",
    titulo: "Glosario",
    descripcion: "Los conceptos.",
    seccion: "referencia",
    orden: 1,
    nodo: "",
    publicada: true,
    publicada_en: "2026-10-01T12:00:00Z",
  },
];

/** Lo mínimo para que las páginas públicas carguen sin sesión. */
export const PUBLICO: Backend = {
  "/ambitos": { json: [{ nombre: "Territorio", orden: 1 }] },
  "/nodos": { json: [NODO_RESUMEN] },
  "/nodos/cut": { json: NODO },
  "/servicios": { json: [] },
  "/wiki": { json: ENTRADAS },
  "/wiki/inicio": { json: ENTRADA_INICIO },
  "/wiki/glosario": {
    json: {
      ...ENTRADA_INICIO,
      ...ENTRADAS[1],
      html: '<h2 id="comprobante">Comprobante</h2><p>Ver <a href="/wiki/inicio">inicio</a>.</p>',
    },
  },
};
