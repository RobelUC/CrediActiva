export function badgeEval(estado: string): string {
  const map: Record<string, string> = {
    PENDIENTE: 'warning',
    APROBADO: 'success',
    RECHAZADO: 'danger',
  };
  return map[estado] ?? 'secondary';
}

export function badgeAport(estado: string): string {
  const map: Record<string, string> = {
    PAGADO: 'success',
    PENDIENTE: 'primary',
    VENCIDO: 'danger',
  };
  return map[estado] ?? 'secondary';
}
