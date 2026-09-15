# Nodo SUBDERE — maqueta del sitio

Maqueta estática para revisión, previa al desarrollo en Django + React.
Sin build, sin dependencias: se abre con doble clic o se publica tal cual.

## Páginas

| Archivo | Qué es |
|---|---|
| `index.html` | Landing — qué es el nodo y para quién |
| `que-es.html` | Descripción general: cómo funciona, alcance de la validación, los tres casos de municipio |
| `catalogo.html` | Catálogo de nodos, con filtro por ámbito y buscador |
| `nodo.html?id=<slug>` | Ficha de un nodo. Una sola plantilla sirve a los trece |
| `participar.html` | Cómo participar y qué está definido y qué no |
| `comentarios.html` | A quién escribir, cuatro preguntas para el QA y lo que ya sabemos que falta |
| `404.html` | Página de error. Usa rutas absolutas `/nodo-subdere/…` porque se sirve desde cualquier URL — **por eso se ve sin estilos si se abre con doble clic**, y bien una vez publicada |
| `assets/data.js` | **Los datos y el modelo.** Cada campo de aquí debería existir en el modelo Django |
| `assets/styles.css` | Estilos, con la paleta del proyecto en variables CSS |
| `assets/favicon.svg` | Ícono del sitio |
| `assets/og.png` | Imagen de previsualización cuando se comparte el enlace |

Las rutas son todas relativas —salvo las de `404.html`, por lo dicho arriba—, así que el sitio funciona igual en un subdirectorio que en la raíz. Cómo publicarlo está en el [README del repositorio](../README.md).

El catálogo guarda el filtro y la búsqueda en la dirección, así que `catalogo.html?ambito=Pagos` se puede compartir tal cual.

## El modelo del catálogo

`assets/data.js` es la maqueta del modelo. Los campos:

| Campo | Tipo | Nota |
|---|---|---|
| `id` | slug | Clave de la URL de la ficha |
| `nombre` | texto | |
| `ambito` | opción | Justicia local · Pagos · Identidad · Municipal · Transversal |
| `funcion` | texto corto | Una línea, aparece en la tarjeta del catálogo |
| `descripcion` | texto largo | Cuerpo de la ficha |
| `instituciones` | lista | Relación en Django, no texto libre |
| `intercambio` | opción | Bidireccional · El municipio entrega · El municipio consulta · Transversal |
| `madurez` | opción | Deseable · En evaluación · En desarrollo · Operativo |
| `factibilidad` | opción | Por evaluar · Alta · Media · Baja |
| `origen` | texto | De dónde salió el nodo, para poder auditar el catálogo |
| `nota` | texto | Advertencia destacada en la ficha, opcional |

Los dos campos que conviene no dejar para después son **`madurez`** y **`factibilidad`**: agregar una columna a un modelo que ya tiene datos y vistas siempre cuesta más que preverla. María José dejó esa evaluación explícitamente pendiente, y el catálogo es el lugar natural donde vive.

Faltan por definir, y están como bloques «Pendiente» en la ficha: el estándar técnico de cada nodo, sus operaciones y el ambiente de pruebas.

## Datos

Los trece nodos vienen del mapeo de interoperabilidad del Juzgado de Policía Local, enviado por María José Besa el 8 de septiembre de 2026 tras la reunión con el JPL de Lo Barnechea. Los tres últimos los agregó Allison Díaz. Todos están declarados a nivel **deseable**; la evaluación de complejidad y factibilidad está pendiente y el catálogo lo muestra explícitamente.

## Para el QA

Tres preguntas que conviene hacer junto con el enlace, porque son las que definen lo que sigue:

1. ¿El catálogo es la pieza central del sitio, o es un anexo de la descripción del nodo?
2. ¿Qué le falta a la ficha de un nodo para que a una contraparte le sirva de verdad?
3. ¿El sitio es interno de SUBDERE o se abre a municipios y proveedores? Cambia el tono de todo el contenido y el nivel de terminación que necesita.
