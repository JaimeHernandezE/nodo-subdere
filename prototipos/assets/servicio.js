/* Plantilla de la página de un servicio.

   Lo que es texto o dato sale de SERVICIOS (data.js), que es lo que editará
   el mantenedor. La página aporta solo su herramienta, que es código:

     <main data-servicio="buscador-cut">
       <div id="herramienta"> … campo, resultados … </div>
     </main>
     <script src="assets/data.js"></script>
     <script src="assets/servicio.js"></script>
     <script> … lógica de la herramienta … </script>

   Este archivo arma alrededor de la herramienta la cabecera, el panel lateral
   (documentación y estado) y la sección de fuentes, y deja vacío el recuadro
   #estado-fuente para que la herramienta diga si responde en vivo o con datos
   de prueba. Corre al cargarse, antes del script de la página, así que los
   elementos de la herramienta ya están en su lugar cuando ese script los busca.

   Secciones y campos: docs/plantillas.md. */

(function () {
  var main = document.querySelector('main[data-servicio]');
  if (!main || typeof SERVICIOS === 'undefined') return;

  var id = main.getAttribute('data-servicio');
  var s = SERVICIOS.filter(function (x) { return x.id === id; })[0];
  if (!s) return;
  var n = (typeof NODOS !== 'undefined' ? NODOS : []).filter(function (x) { return x.id === s.nodo; })[0];

  function esc(t) {
    return String(t).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  var texto = typeof conTerminos === 'function' ? conTerminos : esc;

  var ESTADO = { 'En construcción': 'tag tag-dev', 'Disponible': 'tag', 'Deseable': 'tag tag-mad' };
  var MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
  function fechaLarga(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || '');
    return m ? (+m[3]) + ' de ' + MESES[+m[2] - 1] + ' de ' + m[1] : '';
  }

  var wiki = s.wiki
    || (n && n.espec && n.espec.procedencia && n.espec.procedencia.observaciones) || null;

  function enlace(url, titulo, detalle) {
    return '<li><a href="' + esc(url) + '"><b>' + esc(titulo) + '</b>'
      + (detalle ? '<span>' + esc(detalle) + '</span>' : '') + '</a></li>';
  }
  var enlaces = ''
    + (n ? enlace('nodo.html?id=' + n.id, 'La API que usa', n.nombre) : '')
    + (n && n.sandbox ? enlace('nodo.html?id=' + n.id + '#probar', 'Probar la API', 'Ambiente de pruebas, en la ficha de la API') : '')
    + (wiki ? enlace(wiki.url, 'Entrada de wiki', wiki.texto) : '');

  var panel = '<div class="ficha-lado">'
    + (enlaces
        ? '<aside class="panel"><p class="panel-tit">Documentación</p><ul class="panel-enlaces">' + enlaces + '</ul></aside>'
        : '')
    + '<aside class="panel"><dl>'
    +   '<dt>Estado</dt><dd><span class="' + (ESTADO[s.estado] || 'tag') + '">' + esc(s.estado) + '</span></dd>'
    +   (s.actualizado ? '<dt>Actualizado por última vez</dt><dd>' + fechaLarga(s.actualizado) + '</dd>' : '')
    + '</dl></aside>'
    + '</div>';

  var fuentes = s.fuentes && s.fuentes.length
    ? '<div class="tabla-ancha"><table>'
      + '<tr><th>Dato</th><th>De dónde viene</th></tr>'
      + s.fuentes.map(function (f) {
          return '<tr><td>' + esc(f.dato) + '</td><td>' + esc(f.origen) + '</td></tr>';
        }).join('')
      + '</table></div>'
    : '';

  var herramienta = document.getElementById('herramienta');

  main.innerHTML =
    '<section style="padding-bottom:10px"><div class="wrap">'
    + '<p class="miga"><a href="catalogo.html">Servicios</a> / ' + esc(s.nombre) + '</p>'
    + '<p class="eyebrow">Servicio</p>'
    + '<h2>' + esc(s.nombre) + '</h2>'
    + '<div class="servicio-grid"><div id="servicio-principal">'
    +   (s.descripcion ? '<p class="lead">' + texto(s.descripcion) + '</p>' : '')
    +   (s.nota ? '<div class="aviso"><p>' + texto(s.nota) + '</p></div>' : '')
    + '</div>' + panel + '</div>'
    + '</div></section>'
    + '<section class="gris"><div class="wrap">'
    + '<p class="eyebrow">De dónde salen estos datos</p>'
    + '<h2>Quién genera cada dato</h2>'
    + (s.fuentes_intro ? '<p class="lead">' + texto(s.fuentes_intro) + '</p>' : '')
    + fuentes
    + '<div class="aviso" id="estado-fuente"></div>'
    + '</div></section>';

  if (herramienta) document.getElementById('servicio-principal').appendChild(herramienta);
})();
