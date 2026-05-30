import type { TipoCredito } from './credito.types';

/**
 * Cuerpo POST /api/v1/solicitudes — alineado con Pydantic SolicitudCredito.
 */
export interface SolicitudRequest {
  monto: number;
  plazo_meses: number;
  tipo_credito: TipoCredito;
  dni_usuario: string;
}

export type EstadoPreaprobacion = 'APROBADO_PRELIMINAR' | 'EN_REVISION';

export interface AuditoriaInteres {
  tea_aplicada: number;
  tasa_mensual_efectiva: number;
  cuota_mensual: number;
  interes_total: number;
  monto_total_a_pagar: number;
}

/**
 * Respuesta POST /api/v1/solicitudes — alineado con SolicitudCreditoResponse.
 */
export interface SolicitudResponse {
  id_solicitud: string;
  estado: EstadoPreaprobacion;
  mensaje: string;
  fecha_registro: string;
  auditoria: AuditoriaInteres;
  monto: number;
  plazo_meses: number;
  tipo_credito: TipoCredito;
  dni_usuario: string;
}
