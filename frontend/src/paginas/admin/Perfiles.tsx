import { useMemo, useState, type FormEvent } from "react";

import {
  useCrearPerfil,
  useDesignarEncargado,
  useModificarPerfil,
  useMunicipios,
  usePerfiles,
  type FiltroPerfiles,
} from "../../api/administracion";
import { Cargando, ErrorDeCarga } from "../../componentes/Estados";
import { ROLES, useSesion } from "../../sesion/Sesion";
import type { Perfil, Rol, Yo } from "../../tipos";
import { useTitulo } from "../../util/formato";
import { ErrorDeAccion, gestionaPerfiles, Registrado, SinPermiso, type Resultado } from "./comun";

const LISTA_ROLES = Object.keys(ROLES) as Rol[];

export function Perfiles() {
  useTitulo("Perfiles · Administración");
  const { yo } = useSesion();
  if (!yo || !gestionaPerfiles(yo)) return <SinPermiso />;
  return <PantallaPerfiles yo={yo} />;
}

/** La misma pantalla para un administrador y para el encargado de un municipio, que solo ve su
 * equipo, solo crea lectores y no se modifica a sí mismo. */
function PantallaPerfiles({ yo }: { yo: Yo }) {
  const admin = yo.rol === "administrador";
  const [filtro, setFiltro] = useState<FiltroPerfiles>({ rol: "", municipio: "", activo: "" });
  const perfiles = usePerfiles(admin ? filtro : {});
  const municipios = useMunicipios(admin);
  const nombres = useMemo(
    () => new Map((municipios.data ?? []).map((m) => [m.cut, m.nombre])),
    [municipios.data],
  );
  if (yo.municipio) nombres.set(yo.municipio.cut, yo.municipio.nombre);

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

  const municipio = (cut: string | null | undefined) =>
    cut ? `${nombres.get(cut) ?? "Comuna"} (${cut})` : "SUBDERE";

  return (
    <>
      <h2>{admin ? "Perfiles" : `Equipo de ${yo.municipio?.nombre ?? "tu municipio"}`}</h2>
      <p className="lead">
        {admin
          ? "Quién puede entrar al nodo y qué puede hacer. Los perfiles no se borran: se desactivan, para que su historia siga en la bitácora."
          : "Las personas de tu municipio habilitadas en el nodo. Puedes darlas de alta como lectoras, desactivarlas y reactivarlas."}
      </p>

      <Registrado resultado={resultado} autor={yo.nombre} />
      <ErrorDeAccion error={error} />

      {admin && municipios.data && (
        <datalist id="lista-municipios">
          {municipios.data.map((m) => (
            <option key={m.cut} value={m.cut}>
              {m.nombre}
            </option>
          ))}
        </datalist>
      )}

      <AltaPerfil yo={yo} alAvisar={avisar} alFallar={fallar} />

      {admin && (
        <div className="filtros" role="group" aria-label="Filtrar perfiles">
          <select
            aria-label="Rol"
            className="sb-in admin-filtro"
            value={filtro.rol}
            onChange={(e) => setFiltro({ ...filtro, rol: e.target.value as Rol | "" })}
          >
            <option value="">Todos los roles</option>
            {LISTA_ROLES.map((r) => (
              <option key={r} value={r}>
                {ROLES[r]}
              </option>
            ))}
          </select>
          <input
            aria-label="Municipio (código CUT)"
            className="sb-in admin-filtro"
            list="lista-municipios"
            placeholder="Municipio (CUT)"
            value={filtro.municipio}
            onChange={(e) => setFiltro({ ...filtro, municipio: e.target.value.trim() })}
          />
          <select
            aria-label="Estado"
            className="sb-in admin-filtro"
            value={filtro.activo}
            onChange={(e) => setFiltro({ ...filtro, activo: e.target.value as FiltroPerfiles["activo"] })}
          >
            <option value="">Activos e inactivos</option>
            <option value="true">Solo activos</option>
            <option value="false">Solo inactivos</option>
          </select>
        </div>
      )}

      {perfiles.isPending ? (
        <Cargando />
      ) : perfiles.isError ? (
        <ErrorDeCarga error={perfiles.error} />
      ) : perfiles.data.length === 0 ? (
        <p className="sin-params">No hay perfiles con esos filtros.</p>
      ) : (
        <div className="tabla-ancha">
          <table className="admin-tabla">
            <thead>
              <tr>
                <th>RUN</th>
                <th>Nombre</th>
                <th>Rol</th>
                {admin && <th>Municipio</th>}
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {perfiles.data.map((p) => (
                <FilaPerfil
                  key={p.id}
                  perfil={p}
                  yo={yo}
                  municipio={municipio}
                  alAvisar={avisar}
                  alFallar={fallar}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function FilaPerfil({
  perfil,
  yo,
  municipio,
  alAvisar,
  alFallar,
}: {
  perfil: Perfil;
  yo: Yo;
  municipio: (cut: string | null | undefined) => string;
  alAvisar: (r: Resultado) => void;
  alFallar: (e: unknown) => void;
}) {
  const admin = yo.rol === "administrador";
  const propio = perfil.id === yo.id;
  const modificar = useModificarPerfil();
  const designar = useDesignarEncargado();
  const [editando, setEditando] = useState(false);
  const activo = perfil.activo !== false;

  const alternarActivo = () => {
    if (activo && !window.confirm(`¿Desactivar el perfil de ${perfil.nombre}? No podrá entrar al nodo.`)) return;
    modificar.mutate(
      { id: perfil.id, activo: !activo },
      {
        onSuccess: () => alAvisar({ texto: `Perfil de ${perfil.nombre}: ${activo ? "desactivado" : "reactivado"}` }),
        onError: alFallar,
      },
    );
  };

  const hacerEncargado = () => {
    if (!perfil.municipio) return;
    if (!window.confirm(`¿Designar a ${perfil.nombre} como encargado de ${municipio(perfil.municipio)}? Si había otro, deja de serlo.`))
      return;
    designar.mutate(
      { cut: perfil.municipio, perfil: perfil.id },
      {
        onSuccess: () =>
          alAvisar({ texto: `${perfil.nombre} es ahora encargado de ${municipio(perfil.municipio)}` }),
        onError: alFallar,
      },
    );
  };

  return (
    <tr className={activo ? undefined : "admin-inactiva"}>
      <td>
        <code>{perfil.run}</code>
      </td>
      <td>
        {perfil.nombre}
        {propio && <span className="admin-meta">Tu perfil</span>}
        {editando && (
          <EditarPerfil perfil={perfil} alCerrar={() => setEditando(false)} alAvisar={alAvisar} alFallar={alFallar} />
        )}
      </td>
      <td>{perfil.rol ? ROLES[perfil.rol] : ""}</td>
      {admin && (
        <td>
          {municipio(perfil.municipio)}
          {perfil.es_encargado && <span className="tag tag-ambito admin-encargado">Encargado</span>}
        </td>
      )}
      <td>
        <span className={activo ? "tag tag-dev" : "tag tag-sin"}>{activo ? "Activo" : "Inactivo"}</span>
        {!admin && perfil.es_encargado && <span className="tag tag-ambito admin-encargado">Encargado</span>}
      </td>
      <td className="admin-acciones">
        {!propio && (
          <>
            {admin && (
              <button type="button" className="btn-copiar" onClick={() => setEditando((v) => !v)}>
                {editando ? "Cerrar edición" : "Editar"}
              </button>
            )}
            <button type="button" className="btn-copiar" onClick={alternarActivo} disabled={modificar.isPending}>
              {activo ? "Desactivar" : "Reactivar"}
            </button>
            {admin && perfil.municipio && activo && !perfil.es_encargado && (
              <button type="button" className="btn-copiar" onClick={hacerEncargado} disabled={designar.isPending}>
                Designar encargado
              </button>
            )}
          </>
        )}
      </td>
    </tr>
  );
}

function AltaPerfil({
  yo,
  alAvisar,
  alFallar,
}: {
  yo: Yo;
  alAvisar: (r: Resultado) => void;
  alFallar: (e: unknown) => void;
}) {
  const admin = yo.rol === "administrador";
  const crear = useCrearPerfil();
  const [run, setRun] = useState("");
  const [nombre, setNombre] = useState("");
  const [rol, setRol] = useState<Rol>("lector");
  const [municipio, setMunicipio] = useState("");

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    crear.mutate(
      {
        run: run.trim(),
        nombre: nombre.trim(),
        rol: admin ? rol : "lector",
        municipio: admin ? municipio.trim() || null : (yo.municipio?.cut ?? null),
      },
      {
        onSuccess: (p) => {
          alAvisar({ texto: `Perfil creado: ${p.nombre} (${p.run}), ${ROLES[p.rol ?? "lector"].toLowerCase()}` });
          setRun("");
          setNombre("");
        },
        onError: alFallar,
      },
    );
  };

  return (
    <details className="admin-form">
      <summary>{admin ? "Dar de alta un perfil" : "Dar de alta a una persona de tu equipo"}</summary>
      <form onSubmit={enviar}>
        <div className="admin-fila">
          <div className="campo">
            <label htmlFor="perfil-run">RUN</label>
            <input
              id="perfil-run"
              required
              placeholder="12.345.678-5"
              autoComplete="off"
              value={run}
              onChange={(e) => setRun(e.target.value)}
            />
          </div>
          <div className="campo">
            <label htmlFor="perfil-nombre">Nombre</label>
            <input id="perfil-nombre" required value={nombre} onChange={(e) => setNombre(e.target.value)} />
          </div>
        </div>
        {admin ? (
          <div className="admin-fila">
            <div className="campo">
              <label htmlFor="perfil-rol">Rol</label>
              <select id="perfil-rol" className="sb-in" value={rol} onChange={(e) => setRol(e.target.value as Rol)}>
                {LISTA_ROLES.map((r) => (
                  <option key={r} value={r}>
                    {ROLES[r]}
                  </option>
                ))}
              </select>
            </div>
            <div className="campo">
              <label htmlFor="perfil-municipio">Municipio (código CUT)</label>
              <input
                id="perfil-municipio"
                list="lista-municipios"
                placeholder="Vacío: persona de SUBDERE"
                value={municipio}
                onChange={(e) => setMunicipio(e.target.value)}
              />
            </div>
          </div>
        ) : (
          <p className="admin-meta">
            Se crea como <strong>lector</strong> de {yo.municipio?.nombre ?? "tu municipio"}. Los roles
            superiores actúan sobre el catálogo nacional y los asigna un administrador de SUBDERE.
          </p>
        )}
        <p className="admin-meta">El nombre es provisional: se actualiza con el de Clave Única la primera vez que la persona entra.</p>
        <p>
          <button className="btn btn-p" type="submit" disabled={crear.isPending}>
            Crear perfil
          </button>
        </p>
      </form>
    </details>
  );
}

function EditarPerfil({
  perfil,
  alCerrar,
  alAvisar,
  alFallar,
}: {
  perfil: Perfil;
  alCerrar: () => void;
  alAvisar: (r: Resultado) => void;
  alFallar: (e: unknown) => void;
}) {
  const modificar = useModificarPerfil();
  const [rol, setRol] = useState<Rol>(perfil.rol ?? "lector");
  const [municipio, setMunicipio] = useState(perfil.municipio ?? "");

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    modificar.mutate(
      { id: perfil.id, rol, municipio: municipio.trim() || null },
      {
        onSuccess: () => {
          alAvisar({ texto: `Perfil de ${perfil.nombre} modificado: ${ROLES[rol].toLowerCase()}` });
          alCerrar();
        },
        onError: alFallar,
      },
    );
  };

  return (
    <form className="admin-editar" onSubmit={enviar}>
      <div className="admin-fila">
        <div className="campo">
          <label htmlFor={`rol-${perfil.id}`}>Rol</label>
          <select id={`rol-${perfil.id}`} className="sb-in" value={rol} onChange={(e) => setRol(e.target.value as Rol)}>
            {LISTA_ROLES.map((r) => (
              <option key={r} value={r}>
                {ROLES[r]}
              </option>
            ))}
          </select>
        </div>
        <div className="campo">
          <label htmlFor={`municipio-${perfil.id}`}>Municipio (CUT)</label>
          <input
            id={`municipio-${perfil.id}`}
            list="lista-municipios"
            placeholder="Vacío: SUBDERE"
            value={municipio}
            onChange={(e) => setMunicipio(e.target.value)}
          />
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
