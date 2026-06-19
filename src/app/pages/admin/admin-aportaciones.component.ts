import { DatePipe } from '@angular/common';
import { SolesPipe } from '../../core/pipes/soles.pipe';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { forkJoin } from 'rxjs';
import type { Aportacion, ResumenAportaciones } from '../../core/models/admin.models';
import { SoloNumerosDirective } from '../../core/directives/solo-numeros.directive';
import { AdminService } from '../../core/services/admin.service';
import { badgeAport } from './admin.utils';

const PAGE_SIZE = 10;

interface SocioCreditoAprobado {
  dni: string;
  nombre: string;
}

@Component({
  selector: 'ca-admin-aportaciones',
  standalone: true,
  imports: [DatePipe, SolesPipe, SoloNumerosDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-aportaciones.component.html',
  styleUrl: './admin-shared.scss',
})
export class AdminAportacionesComponent implements OnInit {
  private readonly admin = inject(AdminService);
  readonly badgeAport = badgeAport;
  readonly PAGE_SIZE = PAGE_SIZE;

  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);
  readonly aportaciones = signal<Aportacion[]>([]);
  readonly resumen = signal<ResumenAportaciones | null>(null);
  readonly sociosAprobados = signal<SocioCreditoAprobado[]>([]);
  readonly cargando = signal(false);

  readonly dniBusqueda = signal('');
  readonly dniFiltro = signal('');
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
  readonly dniBusquedaInvalido = computed(
    () => this.dniBusqueda().length > 0 && !/^\d{8}$/.test(this.dniBusqueda()),
  );
  readonly nombreSocioFiltrado = computed(() => {
    const dni = this.dniFiltro();
    if (!dni) {
      return null;
    }
    return this.sociosAprobados().find((s) => s.dni === dni)?.nombre ?? null;
  });

  ngOnInit(): void {
    this.cargarSociosConCreditoAprobado();
  }

  private cargarSociosConCreditoAprobado(): void {
    forkJoin({
      solicitudes: this.admin.listarSolicitudes(),
      socios: this.admin.listarSocios(),
    }).subscribe({
      next: ({ solicitudes, socios }) => {
        const dnisAprobados = [
          ...new Set(
            solicitudes
              .filter((s) => s.estado_evaluacion === 'APROBADO')
              .map((s) => s.dni_usuario),
          ),
        ];

        const sociosPorDni = new Map(socios.map((s) => [s.dni, `${s.nombres} ${s.apellidos}`]));
        this.sociosAprobados.set(
          dnisAprobados
            .sort()
            .map((dni) => ({
              dni,
              nombre: sociosPorDni.get(dni) ?? `Socio ${dni}`,
            })),
        );
      },
    });
  }

  actualizarDniBusqueda(valor: string): void {
    this.dniBusqueda.set(valor.replace(/\D/g, '').slice(0, 8));
    this.mensaje.set(null);
    this.esError.set(false);
  }

  buscarPorDni(): void {
    const dni = this.dniBusqueda().trim();
    this.mensaje.set(null);
    this.esError.set(false);

    if (!dni) {
      this.mensaje.set('Ingrese un DNI de 8 dígitos para consultar aportaciones.');
      this.esError.set(true);
      return;
    }

    if (!/^\d{8}$/.test(dni)) {
      this.mensaje.set('Ingrese un DNI válido de 8 dígitos.');
      this.esError.set(true);
      return;
    }

    const socio = this.sociosAprobados().find((s) => s.dni === dni);
    if (!socio) {
      this.mensaje.set('Este DNI no tiene créditos aprobados.');
      this.esError.set(true);
      return;
    }

    this.dniFiltro.set(dni);
    this.paginaActual.set(1);
    this.refrescar();
  }

  irPagina(pagina: number): void {
    if (pagina < 1 || pagina > this.totalPaginas() || pagina === this.paginaActual()) {
      return;
    }
    this.paginaActual.set(pagina);
    this.refrescar();
  }

  refrescar(recargarSocios = false): void {
    if (recargarSocios) {
      this.cargarSociosConCreditoAprobado();
    }

    const dni = this.dniFiltro();
    if (!dni) {
      return;
    }

    this.cargando.set(true);

    this.admin
      .listarAportaciones({
        dni,
        page: this.paginaActual(),
        page_size: PAGE_SIZE,
      })
      .subscribe({
        next: (data) => {
          this.aportaciones.set(data.items);
          this.totalRegistros.set(data.total);
          this.totalPaginas.set(data.total_pages);
          if (data.total_pages > 0 && this.paginaActual() > data.total_pages) {
            this.paginaActual.set(data.total_pages);
            this.refrescar();
            return;
          }
          this.cargando.set(false);
        },
        error: () => {
          this.cargando.set(false);
        },
      });

    this.admin.resumenAportaciones(dni).subscribe({
      next: (r) => this.resumen.set(r),
    });
  }

  registrarPago(a: Aportacion): void {
    if (a.estado === 'PAGADO') {
      return;
    }
    this.admin.registrarPago(a.id_aportacion).subscribe({
      next: () => {
        this.mensaje.set('Pago registrado.');
        this.esError.set(false);
        this.refrescar();
      },
      error: () => {
        this.mensaje.set('Error al registrar pago.');
        this.esError.set(true);
      },
    });
  }
}
