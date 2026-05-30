export interface ValorCooperativa {
  icono: string;
  titulo: string;
  descripcion: string;
}

export interface Testimonio {
  nombre: string;
  rol: string;
  ubicacion: string;
  texto: string;
  estrellas: number;
}

export interface PreguntaFrecuente {
  id: number;
  pregunta: string;
  respuesta: string;
}

export const VALORES_CREDIACTIVA: readonly ValorCooperativa[] = [
  {
    icono: 'bi-shield-check',
    titulo: 'Transparencia',
    descripcion:
      'Tasas claras, sin letra pequeña. Cada socio conoce su cronograma antes de firmar.',
  },
  {
    icono: 'bi-graph-up-arrow',
    titulo: 'Crecimiento',
    descripcion:
      'Financiamos emprendimientos, vivienda y producción agrícola en toda la región Junín.',
  },
  {
    icono: 'bi-people-fill',
    titulo: 'Comunidad',
    descripcion:
      'Más de 18,000 socios en Huancayo y provincias vecinas confían en nuestra cooperativa.',
  },
  {
    icono: 'bi-hand-thumbs-up',
    titulo: 'Compromiso',
    descripcion:
      'Asesoría personalizada en sede y agencias para acompañarte en cada etapa del crédito.',
  },
];

export const TESTIMONIOS: readonly Testimonio[] = [
  {
    nombre: 'María Elena Rojas',
    rol: 'Comerciante',
    ubicacion: 'Huancayo',
    texto:
      'Solicité un crédito emprendedor y en 48 horas tenía la pre-aprobación. El trato fue cercano y las cuotas se ajustaron a mi negocio.',
    estrellas: 5,
  },
  {
    nombre: 'Carlos Mendoza Quispe',
    rol: 'Productor agrícola',
    ubicacion: 'Chupaca',
    texto:
      'El crédito agrícola me permitió comprar semilla y maquinaria. La TEA fue competitiva y el pago en cosecha facilitó todo.',
    estrellas: 5,
  },
  {
    nombre: 'Rosa Vilca Torres',
    rol: 'Ama de casa',
    ubicacion: 'El Tambo',
    texto:
      'Financiamos la mejora de nuestra vivienda con plazos cómodos. CrediActiva explicó cada paso sin presiones.',
    estrellas: 5,
  },
  {
    nombre: 'Jorge Luis Paredes',
    rol: 'Taxista independiente',
    ubicacion: 'Huancayo',
    texto:
      'Renové mi unidad con el simulador en línea: supe mi cuota antes de ir a la oficina. Muy recomendable.',
    estrellas: 4,
  },
];

export const PREGUNTAS_FRECUENTES: readonly PreguntaFrecuente[] = [
  {
    id: 1,
    pregunta: '¿Cuál es el monto mínimo para solicitar un crédito?',
    respuesta:
      'El monto mínimo es S/. 1,000 para todos nuestros productos de crédito. Puede simular montos mayores desde la web o en cualquier agencia CrediActiva.',
  },
  {
    id: 2,
    pregunta: '¿Qué documentos necesito para una solicitud?',
    respuesta:
      'DNI vigente, sustento de ingresos (boletas, RUC o declaración jurada según el caso) y comprobante de domicilio en la zona de influencia de la cooperativa.',
  },
  {
    id: 3,
    pregunta: '¿Cuánto demora la evaluación de mi crédito?',
    respuesta:
      'Las solicitudes menores a S/. 20,000 pueden recibir pre-aprobación preliminar de forma ágil. Montos mayores son revisados por un asesor en la sede de Huancayo en un máximo de 48 horas hábiles.',
  },
  {
    id: 4,
    pregunta: '¿Qué tipos de crédito ofrece CrediActiva?',
    respuesta:
      'Crédito Emprendedor (TEA 14.5%), Crédito Vivienda (TEA 10.5%) y Crédito Agrícola (TEA 12.0%), con plazos de 12 a 48 meses según el perfil del socio.',
  },
  {
    id: 5,
    pregunta: '¿Puedo pagar mi crédito antes del plazo?',
    respuesta:
      'Sí. Ofrecemos amortización anticipada con recálculo de intereses según el reglamento vigente de la cooperativa. Consulte condiciones en agencia.',
  },
  {
    id: 6,
    pregunta: '¿Dónde están ubicadas las oficinas?',
    respuesta:
      'Nuestra sede principal está en Huancayo. También atendemos en agencias de la región Junín. Horario de atención: lunes a viernes de 9:00 a 18:00 y sábados de 9:00 a 13:00.',
  },
];
