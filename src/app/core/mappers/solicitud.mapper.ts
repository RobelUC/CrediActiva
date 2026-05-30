import type { ResumenSimulacion } from '../../components/credit-simulator/credit-simulator.types';
import type { SolicitudRequest } from '../models/solicitud.models';

/** Convierte el resumen del simulador al payload FastAPI (SolicitudCredito). */
export function resumenASolicitudRequest(
  resumen: ResumenSimulacion,
  dniUsuario: string,
): SolicitudRequest {
  return {
    monto: resumen.monto,
    plazo_meses: resumen.plazo,
    tipo_credito: resumen.tipoCredito,
    dni_usuario: dniUsuario,
  };
}
