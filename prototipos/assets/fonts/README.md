# Tipografía gobCL

El Kit Gráfico de Gobierno define **gobCL** para titulares (en Bold) y **Museo Sans**
para cuerpo de texto. Museo Sans es comercial, así que el sitio usa una pila de
sistema para el cuerpo y reserva gobCL para los titulares.

Para activarla, dejar en esta carpeta:

    gobCL-Regular.woff2
    gobCL-Bold.woff2

Las `@font-face` ya están declaradas en `../styles.css`. Sin los archivos el sitio
cae en la pila de respaldo y no se rompe nada: los titulares se ven en la
tipografía de sistema.

Los archivos vienen del Kit Digital de Gobierno: <https://framework.digital.gob.cl>
