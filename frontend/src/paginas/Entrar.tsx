import { useEffect, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router";

import { ErrorApi, esError } from "../api/cliente";
import { completarIngreso, hayKeycloak, irAKeycloak } from "../sesion/oidc";
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
        {error && (
          <p className="error-campo" role="alert">
            {error}
          </p>
        )}
        <p className="clave-unica">
          <button className="clave-unica__btn" type="button" onClick={ir} disabled={enviando}>
            <LogoClaveUnica />
            {enviando ? (
              <span>Redirigiendo…</span>
            ) : (
              <span>
                Iniciar sesión <span className="oculto">con Clave Única</span>
              </span>
            )}
          </button>
        </p>
      </div>
    </section>
  );
}

/** El logo oficial de Clave Única, en blanco: el mismo que usa Banco de Proyectos. */
function LogoClaveUnica() {
  return (
    <svg className="clave-unica__logo" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path
        fill="currentColor"
        fillRule="evenodd"
        d="M11.47,14a.65.65,0,0,1-.21-.54.64.64,0,0,1,.29-.5.68.68,0,0,1,.53-.19.73.73,0,0,1,.49.27.75.75,0,0,1-.08,1,.7.7,0,0,1-.53.19.71.71,0,0,1-.49-.27Zm3.8-8.66A9,9,0,0,1,21,13.57a9,9,0,0,1-18,0A8.78,8.78,0,0,1,8.45,5.32c.37-.09.64-.09.82.36a.76.76,0,0,1-.36,1,7.52,7.52,0,1,0,5.82-.09.66.66,0,0,1-.4-.37.64.64,0,0,1,0-.54.62.62,0,0,1,.37-.39A.64.64,0,0,1,15.27,5.32Zm-7.77,8a4.64,4.64,0,0,1,3.75-4.59V2.33A.91.91,0,0,1,12,1.5h3.31a.75.75,0,0,1,.7.75.78.78,0,0,1-.7.75H12.75V8.76a4.5,4.5,0,0,1,3.75,4.58A4.61,4.61,0,0,1,12,18,4.61,4.61,0,0,1,7.5,13.33Zm7.5.09a3.1,3.1,0,0,0-3-3.12,3.12,3.12,0,0,0,0,6.2A3.09,3.09,0,0,0,15,13.42Z"
      />
    </svg>
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
      .catch((e: unknown) => {
        if (!vigente) return;
        const detalle = (e as { error_description?: string } | null)?.error_description;
        setError(
          detalle
            ? `No se pudo completar el ingreso. Keycloak respondió: ${detalle}`
            : "No se pudo completar el ingreso. Puede que el enlace haya vencido.",
        );
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
