// Las pruebas mínimas del §6 de INSTRUCCIONES.md que tocan el sitio público. La 5 (pantalla de
// visibilidad) llega con la administración.
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ENTRADAS, renderizar, ubicacionActual } from "./util";

const YO = {
  id: 1,
  nombre: "Ana Pérez",
  rol: "lector",
  municipio: { id: 1, nombre: "Talca", cut: "07101" },
  es_encargado: false,
};

async function entrarCon(usuario: ReturnType<typeof userEvent.setup>) {
  await usuario.type(screen.getByLabelText("Token"), "token-de-prueba");
  await usuario.click(screen.getByRole("button", { name: "Entrar" }));
}

describe("1. Las rutas públicas cargan sin sesión", () => {
  it.each([
    ["/", "heading", /nodo/i],
    ["/que-es", "heading", /./],
    ["/apis", "link", /Códigos Únicos Territoriales/],
    ["/apis/cut", "heading", /Códigos Únicos Territoriales/],
    ["/servicios", "heading", /Aplicaciones al alcance/],
    ["/wiki", "heading", /La wiki/],
    ["/wiki/glosario", "heading", /Comprobante/],
    ["/participar", "heading", /./],
  ] as const)("%s", async (ruta, rol, nombre) => {
    const { fetch } = renderizar(ruta, { "/nodos/cut/especificacion/archivo": { texto: "openapi: 3.0.3\npaths: {}\n" } });
    expect((await screen.findAllByRole(rol, { name: nombre })).length).toBeGreaterThan(0);
    expect(screen.queryByText(/No se pudo/)).not.toBeInTheDocument();
    for (const [, init] of fetch.mock.calls) {
      expect(new Headers(init?.headers).has("Authorization")).toBe(false);
    }
  });
});

describe("2. Un 403 SIN_PERFIL lleva a su pantalla", () => {
  it("al entrar con un token sin perfil", async () => {
    const usuario = userEvent.setup();
    renderizar("/entrar", {
      "/yo": { status: 403, json: { error: { codigo: "SIN_PERFIL", mensaje: "Sin perfil." } } },
    });
    await entrarCon(usuario);
    expect(await screen.findByRole("heading", { name: /no tienes perfil/i })).toBeInTheDocument();
    expect(ubicacionActual()).toBe("/sin-perfil");
  });

  it("cuando lo responde cualquier consulta", async () => {
    renderizar("/apis", {
      "/nodos": { status: 403, json: { error: { codigo: "SIN_PERFIL", mensaje: "Sin perfil." } } },
    });
    expect(await screen.findByRole("heading", { name: /no tienes perfil/i })).toBeInTheDocument();
    expect(screen.queryByText(/No se pudo/)).not.toBeInTheDocument();
  });
});

describe("3. La respuesta con datos de muestra se marca en pantalla", () => {
  it("en el buscador CUT", async () => {
    const usuario = userEvent.setup();
    renderizar("/servicios/buscador-cut", {
      "/servicios/buscador-cut": {
        json: {
          slug: "buscador-cut",
          nodo: "cut",
          nombre: "Buscador de códigos territoriales",
          funcion: "Encuentra el código de una comuna.",
          descripcion: "",
          tareas: [],
          fuentes: [{ dato: "Códigos", origen: "SUBDERE" }],
          estado: "disponible",
          nota: "",
          actualizado: "2026-10-01T12:00:00Z",
        },
      },
      "/servicios/cut/buscar": {
        json: {
          datos: [
            {
              nivel: "comuna",
              codigo: "07101",
              nombre: "Talca",
              provincia: { codigo: "071", nombre: "Talca" },
              region: { codigo: "07", nombre: "Del Maule" },
            },
          ],
          origen: "muestra",
          obtenido_en: "2026-10-10T12:00:00Z",
        },
      },
    });
    await usuario.type(await screen.findByLabelText(/Comuna, provincia/), "Talca");
    expect(await screen.findByText("Datos de muestra")).toHaveAttribute("data-origen", "muestra");
    expect(screen.getByText(/Los datos de esta pantalla son ficticios/)).toBeInTheDocument();
  });
});

describe("Permisos de circulación", () => {
  it("sin sesión no consulta: pide entrar", async () => {
    const { fetch } = renderizar("/servicios/consulta-permiso-circulacion", {
      "/servicios/consulta-permiso-circulacion": {
        json: {
          slug: "consulta-permiso-circulacion",
          nodo: "permisos-de-circulacion",
          nombre: "Consulta de permisos de circulación",
          funcion: "",
          descripcion: "",
          tareas: [],
          fuentes: [],
          estado: "en_construccion",
          nota: "",
          actualizado: "2026-10-01T12:00:00Z",
        },
      },
    });
    expect(await screen.findByText(/exige sesión/)).toBeInTheDocument();
    expect(screen.queryByLabelText("Patente")).not.toBeInTheDocument();
    expect(fetch.mock.calls.some(([u]) => String(u).includes("/servicios/permisos/"))).toBe(false);
  });
});

describe("4. La ficha renderiza una especificación con referencias internas", () => {
  const ESPECIFICACION = `
openapi: 3.0.3
info: {title: CUT, version: 1.0.0}
servers: [{url: https://api.example/cut}]
paths:
  /comunas/{codigo}:
    get:
      tags: [Comunas]
      summary: Una comuna por su código
      parameters:
        - $ref: '#/components/parameters/Codigo'
      responses:
        '200':
          description: La comuna
          content:
            application/json:
              schema: {$ref: '#/components/schemas/Comuna'}
components:
  parameters:
    Codigo: {name: codigo, in: path, required: true, schema: {type: string}}
  schemas:
    Comuna:
      type: object
      properties:
        codigo: {type: string, example: '07101'}
        region: {$ref: '#/components/schemas/Region'}
    Region:
      type: object
      properties:
        nombre: {type: string, example: Del Maule}
`;

  it("con parámetros y ejemplos resueltos", async () => {
    const usuario = userEvent.setup();
    renderizar("/apis/cut", { "/nodos/cut/especificacion/archivo": { texto: ESPECIFICACION } });
    const operacion = await screen.findByText("Una comuna por su código");
    await usuario.click(operacion);
    const cuerpo = operacion.closest("details")!;
    expect(within(cuerpo).getByText("codigo", { selector: "code" })).toBeInTheDocument();
    expect(within(cuerpo).getByText(/"nombre": "Del Maule"/)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Comunas" })).toBeInTheDocument();
  });
});

describe("6. El menú de sesión se maneja con teclado", () => {
  it("se abre con Enter, se cierra con Escape y el foco vuelve", async () => {
    const usuario = userEvent.setup();
    renderizar("/entrar", { "/yo": { json: YO } });
    await entrarCon(usuario);
    const resumen = await screen.findByText("Ana Pérez", { selector: "summary" });
    const menu = resumen.closest("details")!;

    resumen.focus();
    await usuario.keyboard("{Enter}");
    expect(menu).toHaveAttribute("open");
    expect(within(menu).getByText(/Municipio: Talca/)).toBeVisible();

    await usuario.tab();
    expect(within(menu).getByRole("button", { name: "Salir" })).toHaveFocus();

    await usuario.keyboard("{Escape}");
    expect(menu).not.toHaveAttribute("open");
    expect(resumen).toHaveFocus();

    await usuario.keyboard(" ");
    expect(menu).toHaveAttribute("open");
  });
});

describe("7. Las direcciones viejas redirigen", () => {
  it.each([
    ["/nodo.html?id=division-territorial", "/apis/cut"],
    ["/apis.html?q=talca", "/apis?q=talca"],
    ["/wiki-glosario.html", "/wiki/glosario"],
    ["/wiki-intercambios.html", "/wiki#intercambios"],
    ["/index.html", "/"],
  ])("%s → %s", async (vieja, nueva) => {
    renderizar(vieja);
    await waitFor(() => expect(ubicacionActual()).toBe(nueva));
  });

  it("una dirección que no existe muestra la página 404", async () => {
    renderizar("/no-existe");
    expect(await screen.findByRole("heading", { name: /no existe/i })).toBeInTheDocument();
  });
});

describe("Wiki", () => {
  it("los enlaces del contenido navegan dentro del sitio", async () => {
    const usuario = userEvent.setup();
    renderizar("/wiki/glosario");
    await usuario.click(await screen.findByRole("link", { name: "inicio" }));
    await waitFor(() => expect(ubicacionActual()).toBe("/wiki/inicio"));
  });

  it("el menú marca la página actual", async () => {
    renderizar("/wiki/glosario");
    const menu = await screen.findByRole("complementary", { name: "Menú de la wiki" });
    expect(await within(menu).findByRole("link", { name: ENTRADAS[1]!.titulo })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });
});
