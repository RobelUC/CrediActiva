/** Datos de prueba para modo solo frontend (sin backend). */

import type {
  Aportacion,
  DashboardAdmin,
  ReporteAuditoria,
  Socio,
  SolicitudAdmin,
} from '../models/admin.models';
import type {
  AporteHistorial,
  CreditoSocio,
  PerfilSocio,
  ResumenCuenta,
} from '../models/portal.models';
import type { ConsultaDniResponse } from '../models/auth.models';
import type { SolicitudResponse } from '../models/solicitud.models';

const AHORA = new Date().toISOString();

export const DEMO_DNI = '74874853';
export const DEMO_PASSWORD = 'demo1234';
export const DEMO_ADMIN_DNI = '00000000';
export const DEMO_ADMIN_PASSWORD = 'admin123';

export const MOCK_CONSULTA_DNI: ConsultaDniResponse = {
  dni: DEMO_DNI,
  nombres: 'OLIVER ALE',
  apellidos: 'SILES VIA Y RADA',
};

export const MOCK_DASHBOARD: DashboardAdmin = {
  total_socios: 24,
  total_solicitudes: 18,
  solicitudes_pendientes: 3,
  solicitudes_aprobadas: 12,
  solicitudes_rechazadas: 3,
  monto_colocado: 185000,
  monto_por_cobrar: 12450,
  tasa_aprobacion: 80,
  aportaciones: {
    total: 48,
    pagadas: 32,
    pendientes: 14,
    vencidas: 2,
    monto_pagado: 28600,
    monto_pendiente: 12450,
    actualizado_en: AHORA,
  },
  actualizado_en: AHORA,
};

export const MOCK_SOCIOS: Socio[] = [
  {
    id_socio: 'demo-1',
    nombres: 'OLIVER ALE',
    apellidos: 'SILES VIA Y RADA',
    dni: DEMO_DNI,
    email: 'demo.socio@crediactiva.pe',
    telefono: '987654321',
    aporte_mensual: 50,
    fecha_registro: AHORA,
    activo: true,
  },
  {
    id_socio: 'demo-2',
    nombres: 'María Elena',
    apellidos: 'Rojas Quispe',
    dni: '45678912',
    email: 'maria.rojas@crediactiva.pe',
    telefono: '912345678',
    aporte_mensual: 75,
    fecha_registro: AHORA,
    activo: true,
  },
];

export const MOCK_SOLICITUDES: SolicitudAdmin[] = [
  {
    id_solicitud: 'sol-demo-001',
    dni_usuario: DEMO_DNI,
    monto: 15000,
    plazo_meses: 24,
    tipo_credito: 'Emprendedor',
    estado_preaprobacion: 'APROBADO_PRELIMINAR',
    estado_evaluacion: 'PENDIENTE',
    fecha_registro: AHORA,
    observaciones: '',
    cronograma: [],
  },
  {
    id_solicitud: 'sol-demo-002',
    dni_usuario: '45678912',
    monto: 8000,
    plazo_meses: 12,
    tipo_credito: 'Vivienda',
    estado_preaprobacion: 'APROBADO_PRELIMINAR',
    estado_evaluacion: 'APROBADO',
    fecha_registro: AHORA,
    observaciones: 'Aprobado en demo',
    cronograma: [
      {
        numero_cuota: 1,
        fecha_vencimiento: '2026-06-29',
        cuota: 720.5,
        capital: 650,
        interes: 70.5,
        saldo_restante: 7350,
      },
    ],
  },
];

export const MOCK_APORTACIONES: Aportacion[] = [
  {
    id_aportacion: 'ap-demo-1',
    id_solicitud: 'sol-demo-002',
    dni_socio: '45678912',
    nombre_socio: 'María Elena Rojas Quispe',
    numero_cuota: 1,
    monto_cuota: 720.5,
    fecha_vencimiento: '2026-05-29',
    estado: 'PAGADO',
    fecha_pago: '2026-05-28',
  },
  {
    id_aportacion: 'ap-demo-2',
    id_solicitud: 'sol-demo-002',
    dni_socio: '45678912',
    nombre_socio: 'María Elena Rojas Quispe',
    numero_cuota: 2,
    monto_cuota: 720.5,
    fecha_vencimiento: '2026-06-29',
    estado: 'PENDIENTE',
    fecha_pago: null,
  },
];

export const MOCK_REPORTE: ReporteAuditoria = {
  actualizado_en: AHORA,
  cartera_por_producto: [
    { tipo_credito: 'Emprendedor', cantidad: 8, monto_total: 95000 },
    { tipo_credito: 'Vivienda', cantidad: 5, monto_total: 62000 },
    { tipo_credito: 'Agrícola', cantidad: 5, monto_total: 28000 },
  ],
  solicitudes: MOCK_SOLICITUDES.map((s) => ({
    id_solicitud: s.id_solicitud,
    dni_usuario: s.dni_usuario,
    monto: s.monto,
    tipo_credito: s.tipo_credito,
    estado_evaluacion: s.estado_evaluacion,
    tea_aplicada: s.estado_evaluacion === 'APROBADO' ? 14.5 : null,
    cuota_mensual: s.cronograma[0]?.cuota ?? null,
    interes_total: null,
    observaciones: s.observaciones,
  })),
  resumen_financiero: {
    monto_colocado: 185000,
    interes_generado: 22400,
    cuotas_pagadas: 32,
    cuotas_vencidas: 2,
    indice_morosidad: 4.2,
  },
};

export const MOCK_RESUMEN_CUENTA: ResumenCuenta = {
  dni: DEMO_DNI,
  nombres: 'OLIVER ALE',
  apellidos: 'SILES VIA Y RADA',
  email: 'demo.socio@crediactiva.pe',
  telefono: '987654321',
  aporte_mensual: 50,
  creditos_activos: 1,
  monto_total_credito: 15000,
  saldo_pendiente: 0,
  cuotas_pagadas: 0,
  cuotas_pendientes: 0,
  cuotas_vencidas: 0,
  proxima_cuota: null,
  estado_cuenta: 'AL_DIA',
  actualizado_en: AHORA,
};

export const MOCK_CREDITOS_SOCIO: CreditoSocio[] = [
  {
    id_solicitud: 'sol-demo-001',
    tipo_credito: 'Emprendedor',
    monto: 15000,
    plazo_meses: 24,
    estado_evaluacion: 'PENDIENTE',
    estado_preaprobacion: 'APROBADO_PRELIMINAR',
    cuota_mensual: 712.4,
    saldo_pendiente: 15000,
    cuotas_pagadas: 0,
    fecha_registro: AHORA,
    cronograma: [],
  },
];

export const MOCK_APORTES_SOCIO: AporteHistorial[] = [];

export const MOCK_PERFIL: PerfilSocio = {
  id_socio: 'demo-1',
  nombres: 'OLIVER ALE',
  apellidos: 'SILES VIA Y RADA',
  dni: DEMO_DNI,
  email: 'demo.socio@crediactiva.pe',
  telefono: '987654321',
  aporte_mensual: 50,
  fecha_registro: AHORA,
};

export function mockSolicitudResponse(dni: string, monto: number, plazo: number, tipo: string): SolicitudResponse {
  return {
    id_solicitud: 'sol-mock-' + Date.now(),
    estado: monto < 20000 ? 'APROBADO_PRELIMINAR' : 'EN_REVISION',
    mensaje:
      monto < 20000
        ? '¡Solicitud pre-aprobada! (modo demo sin backend)'
        : 'Solicitud registrada para revisión. (modo demo sin backend)',
    fecha_registro: AHORA,
    auditoria: {
      tea_aplicada: 14.5,
      tasa_mensual_efectiva: 1.13,
      cuota_mensual: 712.4,
      interes_total: 2097.6,
      monto_total_a_pagar: 17097.6,
    },
    monto,
    plazo_meses: plazo,
    tipo_credito: tipo as SolicitudResponse['tipo_credito'],
    dni_usuario: dni,
  };
}
