/* Desplegables de la barra superior.

   El menú es un <details>/<summary> nativo: funciona con teclado y sin
   JavaScript. Esto solo agrega lo que el elemento nativo no trae —cerrar
   al hacer clic afuera y con Escape— y no es indispensable. */
(function () {
  var menus = Array.prototype.slice.call(document.querySelectorAll('.nav-menu'));
  if (!menus.length) return;

  function cerrarOtros(abierto) {
    menus.forEach(function (m) { if (m !== abierto) m.open = false; });
  }

  menus.forEach(function (m) {
    m.addEventListener('toggle', function () { if (m.open) cerrarOtros(m); });
  });

  document.addEventListener('click', function (e) {
    menus.forEach(function (m) { if (!m.contains(e.target)) m.open = false; });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    menus.forEach(function (m) {
      if (!m.open) return;
      m.open = false;
      var s = m.querySelector('summary');
      if (s) s.focus();
    });
  });
})();
