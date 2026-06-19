import { SolesPipe } from '../../core/pipes/soles.pipe';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import type {
  AporteHistorial,
  AportesHistorialFiltro,
} from '../../core/models/portal.models';
import { AuthService } from '../../core/services/auth.service';
import { PortalSocioService } from '../../core/services/portal-socio.service';

const PAGE_SIZE = 15;
type FiltroEstado = 'TODOS' | 'PAGADO' | 'PENDIENTE' | 'VENCIDO';

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

  readonly PAGE_SIZE = PAGE_SIZE;
  readonly aportes = signal<AporteHistorial[]>([]);
  readonly cargando = signal(false);
  readonly filtro = signal<FiltroEstado>('TODOS');
  readonly paginaActual = signal(1);
  readonly totalRegistros = signal(0);
  readonly totalPaginas = signal(0);

  readonly hayPaginaAnterior = computed(() => this.paginaActual() > 1);
  readonly hayPaginaSiguiente = computed(() => this.paginaActual() < this.totalPaginas());
  readonly paginas = computed(() =>
    Array.from({ length: this.totalPaginas() }, (_, index) => index + 1),
  );
  readonly rangoRegistros = computed(() => {
    const total = this.totalRegistros();
    if (total === 0) {
      return '0 registros';
    }
    const inicio = (this.paginaActual() - 1) * PAGE_SIZE + 1;
    const fin = Math.min(this.paginaActual() * PAGE_SIZE, total);
    return `${inicio}-${fin} de ${total}`;
  });

  ngOnInit(): void {
    this.cargar();
  }

  cambiarFiltro(estado: FiltroEstado): void {
    if (this.filtro() === estado) {
      return;
    }
    this.filtro.set(estado);
    this.paginaActual.set(1);
    this.cargar();
  }

  irPagina(pagina: number): void {
    if (pagina < 1 || pagina > this.totalPaginas() || pagina === this.paginaActual()) {
      return;
    }
    this.paginaActual.set(pagina);
    this.cargar();
  }

  cargar(refrescar = false): void {
    const dni = this.auth.usuario()?.dni;
    if (!dni) {
      return;
    }

    const filtro: AportesHistorialFiltro = {
      page: this.paginaActual(),
      page_size: PAGE_SIZE,
      refrescar,
    };
    const estado = this.filtro();
    if (estado !== 'TODOS') {
      filtro.estado = estado;
    }

    this.cargando.set(true);
    this.portal.obtenerHistorialAportes(dni, filtro).subscribe({
      next: (data) => {
        this.aportes.set(data.items);
        this.totalRegistros.set(data.total);
        this.totalPaginas.set(data.total_pages);
        if (data.total_pages > 0 && this.paginaActual() > data.total_pages) {
          this.paginaActual.set(data.total_pages);
          this.cargar(refrescar);
          return;
        }
        this.cargando.set(false);
      },
      error: () => {
        this.cargando.set(false);
      },
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
