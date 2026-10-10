import { useEffect, useMemo, useState, type MouseEvent, type ReactNode } from "react";
import { Link, useLocation, useNavigate, useParams, useSearchParams } from "react-router";

import { esEstado } from "../api/cliente";
import { useEntrada, useEntradas, useNodos } from "../api/consultas";
import { Cargando, ErrorDeCarga } from "../componentes/Estados";
import type { Entrada, EntradaResumen } from "../tipos";
import { sinTildes, useIrAlAncla, useTitulo } from "../util/formato";

const SECCIONES: { clave: string; texto: string }[] = [
  { clave: "usar_el_nodo", texto: "Usar el nodo" },
  { clave: "intercambios", texto: "Intercambios" },
  { clave: "codigos", texto: "Códigos y datos maestros" },
  { clave: "normas", texto: "Marco normativo" },
  { clave: "referencia", texto: "Referencia" },
];
const TEXTO_SECCION = Object.fromEntries(SECCIONES.map((s) => [s.clave, s.texto]));
const INDICE_INTERCAMBIOS = "/wiki#intercambios";

/** Menú, contenido y «En esta página», como en la maqueta. `actual` es la ruta que se marca. */
function Diseno({ actual, html, children }: { actual: string; html: string; children: ReactNode }) {
  const navegar = useNavigate();
  const titulos = useMemo(() => titulosDe(html), [html]);

  // Los enlaces del HTML de la wiki son <a> sueltos: sin esto, cada uno recargaría el sitio.
  const interceptar = (evento: MouseEvent<HTMLElement>) => {
    if (evento.defaultPrevented || evento.button !== 0) return;
    if (evento.metaKey || evento.ctrlKey || evento.shiftKey || evento.altKey) return;
    const enlace = (evento.target as HTMLElement).closest("a");
    const destino = enlace?.getAttribute("href");
    if (!enlace || !destino || enlace.target || enlace.hasAttribute("download")) return;
    if (!destino.startsWith("/") && !destino.startsWith("#")) return;
    if (destino.startsWith("//")) return;
    evento.preventDefault();
    if (destino.startsWith("#")) {
      navegar({ hash: destino });
      document.getElementById(decodeURIComponent(destino.slice(1)))?.scrollIntoView?.();
    } else {
      navegar(destino);
    }
  };

  return (
    <div className="wrap wiki-layout">
      <MenuDeLaWiki actual={actual} />
      <main className="wiki-main" onClick={interceptar}>
        {children}
      </main>
      {titulos.length >= 2 ? (
        <nav className="wiki-toc" aria-label="En esta página">
          <p className="wiki-toc__tit">En esta página</p>
          <ul>
            {titulos.map((t) => (
              <li key={t.id}>
                <a href={`#${t.id}`} onClick={(e) => irA(e, t.id, navegar)}>
                  {t.texto}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      ) : (
        <nav className="wiki-toc" aria-label="En esta página" hidden />
      )}
    </div>
  );
}

function irA(evento: MouseEvent, id: string, navegar: ReturnType<typeof useNavigate>) {
  evento.preventDefault();
  navegar({ hash: `#${id}` });
  document.getElementById(id)?.scrollIntoView?.();
}

function titulosDe(html: string) {
  if (!html) return [];
  const doc = new DOMParser().parseFromString(html, "text/html");
  return Array.from(doc.querySelectorAll("h2[id]")).map((h) => ({
    id: h.id,
    texto: h.textContent ?? "",
  }));
}

function useEsEscritorio() {
  const consulta = "(min-width: 901px)";
  const [es, setEs] = useState(() => window.matchMedia?.(consulta).matches ?? true);
  useEffect(() => {
    const mq = window.matchMedia?.(consulta);
    if (!mq) return;
    const cambiar = () => setEs(mq.matches);
    mq.addEventListener("change", cambiar);
    return () => mq.removeEventListener("change", cambiar);
  }, []);
  return es;
}

function MenuDeLaWiki({ actual }: { actual: string }) {
  const entradas = useEntradas();
  const escritorio = useEsEscritorio();
  const [abierto, setAbierto] = useState(escritorio);
  useEffect(() => setAbierto(escritorio), [escritorio]);

  const lista = entradas.data ?? [];
  const enlace = (ruta: string, texto: string) => (
    <li key={ruta}>
      <Link to={ruta} aria-current={ruta === actual ? "page" : undefined}>
        {texto}
      </Link>
    </li>
  );

  return (
    <aside className="wiki-nav" aria-label="Menú de la wiki">
      <details
        className="wiki-nav__plegable"
        open={abierto}
        onToggle={(e) => setAbierto(e.currentTarget.open)}
      >
        <summary>Menú de la wiki</summary>
        <ul className="wiki-nav__lista">
          {enlace("/wiki", "Inicio de la wiki")}
          {SECCIONES.map(({ clave, texto }) => {
            const grupo = lista
              .filter((e) => e.seccion === clave)
              .sort((a, b) => a.orden - b.orden || a.titulo.localeCompare(b.titulo, "es"));
            if (!grupo.length) return null;
            return [
              <li key={`div-${clave}`} className="wiki-nav__div" role="separator" />,
              <li key={`grupo-${clave}`} className="wiki-nav__grupo">
                {texto}
              </li>,
              // Lo que crece sin límite, una entrada por intercambio, va en un índice.
              ...(clave === "intercambios"
                ? [enlace(INDICE_INTERCAMBIOS, "Índice de entradas")]
                : grupo.map((e) => enlace(`/wiki/${e.slug}`, e.titulo))),
            ];
          })}
        </ul>
      </details>
    </aside>
  );
}

function rutaEnElMenu(entrada: { slug: string; seccion: string }) {
  return entrada.seccion === "intercambios" ? INDICE_INTERCAMBIOS : `/wiki/${entrada.slug}`;
}

function Contenido({ html }: { html: string }) {
  return <div className="wiki-contenido" dangerouslySetInnerHTML={{ __html: html }} />;
}

export function WikiPortada() {
  useTitulo("Wiki");
  const { hash } = useLocation();
  const inicio = useEntrada("inicio");
  const html = inicio.data?.html ?? "";
  useIrAlAncla(hash, !inicio.isPending);

  return (
    <Diseno actual={hash === "#intercambios" ? INDICE_INTERCAMBIOS : "/wiki"} html={html}>
      <section>
        <div className="wrap">
          {inicio.isPending ? (
            <Cargando />
          ) : inicio.isError ? (
            <ErrorDeCarga error={inicio.error} />
          ) : (
            <Contenido html={html} />
          )}
        </div>
      </section>
      <IndiceDeIntercambios />
    </Diseno>
  );
}

/** Una tarjeta por intercambio visible del catálogo, con su entrada si ya está escrita. */
function IndiceDeIntercambios() {
  const [params, setParams] = useSearchParams();
  const texto = params.get("q") ?? "";
  const nodos = useNodos();
  const entradas = useEntradas();

  const porNodo = new Map<string, EntradaResumen>();
  for (const e of entradas.data ?? []) {
    if (e.seccion === "intercambios" && e.nodo) porNodo.set(e.nodo, e);
  }
  const todos = nodos.data ?? [];
  const buscado = sinTildes(texto.trim());
  const hallados = todos.filter(
    (n) => !buscado || sinTildes(`${n.nombre} ${n.funcion}`).includes(buscado),
  );

  return (
    <section className="gris" id="intercambios">
      <div className="wrap">
        <p className="eyebrow">Intercambios</p>
        <h2>Una entrada para cada intercambio</h2>
        <p className="lead">
          Cada intercambio del <Link to="/apis">catálogo de APIs</Link> tiene aquí su explicación: cómo
          funciona, qué norma lo respalda y qué observamos en su contrato —la descripción de qué se puede
          pedir y qué se recibe—. La lista se arma sola con el catálogo.
        </p>
        <div className="filtros">
          <input
            className="buscador"
            type="search"
            placeholder="Buscar un intercambio…"
            aria-label="Buscar intercambios"
            value={texto}
            onChange={(e) =>
              setParams(e.target.value.trim() ? { q: e.target.value } : {}, {
                replace: true,
                preventScrollReset: true,
              })
            }
          />
        </div>
        {nodos.isPending ? (
          <Cargando />
        ) : nodos.isError ? (
          <ErrorDeCarga error={nodos.error} />
        ) : (
          <>
            <p className="conteo">
              {hallados.length === todos.length
                ? todos.length === 1
                  ? "1 intercambio"
                  : `${todos.length} intercambios`
                : `${hallados.length} de ${todos.length} intercambios`}
            </p>
            {todos.length === 0 ? (
              <p className="pendiente">Todavía no hay intercambios publicados en el catálogo.</p>
            ) : hallados.length === 0 ? (
              <p className="pendiente">
                Ningún intercambio coincide con esa búsqueda. Prueba con otra palabra o revisa el{" "}
                <Link to="/apis">catálogo de APIs</Link>.
              </p>
            ) : (
              <div className="grid-nodos">
                {hallados.map((n) => {
                  const entrada = porNodo.get(n.identificador);
                  return (
                    <div className="nodo" key={n.identificador}>
                      <div className="cab">
                        <h4>{n.nombre}</h4>
                        {!entrada && <span className="tag tag-mad">Entrada pendiente</span>}
                      </div>
                      <p className="func">{n.funcion}</p>
                      <p className="nodo-enlaces">
                        {entrada && (
                          <Link to={`/wiki/${entrada.slug}`}>
                            <strong>Leer la entrada</strong>
                          </Link>
                        )}
                        <Link to={`/apis/${encodeURIComponent(n.identificador)}`}>Ficha en APIs</Link>
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
}

export function WikiEntrada() {
  const { slug = "" } = useParams();
  const { hash } = useLocation();
  const consulta = useEntrada(slug);
  useIrAlAncla(hash, !!consulta.data);

  if (slug === "inicio") return <WikiPortada />;

  return (
    <Diseno
      actual={consulta.data ? rutaEnElMenu(consulta.data) : `/wiki/${slug}`}
      html={consulta.data?.html ?? ""}
    >
      {consulta.isPending ? (
        <section>
          <div className="wrap">
            <Cargando />
          </div>
        </section>
      ) : consulta.isError ? (
        <section>
          <div className="wrap">
            {esEstado(consulta.error, 404) ? <EntradaNoExiste /> : <ErrorDeCarga error={consulta.error} />}
          </div>
        </section>
      ) : (
        <PaginaDeEntrada entrada={consulta.data} />
      )}
    </Diseno>
  );
}

function PaginaDeEntrada({ entrada }: { entrada: Entrada }) {
  useTitulo(`${entrada.titulo} · Wiki`);
  const seccion = TEXTO_SECCION[entrada.seccion];
  return (
    <section>
      <div className="wrap">
        <p className="miga">
          <Link to="/wiki">Wiki</Link> /{" "}
          {entrada.seccion === "intercambios" && (
            <>
              <Link to={INDICE_INTERCAMBIOS}>Intercambios</Link> /{" "}
            </>
          )}
          {entrada.titulo}
        </p>
        {seccion && <p className="eyebrow">{seccion}</p>}
        <Contenido html={entrada.html} />
      </div>
    </section>
  );
}

function EntradaNoExiste() {
  useTitulo("Entrada no encontrada · Wiki");
  return (
    <>
      <p className="miga">
        <Link to="/wiki">Wiki</Link> / No encontrada
      </p>
      <h2>Esta entrada no existe</h2>
      <p className="lead">
        Puede que haya cambiado de nombre o que todavía no esté publicada. El menú de la izquierda tiene
        todas las entradas de la wiki.
      </p>
    </>
  );
}
