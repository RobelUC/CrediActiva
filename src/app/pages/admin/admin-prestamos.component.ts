import { CurrencyPipe, DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import type { SolicitudAdmin } from '../../core/models/admin.models';
import { AdminService } from '../../core/services/admin.service';
import { badgeEval } from './admin.utils';

@Component({
  selector: 'ca-admin-prestamos',
  standalone: true,
  imports: [FormsModule, CurrencyPipe, DecimalPipe],
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

  ngOnInit(): void {
    this.cargarSolicitudes();
  }

  cargarSolicitudes(): void {
    this.admin.listarSolicitudes().subscribe({
      next: (data) => this.solicitudes.set(data),
      error: () => this.notificar('No se pudo cargar préstamos.', true),
    });
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

  private notificar(texto: string, error: boolean): void {
    this.mensaje.set(texto);
    this.esError.set(error);
  }
}
