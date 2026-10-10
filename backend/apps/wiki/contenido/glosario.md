## Las palabras del nodo, explicadas una sola vez

Aquí están las palabras que usamos en más de una página. Cuando una aparece subrayada con puntos en otra parte del sitio, el enlace trae hasta aquí.

### API

Una dirección en internet a la que un sistema le pide datos y recibe la respuesta al instante, sin que ninguna persona tenga que intervenir. Es la forma en que dos sistemas se hablan.

El [catálogo de APIs](/apis) reúne las que ofrece el nodo, cada una con su ficha.

[Cómo se usa una API →](/wiki/consumir)

### Aplicación

Una pantalla del [catálogo de servicios](/servicios) que resuelve una tarea concreta, sin instalar nada ni escribir código. Por ejemplo, buscar el código de una comuna o revisar el permiso de circulación de un vehículo.

Cada aplicación le pide los datos a una API del catálogo, con las mismas reglas que cualquier otro sistema. Lo que hace una aplicación lo puede hacer también un sistema conectado.

### Clave Única

La clave con la que las personas se identifican ante el Estado en internet. Es la forma en que una persona entra al nodo; los sistemas, en cambio, entran con una [credencial](/wiki/glosario#credencial).

### Comprobante

El registro que queda cuando un municipio entrega un informe: qué se envió, cuándo, a quién y con qué versión de las reglas se revisó.

Lo emite el servicio que recibe la entrega, y se consulta después en el mismo lugar para todos los intercambios.

[Ver el recorrido de una entrega →](/wiki/recorrido)

### Credencial

La identificación con la que un sistema pide datos a nombre de un municipio. Con ella, el sistema le pide a la [puerta de acceso](/wiki/glosario#puerta-de-acceso) un permiso de entrada que dura poco y se renueva cada vez.

Se entrega cuando el municipio acepta los [Términos y Condiciones](/wiki/glosario#terminos-y-condiciones) con SUBDERE. Sin ella no se trabaja con datos reales.

**Estado:** por definir.

### Estándar

También le decimos **contrato** y, en lenguaje técnico, **especificación**.

La descripción publicada de antemano de qué se entrega o se pide en un intercambio, y en qué forma. Está escrita para que la entienda tanto una persona como un programa, y así se puede revisar automáticamente si un sistema la cumple.

Cada versión queda registrada y ninguna se corrige: si algo cambia, se publica una nueva. El catálogo muestra el estándar tal como lo entregó su responsable, sin editarlo.

::: tecnico
**Para quien programa:** los intercambios por internet se describen en OpenAPI; el contenido de un informe, en JSON Schema.
:::

[Cómo cambian las versiones →](/wiki/conectar#lo-que-ya-funciona-no-se-rompe-de-un-dia-para-otro)

### Nodo

Tiene dos sentidos en el sitio:

**El Nodo SUBDERE** es el punto donde se cruzan los intercambios entre los municipios y otras instituciones. Publica el estándar de cada uno y los ofrece por una sola puerta.

**Un nodo**, en minúscula, es cada intercambio del catálogo de APIs, con su ficha. Cuando una ficha dice «este nodo», habla de ese intercambio.

### Procedencia

El apartado de cada ficha que dice de dónde sale el contrato: quién responde por él, dónde está la versión que rige y si lo que muestra el catálogo es una copia exacta, una foto tomada en una fecha, una propuesta nuestra o nada más que un enlace.

[Qué significa cada etiqueta →](/wiki/ficha#cuanto-se-le-puede-creer-a-lo-que-muestra-el-catalogo)

### Puerta de acceso

El nombre es provisional. También se le dice **Plataforma de Control**.

El único camino por el que un sistema o una persona llega a una API del catálogo. Revisa quién pide, cuánto puede pedir y deja constancia.

Tiene dos partes. Una sabe **quién es cada municipio o sistema** y le entrega un permiso temporal. La otra **revisa ese permiso en cada pedido**, limita cuánto se puede pedir y lo anota. Las personas entran con [Clave Única](/wiki/glosario#clave-unica) y los sistemas con una [credencial](/wiki/glosario#credencial) del municipio; los dos pasan por aquí, y nadie tiene atajos.

No decide nada sobre el contenido: revisar lo que se envía, devolver observaciones y emitir el comprobante lo hace cada servicio. Tampoco es la base común del SGM: esa es la base del sistema, y esta controla quién entra.

**Estado:** diseñada, no construida.

[Ver el paso por la puerta →](/wiki/recorrido) · [Leer la nota técnica →](https://github.com/JaimeHernandezE/nodo-subdere/blob/main/docs/plataforma-control.md)

### Servicio

Tiene dos sentidos en el sitio:

**El servicio detrás de una API** es el sistema que atiende ese intercambio: revisa lo que se le envía, devuelve observaciones, recibe la entrega y emite el comprobante, o responde cuando le preguntan.

**La pestaña «Servicios»** reúne [aplicaciones](/wiki/glosario#aplicacion): pantallas que usan esos servicios.

::: aviso
Por discutir con el equipo: una opción para evitar la confusión es renombrar la pestaña a «Aplicaciones».
:::

### SGM

**Sistema de Gestión Municipal.**

El sistema para municipios que desarrolla SUBDERE. Es el primer sistema conectado al nodo y el primero en cumplir sus estándares, así que sirve de referencia: con él comprobamos que cada estándar funciona antes de que se conecten otros.

No tiene atajos: entra por la misma [puerta](/wiki/glosario#puerta-de-acceso) que el sistema de cualquier municipio o proveedor.

[Conocer el SGM →](https://jaimehernandeze.github.io/sgm-nueva-arquitectura/)

### Términos y Condiciones

En el sitio también aparece como **Uso de Términos y Condiciones**.

Lo que un municipio acepta con SUBDERE para trabajar con sus datos reales a través del nodo. Al aceptarlo recibe una [credencial](/wiki/glosario#credencial) a su nombre. Para practicar con datos inventados no hace falta.

**Estado:** por definir. Todavía no está redactado.

### Zona de práctica

En lenguaje técnico, **sandbox**.

Un espacio con datos inventados donde cualquiera puede probar un servicio sin pedir permiso ni aceptar Términos y Condiciones. La idea es que cada servicio publicado tenga el suyo, y que responda igual que el real.

No es lo mismo que el ambiente de pruebas que hoy tienen algunas fichas, como la del CUT o la de permisos de circulación: esos funcionan dentro del navegador y sirven para conocer el contrato, no para conectar un sistema.

**Estado:** por construir. Todavía no existe ninguna.
