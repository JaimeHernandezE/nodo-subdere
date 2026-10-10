// Las direcciones de la maqueta ya circularon: cada una lleva a su ruta real.

// Dos nodos que la maqueta llamaba distinto. El catálogo real parte con estos nombres y el
// backend no tiene esos alias, así que la traducción es del frontend.
const NODOS_DE_LA_MAQUETA: Record<string, string> = {
  "division-territorial": "cut",
  fiscalizacion: "permisos-de-circulacion",
};

const PAGINAS: Record<string, string> = {
  "index.html": "/",
  "que-es.html": "/que-es",
  "apis.html": "/apis",
  "catalogo.html": "/servicios",
  "participar.html": "/participar",
  "servicio-cut.html": "/servicios/buscador-cut",
  "servicio-fiscalizacion.html": "/servicios/consulta-permiso-circulacion",
  "wiki.html": "/wiki",
  "wiki-intercambios.html": "/wiki#intercambios",
  "wiki-recorrido.html": "/wiki/recorrido",
  "wiki-consumir.html": "/wiki/consumir",
  "wiki-conectar.html": "/wiki/conectar",
  "wiki-ficha.html": "/wiki/ficha",
  "wiki-cut.html": "/wiki/cut",
  "wiki-fiscalizacion.html": "/wiki/permisos-de-circulacion",
  "wiki-codigos.html": "/wiki/codigos",
  "wiki-normas.html": "/wiki/normas",
  "wiki-glosario.html": "/wiki/glosario",
  "wiki-decisiones.html": "/wiki/decisiones",
};

// Anclas que la maqueta escribía a mano y que en la wiki salen del texto del título.
const ANCLAS: Record<string, string> = {
  "/wiki/conectar#versiones": "/wiki/conectar#lo-que-ya-funciona-no-se-rompe-de-un-dia-para-otro",
  "/wiki/ficha#procedencia": "/wiki/ficha#cuanto-se-le-puede-creer-a-lo-que-muestra-el-catalogo",
};

/** La ruta nueva de una dirección de la maqueta, o `null` si no es una de ellas. */
export function rutaNueva(pathname: string, search: string, hash: string): string | null {
  const archivo = pathname.split("/").pop() ?? "";
  const params = new URLSearchParams(search);

  if (archivo === "nodo.html") {
    const id = params.get("id");
    if (!id) return "/apis";
    return `/apis/${encodeURIComponent(NODOS_DE_LA_MAQUETA[id] ?? id)}${hash}`;
  }

  const destino = PAGINAS[archivo];
  if (!destino) return null;
  if (destino.includes("#")) return destino;

  // El buscador del CUT y el catálogo conservan su búsqueda; la consulta de permisos no,
  // porque ahora exige sesión y un trámite.
  const conserva = ["apis.html", "catalogo.html", "servicio-cut.html"].includes(archivo);
  const consulta = conserva ? search : "";
  return ANCLAS[`${destino}${hash}`] ?? `${destino}${consulta}${hash}`;
}
