/* Barra lateral de la wiki e índice «En esta página».
   El menú es una lista de datos, como el de WikiGuías (header / link / divider).
   Solo lleva secciones fijas: lo que crece sin límite (una entrada por
   intercambio) va en un índice, y la página declara a qué sección pertenece con
   <main class="wiki-main" data-wiki-seccion="wiki-intercambios.html">. */
var WIKI_NAV = [
  { k: "link",    l: "Inicio de la wiki", t: "wiki.html" },
  { k: "divider" },
  { k: "header",  l: "Usar el nodo" },
  { k: "link",    l: "Cómo funciona un intercambio", t: "wiki-recorrido.html" },
  { k: "link",    l: "Cómo se usa una API", t: "wiki-consumir.html" },
  { k: "link",    l: "Conectar un sistema", t: "wiki-conectar.html" },
  { k: "link",    l: "Cómo leer una ficha", t: "wiki-ficha.html" },
  { k: "divider" },
  { k: "header",  l: "Intercambios" },
  { k: "link",    l: "Índice de entradas", t: "wiki-intercambios.html" },
  { k: "divider" },
  { k: "header",  l: "Códigos y datos maestros" },
  { k: "link",    l: "Índice de códigos", t: "wiki-codigos.html" },
  { k: "divider" },
  { k: "header",  l: "Marco normativo" },
  { k: "link",    l: "Normas", t: "wiki-normas.html" },
  { k: "divider" },
  { k: "header",  l: "Referencia" },
  { k: "link",    l: "Glosario", t: "wiki-glosario.html" },
  { k: "link",    l: "Decisiones de arquitectura", t: "wiki-decisiones.html" }
];

(function(){
  var ESCRITORIO = window.matchMedia("(min-width: 901px)");

  function el(tag, cls, txt){
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt) n.textContent = txt;
    return n;
  }

  function actual(){
    var main = document.querySelector(".wiki-main[data-wiki-seccion]");
    if (main) return main.getAttribute("data-wiki-seccion");
    var f = location.pathname.split("/").pop();
    return f || "wiki.html";
  }

  function pintarMenu(){
    var aside = document.getElementById("wiki-nav");
    if (!aside) return;
    var aqui = actual();

    var plegable = el("details", "wiki-nav__plegable");
    plegable.appendChild(el("summary", null, "Menú de la wiki"));
    var ul = el("ul", "wiki-nav__lista");

    WIKI_NAV.forEach(function(it){
      var li;
      if (it.k === "header") {
        li = el("li", "wiki-nav__grupo", it.l);
      } else if (it.k === "divider") {
        li = el("li", "wiki-nav__div");
        li.setAttribute("role", "separator");
      } else {
        li = el("li");
        var a = el("a", null, it.l);
        a.href = it.t;
        if (it.t === aqui) a.setAttribute("aria-current", "page");
        li.appendChild(a);
      }
      ul.appendChild(li);
    });

    plegable.appendChild(ul);
    aside.textContent = "";
    aside.appendChild(plegable);

    function sincronizar(){ plegable.open = ESCRITORIO.matches; }
    sincronizar();
    if (ESCRITORIO.addEventListener) ESCRITORIO.addEventListener("change", sincronizar);
  }

  function slug(s){
    return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  function pintarIndice(){
    var toc = document.getElementById("wiki-toc");
    var main = document.querySelector(".wiki-main");
    if (!toc || !main) return;
    var titulos = main.querySelectorAll("h2");
    if (titulos.length < 2) { toc.hidden = true; return; }

    toc.appendChild(el("p", "wiki-toc__tit", "En esta página"));
    var ul = el("ul");
    Array.prototype.forEach.call(titulos, function(h){
      if (!h.id) h.id = slug(h.textContent);
      var li = el("li");
      var a = el("a", null, h.textContent);
      a.href = "#" + h.id;
      li.appendChild(a);
      ul.appendChild(li);
    });
    toc.appendChild(ul);
  }

  pintarMenu();
  pintarIndice();
})();
