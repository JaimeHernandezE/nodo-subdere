# Nodo SUBDERE

Repositorio del Nodo SUBDERE: el catálogo de estándares e intercambios del dominio municipal, las pantallas que los usan y la documentación de cómo funcionan.

Es un monorepo. Contiene la maqueta que sirve para conversar, el código de producto, y las decisiones que llevaron de una a otro.

**Maqueta publicada:** https://jaimehernandeze.github.io/nodo-subdere/

---

## Qué hay acá

| Ruta | Qué es | Estado |
|---|---|---|
| [`prototipos/`](prototipos/) | La maqueta del sitio. HTML, CSS y JS a mano, sin build ni dependencias | En uso. Es la referencia de contenido y diseño |
| [`backend/`](backend/) | API en Django: catálogos, wiki y adaptadores a servicios externos | Estructura inicial |
| [`frontend/`](frontend/) | El sitio en React | Estructura inicial |
| [`docs/`](docs/) | Decisiones, notas técnicas y la memoria del proyecto | En uso |

**La maqueta no se retira cuando llegue el código.** Cumple una función que el producto no cumple: permite proponer una pantalla y discutirla en el mismo día, sin migraciones ni despliegues. Mientras siga sirviendo para eso, se queda. Cada README dice qué toma de ella.

---

## Las tres piezas del sitio

La barra superior del sitio separa tres usos que conviene no mezclar:

| | Para qué se entra | Ejemplo |
|---|---|---|
| **APIs** | Construir contra un contrato publicado | La especificación del CUT, operación por operación |
| **Servicios** | Resolver una tarea sin programar | Buscar el código de una comuna |
| **Wiki** | Entender cómo se usa y por qué está definido así | Cómo se compone el CUT y qué decreto lo fija |

Hoy hay dos intercambios en el catálogo, y los dos tienen las tres vistas escritas: los **Códigos Únicos Territoriales** y los **permisos de circulación por patente**, este último como demostración con datos inventados.

El catálogo parte corto a propósito: es preferible una entrada completa —contrato, pantalla y entrada de wiki— que una lista larga de intenciones.

---

## Documentación

| Documento | Qué contiene |
|---|---|
| [`docs/hoja-de-ruta.md`](docs/hoja-de-ruta.md) | **Documento rector.** Qué es el nodo, para quién, qué hace, cómo se gobierna y hacia dónde va, con las etapas y todas las preguntas abiertas. De aquí se alimenta el sitio |
| [`docs/maqueta.md`](docs/maqueta.md) | **El documento del sitio.** Las páginas del sitio, el modelo de datos del catálogo, la identidad gráfica, qué describe el sitio y qué no, y las decisiones de cada cambio |
| [`docs/adr-2026-09-estandar-legible-por-maquina.md`](docs/adr-2026-09-estandar-legible-por-maquina.md) | **Decisión.** El estándar de cada nodo se publica como especificación legible por máquina; el catálogo la renderiza y no la transcribe |
| [`docs/adr-2026-10-acceso-directo-primera-etapa.md`](docs/adr-2026-10-acceso-directo-primera-etapa.md) | **Decisión.** La primera etapa consume el CUT y los permisos de circulación directo desde su fuente, sin nodo de la Red, con el contrato escrito en forma PISEE para que migrar sea configuración |
| [`docs/plataforma-control.md`](docs/plataforma-control.md) | **Propuesta.** Quién es quién y control de paso: las dos piezas de la puerta de acceso |
| [`docs/flujo_1.md`](docs/flujo_1.md) · [`docs/flujo_2.md`](docs/flujo_2.md) | Diagramas de la plataforma de control: demostración y producción |
| [`docs/esquemas-de-intercambio.html`](docs/esquemas-de-intercambio.html) | **Los cinco esquemas de intercambio.** Tipo A y tipo B de la minuta de la Red, los precedentes de SICEX y del Nodo Laboral y Previsional, y la puerta de SUBDERE, con la diferencia entre alojar el nodo del municipio y sustituirlo como titular. Se abre en el navegador |
| [`docs/esquemas-de-repositorios.html`](docs/esquemas-de-repositorios.html) | **La organización de los repositorios.** De dónde sale cada ficha, qué publica la aplicación y qué es público. Se abre en el navegador |
| [`docs/nodo-lp-precedente.md`](docs/nodo-lp-precedente.md) | El Nodo Laboral y Previsional de la Subsecretaría de Previsión Social, en operación desde noviembre de 2025: qué se copia, qué no, y qué advertencias deja |

---

## Ver la maqueta

**Conviene servir la carpeta.** El doble clic funciona para casi todo, pero dos cosas no: `404.html` usa rutas absolutas porque se sirve desde cualquier URL, y la ficha de un intercambio con especificación necesita leer un archivo del disco, que el navegador bloquea en páginas locales.

```bash
python -m http.server 8000 --directory prototipos
# http://localhost:8000
```

Las pantallas de servicio consultan APIs externas y, cuando no están alcanzables, funcionan con datos de demostración diciéndolo en pantalla. Para apuntarlas a un servicio real se agrega `?api=` a la dirección.

## Construir el producto

Cada parte tiene sus instrucciones de construcción, pensadas para trabajar con asistencia de IA: [`backend/INSTRUCCIONES.md`](backend/INSTRUCCIONES.md) con el contrato común y el orden de las aplicaciones, un `INSTRUCCIONES.md` por aplicación en `backend/apps/`, y [`frontend/INSTRUCCIONES.md`](frontend/INSTRUCCIONES.md). Lo que no está en ellos no es libertad creativa: es una pregunta abierta, y las preguntas viven en la Parte III de la hoja de ruta.

## Levantar el producto

Cada parte tiene su README con el detalle:

```bash
# backend  → http://localhost:8000
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" && cp .env.example .env && python manage.py migrate && python manage.py runserver

# frontend → http://localhost:5173
cd frontend && npm install && cp .env.example .env.local && npm run dev
```

## Publicar la maqueta

Va a **GitHub Pages** al hacer push a `main`, por el workflow [`.github/workflows/pages-prototipos.yml`](.github/workflows/pages-prototipos.yml). Solo se dispara con cambios en `prototipos/**`, así que tocar el backend o la documentación no redespliega el sitio.

## Espejo en GitLab SUBDERE

GitHub es el origen. GitLab SUBDERE guarda un respaldo que se sobrescribe con `git push --mirror` desde el job `sync_from_github` de [`.gitlab-ci.yml`](.gitlab-ci.yml), por programación o con *Run pipeline*. La maqueta se publica solo en GitHub Pages. En GitLab no se trabaja: lo que se suba directo se pierde en la siguiente sincronización.

## Contribuir

Todo cambio entra por una rama y un Pull Request revisado; nadie hace push directo a `main`. El flujo, las convenciones y las reglas de cada carpeta están en [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Dos reglas que ordenan el proyecto

**Nadie tiene atajos.** Toda pantalla —incluida la nuestra— consume la misma interfaz pública que usaría el sistema de un municipio o de un proveedor. Si una vista de SUBDERE pudiera llegar a datos que la interfaz no expone, el catálogo dejaría de describir lo que de verdad se puede construir.

**La crítica va en la wiki, no en el catálogo.** El catálogo publica cada contrato tal como se entregó, sin editarlo, porque su valor es ser copia fiel y auditable. Las observaciones sobre un contrato viven en su entrada de wiki. Mantener esa separación es lo que permite que el catálogo siga siendo confiable mientras la discusión avanza.

---

## Estado

**Maqueta para revisión, septiembre de 2026.** Nada de lo que muestra está comprometido institucionalmente, y los datos de las pantallas de servicio son inventados.

Backend y frontend tienen su estructura de carpetas y su documentación inicial; todavía no hay código.

Comentarios a jaime.hernandez@subdere.gov.cl — División de Políticas y Estudios, SUBDERE.
