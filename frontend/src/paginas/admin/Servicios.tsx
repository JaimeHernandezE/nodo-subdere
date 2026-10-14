import { Fragment, useState, type FormEvent } from "react";
import { Link } from "react-router";

import {
  useCrearServicio,
  useEditarServicio,
  useNodosTodos,
  useServiciosTodos,
  type DatosServicio,
} from "../../api/administracion";
import { Cargando, ErrorDeCarga } from "../../componentes/Estados";
import { ESTADO_SERVICIO } from "../../componentes/etiquetas";
import { useSesion } from "../../sesion/Sesion";
import type { EstadoServicio, NodoResumen, Servicio } from "../../tipos";
import { fechaHora, useTitulo } from "../../util/formato";
import { tieneHerramienta } from "../Servicio";
import { ErrorDeAccion, puede, Registrado, type Resultado } from "./comun";
import { VISIBILIDAD } from "./Nodos";

const ESTADOS = Object.keys(ESTADO_SERVICIO) as EstadoServicio[];

type Fila = { dato: string; origen: string };

export function Servicios() {
  useTitulo("Servicios · Administración");
  const { yo } = useSesion();
  const servicios = useServiciosTodos();
  const nodos = useNodosTodos();
  const [editando, setEditando] = useState<string | null>(null);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [error, setError] = useState<unknown>(null);
  const editable = puede(yo, "curador");

  const avisar = (r: Resultado) => {
    setError(null);
    setResultado(r);
  };
  const fallar = (e: unknown) => {
    setResultado(null);
    setError(e);
  };

  const visibilidadDe = (identificador: string) =>
    nodos.data?.find((n) => n.identificador === identificador)?.visibilidad;

  return (
    <>
      <h2>Servicios</h2>
      <p className="lead">
        Las pantallas para funcionarios construidas sobre un nodo. El texto lo escribe un curador; la
        herramienta es código y sale del nodo. Un servicio aparece en el sitio cuando su nodo está
        publicado.
      </p>

      <Registrado resultado={resultado} autor={yo?.nombre} />
      <ErrorDeAccion error={error} />

      {editable && nodos.data && (
        <details className="admin-form">
          <summary>Crear un servicio</summary>
          <FormularioServicio
            nodos={nodos.data.filter((n) => n.visibilidad !== "retirado")}
            alGuardar={avisar}
            alFallar={fallar}
          />
        </details>
      )}

      {servicios.isPending ? (
        <Cargando />
      ) : servicios.isError ? (
        <ErrorDeCarga error={servicios.error} />
      ) : servicios.data.length === 0 ? (
        <p className="sin-params">Todavía no hay servicios.</p>
      ) : (
        <div className="tabla-ancha">
          <table className="admin-tabla">
            <thead>
              <tr>
                <th>Servicio</th>
                <th>Nodo</th>
                <th>Estado</th>
                <th>Revisado</th>
                {editable && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {servicios.data.map((s) => {
                const visibilidad = visibilidadDe(s.nodo);
                return (
                  <Fragment key={s.slug}>
                    <tr>
                      <td>
                        <Link to={`/servicios/${s.slug}`}>{s.nombre}</Link>
                        <span className="admin-meta">
                          <code>{s.slug}</code>
                        </span>
                      </td>
                      <td>
                        <code>{s.nodo}</code>
                        {visibilidad && (
                          <span className="admin-meta">
                            <span className={VISIBILIDAD[visibilidad].clase}>{VISIBILIDAD[visibilidad].texto}</span>
                          </span>
                        )}
                        {visibilidad && visibilidad !== "publicado" && (
                          <span className="admin-motivo">No aparece en el sitio hasta publicar el nodo.</span>
                        )}
                      </td>
                      <td>
                        <span className={ESTADO_SERVICIO[s.estado].clase}>{ESTADO_SERVICIO[s.estado].texto}</span>
                      </td>
                      <td className="admin-meta">{fechaHora(s.actualizado)}</td>
                      {editable && (
                        <td className="admin-acciones">
                          <button
                            type="button"
                            className="btn-copiar"
                            aria-expanded={editando === s.slug}
                            onClick={() => setEditando((e) => (e === s.slug ? null : s.slug))}
                          >
                            {editando === s.slug ? "Cerrar" : "Editar"}
                          </button>
                        </td>
                      )}
                    </tr>
                    {editando === s.slug && (
                      <tr>
                        <td colSpan={5}>
                          <FormularioServicio
                            servicio={s}
                            alGuardar={(r) => {
                              avisar(r);
                              setEditando(null);
                            }}
                            alFallar={fallar}
                          />
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

/** Crear, con `nodos`, o editar, con `servicio`. `slug` y `nodo` no cambian después de creado. */
function FormularioServicio({
  servicio,
  nodos = [],
  alGuardar,
  alFallar,
}: {
  servicio?: Servicio;
  nodos?: NodoResumen[];
  alGuardar: (r: Resultado) => void;
  alFallar: (e: unknown) => void;
}) {
  const crear = useCrearServicio();
  const editar = useEditarServicio();
  const id = servicio?.slug ?? "nuevo";
  const [slug, setSlug] = useState("");
  const [nodo, setNodo] = useState(nodos[0]?.identificador ?? "");
  const [nombre, setNombre] = useState(servicio?.nombre ?? "");
  const [funcion, setFuncion] = useState(servicio?.funcion ?? "");
  const [descripcion, setDescripcion] = useState(servicio?.descripcion ?? "");
  const [tareas, setTareas] = useState((servicio?.tareas ?? []).join("\n"));
  const [fuentes, setFuentes] = useState<Fila[]>(
    servicio?.fuentes.length ? servicio.fuentes.map((f) => ({ ...f })) : [{ dato: "", origen: "" }],
  );
  const [estado, setEstado] = useState<EstadoServicio>(servicio?.estado ?? "en_construccion");
  const [nota, setNota] = useState(servicio?.nota ?? "");
  const pendiente = crear.isPending || editar.isPending;

  const cambiarFuente = (i: number, campo: keyof Fila, valor: string) =>
    setFuentes((fs) => fs.map((f, j) => (j === i ? { ...f, [campo]: valor } : f)));

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    const datos: DatosServicio = {
      nombre: nombre.trim(),
      funcion: funcion.trim(),
      descripcion: descripcion.trim(),
      tareas: tareas
        .split("\n")
        .map((t) => t.trim())
        .filter(Boolean),
      fuentes: fuentes
        .map((f) => ({ dato: f.dato.trim(), origen: f.origen.trim() }))
        .filter((f) => f.dato || f.origen),
      estado,
      nota: nota.trim(),
    };
    if (servicio) {
      editar.mutate(
        { slug: servicio.slug, ...datos },
        { onSuccess: () => alGuardar({ texto: `Servicio ${servicio.slug} guardado` }), onError: alFallar },
      );
      return;
    }
    crear.mutate(
      { slug: slug.trim(), nodo, ...datos },
      {
        onSuccess: (s) => {
          const publicado = nodos.find((n) => n.identificador === s.nodo)?.visibilidad === "publicado";
          alGuardar({
            texto: publicado
              ? `Servicio ${s.slug} creado sobre ${s.nodo}; ya aparece en el sitio`
              : `Servicio ${s.slug} creado sobre ${s.nodo}; aparecerá en el sitio cuando se publique el nodo`,
          });
          setSlug("");
          setNombre("");
          setFuncion("");
          setDescripcion("");
          setTareas("");
          setFuentes([{ dato: "", origen: "" }]);
          setNota("");
        },
        onError: alFallar,
      },
    );
  };

  return (
    <form className={servicio ? "admin-editar" : undefined} onSubmit={enviar}>
      {!servicio && (
        <div className="admin-fila">
          <div className="campo">
            <label htmlFor="servicio-nodo">Nodo</label>
            <select id="servicio-nodo" required value={nodo} onChange={(e) => setNodo(e.target.value)}>
              {nodos.map((n) => (
                <option key={n.identificador} value={n.identificador}>
                  {n.nombre} ({n.identificador})
                </option>
              ))}
            </select>
          </div>
          <div className="campo">
            <label htmlFor="servicio-slug">Slug</label>
            <input
              id="servicio-slug"
              required
              pattern="[a-z0-9]+(-[a-z0-9]+)*"
              title="Minúsculas, números y guiones."
              placeholder="consulta-permiso-circulacion"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
            />
          </div>
        </div>
      )}
      {!servicio && nodo && !tieneHerramienta(nodo) && (
        <p className="admin-motivo">
          Este nodo todavía no tiene herramienta construida: la página del servicio mostrará solo el texto.
        </p>
      )}
      {!servicio && (
        <p className="admin-meta">El slug y el nodo no cambian después: otro nodo es otro servicio.</p>
      )}

      <div className="campo">
        <label htmlFor={`${id}-nombre`}>Nombre de la herramienta</label>
        <input id={`${id}-nombre`} required maxLength={200} value={nombre} onChange={(e) => setNombre(e.target.value)} />
      </div>
      <div className="campo">
        <label htmlFor={`${id}-funcion`}>Función, en una línea para la tarjeta</label>
        <input id={`${id}-funcion`} required maxLength={300} value={funcion} onChange={(e) => setFuncion(e.target.value)} />
      </div>
      <div className="campo">
        <label htmlFor={`${id}-descripcion`}>Descripción</label>
        <textarea
          id={`${id}-descripcion`}
          className="admin-nota"
          required
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
        />
      </div>
      <div className="campo">
        <label htmlFor={`${id}-tareas`}>Tareas, una por línea</label>
        <textarea id={`${id}-tareas`} className="admin-nota" value={tareas} onChange={(e) => setTareas(e.target.value)} />
      </div>

      <fieldset className="admin-editorial">
        <legend>De dónde sale cada dato</legend>
        {fuentes.map((f, i) => (
          <div className="admin-fila" key={i}>
            <div className="campo">
              <label htmlFor={`${id}-dato-${i}`}>Dato</label>
              <input id={`${id}-dato-${i}`} maxLength={300} value={f.dato} onChange={(e) => cambiarFuente(i, "dato", e.target.value)} />
            </div>
            <div className="campo">
              <label htmlFor={`${id}-origen-${i}`}>Origen</label>
              <input
                id={`${id}-origen-${i}`}
                maxLength={300}
                value={f.origen}
                onChange={(e) => cambiarFuente(i, "origen", e.target.value)}
              />
            </div>
            <button
              type="button"
              className="btn-copiar"
              onClick={() => setFuentes((fs) => fs.filter((_, j) => j !== i))}
              aria-label={`Quitar la fuente ${i + 1}`}
            >
              Quitar
            </button>
          </div>
        ))}
        <p>
          <button type="button" className="btn-copiar" onClick={() => setFuentes((fs) => [...fs, { dato: "", origen: "" }])}>
            Agregar un dato
          </button>
        </p>
      </fieldset>

      <div className="admin-fila">
        <div className="campo">
          <label htmlFor={`${id}-estado`}>Estado de la pantalla</label>
          <select id={`${id}-estado`} value={estado} onChange={(e) => setEstado(e.target.value as EstadoServicio)}>
            {ESTADOS.map((e) => (
              <option key={e} value={e}>
                {ESTADO_SERVICIO[e].texto}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="campo">
        <label htmlFor={`${id}-nota`}>Nota destacada (opcional)</label>
        <textarea id={`${id}-nota`} className="admin-nota" value={nota} onChange={(e) => setNota(e.target.value)} />
      </div>
      <p>
        <button className="btn btn-p" type="submit" disabled={pendiente}>
          {servicio ? "Guardar" : "Crear servicio"}
        </button>
      </p>
    </form>
  );
}
