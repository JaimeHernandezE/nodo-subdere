// El ingreso con el realm configurado. `oidc-client-ts` no se ejerce acá: se reemplazan las
// funciones de `sesion/oidc`, que son la única puerta hacia Keycloak.
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import * as oidc from "../sesion/oidc";
import { renderizar, ubicacionActual } from "./util";

vi.mock("../sesion/oidc", async (original) => ({
  ...(await original<typeof import("../sesion/oidc")>()),
  hayKeycloak: () => true,
  irAKeycloak: vi.fn(async () => {}),
  completarIngreso: vi.fn(),
  salirDeKeycloak: vi.fn(async () => {}),
  gestorOidc: () => ({
    events: {
      addUserLoaded: () => () => {},
      addAccessTokenExpired: () => () => {},
      addSilentRenewError: () => () => {},
    },
  }),
}));

const YO = {
  id: 1,
  nombre: "Ana Pérez",
  rol: "lector",
  municipio: { id: 1, nombre: "Talca", cut: "07101" },
  es_encargado: false,
};

describe("Entrar con Keycloak", () => {
  it("no pide un token: lleva al realm", async () => {
    const usuario = userEvent.setup();
    renderizar("/entrar");

    expect(screen.queryByLabelText("Token")).not.toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Iniciar sesión con Clave Única" }));

    expect(oidc.irAKeycloak).toHaveBeenCalledWith("/");
  });

  it("al volver, usa el token, pide /yo y sigue a donde iba", async () => {
    vi.mocked(oidc.completarIngreso).mockResolvedValue({ token: "token-del-realm", volverA: "/apis" });
    const { fetch } = renderizar("/entrar/retorno", { "/yo": { json: YO } });

    await waitFor(() => expect(ubicacionActual()).toBe("/apis"));
    expect(await screen.findByText("Ana Pérez", { selector: "summary" })).toBeInTheDocument();
    const yo = fetch.mock.calls.find(([entrada]) => String(entrada).endsWith("/yo"));
    expect(new Headers(yo?.[1]?.headers).get("Authorization")).toBe("Bearer token-del-realm");
  });

  it("al volver sin perfil, lleva a su pantalla", async () => {
    vi.mocked(oidc.completarIngreso).mockResolvedValue({ token: "token-del-realm", volverA: "/" });
    renderizar("/entrar/retorno", {
      "/yo": { status: 403, json: { error: { codigo: "SIN_PERFIL", mensaje: "Sin perfil." } } },
    });

    expect(await screen.findByRole("heading", { name: /no tienes perfil/i })).toBeInTheDocument();
    expect(ubicacionActual()).toBe("/sin-perfil");
  });

  it("si el retorno falla, lo dice y deja volver a intentar", async () => {
    vi.mocked(oidc.completarIngreso).mockRejectedValue(new Error("state inválido"));
    renderizar("/entrar/retorno");

    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo completar el ingreso");
    expect(screen.getByRole("link", { name: "Intentar de nuevo" })).toHaveAttribute("href", "/entrar");
  });

  it("salir cierra también la sesión del realm", async () => {
    const usuario = userEvent.setup();
    vi.mocked(oidc.completarIngreso).mockResolvedValue({ token: "token-del-realm", volverA: "/" });
    renderizar("/entrar/retorno", { "/yo": { json: YO } });

    const resumen = await screen.findByText("Ana Pérez", { selector: "summary" });
    await usuario.click(resumen);
    await usuario.click(within(resumen.closest("details")!).getByRole("button", { name: "Salir" }));

    expect(oidc.salirDeKeycloak).toHaveBeenCalled();
    expect(screen.getByRole("link", { name: "Entrar" })).toBeInTheDocument();
  });
});
