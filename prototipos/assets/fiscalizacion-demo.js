/* Datos de prueba del intercambio de permisos de circulación.

   Los usan dos cosas: el ambiente de pruebas de la ficha (nodo.html?id=fiscalizacion)
   y la aplicación de consulta (servicio-fiscalizacion.html) cuando no se le indica
   un servicio con ?api=.

   Son ficticios: ninguna patente, vehículo, empresa ni persona corresponde a un
   registro real, y ningún dato viene del servicio de Servicios Municipales.
   Cada vehículo existe para ejercitar un caso del contrato; ver `casos` abajo.

   Las comunas llevan su Código Único Territorial, que es el punto: el permiso
   de circulación identifica a la institución recaudadora por código y no por
   el nombre escrito a mano. */

const FISCALIZACION_DEMO = {

  vehiculos: {
    "BDPF18": {
      patente: "BDPF18", marca: "TOYOTA", modelo: "YARIS",
      color: "BLANCO", anio_fabricacion: 2019, tipo: "AUTOMOVIL"
    },
    "CHCR68": {
      patente: "CHCR68", marca: "SUZUKI", modelo: "SWIFT",
      color: "GRIS", anio_fabricacion: 2021, tipo: "AUTOMOVIL"
    },
    "AB0251": {
      patente: "AB0251", marca: "YAMAHA", modelo: "XTZ 750",
      color: "AZUL", anio_fabricacion: 1995, tipo: "MOTOCICLETA"
    },
    "DLYP38": {
      patente: "DLYP38", marca: "HYUNDAI", modelo: "H1",
      color: "PLATEADO", anio_fabricacion: 2016, tipo: "FURGON"
    },
    "KR4419": {
      patente: "KR4419", marca: "CHEVROLET", modelo: "N400",
      color: "BLANCO", anio_fabricacion: 2022, tipo: "FURGON"
    },
    "FGHJ27": {
      patente: "FGHJ27", marca: "NISSAN", modelo: "VERSA",
      color: "ROJO", anio_fabricacion: 2020, tipo: "AUTOMOVIL"
    }
  },

  permisos: {
    "BDPF18": [
      { anio: 2026, estado: "VIGENTE", comuna: { cut: "13101", nombre: "Santiago" },
        monto_total: 214300, vigente_hasta: "2027-03-31",
        cuotas: [
          { numero: 1, monto: 107150, fecha_pago: "2026-03-18", medio_pago: "EN LINEA" },
          { numero: 2, monto: 107150, fecha_pago: "2026-08-14", medio_pago: "EN LINEA" }
        ] },
      { anio: 2025, estado: "VENCIDO", comuna: { cut: "13101", nombre: "Santiago" },
        monto_total: 198400, vigente_hasta: "2026-03-31",
        cuotas: [ { numero: 1, monto: 198400, fecha_pago: "2025-03-20", medio_pago: "PRESENCIAL" } ] },
      { anio: 2024, estado: "VENCIDO", comuna: { cut: "13123", nombre: "Providencia" },
        monto_total: 186900, vigente_hasta: "2025-03-31",
        cuotas: [ { numero: 1, monto: 186900, fecha_pago: "2024-03-22", medio_pago: "EN LINEA" } ] }
    ],
    "CHCR68": [
      { anio: 2026, estado: "VIGENTE", comuna: { cut: "07101", nombre: "Talca" },
        monto_total: 141200, vigente_hasta: "2027-03-31",
        cuotas: [ { numero: 1, monto: 141200, fecha_pago: "2026-03-05", medio_pago: "EN LINEA" } ] },
      { anio: 2025, estado: "VENCIDO", comuna: { cut: "07101", nombre: "Talca" },
        monto_total: 133800, vigente_hasta: "2026-03-31",
        cuotas: [ { numero: 1, monto: 133800, fecha_pago: "2025-03-14", medio_pago: "EN LINEA" } ] }
    ],
    "AB0251": [
      { anio: 2025, estado: "VENCIDO", comuna: { cut: "14101", nombre: "Valdivia" },
        monto_total: 33715, vigente_hasta: "2026-03-31",
        cuotas: [ { numero: 1, monto: 33715, fecha_pago: "2025-03-18", medio_pago: "PRESENCIAL" } ] }
    ],
    "DLYP38": [
      { anio: 2026, estado: "VIGENTE", comuna: { cut: "01101", nombre: "Iquique" },
        monto_total: 262500, vigente_hasta: "2027-03-31",
        cuotas: [
          { numero: 1, monto: 131250, fecha_pago: "2026-03-27", medio_pago: "PRESENCIAL" },
          { numero: 2, monto: 131250, fecha_pago: "2026-08-22", medio_pago: "PRESENCIAL" }
        ] }
    ],
    "KR4419": [],
    "FGHJ27": [
      { anio: 2026, estado: "ANULADO", comuna: { cut: "05101", nombre: "Valparaíso" },
        monto_total: 156800,
        cuotas: [ { numero: 1, monto: 78400, fecha_pago: "2026-03-30", medio_pago: "EN LINEA" } ] },
      { anio: 2025, estado: "VENCIDO", comuna: { cut: "05101", nombre: "Valparaíso" },
        monto_total: 149300, vigente_hasta: "2026-03-31",
        cuotas: [ { numero: 1, monto: 149300, fecha_pago: "2025-03-28", medio_pago: "EN LINEA" } ] }
    ]
  },

  provisionales: {
    "PR0909": [
      { anio: 2026, semestre: 2, comuna: { cut: "13123", nombre: "Providencia" },
        marca: "HONDA", modelo: "PILOT",
        titular: { rut: "77777777-7", razon_social: "AUTOMOTORA DE EJEMPLO SPA" } }
    ],
    "PR0910": [
      { anio: 2026, semestre: 1, comuna: { cut: "12101", nombre: "Punta Arenas" },
        marca: "KIA", modelo: "SPORTAGE",
        titular: { rut: "88888888-8", razon_social: "VEHICULOS DE MUESTRA LTDA" } }
    ]
  }
};

if (typeof Sandbox !== 'undefined') {
  Sandbox.registra('fiscalizacion', {
    token: 'prueba-nodo-subdere',
    datos: FISCALIZACION_DEMO,
    archivoDatos: 'fiscalizacion.datos-prueba.json',

    casos: [
      { ruta: '/vehiculos/{patente}/permisos', valores: { patente: 'BDPF18' },
        que: 'Permiso vigente pagado en dos cuotas; en 2024 lo recaudó otra comuna.' },
      { ruta: '/vehiculos/{patente}/permisos', valores: { patente: 'BDPF18', desde_anio: '2025' },
        que: 'El mismo vehículo, filtrando desde 2025 con el parámetro de consulta.' },
      { ruta: '/vehiculos/{patente}', valores: { patente: 'AB0251' },
        que: 'Motocicleta con patente de formato antiguo (dos letras y cuatro dígitos).' },
      { ruta: '/vehiculos/{patente}/permisos', valores: { patente: 'AB0251' },
        que: 'Sin permiso vigente: el último está vencido.' },
      { ruta: '/vehiculos/{patente}/permisos', valores: { patente: 'FGHJ27' },
        que: 'Permiso del año anulado, con el anterior vencido.' },
      { ruta: '/vehiculos/{patente}/permisos', valores: { patente: 'KR4419' },
        que: 'Vehículo inscrito que nunca ha pagado un permiso: lista vacía, no error.' },
      { ruta: '/permisos-provisionales/{patente}', valores: { patente: 'PR0909' },
        que: 'Patente provisoria: el titular es la automotora, sin datos de su representante.' },
      { ruta: '/vehiculos/{patente}', valores: { patente: 'ZZZZ99' },
        que: 'Patente con formato válido que no está inscrita: 404.' },
      { ruta: '/vehiculos/{patente}', valores: { patente: 'BDPF-18' },
        que: 'Patente con guion: el contrato la rechaza con 400 antes de buscar.' },
      { ruta: '/vehiculos/{patente}', valores: { patente: 'BDPF18' }, sinToken: true,
        que: 'La misma consulta sin credencial: 401.' }
    ],

    responder: function (req) {
      var d = FISCALIZACION_DEMO;
      var pat = req.path.patente;
      switch (req.ruta) {
        case '/vehiculos/{patente}':
          return d.vehiculos[pat] ? { status: 200, body: d.vehiculos[pat] } : { status: 404 };
        case '/vehiculos/{patente}/permisos':
          if (!d.vehiculos[pat]) return { status: 404 };
          var desde = Number(req.query.desde_anio || 0);
          return { status: 200, body: (d.permisos[pat] || []).filter(function (p) { return p.anio >= desde; }) };
        case '/permisos-provisionales/{patente}':
          var l = d.provisionales[pat];
          return l && l.length ? { status: 200, body: l } : { status: 404 };
      }
      return { status: 404 };
    }
  });
}
