import { DatePipe } from '@angular/common';
import { SolesPipe } from '../../core/pipes/soles.pipe';
import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import type { ResumenCuenta } from '../../core/models/portal.models';
import { AuthService } from '../../core/services/auth.service';
import { PortalSocioService } from '../../core/services/portal-socio.service';

@Component({
  selector: 'ca-portal-resumen',
  standalone: true,
  imports: [DatePipe, RouterLink, SolesPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './portal-resumen.component.html',
  styleUrl: './portal-shared.scss',
})
export class PortalResumenComponent implements OnInit {
  private readonly portal = inject(PortalSocioService);
  private readonly auth = inject(AuthService);

  readonly resumen = signal<ResumenCuenta | null>(null);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    const dni = this.auth.usuario()?.dni;
    if (!dni) {
      return;
    }
    this.portal.obtenerResumen(dni).subscribe({
      next: (r) => this.resumen.set(r),
      error: () =>
        this.error.set('No se pudo cargar el resumen. Verifique que el servidor esté activo.'),
    });
  }

  estadoBadge(estado: string): string {
    const map: Record<string, string> = {
      AL_DIA: 'success',
      PENDIENTE: 'warning',
      MOROSO: 'danger',
    };
    return map[estado] ?? 'secondary';
  }

  estadoLabel(estado: string): string {
    const map: Record<string, string> = {
      AL_DIA: 'Al día',
      PENDIENTE: 'Cuota pendiente',
      MOROSO: 'En mora',
    };
    return map[estado] ?? estado;
  }
}
