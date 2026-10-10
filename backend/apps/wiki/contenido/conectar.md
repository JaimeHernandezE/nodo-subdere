## Conectarse sin cambiar de sistema

Al nodo no le importa quién hizo el sistema del municipio, solo que cumpla lo publicado. Aquí explicamos qué se puede hacer hoy para conectarse, qué falta y qué pasa cuando cambian las reglas.

## Cómo se conecta un sistema, hoy y más adelante

::::: tarjetas
:::: tarjeta
**A**

### El SGM, sistema de referencia

El [SGM](/wiki/glosario#sgm) es el primer sistema de gestión municipal conectado al nodo y el primero en cumplir sus estándares. Con él comprobamos que cada estándar funciona antes de que se conecten otros sistemas.
::::

:::: tarjeta
**B**

### Un municipio con otro sistema

Lo publicado es público y cualquiera puede construir a partir de ahí: el proveedor del municipio o su propio equipo de informática. Para trabajar con datos reales hacen falta los [Términos y Condiciones](/wiki/glosario#terminos-y-condiciones) y la [credencial](/wiki/glosario#credencial).
::::

:::: tarjeta
**C**

### Cuando sale una versión nueva

Cada API informa en su propio contrato su versión, su fecha de publicación y el plazo de gracia vigente. Cuando sale una versión nueva, la anterior sigue funcionando hasta que vence ese plazo, así cada sistema sabe cuánto tiempo tiene para actualizarse sin cortar sus entregas. [Más sobre versiones](/wiki/conectar#lo-que-ya-funciona-no-se-rompe-de-un-dia-para-otro).
::::
:::::

## Qué hacer para conectar tu sistema

1. **Busca el intercambio en el [catálogo de APIs](/apis).** Cada tarjeta dice qué entrega, cómo se entra y si está funcionando; qué significa cada etiqueta está en [cómo leer una ficha](/wiki/ficha).
1. **Lee la ficha.** Dice qué entrega el servicio, qué se le puede pedir, de qué otros módulos depende y cómo se entra.
1. **Descarga el contrato.** Es el archivo que describe qué se puede pedir y qué se recibe, en un formato que leen los programas. Se abre tal cual en herramientas de prueba como Postman o Insomnia.
1. **Practica donde se pueda.** Algunas fichas tienen un ambiente de pruebas que responde con datos inventados, dentro del mismo navegador.
1. **Para trabajar con datos reales**, el municipio acepta los Términos y Condiciones con SUBDERE y recibe una credencial a su nombre.

::: aviso
El último paso todavía no se puede dar: los Términos y Condiciones no están redactados y la [puerta de acceso](/wiki/glosario#puerta-de-acceso) que revisa la credencial está diseñada, pero no construida.
:::

## Un espacio para practicar y otro para trabajar de verdad

Lo que el servicio promete entregar es lo mismo en los dos; cambian los datos y el permiso que hace falta.

|  | Para practicar | Para trabajar de verdad |
|---|---|---|
| **Quién** | Cualquiera que esté construyendo un sistema | El municipio, o el sistema que él autorice |
| **Con qué datos** | Datos inventados; ninguno de un municipio real | Los datos del municipio que autorizó |
| **¿Hace falta aceptar Términos y Condiciones?** | No | Sí, con SUBDERE |
| **Permiso** | Abierto o de prueba, según el servicio | Una credencial a nombre del municipio, que se entrega al aceptar los Términos y Condiciones |

::: aviso
**La [zona de práctica](/wiki/glosario#zona-de-practica) todavía no existe.** La idea es que cada servicio publicado tenga una, con datos inventados, para construir sin pedir permiso. Los ambientes de prueba que hoy tienen las fichas del [CUT](/apis/cut) y de [permisos de circulación](/apis/permisos-de-circulacion) funcionan dentro del navegador y sirven para conocer el contrato, no para conectar un sistema.
:::

## Lo que ya funciona no se rompe de un día para otro

Cada contrato publicado queda registrado con su versión. Eso significa:

- **Ninguna versión se borra ni se corrige.** Si algo cambia, registramos una versión nueva.
- **Siempre se sabe cuál rige**, y se puede ver qué cambió entre una y otra.
- **La API lo dice sola.** Cada API publicada informa, dentro de su propio contrato, su versión, su fecha de publicación y el plazo de gracia vigente.
- **Quienes estén conectados reciben aviso con antelación**, y la versión anterior sigue funcionando durante un período de gracia.

::: aviso
Por definir: qué cambio obliga a una versión mayor, cómo se avisa a quienes están conectados y cuánto dura el período de gracia. Es la política de versionado que la nota de arquitectura deja pendiente (X-109).
:::

[Ver las decisiones de arquitectura →](/wiki/decisiones)
