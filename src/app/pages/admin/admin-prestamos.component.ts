import { DecimalPipe, TitleCasePipe } from '@angular/common';
import { SolesPipe } from '../../core/pipes/soles.pipe';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import type { SolicitudAdmin } from '../../core/models/admin.models';
import { AdminService } from '../../core/services/admin.service';
import { badgeEval } from './admin.utils';

type EstadoSeccion = 'PENDIENTE' | 'APROBADO' | 'RECHAZADO';

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
export class AdminPrestamosComponent implements OnInit {
  private readonly admin = inject(AdminService);
  readonly badgeEval = badgeEval;

  readonly cargando = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);
  readonly solicitudes = signal<SolicitudAdmin[]>([]);
  readonly solicitudSeleccionada = signal<SolicitudAdmin | null>(null);
  readonly observacionesEval = signal('');
  readonly seccionActiva = signal<EstadoSeccion>('PENDIENTE');

  readonly secciones: readonly SeccionPrestamo[] = [
    { id: 'PENDIENTE', label: 'Pendiente' },
    { id: 'APROBADO', label: 'Aprobado' },
    { id: 'RECHAZADO', label: 'Rechazado' },
  ];

  readonly solicitudesFiltradas = computed(() =>
    this.solicitudes().filter(
      (s) => this.normalizarEstado(s.estado_evaluacion) === this.seccionActiva(),
    ),
  );

  ngOnInit(): void {
    this.cargarSolicitudes();
  }

  cargarSolicitudes(): void {
    this.admin.listarSolicitudes().subscribe({
      next: (data) => {
        this.solicitudes.set(data);
        this.actualizarSeleccion(data);
      },
      error: () => this.notificar('No se pudo cargar préstamos.', true),
    });
  }

  cambiarSeccion(seccion: EstadoSeccion): void {
    this.seccionActiva.set(seccion);
    this.actualizarSeleccion(this.solicitudes());
  }

  contarSeccion(seccion: EstadoSeccion): number {
    return this.solicitudes().filter(
      (s) => this.normalizarEstado(s.estado_evaluacion) === seccion,
    ).length;
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
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE: 'Sin solicitudes pendientes de evaluación',
      APROBADO: 'Sin créditos aprobados',
      RECHAZADO: 'Sin solicitudes rechazadas',
    };
    return map[seccion];
  }

  mensajeSeccionVacia(seccion: EstadoSeccion): string {
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE: 'Las nuevas solicitudes de socios aparecerán aquí para su evaluación.',
      APROBADO: 'Al aprobar una solicitud, se generará el cronograma de pagos automáticamente.',
      RECHAZADO: 'Las solicitudes rechazadas quedarán registradas en esta sección.',
    };
    return map[seccion];
  }

  seleccionarSolicitud(s: SolicitudAdmin): void {
    this.solicitudSeleccionada.set(s);
    this.observacionesEval.set('');
    this.admin.obtenerSolicitud(s.id_solicitud).subscribe({
      next: (det) => this.solicitudSeleccionada.set(det),
    });
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
          this.cargarSolicitudes();
        },
        error: (err) => {
          this.cargando.set(false);
          this.notificar(err?.error?.detail ?? 'Error al evaluar.', true);
        },
      });
  }

  private actualizarSeleccion(data: SolicitudAdmin[]): void {
    const seccion = this.seccionActiva();
    const filtradas = data.filter(
      (s) => this.normalizarEstado(s.estado_evaluacion) === seccion,
    );
    const actual = this.solicitudSeleccionada();
    this.solicitudSeleccionada.set(
      actual && filtradas.some((s) => s.id_solicitud === actual.id_solicitud)
        ? actual
        : filtradas[0] ?? null,
    );
  }

  private normalizarEstado(estado: string | null | undefined): EstadoSeccion {
    const valor = (estado ?? 'PENDIENTE').trim().toUpperCase();
    if (valor === 'APROBADO' || valor === 'RECHAZADO') {
      return valor;
    }
    return 'PENDIENTE';
  }

  private notificar(texto: string, error: boolean): void {
    this.mensaje.set(texto);
    this.esError.set(error);
  }
}
