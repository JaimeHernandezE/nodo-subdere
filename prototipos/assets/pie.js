/* Pie común del sitio. Cada página deja <footer id="pie"></footer> y carga este
   archivo justo después, antes de sus propios scripts.
   - data-nota reemplaza la segunda línea (crédito de la fuente en las entradas).
   - La fecha queda en <span class="pie-fecha">; apis.html la reemplaza por la del
     nodo actualizado más recientemente.
   El logotipo se resuelve contra la ubicación de este archivo, para que funcione
   también desde 404.html, que GitHub Pages sirve en cualquier ruta. */
(function(){
  var PIE = {
    fecha: "septiembre de 2026",
    nota: "División de Políticas y Estudios · Subsecretaría de Desarrollo Regional y Administrativo",
    logo: "logo-subdere-blanco.png",
    alt: "Subsecretaría de Desarrollo Regional y Administrativo · Gobierno de Chile"
  };

  var pie = document.getElementById("pie");
  if (!pie) return;

  var base = document.currentScript ? document.currentScript.src : "assets/pie.js";

  function el(tag, cls, txt){
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt) n.textContent = txt;
    return n;
  }

  var wrap = el("div", "wrap");

  var marca = el("div", "marca");
  var img = el("img");
  img.src = new URL(PIE.logo, base).href;
  img.alt = PIE.alt;
  img.width = 98;
  img.height = 88;
  marca.appendChild(img);

  var txt = el("div", "pie-txt");
  var l1 = el("div");
  l1.appendChild(el("b", null, "Nodo SUBDERE"));
  l1.appendChild(document.createTextNode(" · Última actualización: "));
  l1.appendChild(el("span", "pie-fecha", PIE.fecha));
  txt.appendChild(l1);
  txt.appendChild(el("div", null, pie.getAttribute("data-nota") || PIE.nota));

  wrap.appendChild(marca);
  wrap.appendChild(txt);
  pie.textContent = "";
  pie.appendChild(wrap);
})();
