import { useState, type FormEvent } from "react";
import { Link } from "react-router";

import {
  useFuentes,
  useLecturas,
  useModificarFuente,
  useRegistrarFuente,
  useSincronizar,
} from "../../api/administracion";
import { Cargando, ErrorDeCarga } from "../../componentes/Estados";
import { useSesion } from "../../sesion/Sesion";
import type { Fuente, Lectura } from "../../tipos";
import { fechaHora, useTitulo } from "../../util/formato";
import { ErrorDeAccion, puede, Registrado, type Resultado } from "./comun";

const corto = (commit: string) => commit.slice(0, 8);

function nombreDe(fuente: Fuente) {
  return fuente.nodo_identificador || fuente.url;
}

export function Fuentes() {
  useTitulo("Fuentes · Administración");
  const { yo } = useSesion();
  const fuentes = useFuentes();
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [error, setError] = useState<unknown>(null);

  const avisar = (r: Resultado) => {
    setError(null);
    setResultado(r);
  };
  const fallar = (e: unknown) => {
    setResultado(null);
    setError(e);
  };

  return (
    <>
      <h2>Fuentes</h2>
      <p className="lead">
        Los repositorios que el nodo lee. Cada lectura valida <code>nodo/ficha.yaml</code> y guarda
        el <em>commit</em> del que la leyó; una lectura inválida no publica nada a medio leer.
      </p>

      <Registrado resultado={resultado} autor={yo?.nombre} />
      <ErrorDeAccion error={error} />

      {puede(yo, "administrador") && <RegistrarFuente alRegistrar={avisar} alFallar={fallar} />}

      {fuentes.isPending ? (
        <Cargando />
      ) : fuentes.isError ? (
        <ErrorDeCarga error={fuentes.error} />
      ) : fuentes.data.length === 0 ? (
        <p className="sin-params">Todavía no hay fuentes registradas.</p>
      ) : (
        <div className="tabla-ancha">
          <table className="admin-tabla">
            <thead>
              <tr>
                <th>Repositorio</th>
                <th>Nodo</th>
                <th>Última lectura</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {fuentes.data.map((f) => (
                <FilaFuente key={f.id} fuente={f} alAvisar={avisar} alFallar={fallar} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function EstadoLectura({ lectura }: { lectura: Fuente["ultima_lectura"] | Lectura }) {
  if (!lectura) return <span className="tag tag-sin">Sin lecturas</span>;
  return (
    <>
      <span className={lectura.valida ? "tag tag-dev" : "tag tag-mad"}>
        {lectura.valida ? "Válida" : "Inválida"}
      </span>{" "}
      <span className="admin-meta">
        {fechaHora(lectura.creado_en)}
        {lectura.commit ? (
          <>
            {" · "}
            <code>{corto(lectura.commit)}</code>
          </>
        ) : null}
        {lectura.perfil ? ` · ${lectura.perfil}` : " · tarea programada"}
      </span>
      {!lectura.valida && lectura.motivo && <p className="admin-motivo">{lectura.motivo}</p>}
    </>
  );
}

function FilaFuente({
  fuente,
  alAvisar,
  alFallar,
}: {
  fuente: Fuente;
  alAvisar: (r: Resultado) => void;
  alFallar: (e: unknown) => void;
}) {
  const { yo } = useSesion();
  const [editando, setEditando] = useState(false);
  const [historial, setHistorial] = useState(false);
  const sincronizar = useSincronizar();
  const modificar = useModificarFuente();
  const lecturas = useLecturas(fuente.id, historial);
  const nombre = nombreDe(fuente);

  const resincronizar = () =>
    sincronizar.mutate(fuente.id, {
      onSuccess: (l) =>
        alAvisar({
          texto: l.valida
            ? `${nombre}: lectura válida en el commit ${corto(l.commit)}`
            : `${nombre}: la lectura no pasó la validación (${l.motivo})`,
          registro: "el historial de lecturas de la fuente",
        }),
      onError: alFallar,
    });

  const alternarActiva = () => {
    if (fuente.activa && !window.confirm(`¿Dar de baja la fuente de ${nombre}? El nodo no se retira.`)) return;
    modificar.mutate(
      { id: fuente.id, activa: !fuente.activa },
      {
        onSuccess: () =>
          alAvisar({ texto: `Fuente de ${nombre}: ${fuente.activa ? "dada de baja" : "reactivada"}` }),
        onError: alFallar,
      },
    );
  };

  return (
    <tr className={fuente.activa ? undefined : "admin-inactiva"}>
      <td>
        <a href={fuente.url} target="_blank" rel="noreferrer">
          {fuente.url.replace(/^https:\/\/[^/]+\//, "")}
        </a>
        <span className="admin-meta">
          {fuente.rama} · {fuente.ruta_ficha}
          {fuente.activa ? "" : " · dada de baja"}
        </span>
        {editando && (
          <EditarFuente
            fuente={fuente}
            alCerrar={() => setEditando(false)}
            alAvisar={alAvisar}
            alFallar={alFallar}
          />
        )}
      </td>
      <td>
        {fuente.nodo_identificador ? (
          <Link to={`/apis/${fuente.nodo_identificador}`}>{fuente.nodo_identificador}</Link>
        ) : (
          <span className="admin-meta">Sin lectura válida todavía</span>
        )}
      </td>
      <td>
        <EstadoLectura lectura={fuente.ultima_lectura} />
        <details className="admin-historial" onToggle={(e) => setHistorial(e.currentTarget.open)}>
          <summary>Historial</summary>
          {lecturas.isPending ? (
            historial && <Cargando />
          ) : lecturas.isError ? (
            <ErrorDeCarga error={lecturas.error} />
          ) : (
            <ol>
              {lecturas.data.map((l) => (
                <li key={l.id}>
                  <EstadoLectura lectura={l} />
                </li>
              ))}
            </ol>
          )}
        </details>
      </td>
      <td className="admin-acciones">
        {puede(yo, "curador") && fuente.activa && (
          <button type="button" className="btn-copiar" onClick={resincronizar} disabled={sincronizar.isPending}>
            {sincronizar.isPending ? "Leyendo…" : "Resincronizar"}
          </button>
        )}
        {puede(yo, "administrador") && (
          <>
            <button type="button" className="btn-copiar" onClick={() => setEditando((v) => !v)}>
              {editando ? "Cerrar edición" : "Editar"}
            </button>
            <button type="button" className="btn-copiar" onClick={alternarActiva} disabled={modificar.isPending}>
              {fuente.activa ? "Dar de baja" : "Reactivar"}
            </button>
          </>
        )}
      </td>
    </tr>
  );
}

function RegistrarFuente({
  alRegistrar,
  alFallar,
}: {
  alRegistrar: (r: Resultado) => void;
  alFallar: (e: unknown) => void;
}) {
  const registrar = useRegistrarFuente();
  const [url, setUrl] = useState("");
  const [rama, setRama] = useState("main");
  const [ruta, setRuta] = useState("nodo/ficha.yaml");

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    registrar.mutate(
      { url: url.trim(), rama: rama.trim(), ruta_ficha: ruta.trim() },
      {
        onSuccess: (f) => {
          const l = f.ultima_lectura;
          alRegistrar({
            texto:
              l && l.valida
                ? `Fuente registrada y leída: ${f.nodo_identificador}, commit ${corto(l.commit)}. Queda oculta hasta que se publique`
                : `Fuente registrada, pero la primera lectura falló (${l?.motivo ?? "sin respuesta"}). Se puede resincronizar cuando la ficha esté lista`,
          });
          setUrl("");
        },
        onError: alFallar,
      },
    );
  };

  return (
    <details className="admin-form">
      <summary>Registrar una fuente</summary>
      <form onSubmit={enviar}>
        <div className="campo">
          <label htmlFor="fuente-url">Dirección del repositorio</label>
          <input
            id="fuente-url"
            type="url"
            required
            placeholder="https://gitlab.subdere.gob.cl/grupo/repositorio"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </div>
        <div className="admin-fila">
          <div className="campo">
            <label htmlFor="fuente-rama">Rama</label>
            <input id="fuente-rama" required value={rama} onChange={(e) => setRama(e.target.value)} />
          </div>
          <div className="campo">
            <label htmlFor="fuente-ruta">Ruta de la ficha</label>
            <input id="fuente-ruta" required value={ruta} onChange={(e) => setRuta(e.target.value)} />
          </div>
        </div>
        <p>
          <button className="btn btn-p" type="submit" disabled={registrar.isPending}>
            {registrar.isPending ? "Registrando y leyendo…" : "Registrar y leer"}
          </button>
        </p>
      </form>
    </details>
  );
}

function EditarFuente({
  fuente,
  alCerrar,
  alAvisar,
  alFallar,
}: {
  fuente: Fuente;
  alCerrar: () => void;
  alAvisar: (r: Resultado) => void;
  alFallar: (e: unknown) => void;
}) {
  const modificar = useModificarFuente();
  const [url, setUrl] = useState(fuente.url);
  const [rama, setRama] = useState(fuente.rama ?? "main");
  const [ruta, setRuta] = useState(fuente.ruta_ficha ?? "nodo/ficha.yaml");

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    const traspaso = url.trim() !== fuente.url;
    modificar.mutate(
      { id: fuente.id, url: url.trim(), rama: rama.trim(), ruta_ficha: ruta.trim() },
      {
        onSuccess: () => {
          alAvisar({
            texto: traspaso
              ? `Traspaso de custodia de ${nombreDe(fuente)}: ahora se lee desde ${url.trim()}`
              : `Fuente de ${nombreDe(fuente)} modificada`,
          });
          alCerrar();
        },
        onError: alFallar,
      },
    );
  };

  return (
    <form className="admin-editar" onSubmit={enviar}>
      <p className="admin-meta">
        Cambiar la dirección es un <strong>traspaso de custodia</strong>: el nodo sigue siendo el
        mismo y el historial de lecturas se conserva. Después conviene resincronizar.
      </p>
      <div className="campo">
        <label htmlFor={`url-${fuente.id}`}>Dirección</label>
        <input id={`url-${fuente.id}`} type="url" required value={url} onChange={(e) => setUrl(e.target.value)} />
      </div>
      <div className="admin-fila">
        <div className="campo">
          <label htmlFor={`rama-${fuente.id}`}>Rama</label>
          <input id={`rama-${fuente.id}`} required value={rama} onChange={(e) => setRama(e.target.value)} />
        </div>
        <div className="campo">
          <label htmlFor={`ruta-${fuente.id}`}>Ruta de la ficha</label>
          <input id={`ruta-${fuente.id}`} required value={ruta} onChange={(e) => setRuta(e.target.value)} />
        </div>
      </div>
      <p>
        <button className="btn btn-p" type="submit" disabled={modificar.isPending}>
          Guardar
        </button>
      </p>
    </form>
  );
}
