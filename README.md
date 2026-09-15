# Nodo SUBDERE

Repositorio del Nodo SUBDERE: el punto único por el que un municipio entrega información a las instituciones que se la piden, y recibe constancia de lo entregado.

Acá se documenta, se prototipa y —más adelante— se construye. Hoy contiene la **maqueta del sitio**, que es una pieza de conversación: existe para que las observaciones sean sobre algo concreto y no sobre lo que cada uno se imaginó.

**Sitio publicado:** https://jaimehernandeze.github.io/nodo-subdere/

---

## Qué hay en este repositorio

| Ruta | Qué es |
|---|---|
| `index.html` y demás `.html` | La maqueta del sitio. HTML, CSS y JS a mano, sin build ni dependencias |
| `assets/` | Estilos, datos semilla, ícono e imagen de previsualización |
| `docs/` | Documentación del nodo |

La maqueta está en la raíz porque así GitHub Pages la publica sin configuración. **Cuando entren el backend y el frontend**, la maqueta se mueve a una carpeta propia y el despliegue pasa a un workflow de Actions — es un commit de migración, no un rediseño.

## Documentación

| Documento | Qué contiene |
|---|---|
| [`docs/maqueta.md`](docs/maqueta.md) | Las páginas de la maqueta, el modelo de datos del catálogo y las preguntas para el QA |
| [`docs/nodo-lp-precedente.md`](docs/nodo-lp-precedente.md) | El Nodo Laboral y Previsional de la Subsecretaría de Previsión Social, en operación desde noviembre de 2025: qué se copia, qué no, y qué advertencias deja |

## Ver la maqueta sin publicarla

Doble clic en `index.html` basta para todo salvo `404.html`, que usa rutas absolutas porque se sirve desde cualquier URL y por eso se ve sin estilos en local. Para verlo tal cual quedará:

```bash
python3 -m http.server 8000
# http://localhost:8000
```

## Publicar

```bash
git add .
git commit -m "Maqueta del sitio del Nodo SUBDERE"
git push -u origin main
```

Después, en GitHub: **Settings → Pages → Source: Deploy from a branch → Branch: `main` / `(root)`**. Queda publicado en un par de minutos.

---

## Estado

Maqueta para revisión, septiembre de 2026. Nada de lo que muestra está comprometido institucionalmente.

Los trece nodos del catálogo vienen del mapeo de interoperabilidad del Juzgado de Policía Local y están declarados a nivel **deseable**: la evaluación de complejidad y factibilidad está pendiente, y el catálogo lo muestra en vez de esconderlo.

Comentarios a jaime.hernandez@subdere.gov.cl — División de Políticas y Estudios, SUBDERE.
