## Que todos los sistemas llamen igual a cada comuna

El Código Único Territorial —el CUT— es el número con el que el Estado identifica cada región, provincia y comuna del país. Casi todo intercambio entre un municipio y una institución empieza por dejar claro de qué comuna se habla. Si cada sistema tiene su propia lista, con sus abreviaturas y sus nombres escritos a su manera, los datos no calzan aunque todo lo demás esté bien.

Aquí explicamos cómo se arma el código, qué norma lo fija y qué conviene revisar antes de usarlo. La ficha técnica está en el [catálogo de APIs](/apis), y para buscar un código sin programar está el [buscador de códigos territoriales](/servicios/buscador-cut).

## Con el número de una comuna ya sabes su provincia y su región

El código de una comuna empieza con el de su provincia, y el de la provincia empieza con el de su región. Mirando solo el número se sabe dónde queda, sin consultar nada más.

| Nivel | Dígitos | Cómo se forma | Ejemplo |
|---|---|---|---|
| **Región** | 2 | Código propio | `13` — Metropolitana de Santiago |
| **Provincia** | 3 | Región + 1 dígito | `131` — Santiago |
| **Comuna** | 5 | Provincia + 2 dígitos | `13101` — Santiago |

::: aviso
**Los ceros a la izquierda son parte del código.** Iquique es `01101`, no `1101`. Las regiones 1 a 9 llevan cero delante, y si un sistema guarda el código como número, el cero desaparece. Es la primera causa de que dos listas de comunas no calcen.
:::

## Qué norma lo fija

**Qué leímos:** la página de SUBDERE que publica los códigos y el documento de códigos que esa página enlaza. **No leímos el texto de los decretos.** Antes de citar esto fuera del equipo, conviene cotejarlo con el Diario Oficial.

| Norma | Qué hace | Estado de la verificación |
|---|---|---|
| **Decreto Supremo N° 1.439**, de 2000 | Determina el sistema de codificación territorial, según consigna el documento de códigos publicado por SUBDERE. | Referencia leída, texto no |
| **Decreto Exento N° 1.115**, del Ministerio del Interior y Seguridad Pública, publicado en el Diario Oficial el 21 de septiembre de 2018 | Establece las abreviaturas de las regiones y unifica los códigos territoriales, incorporando la región de Ñuble con sus provincias y comunas. Es la base de la versión vigente, conocida como **CUT 2018**. | Referencia leída, texto no |

En la práctica: **el CUT tiene versiones, y la versión importa.** Cuando se crea una región o una comuna, los códigos cambian y las listas anteriores quedan desactualizadas. Un sistema que guarda códigos sin anotar de qué versión los sacó no puede reconstruir después qué quiso decir.

## Comuna no es lo mismo que municipio

La comuna es el territorio; la municipalidad es la institución que lo administra. Casi siempre hay una por cada comuna, pero no siempre: algunas comunas no tienen municipalidad propia y las administra la de otra comuna.

Por eso las cifras no coinciden, y las dos son correctas según qué se cuente. La especificación del servicio trae como ejemplo `346` comunas; los programas de SUBDERE trabajan habitualmente con **345 municipalidades**. Un sistema que use el CUT como lista de municipios va a tener una fila que no le calza, y no es un error de datos.

::: aviso
El primer intercambio que usa este estándar es la [consulta de permisos de circulación](/wiki/permisos-de-circulacion): identifica a la municipalidad que cobró por su código de comuna, en vez de escribir el nombre a mano.
:::

::: aviso
**Para quien construye un sistema:** si necesitas el territorio —dónde ocurrió algo, a qué comuna corresponde un domicilio—, el CUT es la lista correcta. Si necesitas la institución que responde —quién entrega el informe, quién firma—, hace falta además un registro de municipalidades, que es otra cosa y todavía no está en el catálogo.
:::

## Qué se le puede pedir

Al servicio solo se le consultan datos; no se le envía nada. Se le puede pedir la lista de regiones, provincias o comunas, lo que hay dentro de cada una, y una comuna con su provincia y su región de una sola vez.

| Para qué | Dirección | Qué entrega |
|---|---|---|
| **Regiones** | `GET /regiones` | Todas las regiones, con código y nombre |
|  | `GET /regiones/{id}/provincias` · `GET /regiones/{id}/comunas` | Lo que hay dentro de una región. La lista de comunas incluye la provincia de cada una |
| **Provincias** | `GET /provincias` | Todas las provincias |
|  | `GET /provincias/{id}` · `GET /provincias/{id}/comunas` | El detalle de una provincia, con su región, y sus comunas |
| **Comunas** | `GET /comunas` | Todas las comunas, con código y nombre |
|  | `GET /comunas/{id}/full` | Una comuna con su provincia y su región, sin tener que hacer tres consultas |
| **Estado del servicio** | `GET /healthz` · `GET /readyz` | Si el servicio está funcionando, y si alcanzó a cargar los códigos |

- **Lo más usado es pedir una comuna completa.** Para eso existe `/comunas/{id}/full`: entrega la comuna con su provincia y su región en una sola respuesta.
- **Las dos últimas direcciones son para quien opera el servicio.** `healthz` y `readyz` dicen si está funcionando; un sistema que solo pide datos no las necesita en su trabajo normal.
- **Actualizar el CUT es reiniciar el servicio con un archivo nuevo.** Los códigos se cargan desde un archivo al encender el servicio, sin base de datos. Eso lo hace rápido y simple.

[Ver la especificación completa](/apis/cut) · [Abrir el buscador](/servicios/buscador-cut)

## Cinco cosas que conviene corregir en la especificación

Son observaciones nuestras sobre la versión de referencia, no fallas del servicio en funcionamiento. Las ponemos aquí y no en el catálogo de APIs a propósito: el catálogo publica el contrato tal como se entregó, sin editarlo, y la conversación sobre él ocurre en la wiki.

::::: tarjetas
:::: tarjeta
**01**

### Los códigos pueden perder el cero inicial

Tal como está escrito, Iquique puede llegar como `1101` en vez de `01101`. Si cada sistema tiene que agregar el cero por su cuenta, alguno no lo va a hacer.

::: tecnico
**Para quien programa:** los identificadores están declarados como `integer`. Declararlos como texto de largo fijo lo resuelve.
:::
::::

:::: tarjeta
**02**

### La respuesta no dice de qué año son los códigos

La descripción dice que es el CUT 2018, pero ninguna respuesta lo indica. Quien guarde estos códigos no puede saber después de qué versión los sacó.

::: tecnico
**Para quien programa:** basta un campo con la versión vigente en cada respuesta.
:::
::::

:::: tarjeta
**03**

### No dice quién puede entrar

El contrato no indica si hay que identificarse. Para datos públicos de solo consulta puede ser a propósito, pero entonces conviene decirlo, porque el resto del sitio explica que todo pasa por la [misma puerta](/wiki/glosario#puerta-de-acceso).

::: tecnico
**Para quien programa:** el contrato no trae esquema de seguridad.
:::
::::

:::: tarjeta
**04**

### Una dirección está escrita distinto a las demás

Una de las direcciones termina en barra y sus vecinas no. Es un detalle, pero obliga a cada sistema a probar las dos formas.

::: tecnico
**Para quien programa:** `/regiones/{id}/` lleva barra final. Los *Lineamientos para el desarrollo de software* de la Secretaría de Gobierno Digital piden no usar barra al final de la URI.
:::
::::

:::: tarjeta
**05**

### No se puede buscar una comuna por nombre

Las listas llegan completas. Para 346 comunas alcanza, pero buscar una comuna por su nombre —lo más frecuente en una pantalla— hoy lo tiene que resolver cada sistema por su lado.

::: tecnico
**Para quien programa:** los mismos lineamientos sugieren parámetros de consulta para filtrar y ordenar.
:::
::::

:::: tarjeta
**06**

### Y una cosa que está bien hecha

El contrato está completo en un solo archivo. Por eso el catálogo lo puede mostrar tal cual, sin armar nada. Suena menor y no lo es: es la diferencia entre publicar un estándar y publicar un enlace a un estándar.

::: tecnico
**Para quien programa:** solo usa referencias internas.
:::
::::
:::::

::: aviso
Ninguna de estas observaciones impide construir con el contrato hoy. Las dos primeras sí conviene resolverlas antes de que alguien guarde códigos en producción, porque corregirlas después obliga a migrar datos.
:::

*Especificación de referencia: Juan Helo, septiembre de 2026 · Códigos: SUBDERE, CUT actualizado a 2018.*
