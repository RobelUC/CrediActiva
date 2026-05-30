/** Validación DNI peruano (8 dígitos + dígito verificador). */
const DNI_COEF = [3, 2, 7, 6, 5, 4, 3, 2] as const;
const DNI_RESERVADOS = new Set(['00000000']);

export function esDniPeruanoValido(dni: string): boolean {
  if (!/^\d{8}$/.test(dni) || DNI_RESERVADOS.has(dni) || new Set(dni).size === 1) {
    return false;
  }
  let suma = 0;
  for (let i = 0; i < 7; i++) {
    suma += Number(dni[i]) * DNI_COEF[i];
  }
  let digito = 11 - (suma % 11);
  if (digito >= 10) {
    digito -= 10;
  }
  return Number(dni[7]) === digito;
}
