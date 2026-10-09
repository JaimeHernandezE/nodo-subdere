# Instrucciones de construcción — frontend del Nodo SUBDERE

Lee también [`README.md`](README.md) y, para las reglas comunes, [`../backend/INSTRUCCIONES.md`](../backend/INSTRUCCIONES.md) secciones 3 a 6.

**No se parte de cero.** La maqueta de [`../prototipos/`](../prototipos/) tiene el contenido escrito, la paleta institucional verificada y las interacciones probadas. Este proyecto **la traduce a componentes; no la rediseña.** Si algo se ve distinto, es un cambio deliberado y debe quedar anotado en [`../docs/maqueta.md`](../docs/maqueta.md).

---

## 1. Decisiones tomadas

Vite · React 19 · TypeScript · React Router · TanStack Query · Vitest y Testing Library. **Sin framework de componentes**: la paleta es la del Gobierno y un framework traería la suya. Son siete pantallas y un puñado de patrones — tarjeta, etiqueta, tabla, aviso, buscador.

Los tipos de `src/tipos/` **se generan desde el OpenAPI del backend**, no se escriben a mano, para que un cambio en el modelo rompa la compilación en vez de romperse en producción.

Los estilos salen de `prototipos/assets/styles.css` con sus *tokens* intactos. Dos cosas que se pierden fácil al traducir:

- **El rojo `#FF1D3D` no alcanza el contraste mínimo para texto pequeño** (3,8:1 sobre blanco). Para texto va `--rojo-tx` (`#D6102B`); el rojo pleno queda para elementos gráficos.
- **La tipografía gobCL se carga desde `assets/fonts/`** y el sitio degrada sin ella. Si los `.woff2` no están, no se rompe nada.

Accesibilidad de teclado y foco visible se cuidan desde el principio. El desplegable de la barra en la maqueta es un `<details>`/`<summary>` nativo justamente por eso: la versión en React debe seguir siéndolo o equivalerle.

## 2. Autenticación

Authorization Code + PKCE contra el *realm* de Keycloak, como **cliente público**. Biblioteca estándar de OIDC para navegador; no escribir el flujo a mano.

- El *access token* va en `Authorization: Bearer` en cada llamada al backend.
- El token **no** se guarda en `localStorage`. En memoria, con refresco silencioso.
- Al entrar, la aplicación llama `GET /api/v1/yo` y de ahí saca nombre, rol y municipio. **La interfaz se arma con eso, no con los *claims* del token.**
- Un `403` con código `SIN_PERFIL` tiene su propia pantalla: «te autenticaste, pero no tienes perfil en el nodo», con a quién escribir. No es un error genérico.

Las partes públicas —portada, catálogos, fichas, wiki, buscador del CUT— **funcionan sin sesión**. La sesión solo hace falta para administrar y para la consulta de permisos de circulación.

## 3. Rutas

Salen de la maqueta y conviene conservarlas, porque ya se compartieron enlaces.

| Ruta | Qué es | En la maqueta |
|---|---|---|
| `/` | Portada | `index.html` |
| `/que-es` | Descripción general | `que-es.html` |
| `/apis` · `/apis/:id` | Catálogo de intercambios y ficha, con su especificación | `apis.html` · `nodo.html?id=` |
| `/servicios` · `/servicios/:slug` | Catálogo de pantallas y cada pantalla | `catalogo.html` · `servicio-*.html` |
| `/wiki` · `/wiki/:slug` | Índice y entrada | `wiki.html` · `wiki-*.html` |
| `/participar` | Cómo participar | `participar.html` |
| `/admin/*` | Administración: fuentes, visibilidad, perfiles, wiki | no existe en la maqueta |

Dejar redirecciones desde las direcciones viejas, incluida `nodo.html?id=division-territorial`, que apunta a un nodo renombrado. El backend ya resuelve el alias; el frontend solo tiene que no romper el enlace.

## 4. Los dos patrones que la maqueta ya resolvió

**La ficha de un nodo se compone de tres pedidos.** `GET /api/v1/nodos/{id}` trae la ficha; `GET /api/v1/wiki?nodo={id}` su entrada de wiki, y `GET /api/v1/servicios?nodo={id}` las pantallas construidas sobre él. El backend no las junta porque `catalogo` no depende de `wiki` ni de `servicios`. Si el nodo responde por un alias, la ruta se reescribe al identificador vigente que viene en la respuesta. Un `410` con `NODO_RETIRADO` tiene su propia vista: qué fue y hasta cuándo se leyó. Si hay sesión, la ficha manda el token aunque la ruta sea pública: es lo que permite revisar un nodo oculto, que se muestra con un aviso visible de que no está publicado. Sin sesión, un oculto es un `404` como cualquier otro.

**La especificación se renderiza, no se transcribe.** La ficha lee el archivo OpenAPI desde `GET /api/v1/nodos/{id}/especificacion/archivo` y lo dibuja operación por operación. Si el nodo publica solo metadato, la ficha lo dice y no inventa operaciones. No hay una lista de operaciones escrita a mano en ninguna parte, y ese es el punto: si alguien edita la especificación y la ficha no cambia, la ficha está mintiendo. En React es un componente `<Especificacion archivo={...} />` que hace lo que hoy hace `assets/openapi.js`. Límite conocido que conviene no perder: solo resuelve referencias internas (`#/…`); una especificación repartida en varios archivos no se ensambla.

**Las pantallas degradan con honestidad.** Cuando la fuente no responde, el backend devuelve datos de muestra con un campo que lo declara. La pantalla **tiene que mostrarlo**, visible, al lado del dato. Intentar, y si falla, mostrar la muestra con su etiqueta.

Y una tercera, nueva: **las pantallas que entregan datos de personas avisan que la consulta queda registrada.** No en letra chica.

## 5. La administración

Es la parte que no existe en la maqueta, así que acá sí hay diseño nuevo. Cuatro pantallas, en este orden de construcción:

1. **Fuentes.** Lista con su última lectura: *commit*, fecha, válida o no, y el motivo cuando falló. Botón de resincronizar. Es la pantalla que más se va a usar.
2. **Visibilidad.** Lista todos los nodos con `GET /api/v1/nodos?visibilidad=todas`. Publicar, ocultar y retirar un nodo; de `retirado` solo se vuelve a `oculto`. **Los campos que vienen de la ficha se muestran en gris y no se pueden editar**, con una nota de por qué: los escribe la sincronización. Que el formulario lo diga evita la pregunta.
3. **Wiki.** Editor de Markdown con vista previa, historial de versiones y botón de publicar.
4. **Perfiles y equipos.** Alta por RUN, rol, activar y desactivar, y designar al encargado de un municipio. La misma pantalla la usa el encargado municipal para su equipo, **mostrando solo lo que puede hacer**: crea solo lectores, solo en su municipio, y no se edita a sí mismo. El backend lo impide igual; la pantalla evita que lo intente.

Cada acción que cambia algo muestra qué quedó registrado en la bitácora. Es barato y hace que la gente confíe en la herramienta.

## 6. Pruebas mínimas

1. Las rutas públicas cargan sin sesión.
2. Un `403` con `SIN_PERFIL` lleva a su pantalla, no al error genérico.
3. La respuesta con datos de muestra se muestra marcada en pantalla.
4. La ficha renderiza una especificación de prueba con referencias internas.
5. Los campos de ficha en la pantalla de visibilidad no son editables.
6. El desplegable de la barra se abre y se cierra con teclado, y el foco es visible.
7. Las direcciones viejas redirigen sin romperse.

## 7. Qué no implementar

- Ninguna llamada directa del navegador a las fuentes externas. Todo pasa por el backend, que es el único que conoce el camino a SEM y el que registra los accesos.
- Ningún dato en `localStorage`: ni tokens, ni respuestas, ni datos de personas.
- Ningún texto nuevo de contenido institucional. El contenido viene de la maqueta y de la wiki; si falta algo, se agrega allá primero.
- Representación en el servidor, por ahora. Es una decisión abierta y afecta cómo se publica (HR-20).
