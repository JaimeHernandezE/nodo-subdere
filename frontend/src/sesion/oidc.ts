// El ingreso contra el realm de Keycloak: Authorization Code + PKCE, como cliente público.
// Sin `VITE_KEYCLOAK_URL` y `VITE_KEYCLOAK_CLIENTE` no hay realm, y `/entrar` recibe un token
// pegado del emisor local del backend.
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

/** PKCE necesita `crypto.subtle`, y el navegador solo lo da en HTTPS o en localhost. */
export function contextoSeguro(): boolean {
  return window.isSecureContext && Boolean(window.crypto?.subtle);
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
      // Los tokens, solo en memoria. El estado del pedido sí tiene que sobrevivir a la
      // redirección: vive en sessionStorage y se borra al volver.
      userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),
      stateStore: new WebStorageStateStore({ store: window.sessionStorage }),
      automaticSilentRenew: true,
    });
  }
  return gestor;
}

export function irAKeycloak(volverA: string): Promise<void> {
  return gestorOidc().signinRedirect({ state: { volverA } satisfies Estado });
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
