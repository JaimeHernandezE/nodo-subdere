import { useEffect, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router";

import { ErrorApi, esError } from "../api/cliente";
import { completarIngreso, contextoSeguro, hayKeycloak, irAKeycloak } from "../sesion/oidc";
import { useSesion } from "../sesion/Sesion";
import { useTitulo } from "../util/formato";

/** Con el realm configurado se entra por Keycloak. Sin él, con un token pegado del emisor
 * local del backend, que solo existe en desarrollo. */
export function Entrar() {
  useTitulo("Entrar");
  const volverA = (useLocation().state as { volverA?: string } | null)?.volverA ?? "/";
  return hayKeycloak() ? <EntrarConKeycloak volverA={volverA} /> : <EntrarConToken volverA={volverA} />;
}

function EntrarConKeycloak({ volverA }: { volverA: string }) {
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);
  const seguro = contextoSeguro();

  const ir = async () => {
    setEnviando(true);
    setError("");
    try {
      await irAKeycloak(volverA);
    } catch {
      setError("No se pudo contactar al servicio de autenticación. Intenta de nuevo en un momento.");
      setEnviando(false);
    }
  };

  return (
    <section>
      <div className="wrap">
        <p className="eyebrow">Sesión</p>
        <h2>Entrar al nodo</h2>
        <p className="lead">
          Se entra con Clave Única. Al volver, el nodo revisa tu perfil: rol, municipio y lo que puedes
          administrar.
        </p>
        {!seguro && (
          <p className="error-campo" role="alert">
            El ingreso necesita que el sitio se abra por HTTPS. Por HTTP el navegador no permite completar
            el inicio de sesión de forma segura.
          </p>
        )}
        {error && (
          <p className="error-campo" role="alert">
            {error}
          </p>
        )}
        <p>
          <button className="btn btn-p" type="button" onClick={ir} disabled={!seguro || enviando}>
            {enviando ? "Redirigiendo…" : "Entrar con Clave Única"}
          </button>
        </p>
      </div>
    </section>
  );
}

function EntrarConToken({ volverA }: { volverA: string }) {
  const { entrar } = useSesion();
  const navegar = useNavigate();
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

/** Adonde vuelve Keycloak con el código: se canjea por el token y se pide `/yo`. */
export function RetornoDeKeycloak() {
  useTitulo("Entrar");
  const { entrar } = useSesion();
  const navegar = useNavigate();
  const [error, setError] = useState("");

  useEffect(() => {
    let vigente = true;
    completarIngreso()
      .then(async ({ token, volverA }) => {
        try {
          await entrar(token);
          if (vigente) navegar(volverA, { replace: true });
        } catch (e) {
          if (!vigente) return;
          if (esError(e, "SIN_PERFIL")) navegar("/sin-perfil", { replace: true });
          else setError("Entraste con Clave Única, pero el nodo no pudo verificar tu sesión.");
        }
      })
      .catch(() => {
        if (vigente) setError("No se pudo completar el ingreso. Puede que el enlace haya vencido.");
      });
    return () => {
      vigente = false;
    };
  }, [entrar, navegar]);

  return (
    <section>
      <div className="wrap">
        <p className="eyebrow">Sesión</p>
        <h2>Entrar al nodo</h2>
        {error ? (
          <>
            <p className="error-campo" role="alert">
              {error}
            </p>
            <p>
              <Link className="btn btn-p" to="/entrar">
                Intentar de nuevo
              </Link>
            </p>
          </>
        ) : (
          <p className="lead" role="status">
            Verificando tu sesión…
          </p>
        )}
      </div>
    </section>
  );
}
