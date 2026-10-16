import { InMemoryWebStorage } from "oidc-client-ts";
import { vi } from "vitest";

describe("La configuración de OIDC", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("sin realm configurado, no hay Keycloak", async () => {
    vi.stubEnv("VITE_KEYCLOAK_URL", "");
    vi.stubEnv("VITE_KEYCLOAK_CLIENTE", "");
    const { hayKeycloak } = await import("../sesion/oidc");

    expect(hayKeycloak()).toBe(false);
  });

  it("vuelve a /entrar/retorno, pide solo openid y guarda los tokens en memoria", async () => {
    vi.stubEnv("VITE_KEYCLOAK_URL", "https://sso.prueba/realms/nodo/");
    vi.stubEnv("VITE_KEYCLOAK_CLIENTE", "nodo-web");
    const { gestorOidc, hayKeycloak } = await import("../sesion/oidc");

    const { settings } = gestorOidc();

    expect(hayKeycloak()).toBe(true);
    expect(settings.authority).toBe("https://sso.prueba/realms/nodo");
    expect(settings.client_id).toBe("nodo-web");
    expect(settings.redirect_uri).toBe(`${window.location.origin}/entrar/retorno`);
    expect(settings.scope).toBe("openid");
    expect(settings.response_type).toBe("code");
    expect((settings.userStore as unknown as { _store: unknown })._store).toBeInstanceOf(
      InMemoryWebStorage,
    );
  });

  it("el desafío PKCE es el SHA-256 del verificador en base64url, sin relleno", async () => {
    const { desafioPkce } = await import("../sesion/oidc");

    // Calculado aparte con hashlib y base64.urlsafe_b64encode de Python.
    expect(desafioPkce("dBjftJeZ4CVP-mJ0kKnq2u9yuhT2xnTGTlNuaWNTqbA")).toBe(
      "I83nZ0PlbDjIhq_iiRFKnp0SRdMxGxXJ8TRGA8pRrzs",
    );
  });

  it("cada verificador es nuevo y cumple el largo y el alfabeto de PKCE", async () => {
    const { parPkce, desafioPkce } = await import("../sesion/oidc");

    const uno = parPkce();
    const otro = parPkce();

    expect(uno.verificador).not.toBe(otro.verificador);
    expect(uno.verificador).toMatch(/^[A-Za-z0-9\-._~]{43,128}$/);
    expect(uno.desafio).toBe(desafioPkce(uno.verificador));
  });

  it("al ir al realm, manda el desafío S256 y guarda el verificador para el canje", async () => {
    vi.stubEnv("VITE_KEYCLOAK_URL", "https://sso.prueba/realms/nodo");
    vi.stubEnv("VITE_KEYCLOAK_CLIENTE", "nodo-web");
    const { gestorOidc, irAKeycloak, desafioPkce } = await import("../sesion/oidc");
    const ir = vi.spyOn(gestorOidc(), "signinRedirect").mockResolvedValue();

    await irAKeycloak("/admin");

    expect(gestorOidc().settings.disablePKCE).toBe(true);
    const pedido = ir.mock.calls[0]![0]!;
    const verificador = pedido.extraTokenParams!.code_verifier as string;
    expect(pedido.state).toEqual({ volverA: "/admin" });
    expect(pedido.extraQueryParams).toEqual({
      code_challenge: desafioPkce(verificador),
      code_challenge_method: "S256",
    });
  });
});
