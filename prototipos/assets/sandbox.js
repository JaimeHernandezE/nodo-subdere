/* Ambiente de pruebas de una ficha.

   Ejecuta las operaciones de un contrato OpenAPI contra un conjunto fijo de
   datos ficticios, sin servidor. Lo que no depende de los datos lo decide el
   propio contrato, no este archivo:
     - si la operación pide credencial (security)      → 401 sin ella
     - el formato de cada parámetro de ruta (pattern)  → 400 si no calza y el
                                                         contrato define 400;
                                                         si no, no se envía
     - el cuerpo de cada error                         → el ejemplo del contrato
   Lo único que aporta cada nodo es `responder`, que busca en sus datos.

   Registro, desde el archivo de datos de cada nodo:
     Sandbox.registra(id, {
       token?,         credencial de prueba que se muestra y se envía (si el contrato pide)
       datos,          objeto que se ofrece como descarga JSON
       archivoDatos,   nombre del archivo descargado
       casos,          [{ ruta, valores, que, sinToken? }]
       responder(req)  req = { metodo, ruta, path, query } → { status, body? }
                       Si no trae body, se usa el ejemplo del contrato para ese status.
     });

   Depende de openapi.js (deref, ejemplo). */

var Sandbox = (function () {
  var registro = {};

  var TEXTO_STATUS = { 200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 404: 'Not Found', 500: 'Internal Server Error' };
  var METODOS = ['get', 'post', 'put', 'patch', 'delete'];

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function operaciones(doc) {
    var lista = [];
    Object.keys(doc.paths || {}).forEach(function (ruta) {
      METODOS.forEach(function (m) {
        var op = doc.paths[ruta][m];
        if (!op) return;
        var params = (op.parameters || []).map(function (p) { return OpenAPI.deref(doc, p); });
        var seguridad = op.security !== undefined ? op.security : doc.security;
        lista.push({ ruta: ruta, metodo: m, op: op, params: params,
                     pideCredencial: !!(seguridad && seguridad.length) });
      });
    });
    return lista;
  }

  function ejemploRespuesta(doc, op, status) {
    var r = op.responses && op.responses[String(status)];
    if (!r) return null;
    r = OpenAPI.deref(doc, r);
    var media = r.content && (r.content['application/json'] || r.content[Object.keys(r.content)[0]]);
    if (!media) return null;
    return media.example !== undefined ? media.example : OpenAPI.ejemplo(doc, media.schema);
  }

  function problemaDeTipo(doc, p, valor) {
    var s = OpenAPI.deref(doc, p.schema) || {};
    if (valor === '') return p.required ? 'Es obligatorio.' : null;
    if (s.type === 'integer' || s.type === 'number') {
      if (!/^-?\d+$/.test(valor)) return 'Debe ser un número entero.';
      if (s.minimum !== undefined && Number(valor) < s.minimum) return 'Debe ser ' + s.minimum + ' o más.';
      if (s.maximum !== undefined && Number(valor) > s.maximum) return 'Debe ser ' + s.maximum + ' o menos.';
    }
    if (s.pattern && !new RegExp(s.pattern).test(valor)) return 'No calza con el formato del contrato.';
    return null;
  }

  function monta(caja, doc, cfg) {
    var ops = operaciones(doc);
    if (!ops.length) { caja.innerHTML = ''; return null; }
    var base = ((doc.servers && doc.servers[0] && doc.servers[0].url) || '').replace(/\/+$/, '');
    var actual = ops[0];

    caja.innerHTML =
      '<div class="sb">'
      + '<div class="sb-form">'
      +   '<label class="sb-lbl" for="sbOp">Operación</label>'
      +   '<select id="sbOp" class="sb-in">' + ops.map(function (o, i) {
            return '<option value="' + i + '">' + esc(o.metodo.toUpperCase() + ' ' + o.ruta)
              + (o.op.summary ? ' — ' + esc(o.op.summary) : '') + '</option>';
          }).join('') + '</select>'
      +   '<div id="sbParams"></div>'
      +   '<label class="sb-check"><input type="checkbox" id="sbTok" checked> Enviar con la credencial de prueba'
      +     ' <code>' + esc(cfg.token || '') + '</code></label>'
      +   '<button type="button" class="btn btn-p" id="sbEnviar">Enviar</button>'
      + '</div>'
      + '<div class="sb-salida" id="sbSalida" aria-live="polite">'
      +   '<p class="sin-params">Elige una operación y envíala, o usa uno de los casos de prueba de abajo.</p>'
      + '</div>'
      + '</div>'
      + (cfg.casos && cfg.casos.length
          ? '<h3 class="sb-tit">Casos de prueba</h3>'
            + '<p class="lead-op">Cada caso ejercita una situación distinta del contrato. «Probar» lo carga arriba y lo envía.</p>'
            + '<div class="tabla-ancha"><table class="sb-casos">'
            + '<tr><th>Operación</th><th>Valor</th><th>Qué muestra</th><th></th></tr>'
            + cfg.casos.map(function (c, i) {
                var valores = Object.keys(c.valores || {}).map(function (k) {
                  return '<code>' + esc(c.valores[k]) + '</code>';
                }).join(' ');
                return '<tr><td><code>' + esc(c.ruta) + '</code></td><td>' + (valores || '—')
                  + (c.sinToken ? ' <span class="tag">sin credencial</span>' : '') + '</td>'
                  + '<td>' + esc(c.que) + '</td>'
                  + '<td><button type="button" class="btn-copiar" data-caso="' + i + '">Probar</button></td></tr>';
              }).join('')
            + '</table></div>'
          : '');

    var selOp = caja.querySelector('#sbOp');
    var cajaParams = caja.querySelector('#sbParams');
    var tok = caja.querySelector('#sbTok');
    var salida = caja.querySelector('#sbSalida');

    function pintaParams(valores) {
      valores = valores || {};
      cajaParams.innerHTML = actual.params.length
        ? actual.params.map(function (p, i) {
            var s = OpenAPI.deref(doc, p.schema) || {};
            var ej = s.example !== undefined ? s.example : '';
            return '<label class="sb-lbl" for="sbP' + i + '">' + esc(p.name)
              + ' <span class="sb-donde">' + (p['in'] === 'path' ? 'en la ruta' : 'en la consulta')
              + (p.required ? ' · obligatorio' : ' · opcional') + '</span></label>'
              + '<input class="sb-in" id="sbP' + i + '" data-param="' + esc(p.name) + '" autocomplete="off" spellcheck="false"'
              + ' placeholder="' + esc(ej) + '" value="' + esc(valores[p.name] !== undefined ? valores[p.name] : (p.required ? ej : '')) + '">'
              + '<p class="sb-err" id="sbE' + i + '"></p>';
          }).join('')
        : '<p class="sin-params">Esta operación no tiene parámetros.</p>';
      tok.parentNode.style.display = actual.pideCredencial ? '' : 'none';
    }

    function enviar() {
      var path = {}, query = {}, bloqueado = false;
      var tiene400 = !!(actual.op.responses && actual.op.responses['400']);
      actual.params.forEach(function (p, i) {
        var input = caja.querySelector('#sbP' + i);
        var valor = input.value.trim();
        var err = caja.querySelector('#sbE' + i);
        err.textContent = '';
        // Un parámetro de ruta mal formado se envía igual si el contrato define qué
        // responde (400). Si no lo define, o si es de consulta, se detiene aquí.
        if (p['in'] !== 'path' || !tiene400) {
          var problema = problemaDeTipo(doc, p, valor);
          if (problema) { err.textContent = problema; bloqueado = true; return; }
        }
        if (valor !== '') (p['in'] === 'path' ? path : query)[p.name] = valor;
      });
      if (bloqueado) {
        salida.innerHTML = '<p class="sin-params">No se envió: el valor marcado no calza con lo que pide el contrato.</p>';
        return;
      }

      var url = base + actual.ruta.replace(/\{([^}]+)\}/g, function (_, k) {
        return encodeURIComponent(path[k] || '');
      });
      var qs = Object.keys(query).map(function (k) {
        return encodeURIComponent(k) + '=' + encodeURIComponent(query[k]);
      }).join('&');
      if (qs) url += '?' + qs;
      var conToken = actual.pideCredencial && tok.checked;

      var res;
      if (actual.pideCredencial && !conToken) {
        res = { status: 401 };
      } else {
        var invalido = actual.params.filter(function (p) {
          return p['in'] === 'path' && problemaDeTipo(doc, p, path[p.name] || '');
        })[0];
        res = invalido
          ? { status: 400 }
          : cfg.responder({ metodo: actual.metodo, ruta: actual.ruta, path: path, query: query });
      }
      var cuerpo = res.body !== undefined ? res.body : ejemploRespuesta(doc, actual.op, res.status);

      var peticion = actual.metodo.toUpperCase() + ' ' + url + '\nAccept: application/json'
        + (conToken ? '\nAuthorization: Bearer ' + cfg.token : '');
      salida.innerHTML = '<p class="sin-params">Enviando…</p>';
      var ms = 90 + Math.round(Math.random() * 220);
      setTimeout(function () {
        var ok = String(res.status).charAt(0) === '2';
        salida.innerHTML =
          '<p class="sb-etq">Petición</p>'
          + '<pre class="ejemplo"><code>' + esc(peticion) + '</code></pre>'
          + '<p class="sb-etq">Respuesta <span class="codigo ' + (ok ? 'rc-ok' : 'rc-err') + '">' + res.status + '</span> '
          + esc(TEXTO_STATUS[res.status] || '') + ' <span class="sb-ms">· ' + ms + ' ms</span></p>'
          + (cuerpo !== null && cuerpo !== undefined
              ? '<pre class="ejemplo"><code>' + esc(JSON.stringify(cuerpo, null, 2)) + '</code></pre>'
              : '<p class="sin-params">Sin cuerpo de respuesta.</p>');
      }, ms);
    }

    function selecciona(ruta, valores, sinToken, yEnviar) {
      var i = 0;
      for (var k = 0; k < ops.length; k++) if (ops[k].ruta === ruta) { i = k; break; }
      selOp.value = String(i);
      actual = ops[i];
      pintaParams(valores);
      tok.checked = !sinToken;
      if (yEnviar) enviar();
    }

    selOp.addEventListener('change', function () { actual = ops[Number(selOp.value)]; pintaParams(); });
    caja.querySelector('#sbEnviar').addEventListener('click', enviar);
    cajaParams.addEventListener('keydown', function (e) { if (e.key === 'Enter') enviar(); });
    Array.prototype.forEach.call(caja.querySelectorAll('[data-caso]'), function (b) {
      b.addEventListener('click', function () {
        var c = cfg.casos[Number(b.getAttribute('data-caso'))];
        selecciona(c.ruta, c.valores, c.sinToken, true);
        salida.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      });
    });
    pintaParams();

    return { selecciona: selecciona, rutas: ops.map(function (o) { return o.ruta; }) };
  }

  function descargaDatos(cfg) {
    var blob = new Blob([JSON.stringify(cfg.datos, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = cfg.archivoDatos || 'datos-prueba.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  return {
    registra: function (id, cfg) { registro[id] = cfg; },
    config: function (id) { return registro[id] || null; },
    monta: monta,
    descargaDatos: descargaDatos
  };
})();
