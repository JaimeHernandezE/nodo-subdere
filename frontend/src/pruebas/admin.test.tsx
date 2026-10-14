// La administración: la prueba 5 del §6 de INSTRUCCIONES.md y lo que cada rol puede ver.
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import type { Fuente, NodoResumen, Perfil, Yo } from "../tipos";
import { NODO, NODO_RESUMEN, renderizar, ubicacionActual, type Backend } from "./util";

const ADMIN: Yo = { id: 1, nombre: "Administración local", rol: "administrador", municipio: null, es_encargado: false };
const LECTOR: Yo = { ...ADMIN, id: 2, nombre: "Ana Pérez", rol: "lector" };
const ENCARGADO: Yo = {
  id: 3,
  nombre: "Luis Soto",
  rol: "lector",
  municipio: { cut: "07101", nombre: "Talca" },
  es_encargado: true,
};

const LECTURA_INVALIDA = {
  id: 9,
  creado_en: "2026-10-14T13:00:00Z",
  commit: "92780349c067672d",
  valida: false,
  motivo: "especificacion.version: la ficha declara «0.2.0» y info.version del archivo dice «0.1.0».",
  perfil: "Administración local",
};

const FUENTE: Fuente = {
  id: 2,
  tipo: "repositorio",
  url: "https://gitlab.subdere.gob.cl/modernizacion/nodo-subdere/sem/fiscalizacion",
  rama: "main",
  ruta_ficha: "nodo/ficha.yaml",
  activa: true,
  nodo_identificador: "permisos-de-circulacion",
  ultima_lectura: LECTURA_INVALIDA,
  creado_en: "2026-10-14T13:00:00Z",
  actualizado_en: "2026-10-14T13:00:00Z",
};

const RETIRADO: NodoResumen = { ...NODO_RESUMEN, identificador: "viejo", nombre: "Un nodo retirado", visibilidad: "retirado" };
const OCULTO: NodoResumen = { ...NODO_RESUMEN, visibilidad: "oculto" };

async function entrarComo(yo: Yo, ruta: string, backend: Backend = {}) {
  const usuario = userEvent.setup();
  const r = renderizar("/entrar", { "/yo": { json: yo }, ...backend });
  await usuario.type(screen.getByLabelText("Token"), "token-de-prueba");
  await usuario.click(screen.getByRole("button", { name: "Entrar" }));
  await screen.findByText(yo.nombre, { selector: "summary" });
  await usuario.click(screen.getByText(yo.nombre, { selector: "summary" }));
  await usuario.click(screen.getByRole("link", { name: "Administración" }));
  if (ruta !== "/admin/fuentes") {
    const pestana = { "/admin/nodos": "Visibilidad", "/admin/servicios": "Servicios", "/admin/perfiles": "Perfiles" }[
      ruta
    ]!;
    const secciones = await screen.findByRole("navigation", { name: "Secciones de la administración" });
    await usuario.click(within(secciones).getByRole("link", { name: pestana }));
  }
  return { ...r, usuario };
}

describe("Administración", () => {
  it("sin sesión, /admin lleva a entrar", async () => {
    renderizar("/admin/nodos");
    await waitFor(() => expect(ubicacionActual()).toBe("/entrar"));
  });

  it("fuentes muestra el motivo de una lectura inválida y resincronizar hace POST", async () => {
    const pedidos: string[] = [];
    const { usuario } = await entrarComo(ADMIN, "/admin/fuentes", {
      "/fuentes": { json: [FUENTE] },
      "/fuentes/2/sincronizar": (_, init) => {
        pedidos.push(init?.method ?? "GET");
        return { json: { ...LECTURA_INVALIDA, id: 10, valida: true, motivo: "", contenido: "" } };
      },
    });
    expect(await screen.findByText(/la ficha declara «0.2.0»/)).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Resincronizar" }));
    expect(await screen.findByText(/lectura válida en el commit 92780349/)).toBeInTheDocument();
    expect(screen.getByText(/historial de lecturas de la fuente a nombre de Administración local/)).toBeInTheDocument();
    expect(pedidos).toEqual(["POST"]);
  });

  it("5. en visibilidad, los campos de la ficha no son editables", async () => {
    const { usuario } = await entrarComo(ADMIN, "/admin/nodos", {
      "/nodos": (url) => ({ json: url.searchParams.get("visibilidad") === "todas" ? [OCULTO, RETIRADO] : [] }),
      "/nodos/cut": { json: { ...NODO, visibilidad: "oculto" } },
    });
    const fila = (await screen.findByRole("link", { name: OCULTO.nombre })).closest("tr")!;
    await usuario.click(within(fila).getByRole("button", { name: "Detalle" }));

    const ficha = await screen.findByRole("group", { name: "Campos de la ficha" });
    expect(ficha).toBeDisabled();
    for (const campo of within(ficha).getAllByRole("textbox")) expect(campo).toBeDisabled();
    expect(within(ficha).getByLabelText("Nombre")).toHaveValue(OCULTO.nombre);
    await waitFor(() => expect(within(ficha).getByLabelText("Versión del contrato")).toHaveValue("1.0.0"));
    expect(within(ficha).getByText(/Los escribe la sincronización/)).toBeInTheDocument();
    expect(screen.getByRole("group", { name: "Decisión editorial" })).toBeEnabled();
  });

  it("un nodo retirado solo vuelve a oculto, y publicar envía la visibilidad", async () => {
    const cuerpos: unknown[] = [];
    const { usuario } = await entrarComo(ADMIN, "/admin/nodos", {
      "/nodos": (url) => ({ json: url.searchParams.get("visibilidad") === "todas" ? [OCULTO, RETIRADO] : [] }),
      "/nodos/cut": (_, init) => {
        if (init?.method === "PATCH") cuerpos.push(JSON.parse(String(init.body)));
        return { json: { ...NODO, visibilidad: "publicado" } };
      },
    });
    const retirado = (await screen.findByRole("link", { name: RETIRADO.nombre })).closest("tr")!;
    expect(within(retirado).getByRole("button", { name: "Volver a oculto" })).toBeInTheDocument();
    expect(within(retirado).queryByRole("button", { name: "Publicar" })).not.toBeInTheDocument();

    const oculto = screen.getByRole("link", { name: OCULTO.nombre }).closest("tr")!;
    await usuario.click(within(oculto).getByRole("button", { name: "Publicar" }));
    expect(await screen.findByText(/Visibilidad de cut: oculto a publicado/)).toBeInTheDocument();
    expect(cuerpos).toEqual([{ visibilidad: "publicado" }]);
  });

  it("un curador crea un servicio sobre un nodo oculto y se le avisa que aún no aparece", async () => {
    const creados: unknown[] = [];
    const { usuario } = await entrarComo({ ...ADMIN, rol: "curador" }, "/admin/servicios", {
      "/nodos": (url) => ({ json: url.searchParams.get("visibilidad") === "todas" ? [OCULTO, RETIRADO] : [] }),
      "/servicios": (url, init) => {
        if (init?.method === "POST") {
          const cuerpo = JSON.parse(String(init.body));
          creados.push(cuerpo);
          return { status: 201, json: { ...cuerpo, actualizado: "2026-10-14T13:00:00Z" } };
        }
        expect(url.searchParams.get("visibilidad")).toBe("todas");
        return { json: [] };
      },
    });
    expect(await screen.findByText("Todavía no hay servicios.")).toBeInTheDocument();

    await usuario.click(screen.getByText("Crear un servicio"));
    const nodo = screen.getByLabelText("Nodo");
    expect(within(nodo).queryByRole("option", { name: /retirado/ })).not.toBeInTheDocument();
    await usuario.type(screen.getByLabelText("Slug"), "buscador-cut");
    await usuario.type(screen.getByLabelText("Nombre de la herramienta"), "Buscador de códigos territoriales");
    await usuario.type(screen.getByLabelText(/Función/), "Buscar el código de una comuna.");
    await usuario.type(screen.getByLabelText("Descripción"), "Escribe un nombre o un código.");
    await usuario.type(screen.getByLabelText(/Tareas/), "Buscar un código{enter}Ver una comuna");
    await usuario.type(screen.getByLabelText("Dato"), "Los códigos");
    await usuario.type(screen.getByLabelText("Origen"), "SUBDERE");
    await usuario.click(screen.getByRole("button", { name: "Crear servicio" }));

    expect(await screen.findByText(/aparecerá en el sitio cuando se publique el nodo/)).toBeInTheDocument();
    expect(creados).toEqual([
      {
        slug: "buscador-cut",
        nodo: "cut",
        nombre: "Buscador de códigos territoriales",
        funcion: "Buscar el código de una comuna.",
        descripcion: "Escribe un nombre o un código.",
        tareas: ["Buscar un código", "Ver una comuna"],
        fuentes: [{ dato: "Los códigos", origen: "SUBDERE" }],
        estado: "en_construccion",
        nota: "",
      },
    ]);
  });

  it("un lector no ve botones que cambien algo ni la pestaña de perfiles", async () => {
    await entrarComo(LECTOR, "/admin/fuentes", { "/fuentes": { json: [FUENTE] } });
    expect(await screen.findByText(/la ficha declara/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Resincronizar" })).not.toBeInTheDocument();
    expect(screen.queryByText("Registrar una fuente")).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Perfiles" })).not.toBeInTheDocument();
  });

  it("un encargado crea solo lectores de su municipio y no se modifica a sí mismo", async () => {
    const creados: unknown[] = [];
    const equipo: Perfil[] = [
      { id: 3, run: "11.111.111-1", nombre: "Luis Soto", rol: "lector", municipio: "07101", es_encargado: true, activo: true, creado_en: "", actualizado_en: "" },
      { id: 4, run: "22.222.222-2", nombre: "Marta Díaz", rol: "lector", municipio: "07101", es_encargado: false, activo: true, creado_en: "", actualizado_en: "" },
    ];
    const { usuario } = await entrarComo(ENCARGADO, "/admin/perfiles", {
      "/perfiles": (_, init) => {
        if (init?.method === "POST") {
          const cuerpo = JSON.parse(String(init.body));
          creados.push(cuerpo);
          return { status: 201, json: { ...equipo[1], id: 5, ...cuerpo, run: "12.345.678-5" } };
        }
        return { json: equipo };
      },
    });
    expect(await screen.findByRole("heading", { name: "Equipo de Talca" })).toBeInTheDocument();

    const propia = screen.getByText("Tu perfil").closest("tr")!;
    expect(within(propia).queryByRole("button")).not.toBeInTheDocument();
    const otra = screen.getByText("Marta Díaz").closest("tr")!;
    expect(within(otra).getByRole("button", { name: "Desactivar" })).toBeInTheDocument();
    expect(within(otra).queryByRole("button", { name: "Editar" })).not.toBeInTheDocument();

    await usuario.click(screen.getByText("Dar de alta a una persona de tu equipo"));
    expect(screen.queryByLabelText("Rol")).not.toBeInTheDocument();
    await usuario.type(screen.getByLabelText("RUN"), "12345678-5");
    await usuario.type(screen.getByLabelText("Nombre"), "Pedro Rojas");
    await usuario.click(screen.getByRole("button", { name: "Crear perfil" }));
    expect(await screen.findByText(/Perfil creado: Pedro Rojas/)).toBeInTheDocument();
    expect(creados).toEqual([{ run: "12345678-5", nombre: "Pedro Rojas", rol: "lector", municipio: "07101" }]);
  });
});
