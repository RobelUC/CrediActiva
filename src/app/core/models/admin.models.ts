import type { TipoCredito } from './credito.types';

export type EstadoEvaluacion = 'PENDIENTE' | 'APROBADO' | 'RECHAZADO';
export type EstadoAportacion = 'PAGADO' | 'PENDIENTE' | 'VENCIDO';
export interface DashboardAdmin {
  total_socios: number;
  total_solicitudes: number;
  solicitudes_pendientes: number;
  solicitudes_aprobadas: number;
  solicitudes_rechazadas: number;
  monto_colocado: number;
  monto_por_cobrar: number;
  tasa_aprobacion: number;
  aportaciones: ResumenAportaciones;
  actualizado_en: string;
}

export interface CarteraProducto {
  tipo_credito: string;
  cantidad: number;
  monto_total: number;
}

export interface AuditoriaSolicitud {
  id_solicitud: string;
  dni_usuario: string;
  monto: number;
  tipo_credito: string;
  estado_evaluacion: string;
  tea_aplicada: number | null;
  cuota_mensual: number | null;
  interes_total: number | null;
  observaciones: string;
}

export interface ReporteAuditoria {
  actualizado_en: string;
  cartera_por_producto: CarteraProducto[];
  solicitudes: AuditoriaSolicitud[];
  resumen_financiero: Record<string, number>;
}

export interface Socio {
  id_socio: string;
  nombres: string;
  apellidos: string;
  dni: string;
  email: string;
  telefono: string;
  aporte_mensual: number;
  fecha_registro: string;
  activo: boolean;
}

export interface SocioCreate {
  nombres: string;
  apellidos: string;
  dni: string;
  email: string;
  telefono: string;
  aporte_mensual: number;
}

export interface CuotaCronograma {
  numero_cuota: number;
  fecha_vencimiento: string;
  cuota: number;
  capital: number;
  interes: number;
  saldo_restante: number;
}

export interface SolicitudAdmin {
  id_solicitud: string;
  dni_usuario: string;
  monto: number;
  plazo_meses: number;
  tipo_credito: TipoCredito;
  estado_preaprobacion: string;
  estado_evaluacion: EstadoEvaluacion;
  fecha_registro: string;
  observaciones: string;
  cronograma: CuotaCronograma[];
}

export interface EvaluarSolicitudRequest {
  decision: 'APROBADO' | 'RECHAZADO';
  observaciones: string;
}

export interface Aportacion {
  id_aportacion: string;
  id_solicitud: string;
  dni_socio: string;
  nombre_socio: string;
  numero_cuota: number;
  monto_cuota: number;
  fecha_vencimiento: string;
  estado: EstadoAportacion;
  fecha_pago: string | null;
}

export interface ResumenAportaciones {
  total: number;
  pagadas: number;
  pendientes: number;
  vencidas: number;
  monto_pagado: number;
  monto_pendiente: number;
  actualizado_en: string;
}
