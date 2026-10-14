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
});
