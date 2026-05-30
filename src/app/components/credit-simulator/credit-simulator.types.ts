import type { TipoCredito } from '../../core/models/credito.types';

export type { TipoCredito };

export interface ResumenSimulacion {  monto: number;
  plazo: number;
  tipoCredito: TipoCredito;
  tea: number;
  cuotaMensual: number;
}

export const MONTO_MINIMO = 1000;

export const PLAZOS_MESES: readonly number[] = Array.from(
  { length: 48 - 12 + 1 },
  (_, i) => i + 12,
);

/** TEA (%) por tipo — Vivienda: tasa preferencial cooperativa */
export const TEA_POR_TIPO: Record<TipoCredito, number> = {
  Emprendedor: 14.5,
  Vivienda: 10.5,
  Agrícola: 12.0,
};
