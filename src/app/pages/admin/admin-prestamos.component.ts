import { DecimalPipe, TitleCasePipe } from '@angular/common';
import { SolesPipe } from '../../core/pipes/soles.pipe';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnDestroy,
  OnInit,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Subject, of, switchMap, takeUntil } from 'rxjs';
import type { CuotaCronograma, SolicitudAdmin } from '../../core/models/admin.models';
import { AdminService } from '../../core/services/admin.service';
import { badgeEval } from './admin.utils';

type EstadoSeccion = 'PENDIENTE' | 'APROBADO' | 'RECHAZADO';

const CRONOGRAMA_PAGE_SIZE = 10;

interface SeccionPrestamo {
  id: EstadoSeccion;
  label: string;
}

@Component({
  selector: 'ca-admin-prestamos',
  standalone: true,
  imports: [FormsModule, DecimalPipe, SolesPipe, TitleCasePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-prestamos.component.html',
  styleUrl: './admin-shared.scss',
})
export class AdminPrestamosComponent implements OnInit, OnDestroy {
  private readonly admin = inject(AdminService);
  private readonly cargarSolicitudes$ = new Subject<void>();
  private readonly destruir$ = new Subject<void>();
  readonly badgeEval = badgeEval;

  readonly cargando = signal(false);
  readonly buscando = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);
  readonly solicitudes = signal<SolicitudAdmin[]>([]);
  readonly solicitudSeleccionada = signal<SolicitudAdmin | null>(null);
  readonly observacionesEval = signal('');
  readonly seccionActiva = signal<EstadoSeccion>('PENDIENTE');
  readonly paginaCronograma = signal(1);
  readonly busquedaDni = signal('');
  readonly dniBuscado = signal<string | null>(null);
  readonly conteosSeccion = signal<Record<EstadoSeccion, number>>({
    PENDIENTE: 0,
    APROBADO: 0,
    RECHAZADO: 0,
  });

  readonly CRONOGRAMA_PAGE_SIZE = CRONOGRAMA_PAGE_SIZE;

  readonly secciones: readonly SeccionPrestamo[] = [
    { id: 'PENDIENTE', label: 'Pendiente' },
    { id: 'APROBADO', label: 'Aprobado' },
    { id: 'RECHAZADO', label: 'Rechazado' },
  ];

  readonly requiereBusquedaDni = computed(() => this.seccionActiva() !== 'PENDIENTE');

  readonly solicitudesFiltradas = computed(() => {
    const seccion = this.seccionActiva();
    const dni = this.dniBuscado();
    return this.solicitudes().filter((s) => {
      const estado = (s.estado_evaluacion ?? 'PENDIENTE').trim().toUpperCase();
      if (estado !== seccion) {
        return false;
      }
      if (seccion !== 'PENDIENTE' && dni) {
        return s.dni_usuario === dni;
      }
      return true;
    });
  });

  readonly cronogramaSeleccionado = computed<CuotaCronograma[]>(
    () => this.solicitudSeleccionada()?.cronograma ?? [],
  );

  readonly totalPaginasCronograma = computed(() => {
    const total = this.cronogramaSeleccionado().length;
    return total ? Math.ceil(total / CRONOGRAMA_PAGE_SIZE) : 0;
  });

  readonly cronogramaPaginado = computed(() => {
    const inicio = (this.paginaCronograma() - 1) * CRONOGRAMA_PAGE_SIZE;
    return this.cronogramaSeleccionado().slice(inicio, inicio + CRONOGRAMA_PAGE_SIZE);
  });

  readonly hayPaginaAnteriorCronograma = computed(() => this.paginaCronograma() > 1);
  readonly hayPaginaSiguienteCronograma = computed(
    () => this.paginaCronograma() < this.totalPaginasCronograma(),
  );

  readonly paginasCronograma = computed(() =>
    Array.from({ length: this.totalPaginasCronograma() }, (_, index) => index + 1),
  );

  readonly rangoCronograma = computed(() => {
    const total = this.cronogramaSeleccionado().length;
    if (total === 0) {
      return '0 cuotas';
    }
    const inicio = (this.paginaCronograma() - 1) * CRONOGRAMA_PAGE_SIZE + 1;
    const fin = Math.min(this.paginaCronograma() * CRONOGRAMA_PAGE_SIZE, total);
    return `${inicio}-${fin} de ${total} cuotas`;
  });

  ngOnInit(): void {
    this.cargarSolicitudes$
      .pipe(
        switchMap(() => {
          const seccion = this.seccionActiva();
          if (seccion !== 'PENDIENTE' && !this.dniBuscado()) {
            return of([] as SolicitudAdmin[]);
          }
          this.buscando.set(true);
          const opciones =
            seccion === 'PENDIENTE'
              ? { estado: 'PENDIENTE' as const }
              : { estado: seccion, dni: this.dniBuscado()! };
          return this.admin.listarSolicitudes(opciones);
        }),
        takeUntil(this.destruir$),
      )
      .subscribe({
        next: (data) => {
          this.buscando.set(false);
          this.solicitudes.set(data);
          this.actualizarSeleccion(this.solicitudesFiltradas());
        },
        error: () => {
          this.buscando.set(false);
          this.solicitudes.set([]);
          this.solicitudSeleccionada.set(null);
          this.notificar('No se pudo cargar préstamos.', true);
        },
      });

    this.cargarResumen();
    this.cargarSolicitudes();
  }

  ngOnDestroy(): void {
    this.destruir$.next();
    this.destruir$.complete();
  }

  cargarResumen(): void {
    this.admin.resumenSolicitudes().subscribe({
      next: (resumen) => {
        this.conteosSeccion.set({
          PENDIENTE: resumen.pendiente,
          APROBADO: resumen.aprobado,
          RECHAZADO: resumen.rechazado,
        });
      },
      error: () => {
        this.conteosSeccion.set({ PENDIENTE: 0, APROBADO: 0, RECHAZADO: 0 });
      },
    });
  }

  cargarSolicitudes(): void {
    const seccion = this.seccionActiva();
    if (seccion !== 'PENDIENTE' && !this.dniBuscado()) {
      this.solicitudes.set([]);
      this.solicitudSeleccionada.set(null);
      return;
    }

    this.solicitudes.set([]);
    this.solicitudSeleccionada.set(null);
    this.cargarSolicitudes$.next();
  }

  cambiarSeccion(seccion: EstadoSeccion): void {
    this.seccionActiva.set(seccion);
    this.busquedaDni.set('');
    this.dniBuscado.set(null);
    this.solicitudSeleccionada.set(null);
    this.cargarSolicitudes();
  }

  actualizarBusquedaDni(valor: string): void {
    this.busquedaDni.set(valor.replace(/\D/g, '').slice(0, 8));
  }

  buscarPorDni(): void {
    const dni = this.busquedaDni().trim();
    if (!/^\d{8}$/.test(dni)) {
      this.notificar('Ingrese un DNI válido de 8 dígitos.', true);
      return;
    }
    this.dniBuscado.set(dni);
    this.solicitudes.set([]);
    this.solicitudSeleccionada.set(null);
    this.cargarSolicitudes();
  }

  limpiarBusquedaDni(): void {
    this.busquedaDni.set('');
    this.dniBuscado.set(null);
    this.solicitudSeleccionada.set(null);
    this.cargarSolicitudes();
  }

  contarSeccion(seccion: EstadoSeccion): number {
    return this.conteosSeccion()[seccion];
  }

  claseSeccion(seccion: EstadoSeccion): string {
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE: 'admin-prestamos__tab--pendiente',
      APROBADO: 'admin-prestamos__tab--aprobado',
      RECHAZADO: 'admin-prestamos__tab--rechazado',
    };
    return map[seccion];
  }

  badgeSeccion(seccion: EstadoSeccion): string {
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE: 'warning',
      APROBADO: 'success',
      RECHAZADO: 'danger',
    };
    return map[seccion];
  }

  tituloSeccionVacia(seccion: EstadoSeccion): string {
    if (seccion !== 'PENDIENTE' && !this.dniBuscado()) {
      return 'Busque por DNI';
    }
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE: 'Sin solicitudes pendientes de evaluación',
      APROBADO: 'Sin créditos aprobados para este DNI',
      RECHAZADO: 'Sin solicitudes rechazadas para este DNI',
    };
    return map[seccion];
  }

  mensajeSeccionVacia(seccion: EstadoSeccion): string {
    if (seccion !== 'PENDIENTE' && !this.dniBuscado()) {
      return 'Ingrese el DNI del socio y pulse Buscar para ver sus solicitudes.';
    }
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE: 'Las nuevas solicitudes de socios aparecerán aquí para su evaluación.',
      APROBADO: 'Al aprobar una solicitud, se generará el cronograma de pagos automáticamente.',
      RECHAZADO: 'Las solicitudes rechazadas quedarán registradas en esta sección.',
    };
    return map[seccion];
  }

  seleccionarSolicitud(s: SolicitudAdmin): void {
    this.paginaCronograma.set(1);
    this.solicitudSeleccionada.set(s);
    this.observacionesEval.set('');
    this.admin.obtenerSolicitud(s.id_solicitud).subscribe({
      next: (det) => {
        this.paginaCronograma.set(1);
        this.solicitudSeleccionada.set(det);
      },
    });
  }

  irPaginaCronograma(pagina: number): void {
    if (
      pagina < 1 ||
      pagina > this.totalPaginasCronograma() ||
      pagina === this.paginaCronograma()
    ) {
      return;
    }
    this.paginaCronograma.set(pagina);
  }

  evaluar(decision: 'APROBADO' | 'RECHAZADO'): void {
    const sel = this.solicitudSeleccionada();
    if (!sel || sel.estado_evaluacion !== 'PENDIENTE') {
      return;
    }
    this.cargando.set(true);
    this.admin
      .evaluarSolicitud(sel.id_solicitud, {
        decision,
        observaciones: this.observacionesEval(),
      })
      .subscribe({
        next: (actualizada) => {
          this.cargando.set(false);
          this.solicitudSeleccionada.set(actualizada);
          this.notificar(
            decision === 'APROBADO'
              ? 'Préstamo aprobado. Cronograma generado.'
              : 'Solicitud rechazada.',
            false,
          );
          this.cargarResumen();
          this.cargarSolicitudes();
        },
        error: (err) => {
          this.cargando.set(false);
          this.notificar(err?.error?.detail ?? 'Error al evaluar.', true);
        },
      });
  }

  private actualizarSeleccion(data: SolicitudAdmin[]): void {
    const actual = this.solicitudSeleccionada();
    this.solicitudSeleccionada.set(
      actual && data.some((s) => s.id_solicitud === actual.id_solicitud)
        ? actual
        : data[0] ?? null,
    );
  }

  private notificar(texto: string, error: boolean): void {
    this.mensaje.set(texto);
    this.esError.set(error);
  }
}
