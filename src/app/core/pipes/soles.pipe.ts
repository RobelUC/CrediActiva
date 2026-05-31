import { Pipe, PipeTransform } from '@angular/core';

/** Montos en soles peruanos: S/ 1,234.56 */
@Pipe({ name: 'soles', standalone: true })
export class SolesPipe implements PipeTransform {
  transform(value: number | null | undefined, digitsInfo = '1.2-2'): string {
    const numero = value == null || Number.isNaN(Number(value)) ? 0 : Number(value);
    const [minStr, maxStr] = digitsInfo.split('-');
    const min = Number(minStr.split('.')[1] ?? minStr);
    const max = Number(maxStr ?? min);

    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: 'PEN',
      minimumFractionDigits: min,
      maximumFractionDigits: max,
    }).format(numero);
  }
}
