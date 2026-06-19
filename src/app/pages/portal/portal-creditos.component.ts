import { DatePipe, DecimalPipe, TitleCasePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { SolesPipe } from '../../core/pipes/soles.pipe';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  DestroyRef,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router } from '@angular/router';
import { filter, merge, startWith } from 'rxjs';
import type { CreditoSocio } from '../../core/models/portal.models';
import { AuthService } from '../../core/services/auth.service';
import { CreditService } from '../../core/services/credit.service';
import { PortalSocioService } from '../../core/services/portal-socio.service';

type EstadoSeccion = 'PENDIENTE' | 'APROBADO' | 'RECHAZADO';

interface SeccionCredito {
  id: EstadoSeccion;
  label: string;
}

@Component({
  selector: 'ca-portal-creditos',
  standalone: true,
  imports: [DatePipe, DecimalPipe, SolesPipe, TitleCasePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './portal-creditos.component.html',
  styleUrl: './portal-shared.scss',
})
export class PortalCreditosComponent implements OnInit {
  private readonly portal = inject(PortalSocioService);
  private readonly auth = inject(AuthService);
  private readonly creditService = inject(CreditService);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);

  readonly creditos = signal<CreditoSocio[]>([]);
  readonly seleccionado = signal<CreditoSocio | null>(null);
  readonly seccionActiva = signal<EstadoSeccion>('PENDIENTE');
  readonly cargando = signal(false);
  readonly cargandoDetalle = signal(false);
  readonly eliminando = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly error = signal<string | null>(null);

  readonly secciones: readonly SeccionCredito[] = [
    { id: 'PENDIENTE', label: 'Pendiente' },
    { id: 'APROBADO', label: 'Aprobado' },
    { id: 'RECHAZADO', label: 'Rechazado' },
  ];

  readonly creditosFiltrados = computed(() =>
    this.creditos().filter(
      (c) => this.normalizarEstado(c.estado_evaluacion) === this.seccionActiva(),
    ),
  );

  ngOnInit(): void {
    merge(
      this.router.events.pipe(
        filter((event): event is NavigationEnd => event instanceof NavigationEnd),
        filter((event) => event.urlAfterRedirects.includes('/portal/creditos')),
      ),
      this.creditService.solicitudCreada$,
    )
      .pipe(startWith(null), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.cargarCreditos());
  }

  private cargarCreditos(): void {
    const dni = this.auth.usuario()?.dni;
    if (!dni) {
      return;
    }

    this.cargando.set(true);
    this.portal.obtenerCreditos(dni).subscribe({
      next: (data) => {
        this.creditos.set(data);
        this.actualizarSeleccion(data);
        this.cargando.set(false);
      },
      error: () => {
        this.cargando.set(false);
      },
    });
  }

  cambiarSeccion(seccion: EstadoSeccion): void {
    this.seccionActiva.set(seccion);
    this.mensaje.set(null);
    this.error.set(null);

    const filtrados = this.filtrarPorSeccion(this.creditos(), seccion);
    const actual = this.seleccionado();
    this.seleccionado.set(
      actual && filtrados.some((c) => c.id_solicitud === actual.id_solicitud)
        ? actual
        : filtrados[0] ?? null,
    );
    const seleccionado = this.seleccionado();
    if (seleccionado) {
      this.cargarDetalleSiFalta(seleccionado);
    }
  }

  contarSeccion(seccion: EstadoSeccion): number {
    return this.creditos().filter(
      (c) => this.normalizarEstado(c.estado_evaluacion) === seccion,
    ).length;
  }

  seccionVacia(): boolean {
    return this.creditosFiltrados().length === 0;
  }

  claseSeccion(seccion: EstadoSeccion): string {
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE: 'portal-creditos__tab--pendiente',
      APROBADO: 'portal-creditos__tab--aprobado',
      RECHAZADO: 'portal-creditos__tab--rechazado',
    };
    return map[seccion];
  }

  claseEmptySeccion(): string {
    return `portal-creditos__empty--${this.seccionActiva().toLowerCase()}`;
  }

  tituloSeccionVacia(seccion: EstadoSeccion): string {
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE: 'Sin solicitudes pendientes',
      APROBADO: 'Sin créditos aprobados',
      RECHAZADO: 'Sin solicitudes rechazadas',
    };
    return map[seccion];
  }

  private actualizarSeleccion(data: CreditoSocio[]): void {
    const seccion = this.seccionActiva();
    const filtrados = this.filtrarPorSeccion(data, seccion);
    const actual = this.seleccionado();
    const seleccion =
      actual && filtrados.some((c) => c.id_solicitud === actual.id_solicitud)
        ? actual
        : filtrados[0] ?? null;
    this.seleccionado.set(seleccion);
    if (seleccion) {
      this.cargarDetalleSiFalta(seleccion);
    }
  }

  private filtrarPorSeccion(data: CreditoSocio[], seccion: EstadoSeccion): CreditoSocio[] {
    return data.filter((c) => this.normalizarEstado(c.estado_evaluacion) === seccion);
  }

  seleccionar(c: CreditoSocio): void {
    this.seleccionado.set(c);
    this.mensaje.set(null);
    this.error.set(null);
    this.cargarDetalleSiFalta(c);
  }

  private cargarDetalleSiFalta(credito: CreditoSocio): void {
    if (
      this.normalizarEstado(credito.estado_evaluacion) !== 'APROBADO' ||
      credito.cronograma.length > 0 ||
      this.cargandoDetalle()
    ) {
      return;
    }

    const dni = this.auth.usuario()?.dni;
    if (!dni) {
      return;
    }

    this.cargandoDetalle.set(true);
    this.portal.obtenerCreditoDetalle(dni, credito.id_solicitud).subscribe({
      next: (detalle) => {
        const actualizados = this.creditos().map((c) =>
          c.id_solicitud === detalle.id_solicitud ? detalle : c,
        );
        this.creditos.set(actualizados);
        if (this.seleccionado()?.id_solicitud === detalle.id_solicitud) {
          this.seleccionado.set(detalle);
        }
        this.cargandoDetalle.set(false);
      },
      error: () => {
        this.cargandoDetalle.set(false);
      },
    });
  }

  puedeEliminar(c: CreditoSocio): boolean {
    return this.normalizarEstado(c.estado_evaluacion) === 'PENDIENTE';
  }

  private normalizarEstado(estado: string | null | undefined): string {
    return (estado ?? 'PENDIENTE').trim().toUpperCase();
  }

  eliminarCredito(credito: CreditoSocio): void {
    const dni = this.auth.usuario()?.dni;
    if (!dni || !this.puedeEliminar(credito) || this.eliminando()) {
      return;
    }

    this.seleccionado.set(credito);

    const confirmar = confirm(
      '¿Desea eliminar esta solicitud pendiente? Esta acción no se puede deshacer.',
    );
    if (!confirmar) {
      return;
    }

    this.eliminando.set(true);
    this.mensaje.set(null);
    this.error.set(null);

    this.creditService.eliminarSolicitud(dni, credito.id_solicitud).subscribe({
      next: (msg) => {
        this.eliminando.set(false);
        this.mensaje.set(msg);
        this.cargarCreditos();
      },
      error: (err: unknown) => {
        this.eliminando.set(false);
        this.error.set(this.extraerMensajeError(err));
      },
    });
  }

  private extraerMensajeError(err: unknown): string {
    if (err instanceof HttpErrorResponse) {
      const detalle = err.error?.detail ?? err.error?.mensaje;
      if (typeof detalle === 'string') {
        return detalle;
      }
    }
    return 'No se pudo eliminar la solicitud.';
  }

  badgeEstado(estado: string): string {
    return this.badgeEstadoDe(this.normalizarEstado(estado));
  }

  badgeSeccion(seccion: EstadoSeccion): string {
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE: 'warning',
      APROBADO: 'success',
      RECHAZADO: 'danger',
    };
    return map[seccion];
  }

  mensajeSeccionVacia(seccion: EstadoSeccion): string {
    const map: Record<EstadoSeccion, string> = {
      PENDIENTE:
        'No tiene solicitudes en evaluación. Use el simulador para enviar una nueva solicitud.',
      APROBADO:
        'Cuando el administrador apruebe una solicitud, aparecerá aquí con su cronograma de pagos.',
      RECHAZADO:
        'Si una solicitud no es aprobada, podrá consultarla en esta sección.',
    };
    return map[seccion];
  }

  mensajeGlobalVacio(): string {
    return 'Aún no tiene solicitudes registradas. Use el simulador para solicitar un crédito.';
  }

  private badgeEstadoDe(estado: string): string {
    const map: Record<string, string> = {
      APROBADO: 'success',
      PENDIENTE: 'warning',
      RECHAZADO: 'danger',
    };
    return map[estado] ?? 'secondary';
  }
}
