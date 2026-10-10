# Frontend — Nodo SUBDERE

La interfaz del sitio en React: los dos catálogos, las fichas, las pantallas de servicio y la wiki.

> **Para construir:** [`INSTRUCCIONES.md`](INSTRUCCIONES.md) tiene el detalle de rutas, autenticación, patrones a portar y pantallas de administración. Este README explica el diseño.

No se parte de cero. La maqueta de [`prototipos/`](../prototipos/) ya tiene el contenido escrito, la paleta institucional verificada y las interacciones probadas. **Este proyecto la traduce a componentes; no la rediseña.** Si algo se ve distinto, es un cambio deliberado y debería estar anotado en [`docs/maqueta.md`](../docs/maqueta.md).

## Qué está construido

**Primera etapa: el sitio público, la sesión y `/yo`.** Portada, Qué es, Cómo participar, los dos catálogos, la ficha con su especificación renderizada, las pantallas de servicio (buscador CUT y consulta de permisos de circulación), la wiki con su menú e índice, la pantalla `SIN_PERFIL`, la 404 y las redirecciones de la maqueta.

**Falta:** la administración (`/admin/*`, §5 de [`INSTRUCCIONES.md`](INSTRUCCIONES.md)) y el ingreso con Keycloak. Mientras no exista el *realm*, se entra pegando un token del emisor local del backend en `/entrar`.

---

## Estructura

```
frontend/
├── public/             favicon; gobCL va en public/fonts/ si se consigue
├── src/
│   ├── app/            Enrutador, marco, barra superior, pie y redirecciones de la maqueta
│   ├── paginas/        Una por ruta del sitio; herramientas/ tiene las de cada servicio
│   ├── componentes/    Lo reutilizable: especificación, estados, etiquetas, origen del dato
│   ├── api/            Cliente del backend y una función por consulta
│   ├── sesion/         Token en memoria y /yo
│   ├── estilos/        maqueta.css (copia de la maqueta) y sitio.css (lo que agrega React)
│   ├── tipos/          esquema.yaml del backend y los tipos generados desde él
│   ├── util/           Fechas, montos, slugs, título de la pestaña
│   └── pruebas/        Vitest y Testing Library
├── docker-compose.yml  Servicio web (node:22) para desarrollo
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

Lo que sí hace falta cuidar: accesibilidad de teclado y foco visible. La barra de la maqueta es una lista de enlaces simples, sin desplegables, y la versión en React la mantiene así. La única excepción es el menú de sesión, a la derecha: un `<details>` que se abre con Enter o espacio y se cierra con Escape, devolviendo el foco a su botón.

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
- **La tipografía gobCL se carga desde `public/fonts/`** y el sitio degrada sin ella. Si los `.woff2` no están, no se rompe nada; `npm run build` avisa que no los encontró, y es esperado.

`maqueta.css` no se edita: lo que el sitio en React necesita además —foco visible, menú de sesión, contenido de la wiki, formularios— va en `sitio.css`.

### Tipos desde el OpenAPI

El backend publica su esquema. Los tipos de `src/tipos/` se generan desde ahí en vez de escribirse a mano, para que un cambio en el modelo rompa la compilación en lugar de romperse en producción. Cuando cambia el backend:

```powershell
# desde backend/
docker compose --env-file .env.local exec api sh -c "python manage.py spectacular --file /tmp/esquema.yaml"
docker compose --env-file .env.local cp api:/tmp/esquema.yaml ..\frontend\src\tipos\esquema.yaml
# desde frontend/
docker compose run --rm web sh -c "npm run tipos && npm run revisar"
```

`src/tipos/index.ts` les da nombres cortos a los esquemas que usan las páginas.

---

## Dos patrones que la maqueta ya resolvió

Conviene portarlos, no reinventarlos.

### La especificación se renderiza, no se transcribe

La ficha de un intercambio lee el archivo OpenAPI y lo dibuja operación por operación. No hay una lista de operaciones escrita a mano en ninguna parte, y ese es el punto: si alguien edita la especificación y la ficha no cambia, la ficha está mintiendo. En React es un componente `<Especificacion archivo={...} />` que hace lo que hoy hace `assets/openapi.js`.

Límite conocido, que conviene no perder: solo resuelve referencias internas (`#/…`). Una especificación repartida en varios archivos no se ensambla.

### Las pantallas de servicio degradan con honestidad

`servicio-cut.html` y `servicio-fiscalizacion.html` consultan una API externa y, cuando no está alcanzable, funcionan con datos de demostración **diciéndolo en pantalla**, con el número real del catálogo al lado.

Ese comportamiento hay que conservarlo. Una pantalla que se queda en blanco cuando el servicio no responde no se puede mostrar en una reunión; una que finge datos sin avisar es peor. El patrón es: intentar, y si falla, mostrar la muestra con su etiqueta visible.

En el sitio en React la decisión la toma el backend, no la pantalla: cada respuesta de servicio trae `origen` (`fuente`, `foto` o `muestra`) y `obtenido_en`. La pantalla no tiene datos de demostración propios; pinta la etiqueta junto al resultado («En vivo», «Copia guardada», «Datos de muestra») y el aviso de «De dónde salen estos datos». Qué herramienta muestra cada servicio se decide por su `nodo` (`cut` o `permisos-de-circulacion`), en `paginas/Servicio.tsx`.

---

## Cómo levantarlo

Node no hace falta en el equipo: todo corre en Docker. El backend se levanta aparte y queda en `http://localhost:8000`; su `.env.local` necesita `CORS_ALLOWED_ORIGINS=http://localhost:5173` y, para entrar sin Keycloak, `CUENTAS_EMISOR_LOCAL=1`.

```powershell
cd frontend
docker compose up                 # instala y deja Vite en http://localhost:5173
```

Si el backend está en otra dirección, copiar `.env.example` a `.env.local` y cambiar `VITE_API_URL`.

**Entrar.** En `/entrar` se pega un token del emisor local:

```powershell
# desde backend/; el RUN necesita un Perfil activo
docker compose --env-file .env.local exec api sh -c "python manage.py emitir_token_local --run 12345678-5"
```

El token queda solo en memoria: recargar la página cierra la sesión. Un RUN sin perfil lleva a la pantalla `SIN_PERFIL`.

**Revisar y probar:**

```powershell
docker compose run --rm web sh -c "npm run revisar"   # tsc
docker compose run --rm web sh -c "npm test"          # vitest
docker compose run --rm web sh -c "npm run build"     # dist/
```

Las pruebas cubren el §6 de [`INSTRUCCIONES.md`](INSTRUCCIONES.md) menos el punto 5, que es de la administración. Simulan el backend con un `fetch` falso (`src/pruebas/util.tsx`), así que no necesitan nada levantado.

---

## Qué falta decidir

- **Si el sitio se renderiza en el servidor.** Es contenido público y la indexación importa; las *Recomendaciones para sitios web institucionales* insisten en SEO. React puro en el navegador lo complica. Vale evaluar SSR antes de avanzar mucho.
- **Cómo se publica.** Hoy la maqueta va por GitHub Pages. El sitio real necesita otra cosa, y de eso depende si el frontend puede ser estático o no.
- **El idioma de las rutas.** Hoy están en español y así deberían quedar, pero conviene decidirlo ahora y no cuando haya enlaces repartidos.
