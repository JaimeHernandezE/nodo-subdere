/* Resuelve el marcado [[id]] / [[id|texto]] de los textos de data.js
   contra el diccionario TERMINOS. Requiere data.js cargado antes. */
(function(){
  var MARCA = /\[\[([a-z0-9-]+)(?:\|([^\]]+))?\]\]/g;

  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  function termino(id){
    return (typeof TERMINOS !== 'undefined' && TERMINOS[id]) || null;
  }

  function ayuda(t){
    var partes = ['Definición en la wiki'];
    if (t.provisional) partes.push('nombre provisional');
    if (t.alias && t.alias.length) partes.push('también: ' + t.alias.join(', '));
    return partes.join(' · ');
  }

  // Escapa primero y enlaza después: el texto de data.js nunca se inserta como HTML.
  window.conTerminos = function(s){
    return esc(s == null ? '' : s).replace(MARCA, function(_, id, texto){
      var t = termino(id);
      var visible = texto || (t ? t.nombre : id);
      if (!t) return visible;
      return '<a class="termino" href="' + esc(t.wiki) + '" title="' + esc(ayuda(t)) + '">' + visible + '</a>';
    });
  };

  window.textoPlano = function(s){
    return String(s == null ? '' : s).replace(MARCA, function(_, id, texto){
      var t = termino(id);
      return texto || (t ? t.nombre : id);
    });
  };
})();
