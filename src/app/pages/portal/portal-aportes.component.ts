import { SolesPipe } from '../../core/pipes/soles.pipe';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import type { AporteHistorial } from '../../core/models/portal.models';
import { AuthService } from '../../core/services/auth.service';
import { PortalSocioService } from '../../core/services/portal-socio.service';

@Component({
  selector: 'ca-portal-aportes',
  standalone: true,
  imports: [SolesPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './portal-aportes.component.html',
  styleUrl: './portal-shared.scss',
})
export class PortalAportesComponent implements OnInit {
  private readonly portal = inject(PortalSocioService);
  private readonly auth = inject(AuthService);

  readonly aportes = signal<AporteHistorial[]>([]);
  readonly filtro = signal<'TODOS' | 'PAGADO' | 'PENDIENTE' | 'VENCIDO'>('TODOS');

  readonly aportesFiltrados = computed(() => {
    const f = this.filtro();
    const lista = this.aportes();
    if (f === 'TODOS') {
      return lista;
    }
    return lista.filter((a) => a.estado === f);
  });

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    const dni = this.auth.usuario()?.dni;
    if (!dni) {
      return;
    }
    this.portal.obtenerHistorialAportes(dni).subscribe({
      next: (data) => this.aportes.set(data),
    });
  }

  badge(estado: string): string {
    const map: Record<string, string> = {
      PAGADO: 'success',
      PENDIENTE: 'primary',
      VENCIDO: 'danger',
    };
    return map[estado] ?? 'secondary';
  }
}
