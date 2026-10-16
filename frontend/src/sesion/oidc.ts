// El ingreso contra el realm de Keycloak: Authorization Code + PKCE, como cliente público.
// Sin `VITE_KEYCLOAK_URL` y `VITE_KEYCLOAK_CLIENTE` no hay realm, y `/entrar` recibe un token
// pegado del emisor local del backend.
import { sha256 } from "@noble/hashes/sha2.js";
import { InMemoryWebStorage, UserManager, WebStorageStateStore } from "oidc-client-ts";

export const RUTA_RETORNO = "/entrar/retorno";

/** A dónde volver después de entrar: viaja por Keycloak en el `state` del pedido. */
export type Estado = { volverA?: string };

function configuracion() {
  return {
    autoridad: (import.meta.env.VITE_KEYCLOAK_URL ?? "").replace(/\/+$/, ""),
    cliente: import.meta.env.VITE_KEYCLOAK_CLIENTE ?? "",
  };
}

export function hayKeycloak(): boolean {
  const { autoridad, cliente } = configuracion();
  return Boolean(autoridad && cliente);
}

const SIN_RELLENO = /=+$/;

function base64url(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(SIN_RELLENO, "");
}

/** PKCE `S256` (RFC 7636). El SHA-256 es de `@noble/hashes` y no de `crypto.subtle`, que el
 * navegador solo da en HTTPS o en localhost: así el realm puede exigir PKCE aunque el sitio
 * se abra por HTTP. `getRandomValues` sí existe en cualquier contexto. */
export function parPkce(): { verificador: string; desafio: string } {
  const verificador = base64url(crypto.getRandomValues(new Uint8Array(32)));
  return { verificador, desafio: desafioPkce(verificador) };
}

export function desafioPkce(verificador: string): string {
  return base64url(sha256(new TextEncoder().encode(verificador)));
}

let gestor: UserManager | null = null;

export function gestorOidc(): UserManager {
  if (!gestor) {
    const { autoridad, cliente } = configuracion();
    const base = new URL(import.meta.env.BASE_URL ?? "/", window.location.origin);
    gestor = new UserManager({
      authority: autoridad,
      client_id: cliente,
      redirect_uri: new URL(RUTA_RETORNO.slice(1), base).href,
      post_logout_redirect_uri: base.href,
      scope: "openid",
      // El PKCE de la biblioteca usa `crypto.subtle`; el par lo arma `irAKeycloak`.
      disablePKCE: true,
      // Los tokens, solo en memoria. El estado del pedido, con el verificador, sí tiene que
      // sobrevivir a la redirección: vive en sessionStorage y se borra al volver.
      userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),
      stateStore: new WebStorageStateStore({ store: window.sessionStorage }),
      automaticSilentRenew: true,
    });
  }
  return gestor;
}

/** El verificador viaja en `extraTokenParams`, que la biblioteca guarda con el `state` y
 * manda al canjear el código. */
export function irAKeycloak(volverA: string): Promise<void> {
  const { verificador, desafio } = parPkce();
  return gestorOidc().signinRedirect({
    state: { volverA } satisfies Estado,
    extraQueryParams: { code_challenge: desafio, code_challenge_method: "S256" },
    extraTokenParams: { code_verifier: verificador },
  });
}

let retorno: Promise<{ token: string; volverA: string }> | null = null;

/** Completa el ingreso al volver de Keycloak. Una sola vez por carga: StrictMode monta dos
 * veces, y el `state` no se puede canjear dos veces. */
export function completarIngreso(): Promise<{ token: string; volverA: string }> {
  retorno ??= gestorOidc()
    .signinRedirectCallback()
    .then((usuario) => ({
      token: usuario.access_token,
      volverA: (usuario.state as Estado | undefined)?.volverA ?? "/",
    }));
  return retorno;
}

/** Cierra también la sesión del realm; si no, el próximo «Entrar» vuelve sin preguntar. */
export async function salirDeKeycloak(): Promise<void> {
  const oidc = gestorOidc();
  const usuario = await oidc.getUser();
  await oidc.removeUser();
  retorno = null;
  if (usuario) await oidc.signoutRedirect({ id_token_hint: usuario.id_token });
}
