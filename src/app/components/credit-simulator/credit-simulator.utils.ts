/**
 * Cuota mensual — sistema de amortización francés.
 * Convierte TEA a tasa mensual efectiva: (1 + TEA)^(1/12) - 1
 */
export function calcularCuotaFrancesa(
  capital: number,
  teaAnualPorcentaje: number,
  plazoMeses: number,
): number {
  if (capital <= 0 || plazoMeses <= 0 || teaAnualPorcentaje < 0) {
    return 0;
  }

  const tea = teaAnualPorcentaje / 100;
  const tasaMensual = Math.pow(1 + tea, 1 / 12) - 1;
  const factor = Math.pow(1 + tasaMensual, plazoMeses);

  if (factor === 1) {
    return capital / plazoMeses;
  }

  return (capital * tasaMensual * factor) / (factor - 1);
}

export function formatearSoles(valor: number): string {
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(valor);
}

export function formatearPorcentaje(valor: number): string {
  return new Intl.NumberFormat('es-PE', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(valor / 100);
}
