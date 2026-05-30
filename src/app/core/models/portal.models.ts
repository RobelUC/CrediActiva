export type VistaPortal = 'resumen' | 'creditos' | 'aportes' | 'perfil';
export type EstadoCuenta = 'AL_DIA' | 'PENDIENTE' | 'MOROSO';

export interface ProximaCuota {
  fecha_vencimiento: string;
  monto: number;
  numero_cuota: number;
}

export interface ResumenCuenta {
  dni: string;
  nombres: string;
  apellidos: string;
  email: string;
  telefono: string;
  aporte_mensual: number;
  creditos_activos: number;
  monto_total_credito: number;
  saldo_pendiente: number;
  cuotas_pagadas: number;
  cuotas_pendientes: number;
  cuotas_vencidas: number;
  proxima_cuota: ProximaCuota | null;
  estado_cuenta: EstadoCuenta;
  actualizado_en: string;
}

export interface CreditoSocio {
  id_solicitud: string;
  tipo_credito: string;
  monto: number;
  plazo_meses: number;
  estado_evaluacion: string;
  estado_preaprobacion: string;
  cuota_mensual: number;
  saldo_pendiente: number;
  cuotas_pagadas: number;
  fecha_registro: string;
  cronograma: CuotaCronograma[];
}

export interface CuotaCronograma {
  numero_cuota: number;
  fecha_vencimiento: string;
  cuota: number;
  capital: number;
  interes: number;
  saldo_restante: number;
}

export interface AporteHistorial {
  id_aportacion: string;
  id_solicitud: string;
  numero_cuota: number;
  monto_cuota: number;
  fecha_vencimiento: string;
  fecha_pago: string | null;
  estado: string;
  tipo_credito: string;
}

export interface PerfilSocio {
  id_socio: string | null;
  nombres: string;
  apellidos: string;
  dni: string;
  email: string;
  telefono: string;
  aporte_mensual: number;
  fecha_registro: string | null;
}

export interface PerfilSocioUpdate {
  nombres: string;
  apellidos: string;
  email: string;
  telefono: string;
  aporte_mensual: number;
}
