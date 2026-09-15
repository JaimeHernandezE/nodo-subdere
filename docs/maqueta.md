# Nodo SUBDERE — maqueta del sitio

Maqueta estática para revisión, previa al desarrollo en Django + React.
Sin build, sin dependencias: vive en [`prototipos/`](../prototipos/). Se abre con doble clic o se publica tal cual.

## Páginas

| Archivo | Qué es |
|---|---|
| `prototipos/index.html` | Landing — qué es el nodo y para quién |
| `prototipos/que-es.html` | Descripción general: cómo funciona, alcance de la validación, los tres casos de municipio |
| `prototipos/catalogo.html` | Catálogo de nodos, con filtro por ámbito y buscador |
| `prototipos/nodo.html?id=<slug>` | Ficha de un nodo. Una sola plantilla sirve a los diez |
| `prototipos/participar.html` | Cómo participar y qué está definido y qué no |
| `prototipos/comentarios.html` | A quién escribir, cuatro preguntas para el QA y lo que ya sabemos que falta |
| `prototipos/404.html` | Página de error. Usa rutas absolutas `/nodo-subdere/…` porque se sirve desde cualquier URL — **por eso se ve sin estilos si se abre con doble clic**, y bien una vez publicada |
| `prototipos/assets/data.js` | **Los datos y el modelo.** Cada campo de aquí debería existir en el modelo Django |
| `prototipos/estandares/` | Las especificaciones registradas, tal cual las publica cada nodo |
| `prototipos/assets/openapi.js` | Renderiza una especificación OpenAPI en la ficha. Nada de lo que se ve ahí está transcrito |
| `prototipos/assets/js-yaml.min.js` | Lector de YAML, incluido para no depender de la red |
| `prototipos/assets/styles.css` | Estilos, con la paleta del proyecto en variables CSS |
| `prototipos/assets/favicon.svg` | Ícono del sitio |
| `prototipos/assets/og.png` | Imagen de previsualización cuando se comparte el enlace |

Las rutas son todas relativas —salvo las de `404.html`, por lo dicho arriba—, así que el sitio funciona igual en un subdirectorio que en la raíz. Cómo publicarlo está en el [README del repositorio](../README.md).

El catálogo guarda el filtro y la búsqueda en la dirección, así que `catalogo.html?ambito=Pagos` se puede compartir tal cual.

## El modelo del catálogo

`prototipos/assets/data.js` es la maqueta del modelo. Los campos:

| Campo | Tipo | Nota |
|---|---|---|
| `id` | slug | Clave de la URL de la ficha |
| `nombre` | texto | |
| `ambito` | opción | Transversal · Juzgado de Policía Local · Pagos · Municipal |
| `funcion` | texto corto | Una línea, aparece en la tarjeta del catálogo |
| `descripcion` | texto largo | Cuerpo de la ficha |
| `instituciones` | lista | Relación en Django, no texto libre |
| `intercambio` | opción | Bidireccional · El municipio entrega · El municipio consulta · Transversal |
| `madurez` | opción | Deseable · En evaluación · En desarrollo · Operativo |
| `factibilidad` | opción | Por evaluar · Alta · Media · Baja |
| `origen` | texto | De dónde salió el nodo, para poder auditar el catálogo |
| `nota` | texto | Advertencia destacada en la ficha, opcional |

Los dos campos que conviene no dejar para después son **`madurez`** y **`factibilidad`**: agregar una columna a un modelo que ya tiene datos y vistas siempre cuesta más que preverla. María José dejó esa evaluación explícitamente pendiente, y el catálogo es el lugar natural donde vive.

### El contrato técnico, cuando existe

Dos campos más, opcionales. Un nodo que no los trae muestra el bloque «Pendiente» correspondiente en su ficha. Hoy solo `division-territorial` los tiene.

| Campo | Tipo | Nota |
|---|---|---|
| `espec` | objeto | `{ archivo, formato, validador, registrada, origen, acceso }` |
| `pruebas` | texto | Estado del ambiente de pruebas |

**No hay un campo `operaciones`, y es deliberado.** `espec.archivo` apunta a la especificación legible por máquina del nodo, y la ficha la lee y la renderiza cada vez que se abre. Las operaciones, sus parámetros, sus códigos de respuesta y sus ejemplos salen del archivo; el catálogo no guarda una copia. La decisión está en [`adr-2026-09-estandar-legible-por-maquina.md`](adr-2026-09-estandar-legible-por-maquina.md).

En el modelo Django, `espec` es un documento versionado —cada versión se registra, ninguna se corrige— y **se versiona aparte de la ficha**: el contrato puede cambiar sin que cambie la descripción del nodo, y al revés.

Las especificaciones registradas viven en [`prototipos/estandares/`](../prototipos/estandares/). El renderizador es [`prototipos/assets/openapi.js`](../prototipos/assets/openapi.js), y [`js-yaml.min.js`](../prototipos/assets/js-yaml.min.js) viene junto para no depender de la red.

**Una consecuencia práctica:** la ficha de un nodo con especificación **no funciona abriendo el archivo con doble clic**, porque el navegador no permite que una página local lea otro archivo del disco. La página lo explica cuando ocurre. Para verla hay que servir la carpeta.

## Datos

Nueve de los diez nodos vienen del mapeo de interoperabilidad del Juzgado de Policía Local, enviado por María José Besa el 8 de septiembre de 2026 tras la reunión con el JPL de Lo Barnechea. Algunos de esa lista los agregó Allison Díaz. Todos están declarados a nivel **deseable**; la evaluación de complejidad y factibilidad está pendiente y el catálogo lo muestra explícitamente.

### Cuatro nodos del mapeo que no están en el catálogo

El mapeo traía trece. Cuatro se retiraron el 15 de septiembre de 2026: **Registro Civil, Transportes, Obras Públicas (multas TAG) y Carabineros y Gendarmería**.

Los cuatro son consultas del municipio a otro órgano de la Administración del Estado, que es exactamente lo que resuelve la Plataforma Integrada de Servicios Electrónicos del Estado. Publicarlos como nodos del catálogo habría presentado al Nodo SUBDERE como una plataforma paralela a PISEE, que no es lo que se quiere construir — y sería incoherente con el precedente que el propio proyecto adoptó: el [Nodo Laboral y Previsional](nodo-lp-precedente.md) se montó sobre PISEE 2.0 en vez de construir transporte propio.

Se retiran del catálogo, no del levantamiento: siguen siendo intercambios reales que el juzgado necesita. Lo que cambia es quién los provee.

**Queda pendiente verificar si PISEE alcanza hoy a los municipios en la práctica**, no solo en la ley. Si no los alcanza, la decisión habría que revisarla.

El décimo, **División Político-Administrativa**, no viene del mapeo. Es un prototipo levantado sobre el repositorio `utilitarios` del equipo SEM de SUBDERE: una API Flask de regiones, provincias y comunas que ya opera dentro de esa infraestructura, con especificación OpenAPI 3.0.3. Está en el catálogo para mostrar cómo se ve una ficha cuando el estándar existe, y es el único que llena los tres bloques que en los demás dicen «Pendiente».

Que su ficha publique el estándar no significa que el nodo esté disponible: el servicio responde solo dentro de la red de SEM y no tiene nivel de servicio comprometido. La ficha lo dice explícitamente en su nota.

## Para el QA

Tres preguntas que conviene hacer junto con el enlace, porque son las que definen lo que sigue:

1. ¿El catálogo es la pieza central del sitio, o es un anexo de la descripción del nodo?
2. ¿Qué le falta a la ficha de un nodo para que a una contraparte le sirva de verdad?
3. ¿El sitio es interno de SUBDERE o se abre a municipios y proveedores? Cambia el tono de todo el contenido y el nivel de terminación que necesita.
