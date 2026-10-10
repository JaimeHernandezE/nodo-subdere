# Frontend — Nodo SUBDERE

La interfaz del sitio en React: los dos catálogos, las fichas, las pantallas de servicio y la wiki.

> **Para construir:** [`INSTRUCCIONES.md`](INSTRUCCIONES.md) tiene el detalle de rutas, autenticación, patrones a portar y pantallas de administración. Este README explica el diseño.

No se parte de cero. La maqueta de [`prototipos/`](../prototipos/) ya tiene el contenido escrito, la paleta institucional verificada y las interacciones probadas. **Este proyecto la traduce a componentes; no la rediseña.** Si algo se ve distinto, es un cambio deliberado y debería estar anotado en [`docs/maqueta.md`](../docs/maqueta.md).

---

## Estructura

```
frontend/
├── public/
├── src/
│   ├── app/            Enrutador, layout, barra superior y pie
│   ├── paginas/        Una por ruta del sitio
│   ├── componentes/    Lo reutilizable entre páginas
│   ├── api/            Cliente del backend y de los adaptadores
│   ├── estilos/        Tokens y estilos globales
│   └── tipos/          Tipos compartidos, derivados del OpenAPI del backend
├── index.html
├── package.json
├── vite.config.ts
└── .env.example
```

---

## Las rutas

Salen directo de la maqueta y conviene conservarlas, porque ya se compartieron enlaces:

| Ruta | Qué es | Archivo en la maqueta |
|---|---|---|
| `/` | Portada | `index.html` |
| `/que-es` | Descripción general | `que-es.html` |
| `/apis` | Catálogo de intercambios | `apis.html` |
| `/apis/:id` | Ficha de un intercambio, con su especificación | `nodo.html?id=` |
| `/servicios` | Catálogo de pantallas de uso humano | `catalogo.html` |
| `/servicios/:id` | Una pantalla de servicio | `servicio-cut.html`, `servicio-fiscalizacion.html` |
| `/wiki` | Portada e índice de la wiki | `wiki.html`, `wiki-intercambios.html` |
| `/wiki/:slug` | Una entrada; el contenido llega del backend como HTML saneado | `wiki-*.html` (`wiki-fiscalizacion.html` es `/wiki/permisos-de-circulacion`) |
| `/participar` | Cómo participar | `participar.html` |

`catalogo.html` conserva ese nombre en la maqueta por los enlaces ya compartidos, pero **la ruta real es `/servicios`**. Conviene dejar una redirección desde las direcciones viejas —incluida `nodo.html?id=division-territorial`, un nodo que se renombró en la maqueta y que el catálogo real llama `cut` desde el inicio— para no romper lo que ya circuló.

---

## Decisiones técnicas

| | |
|---|---|
| **Vite + React 19 + TypeScript** | |
| **React Router** | |
| **TanStack Query** | Para las consultas al backend y a los adaptadores: caché, reintentos y estados de carga resueltos en un solo lugar |
| **CSS con variables**, sin framework de UI | La maqueta ya tiene los tokens y son pocos. Un framework traería su propio sistema de color, y el nuestro es el del Gobierno |
| **Vitest + Testing Library** | |

### Sin framework de componentes, y por qué

El [Kit Gráfico de Gobierno](../docs/maqueta.md) define la paleta y la tipografía, y los pares de color del sitio ya están verificados contra el mínimo de contraste de la W3C. Traer una biblioteca de componentes significaría o pelear con sus colores o terminar usando los suyos. El sitio tiene siete pantallas y un puñado de patrones: tarjeta, etiqueta, tabla, aviso, buscador.

Lo que sí hace falta cuidar: accesibilidad de teclado y foco visible. La barra de la maqueta es una lista de enlaces simples, sin desplegables, y la versión en React debería mantenerla así.

### Los estilos vienen de la maqueta

`src/estilos/` empieza como una copia de `prototipos/assets/styles.css`, con sus tokens intactos:

```css
--navy: #25306B;   /* Pantone 2756C */
--azul: #006BB9;   /* Pantone 2175C — botón primario y enlaces */
--rojo: #FF1D3D;   /* Pantone 1788c — solo marca gráfica */
--grey: #EDF0F5;   /* Pantone 663C */
```

Dos cosas que hay que mantener al traducir, porque se pierden fácil:

- **El rojo `#FF1D3D` no alcanza el contraste mínimo para texto pequeño** (3,8:1 sobre blanco). Para texto va `--rojo-tx` (`#D6102B`); el rojo pleno queda para elementos gráficos.
- **La tipografía gobCL se carga desde `assets/fonts/`** y el sitio degrada sin ella. Si los `.woff2` no están, no se rompe nada.

### Tipos desde el OpenAPI

El backend publica su esquema. Los tipos de `src/tipos/` se generan desde ahí en vez de escribirse a mano, para que un cambio en el modelo rompa la compilación en lugar de romperse en producción.

---

## Dos patrones que la maqueta ya resolvió

Conviene portarlos, no reinventarlos.

### La especificación se renderiza, no se transcribe

La ficha de un intercambio lee el archivo OpenAPI y lo dibuja operación por operación. No hay una lista de operaciones escrita a mano en ninguna parte, y ese es el punto: si alguien edita la especificación y la ficha no cambia, la ficha está mintiendo. En React es un componente `<Especificacion archivo={...} />` que hace lo que hoy hace `assets/openapi.js`.

Límite conocido, que conviene no perder: solo resuelve referencias internas (`#/…`). Una especificación repartida en varios archivos no se ensambla.

### Las pantallas de servicio degradan con honestidad

`servicio-cut.html` y `servicio-fiscalizacion.html` consultan una API externa y, cuando no está alcanzable, funcionan con datos de demostración **diciéndolo en pantalla**, con el número real del catálogo al lado.

Ese comportamiento hay que conservarlo. Una pantalla que se queda en blanco cuando el servicio no responde no se puede mostrar en una reunión; una que finge datos sin avisar es peor. El patrón es: intentar, y si falla, mostrar la muestra con su etiqueta visible.

Los datos de demostración viven en archivos aparte y claramente nombrados, para poder borrarlos de una vez cuando los servicios estén arriba.

---

## Cómo levantarlo

```bash
cd frontend
npm install
cp .env.example .env          # apuntar VITE_API_URL al backend
npm run dev
```

Queda en `http://localhost:5173`, contra el backend en `http://localhost:8000`.

---

## Qué falta decidir

- **Si el sitio se renderiza en el servidor.** Es contenido público y la indexación importa; las *Recomendaciones para sitios web institucionales* insisten en SEO. React puro en el navegador lo complica. Vale evaluar SSR antes de avanzar mucho.
- **Cómo se publica.** Hoy la maqueta va por GitHub Pages. El sitio real necesita otra cosa, y de eso depende si el frontend puede ser estático o no.
- **El idioma de las rutas.** Hoy están en español y así deberían quedar, pero conviene decidirlo ahora y no cuando haya enlaces repartidos.
