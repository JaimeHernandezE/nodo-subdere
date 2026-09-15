# Nodo SUBDERE

Repositorio del Nodo SUBDERE: el punto único por el que un municipio entrega información a las instituciones que se la piden, y recibe constancia de lo entregado.

Acá se documenta, se prototipa y —más adelante— se construye. Hoy contiene la **maqueta del sitio**, que es una pieza de conversación: existe para que las observaciones sean sobre algo concreto y no sobre lo que cada uno se imaginó.

**Sitio publicado:** https://jaimehernandeze.github.io/nodo-subdere/

---

## Qué hay en este repositorio

| Ruta | Qué es |
|---|---|
| [`prototipos/`](prototipos/) | La maqueta del sitio. HTML, CSS y JS a mano, sin build ni dependencias |
| [`docs/`](docs/) | Documentación del nodo |

Cuando entren el backend y el frontend, la maqueta se queda en `prototipos/` y el código de producto vive en su propia estructura. El despliegue de la maqueta ya corre por un workflow de Actions.

## Documentación

| Documento | Qué contiene |
|---|---|
| [`docs/adr-2026-09-estandar-legible-por-maquina.md`](docs/adr-2026-09-estandar-legible-por-maquina.md) | **Decisión.** El estándar de cada nodo se publica como especificación legible por máquina; el catálogo la renderiza y no la transcribe |
| [`docs/maqueta.md`](docs/maqueta.md) | Las páginas de la maqueta, el modelo de datos del catálogo y las preguntas para el QA |
| [`docs/nodo-lp-precedente.md`](docs/nodo-lp-precedente.md) | El Nodo Laboral y Previsional de la Subsecretaría de Previsión Social, en operación desde noviembre de 2025: qué se copia, qué no, y qué advertencias deja |

## Ver la maqueta sin publicarla

**Conviene servir la carpeta.** El doble clic funciona para casi todo, pero dos cosas no: `404.html` usa rutas absolutas porque se sirve desde cualquier URL, y la ficha de un nodo con especificación necesita leer un archivo del disco, que el navegador bloquea en páginas locales. Ambas se ven bien servidas:

```bash
python -m http.server 8000 --directory prototipos
# http://localhost:8000
```

## Publicar

La maqueta se publica en **GitHub Pages** al hacer push a `main` (workflow [`.github/workflows/pages-prototipos.yml`](.github/workflows/pages-prototipos.yml)).

```bash
git add .
git commit -m "Maqueta del sitio del Nodo SUBDERE"
git push origin main
```

### Activar GitHub Pages (una sola vez)

1. En GitHub: **Settings → Pages**
2. **Build and deployment → Source:** `GitHub Actions`
3. Push a `main` o ejecutar **Actions → Deploy prototipos → Run workflow**
4. Cuando termine en verde: **Settings → Pages** muestra la URL

---

## Estado

Maqueta para revisión, septiembre de 2026. Nada de lo que muestra está comprometido institucionalmente.

Nueve de los diez nodos del catálogo vienen del mapeo de interoperabilidad del Juzgado de Policía Local y están declarados a nivel **deseable**: la evaluación de complejidad y factibilidad está pendiente, y el catálogo lo muestra en vez de esconderlo.

El décimo —división político-administrativa— es un prototipo levantado sobre el repositorio `utilitarios` del equipo SEM, y el único con estándar publicado en su ficha. Está ahí para mostrar a qué debería llegar cada uno de los demás.

El mapeo traía trece nodos: cuatro se retiraron por ser consultas a otros órganos del Estado, que corresponden a PISEE y no a este catálogo. El motivo está en [`docs/maqueta.md`](docs/maqueta.md).

Comentarios a jaime.hernandez@subdere.gov.cl — División de Políticas y Estudios, SUBDERE.
