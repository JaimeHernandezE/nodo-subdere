# Nodo SUBDERE — maqueta del sitio

Prototipo estático para revisión, previa al desarrollo en Django + React. Complementa la documentación en [`docs/`](../docs/) sin sustituirla.

Sin build, sin dependencias: HTML, CSS y JS a mano.

## Relación con docs

| Artefacto | Ubicación | Propósito |
|---|---|---|
| Documentación | [`docs/`](../docs/) | Decisiones, precedente, modelo y preguntas de QA |
| Maqueta HTML | `prototipos/` | Navegación y validación sobre algo concreto |

## Compartir con quien no usa consola

La maqueta se publica en **GitHub Pages** al hacer push a `main` (workflow [`.github/workflows/pages-prototipos.yml`](../.github/workflows/pages-prototipos.yml)).

**URL pública:**

```
https://jaimehernandeze.github.io/nodo-subdere/
```

### Activar GitHub Pages (una sola vez)

1. En GitHub: **Settings → Pages**
2. **Build and deployment → Source:** `GitHub Actions`
3. Push a `main` o ejecutar **Actions → Deploy prototipos → Run workflow**
4. Cuando termine en verde: **Settings → Pages** muestra la URL

### Desarrollo local

Doble clic en `index.html` basta para todo salvo `404.html`, que usa rutas absolutas porque se sirve desde cualquier URL. Para verlo tal cual quedará:

```bash
python -m http.server 8000 --directory prototipos
# http://localhost:8000
```

## Estructura

```
prototipos/
├── index.html          # Landing
├── que-es.html         # Qué es el nodo
├── catalogo.html       # Catálogo (filtro por ámbito + buscador)
├── nodo.html           # Ficha de un nodo (?id=<slug>)
├── participar.html     # Cómo participar
├── comentarios.html    # Canal de comentarios y preguntas de QA
├── 404.html            # Error; rutas absolutas /nodo-subdere/…
└── assets/
    ├── styles.css
    ├── data.js         # Semilla del catálogo = maqueta del modelo Django
    ├── favicon.svg
    └── og.png
```

El detalle de páginas, campos del modelo y preguntas para el QA está en [`docs/maqueta.md`](../docs/maqueta.md).
