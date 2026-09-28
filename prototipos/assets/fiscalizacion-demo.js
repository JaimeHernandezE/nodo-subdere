/* Datos de demostración del servicio de permisos de circulación.

   TODOS LOS DATOS DE ESTE ARCHIVO SON INVENTADOS. Ninguna patente, vehículo,
   empresa ni persona corresponde a un registro real, y ningún dato viene del
   servicio de Servicios Municipales.

   Existe para que la pantalla se pueda mostrar sin el servicio arriba. Cuando
   el servicio esté alcanzable, la pantalla lo consulta y este archivo deja de
   usarse: se borra, no se mantiene sincronizado.

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
    "KR4419": []
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
