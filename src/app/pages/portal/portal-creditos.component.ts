import { DatePipe, DecimalPipe } from '@angular/common';
import { SolesPipe } from '../../core/pipes/soles.pipe';
import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import type { CreditoSocio } from '../../core/models/portal.models';
import { AuthService } from '../../core/services/auth.service';
import { PortalSocioService } from '../../core/services/portal-socio.service';

@Component({
  selector: 'ca-portal-creditos',
  standalone: true,
  imports: [DatePipe, DecimalPipe, SolesPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './portal-creditos.component.html',
  styleUrl: './portal-shared.scss',
})
export class PortalCreditosComponent implements OnInit {
  private readonly portal = inject(PortalSocioService);
  private readonly auth = inject(AuthService);

  readonly creditos = signal<CreditoSocio[]>([]);
  readonly seleccionado = signal<CreditoSocio | null>(null);

  ngOnInit(): void {
    const dni = this.auth.usuario()?.dni;
    if (!dni) {
      return;
    }
    this.portal.obtenerCreditos(dni).subscribe({
      next: (data) => {
        this.creditos.set(data);
        if (data.length > 0) {
          this.seleccionado.set(data[0]);
        }
      },
    });
  }

  seleccionar(c: CreditoSocio): void {
    this.seleccionado.set(c);
  }

  badgeEstado(estado: string): string {
    const map: Record<string, string> = {
      APROBADO: 'success',
      PENDIENTE: 'warning',
      RECHAZADO: 'danger',
    };
    return map[estado] ?? 'secondary';
  }
}
