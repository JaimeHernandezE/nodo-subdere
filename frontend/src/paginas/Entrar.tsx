import { useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router";

import { ErrorApi, esError } from "../api/cliente";
import { useSesion } from "../sesion/Sesion";
import { useTitulo } from "../util/formato";

/** Por ahora se entra con un token del emisor local del backend. Cuando exista el realm de
 * Keycloak, esta pantalla se reemplaza por el flujo OIDC con PKCE. */
export function Entrar() {
  useTitulo("Entrar");
  const { entrar } = useSesion();
  const navegar = useNavigate();
  const volverA = (useLocation().state as { volverA?: string } | null)?.volverA ?? "/";
  const [texto, setTexto] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault();
    const token = texto.trim();
    if (!token) return;
    setEnviando(true);
    setError("");
    try {
      await entrar(token);
      navegar(volverA, { replace: true });
    } catch (e) {
      if (esError(e, "SIN_PERFIL")) {
        navegar("/sin-perfil", { replace: true });
        return;
      }
      setError(
        e instanceof ErrorApi && e.status === 401
          ? "El nodo no aceptó ese token: puede estar vencido o venir de otro emisor."
          : "No se pudo verificar el token con el nodo.",
      );
    } finally {
      setEnviando(false);
    }
  };

  return (
    <section>
      <div className="wrap">
        <p className="eyebrow">Sesión</p>
        <h2>Entrar al nodo</h2>
        <p className="lead">
          En este ambiente se entra con un token del emisor local del backend. Se genera con{" "}
          <code>python manage.py emitir_token_local --run 12345678-5</code>, para un RUN que ya tenga
          perfil.
        </p>
        <p className="lead">
          El token queda solo en la memoria de esta pestaña: al recargar la página, la sesión se pierde.
        </p>
        <form onSubmit={enviar}>
          <div className="campo">
            <label htmlFor="token">Token</label>
            <textarea
              id="token"
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              spellCheck={false}
              autoComplete="off"
              aria-describedby={error ? "error-token" : undefined}
            />
          </div>
          {error && (
            <p className="error-campo" id="error-token" role="alert">
              {error}
            </p>
          )}
          <p>
            <button className="btn btn-p" type="submit" disabled={enviando}>
              {enviando ? "Verificando…" : "Entrar"}
            </button>
          </p>
        </form>
      </div>
    </section>
  );
}
