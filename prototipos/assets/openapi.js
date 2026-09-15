/* Renderiza una especificación OpenAPI 3.x como bloque de ficha.

   Este archivo es la razón de ser del ADR 2026-09: el catálogo no guarda las
   operaciones de un nodo, guarda su especificación y la proyecta. Si algo de
   lo que se ve en la ficha no sale de acá, es una transcripción y está mal.

   Depende de js-yaml, que viene junto en assets/ para no depender de la red. */

var OpenAPI = (function () {

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  // ---- resolución de $ref, solo punteros internos ----
  function deref(doc, nodo, visto) {
    visto = visto || {};
    if (!nodo || typeof nodo !== 'object') return nodo;
    if (!nodo.$ref) return nodo;
    if (visto[nodo.$ref]) return {};            // corta ciclos
    visto[nodo.$ref] = true;
    var partes = nodo.$ref.replace(/^#\//, '').split('/');
    var dest = doc;
    for (var i = 0; i < partes.length; i++) {
      dest = dest && dest[partes[i]];
      if (dest === undefined) return {};
    }
    return deref(doc, dest, visto);
  }

  // ---- ejemplo derivado del propio esquema ----
  function ejemplo(doc, esquema, prof) {
    prof = prof || 0;
    if (prof > 8) return null;
    var s = deref(doc, esquema);
    if (!s || typeof s !== 'object') return null;
    if ('example' in s) return s.example;
    if (s.type === 'array') return [ejemplo(doc, s.items, prof + 1)];
    if (s.properties) {
      var o = {};
      Object.keys(s.properties).forEach(function (k) {
        o[k] = ejemplo(doc, s.properties[k], prof + 1);
      });
      return o;
    }
    if (s.type === 'integer' || s.type === 'number') return 0;
    if (s.type === 'boolean') return true;
    if (s.type === 'string') return '';
    return null;
  }

  function tipo(doc, esquema) {
    var s = deref(doc, esquema);
    if (!s) return '';
    if (s.type === 'array') return 'lista de ' + (tipo(doc, s.items) || 'objetos');
    if (s.properties || s.type === 'object') return 'objeto';
    return s.type || '';
  }

  // ---- operaciones agrupadas según el orden de tags del documento ----
  function agrupa(doc) {
    var orden = (doc.tags || []).map(function (t) { return t.name; });
    var grupos = {};
    Object.keys(doc.paths || {}).forEach(function (ruta) {
      var item = doc.paths[ruta];
      Object.keys(item).forEach(function (metodo) {
        if (['get', 'post', 'put', 'patch', 'delete', 'head', 'options'].indexOf(metodo) < 0) return;
        var op = item[metodo];
        var tag = (op.tags && op.tags[0]) || 'Otras';
        if (orden.indexOf(tag) < 0) orden.push(tag);
        (grupos[tag] = grupos[tag] || []).push({ ruta: ruta, metodo: metodo, op: op });
      });
    });
    return orden.filter(function (t) { return grupos[t]; })
                .map(function (t) { return { tag: t, ops: grupos[t] }; });
  }

  // ---- una operación, desplegable ----
  function operacion(doc, o) {
    var params = (o.op.parameters || []).map(function (p) { return deref(doc, p); });

    var tablaParams = params.length
      ? '<h4>Parámetros</h4><div class="tabla-ancha"><table>'
        + '<tr><th>Nombre</th><th>Dónde</th><th>Tipo</th><th>Obligatorio</th></tr>'
        + params.map(function (p) {
            return '<tr><td><code>' + esc(p.name) + '</code></td>'
              + '<td>' + esc(p['in'] === 'path' ? 'en la ruta' : p['in'] === 'query' ? 'en la consulta' : p['in']) + '</td>'
              + '<td>' + esc(tipo(doc, p.schema)) + '</td>'
              + '<td>' + (p.required ? 'Sí' : 'No') + '</td></tr>';
          }).join('')
        + '</table></div>'
      : '<p class="sin-params">Sin parámetros.</p>';

    var respuestas = Object.keys(o.op.responses || {}).map(function (codigo) {
      var r = deref(doc, o.op.responses[codigo]);
      var media = r.content && (r.content['application/json'] || r.content[Object.keys(r.content)[0]]);
      var ej = media ? ejemplo(doc, media.schema) : null;
      var claseCodigo = codigo.charAt(0) === '2' ? 'rc-ok' : 'rc-err';
      return '<div class="respuesta">'
        + '<div class="rc"><span class="codigo ' + claseCodigo + '">' + esc(codigo) + '</span>'
        + '<span>' + esc(r.description || '') + '</span></div>'
        + (ej !== null
            ? '<pre class="ejemplo"><code>' + esc(JSON.stringify(ej, null, 2)) + '</code></pre>'
            : '<p class="sin-params">Sin cuerpo de respuesta.</p>')
        + '</div>';
    }).join('');

    return '<details class="op">'
      + '<summary>'
      + '<span class="metodo m-' + esc(o.metodo) + '">' + esc(o.metodo.toUpperCase()) + '</span>'
      + '<code class="ruta">' + esc(o.ruta) + '</code>'
      + '<span class="sumario">' + esc(o.op.summary || '') + '</span>'
      + '</summary>'
      + '<div class="op-cuerpo">'
      + (o.op.description ? '<p>' + esc(o.op.description) + '</p>' : '')
      + tablaParams
      + '<h4>Respuestas</h4>' + respuestas
      + '</div></details>';
  }

  // ---- bloque completo ----
  function render(doc) {
    var servidor = (doc.servers && doc.servers[0]) || {};
    var grupos = agrupa(doc);
    var total = grupos.reduce(function (n, g) { return n + g.ops.length; }, 0);

    var cabecera = '<dl class="contrato">'
      + '<dt>Título</dt><dd>' + esc((doc.info && doc.info.title) || '—') + '</dd>'
      + '<dt>Versión</dt><dd>' + esc((doc.info && doc.info.version) || '—') + '</dd>'
      + '<dt>Ruta base</dt><dd><code>' + esc(servidor.url || '—') + '</code></dd>'
      + '<dt>Operaciones</dt><dd>' + total + '</dd>'
      + '</dl>';

    var descripcion = doc.info && doc.info.description
      ? '<p>' + esc(String(doc.info.description).trim()) + '</p>' : '';

    var cuerpo = grupos.map(function (g) {
      return '<h3 class="grupo">' + esc(g.tag) + '</h3>'
        + g.ops.map(function (o) { return operacion(doc, o); }).join('');
    }).join('');

    return descripcion + cabecera + cuerpo;
  }

  return { render: render, ejemplo: ejemplo, deref: deref };
})();
