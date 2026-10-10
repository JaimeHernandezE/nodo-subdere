## Saber de un vistazo si una API ya se puede usar

Cada API del [catálogo](/apis) tiene una tarjeta y una ficha. Las etiquetas de colores responden tres preguntas: si está funcionando ahora, de dónde sale su contrato y cómo se entra.

## La disponibilidad la mide una máquina, no la escribimos a mano

El indicador sale de un monitor que revisa el servicio cada cierto tiempo. Si una API no tiene monitoreo, la tarjeta lo dice en vez de suponer que funciona.

| Indicador | Qué quiere decir |
|---|---|
| **Disponible** | El monitor lo encontró respondiendo en su última revisión. Al pasar el cursor se ve cuándo fue y qué porcentaje del tiempo funcionó en los últimos 30 días. |
| **Degradado** | Responde, pero lento o con errores en parte de las consultas. |
| **Caído** | No respondió en la última revisión. |
| **Solo red interna** | El servicio existe, pero solo responde dentro de la red de SUBDERE. Desde fuera no se puede usar ni medir. |
| **Sin monitoreo** | Todavía no hay un servicio que medir, o no está conectado al monitor. |

## Cuánto se le puede creer a lo que muestra el catálogo

No siempre escribimos nosotros el contrato de una API. Por eso cada ficha tiene un apartado de **procedencia**: quién responde por el contrato, dónde está la versión que rige y qué relación tiene con lo que se ve en el catálogo.

| Etiqueta | Qué quiere decir |
|---|---|
| **Copia exacta** | Lo que se ve es el mismo contrato que entregó el responsable, sin cambios. |
| **Instantánea** | Una foto del contrato tomada en una fecha. La versión oficial puede haber cambiado después. |
| **Propuesta reconstruida** | La escribimos nosotros a partir de lo que nos entregaron. Sirve para conversar, pero no es el contrato oficial. |
| **Sin copia en el catálogo** | El catálogo no guarda el archivo, a propósito, para que no se desactualice. Hay que ir a la fuente oficial que indica la ficha. |

Las diferencias y las preguntas abiertas sobre cada contrato no se escriben dentro de él: van en su entrada de esta wiki, y la ficha enlaza a ella en «Observaciones». Todas las entradas están en el [índice de intercambios](/wiki#intercambios).

## Quién puede pedirle datos

La tarjeta resume en una etiqueta cómo se entra, y la ficha lo explica con detalle en «Quién puede usarlo».

| Etiqueta | Qué quiere decir |
|---|---|
| **Abierto** | No hay que identificarse para consultar. |
| **Con credencial** | El sistema que pide los datos se identifica con una [credencial](/wiki/glosario#credencial) del municipio. |
| **Clave Única** | Una persona entra con su [Clave Única](/wiki/glosario#clave-unica). |

Dos etiquetas más aparecen junto a la de acceso:

- **OpenAPI** o **Sin contrato**: si el contrato ya está publicado, y en qué formato. OpenAPI es un formato estándar para describir APIs, que leen tanto personas como programas.
- **Se puede probar**: la ficha tiene un ambiente de pruebas que responde con datos inventados. Funciona dentro del navegador, así que se puede practicar sin tocar datos reales.

::: aviso
El ambiente de pruebas de una ficha no es la [zona de práctica](/wiki/glosario#zona-de-practica) del nodo, que todavía no existe. Qué se puede hacer hoy y qué falta está en [conectar un sistema](/wiki/conectar).
:::
