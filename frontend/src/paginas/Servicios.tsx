import { Link, useSearchParams } from "react-router";

import { useServicios } from "../api/consultas";
import { Cargando, ErrorDeCarga } from "../componentes/Estados";
import { ESTADO_SERVICIO } from "../componentes/etiquetas";
import { sinTildes, useTitulo } from "../util/formato";

export function Servicios() {
  useTitulo("Catálogo de servicios");
  const [params, setParams] = useSearchParams();
  const texto = params.get("q") ?? "";
  const servicios = useServicios();

  const todos = servicios.data ?? [];
  const buscado = sinTildes(texto.trim());
  const lista = todos.filter(
    (s) =>
      !buscado || sinTildes(`${s.nombre} ${s.funcion} ${s.tareas.join(" ")}`).includes(buscado),
  );

  return (
    <main>
      <section style={{ paddingBottom: 18 }}>
        <div className="wrap">
          <p className="eyebrow">Catálogo de servicios</p>
          <h2>Aplicaciones al alcance de cualquier usuario</h2>
          <p className="lead">
            Cada servicio es una pantalla que resuelve una tarea concreta, sin instalar nada ni escribir
            código. Además, cada uno está construido sobre una API del{" "}
            <Link to="/apis">catálogo de APIs</Link> y la indica, para quien quiera hacer lo mismo desde
            su propio sistema.
          </p>
          <div className="filtros">
            <input
              className="buscador"
              type="search"
              placeholder="Buscar un servicio o una tarea…"
              aria-label="Buscar servicios"
              value={texto}
              onChange={(e) =>
                setParams(e.target.value.trim() ? { q: e.target.value } : {}, { replace: true })
              }
            />
          </div>

          {servicios.isPending ? (
            <Cargando />
          ) : servicios.isError ? (
            <ErrorDeCarga error={servicios.error} />
          ) : (
            <>
              <p className="conteo">
                {lista.length === todos.length
                  ? todos.length === 1
                    ? "1 servicio en el catálogo"
                    : `${todos.length} servicios en el catálogo`
                  : `${lista.length} de ${todos.length} servicios`}
              </p>
              {todos.length === 0 ? (
                <p className="pendiente">
                  Todavía no hay servicios publicados. Mientras tanto, lo que existe está en el{" "}
                  <Link to="/apis">catálogo de APIs</Link>.
                </p>
              ) : lista.length === 0 ? (
                <p className="pendiente">
                  Ningún servicio coincide con esa búsqueda. La lista todavía es muy corta: puede que lo
                  que buscas exista como API y aún no tenga pantalla. Revisa el{" "}
                  <Link to="/apis">catálogo de APIs</Link>.
                </p>
              ) : (
                <div className="grid-nodos">
                  {lista.map((s) => {
                    const estado = ESTADO_SERVICIO[s.estado];
                    return (
                      <Link className="nodo" key={s.slug} to={`/servicios/${s.slug}`}>
                        <div className="cab">
                          <h4>{s.nombre}</h4>
                          <span className={estado.clase}>{estado.texto}</span>
                        </div>
                        <p className="func">{s.funcion}</p>
                        {s.tareas.length > 0 && (
                          <ul className="tareas">
                            {s.tareas.map((t) => (
                              <li key={t}>{t}</li>
                            ))}
                          </ul>
                        )}
                      </Link>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </div>
      </section>

      <section className="gris">
        <div className="wrap">
          <p className="eyebrow">Cómo se construye</p>
          <h2>Mismas reglas para todos</h2>
          <p className="lead">
            Un servicio pide los datos a la misma API, y con las mismas reglas de acceso, que usa
            cualquier otro sistema: el de un municipio, el de un proveedor o el Sistema de Gestión
            Municipal (SGM) que desarrolla SUBDERE.
          </p>
          <p className="lead">
            Así, todo lo que hace una pantalla de este catálogo lo puede hacer también cualquier sistema
            que se conecte a la API, y el catálogo de APIs muestra exactamente lo que se puede construir.
          </p>
          <table>
            <thead>
              <tr>
                <th>Estado</th>
                <th>Qué quiere decir</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <span className="tag tag-mad">Deseable</span>
                </td>
                <td>Se sabe que hace falta y está anotado. Todavía no hay nada construido.</td>
              </tr>
              <tr>
                <td>
                  <span className="tag tag-dev">En construcción</span>
                </td>
                <td>
                  La pantalla existe y se puede probar, pero la API detrás no está alcanzable para todos o
                  el alcance está incompleto.
                </td>
              </tr>
              <tr>
                <td>
                  <span className="tag">Disponible</span>
                </td>
                <td>Funciona de punta a punta y cualquiera puede usarlo.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
