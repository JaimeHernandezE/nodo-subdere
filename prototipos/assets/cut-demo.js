/* Datos del ambiente de pruebas del CUT (nodo.html?id=cut).

   Son códigos oficiales, no inventados, pero es un extracto: tres regiones
   completas, con todas sus provincias y comunas. Se eligieron para ejercitar
   casos distintos:
     Tarapacá  región 1, pocas comunas, y una comuna creada después de las
               demás (Alto Hospicio, 1107) que salta la numeración.
     Maule     la del ejemplo del contrato.
     Ñuble     la región más nueva (16), con códigos de cinco dígitos.
   Lo que no está en el extracto responde 404, igual que un código que no existe.

   `abreviatura` es opcional en el contrato y el extracto no la trae: el
   catálogo no tiene la lista oficial de abreviaturas. */

const CUT_DEMO = {

  regiones: [
    { region_id: 1,  nombre: "Tarapacá" },
    { region_id: 7,  nombre: "Maule" },
    { region_id: 16, nombre: "Ñuble" }
  ],

  provincias: [
    { provincia_id: 11,  nombre: "Iquique",   region_id: 1 },
    { provincia_id: 14,  nombre: "Tamarugal", region_id: 1 },
    { provincia_id: 71,  nombre: "Talca",     region_id: 7 },
    { provincia_id: 72,  nombre: "Cauquenes", region_id: 7 },
    { provincia_id: 73,  nombre: "Curicó",    region_id: 7 },
    { provincia_id: 74,  nombre: "Linares",   region_id: 7 },
    { provincia_id: 161, nombre: "Diguillín", region_id: 16 },
    { provincia_id: 162, nombre: "Itata",     region_id: 16 },
    { provincia_id: 163, nombre: "Punilla",   region_id: 16 }
  ],

  comunas: [
    { comuna_id: 1101, nombre: "Iquique",        provincia_id: 11 },
    { comuna_id: 1107, nombre: "Alto Hospicio",  provincia_id: 11 },
    { comuna_id: 1401, nombre: "Pozo Almonte",   provincia_id: 14 },
    { comuna_id: 1402, nombre: "Camiña",         provincia_id: 14 },
    { comuna_id: 1403, nombre: "Colchane",       provincia_id: 14 },
    { comuna_id: 1404, nombre: "Huara",          provincia_id: 14 },
    { comuna_id: 1405, nombre: "Pica",           provincia_id: 14 },

    { comuna_id: 7101, nombre: "Talca",          provincia_id: 71 },
    { comuna_id: 7102, nombre: "Constitución",   provincia_id: 71 },
    { comuna_id: 7103, nombre: "Curepto",        provincia_id: 71 },
    { comuna_id: 7104, nombre: "Empedrado",      provincia_id: 71 },
    { comuna_id: 7105, nombre: "Maule",          provincia_id: 71 },
    { comuna_id: 7106, nombre: "Pelarco",        provincia_id: 71 },
    { comuna_id: 7107, nombre: "Pencahue",       provincia_id: 71 },
    { comuna_id: 7108, nombre: "Río Claro",      provincia_id: 71 },
    { comuna_id: 7109, nombre: "San Clemente",   provincia_id: 71 },
    { comuna_id: 7110, nombre: "San Rafael",     provincia_id: 71 },
    { comuna_id: 7201, nombre: "Cauquenes",      provincia_id: 72 },
    { comuna_id: 7202, nombre: "Chanco",         provincia_id: 72 },
    { comuna_id: 7203, nombre: "Pelluhue",       provincia_id: 72 },
    { comuna_id: 7301, nombre: "Curicó",         provincia_id: 73 },
    { comuna_id: 7302, nombre: "Hualañé",        provincia_id: 73 },
    { comuna_id: 7303, nombre: "Licantén",       provincia_id: 73 },
    { comuna_id: 7304, nombre: "Molina",         provincia_id: 73 },
    { comuna_id: 7305, nombre: "Rauco",          provincia_id: 73 },
    { comuna_id: 7306, nombre: "Romeral",        provincia_id: 73 },
    { comuna_id: 7307, nombre: "Sagrada Familia", provincia_id: 73 },
    { comuna_id: 7308, nombre: "Teno",           provincia_id: 73 },
    { comuna_id: 7309, nombre: "Vichuquén",      provincia_id: 73 },
    { comuna_id: 7401, nombre: "Linares",        provincia_id: 74 },
    { comuna_id: 7402, nombre: "Colbún",         provincia_id: 74 },
    { comuna_id: 7403, nombre: "Longaví",        provincia_id: 74 },
    { comuna_id: 7404, nombre: "Parral",         provincia_id: 74 },
    { comuna_id: 7405, nombre: "Retiro",         provincia_id: 74 },
    { comuna_id: 7406, nombre: "San Javier",     provincia_id: 74 },
    { comuna_id: 7407, nombre: "Villa Alegre",   provincia_id: 74 },
    { comuna_id: 7408, nombre: "Yerbas Buenas",  provincia_id: 74 },

    { comuna_id: 16101, nombre: "Chillán",       provincia_id: 161 },
    { comuna_id: 16102, nombre: "Bulnes",        provincia_id: 161 },
    { comuna_id: 16103, nombre: "Chillán Viejo", provincia_id: 161 },
    { comuna_id: 16104, nombre: "El Carmen",     provincia_id: 161 },
    { comuna_id: 16105, nombre: "Pemuco",        provincia_id: 161 },
    { comuna_id: 16106, nombre: "Pinto",         provincia_id: 161 },
    { comuna_id: 16107, nombre: "Quillón",       provincia_id: 161 },
    { comuna_id: 16108, nombre: "San Ignacio",   provincia_id: 161 },
    { comuna_id: 16109, nombre: "Yungay",        provincia_id: 161 },
    { comuna_id: 16201, nombre: "Quirihue",      provincia_id: 162 },
    { comuna_id: 16202, nombre: "Cobquecura",    provincia_id: 162 },
    { comuna_id: 16203, nombre: "Coelemu",       provincia_id: 162 },
    { comuna_id: 16204, nombre: "Ninhue",        provincia_id: 162 },
    { comuna_id: 16205, nombre: "Portezuelo",    provincia_id: 162 },
    { comuna_id: 16206, nombre: "Ránquil",       provincia_id: 162 },
    { comuna_id: 16207, nombre: "Treguaco",      provincia_id: 162 },
    { comuna_id: 16301, nombre: "San Carlos",    provincia_id: 163 },
    { comuna_id: 16302, nombre: "Coihueco",      provincia_id: 163 },
    { comuna_id: 16303, nombre: "Ñiquén",        provincia_id: 163 },
    { comuna_id: 16304, nombre: "San Fabián",    provincia_id: 163 },
    { comuna_id: 16305, nombre: "San Nicolás",   provincia_id: 163 }
  ]
};

if (typeof Sandbox !== 'undefined') {
  (function () {
    var d = CUT_DEMO;
    function porId(lista, campo, id) {
      for (var i = 0; i < lista.length; i++) if (lista[i][campo] === id) return lista[i];
      return null;
    }
    function region(id)    { return porId(d.regiones, 'region_id', id); }
    function provincia(id) { return porId(d.provincias, 'provincia_id', id); }
    function comuna(id)    { return porId(d.comunas, 'comuna_id', id); }
    function resumenProv(p) { return { provincia_id: p.provincia_id, nombre: p.nombre }; }
    function resumenCom(c)  { return { comuna_id: c.comuna_id, nombre: c.nombre }; }
    // El contrato no trae el texto del error; se usa la descripción de su respuesta 404.
    var NO_ENCONTRADA = { status: 404, body: { error: 'No encontrada' } };

    Sandbox.registra('cut', {
      datos: CUT_DEMO,
      archivoDatos: 'cut.datos-prueba.json',

      casos: [
        { ruta: '/regiones', valores: {},
          que: 'Las regiones del extracto.' },
        { ruta: '/regiones/{region_id}/', valores: { region_id: '16' },
          que: 'Ñuble, la región más nueva.' },
        { ruta: '/regiones/{region_id}/provincias', valores: { region_id: '7' },
          que: 'Las cuatro provincias del Maule.' },
        { ruta: '/regiones/{region_id}/comunas', valores: { region_id: '1' },
          que: 'Comunas de Tarapacá, cada una con su provincia.' },
        { ruta: '/provincias/{provincia_id}', valores: { provincia_id: '163' },
          que: 'Provincia con la región incluida.' },
        { ruta: '/provincias/{provincia_id}/comunas', valores: { provincia_id: '14' },
          que: 'Comunas de la provincia del Tamarugal.' },
        { ruta: '/comunas/{comuna_id}/full', valores: { comuna_id: '1107' },
          que: 'Alto Hospicio: el código no sigue la numeración de las demás comunas de su provincia.' },
        { ruta: '/comunas/{comuna_id}/full', valores: { comuna_id: '16101' },
          que: 'Chillán: código de cinco dígitos.' },
        { ruta: '/comunas/{comuna_id}/full', valores: { comuna_id: '9999' },
          que: 'Código que no existe: 404.' },
        { ruta: '/comunas/{comuna_id}/full', valores: { comuna_id: 'Talca' },
          que: 'Nombre en vez de código: el contrato pide un número y la consulta no se envía.' },
        { ruta: '/readyz', valores: {},
          que: 'Confirma que el catálogo está cargado y cuántas comunas tiene.' }
      ],

      responder: function (req) {
        var id = Number(req.path.region_id || req.path.provincia_id || req.path.comuna_id);
        var r, p, c;
        switch (req.ruta) {
          case '/healthz':
            return { status: 200, body: { status: 'ok' } };
          case '/readyz':
            return { status: 200, body: { comunas_count: d.comunas.length, catalog_ok: true } };
          case '/regiones':
            return { status: 200, body: d.regiones };
          case '/provincias':
            return { status: 200, body: d.provincias.map(resumenProv) };
          case '/comunas':
            return { status: 200, body: d.comunas.map(resumenCom) };

          case '/regiones/{region_id}/':
            r = region(id);
            return r ? { status: 200, body: { region_id: r.region_id, nombre: r.nombre } } : NO_ENCONTRADA;
          case '/regiones/{region_id}/provincias':
            r = region(id);
            if (!r) return NO_ENCONTRADA;
            return { status: 200, body: { region_id: r.region_id, region: r.nombre,
              provincias: d.provincias.filter(function (x) { return x.region_id === id; }).map(resumenProv) } };
          case '/regiones/{region_id}/comunas':
            r = region(id);
            if (!r) return NO_ENCONTRADA;
            return { status: 200, body: { region_id: r.region_id, region: r.nombre,
              comunas: d.comunas.filter(function (x) { return provincia(x.provincia_id).region_id === id; })
                .map(function (x) {
                  return { comuna_id: x.comuna_id, nombre: x.nombre, provincia: resumenProv(provincia(x.provincia_id)) };
                }) } };

          case '/provincias/{provincia_id}':
            p = provincia(id);
            if (!p) return NO_ENCONTRADA;
            r = region(p.region_id);
            return { status: 200, body: { provincia_id: p.provincia_id, provincia: p.nombre,
              region: { region_id: r.region_id, nombre: r.nombre } } };
          case '/provincias/{provincia_id}/comunas':
            p = provincia(id);
            if (!p) return NO_ENCONTRADA;
            return { status: 200, body: { provincia_id: p.provincia_id, provincia: p.nombre,
              comunas: d.comunas.filter(function (x) { return x.provincia_id === id; }).map(resumenCom) } };

          case '/comunas/{comuna_id}/full':
            c = comuna(id);
            if (!c) return NO_ENCONTRADA;
            p = provincia(c.provincia_id);
            return { status: 200, body: { comuna_id: c.comuna_id, comuna: c.nombre,
              provincia: p.nombre, region: region(p.region_id).nombre } };
        }
        return NO_ENCONTRADA;
      }
    });
  })();
}
