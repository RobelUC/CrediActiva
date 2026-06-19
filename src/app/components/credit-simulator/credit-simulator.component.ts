import { DecimalPipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnInit,
  output,
  signal,
} from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { resumenASolicitudRequest } from '../../core/mappers/solicitud.mapper';
import type { DisponibilidadSolicitud, SolicitudResponse } from '../../core/models/solicitud.models';
import { AuthService } from '../../core/services/auth.service';
import { CreditService, MAX_SOLICITUDES_PENDIENTES } from '../../core/services/credit.service';
import {
  MONTO_MINIMO,
  PLAZOS_MESES,
  TEA_POR_TIPO,
  type ResumenSimulacion,
  type TipoCredito,
} from './credit-simulator.types';
import {
  calcularCuotaFrancesa,
  formatearPorcentaje,
  formatearSoles,
} from './credit-simulator.utils';

@Component({
  selector: 'ca-credit-simulator',
  standalone: true,
  imports: [DecimalPipe, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './credit-simulator.component.html',
  styleUrl: './credit-simulator.component.scss',
})
export class CreditSimulatorComponent implements OnInit {
  readonly auth = inject(AuthService);
  private readonly creditService = inject(CreditService);

  readonly MONTO_MINIMO = MONTO_MINIMO;
  readonly MAX_SOLICITUDES_PENDIENTES = MAX_SOLICITUDES_PENDIENTES;
  readonly plazosDisponibles = PLAZOS_MESES;
  readonly tiposCredito: readonly TipoCredito[] = [
    'Emprendedor',
    'Vivienda',
    'Agrícola',
  ];

  /** Señales de estado del formulario */
  readonly monto = signal(5_000);
  readonly plazoMeses = signal(24);
  readonly tipoCredito = signal<TipoCredito>('Emprendedor');

  readonly dniSesion = computed(() => this.auth.usuario()?.dni ?? '');
  readonly nombreSesion = computed(() => this.auth.usuario()?.nombres ?? '');

  /** TEA según tipo de crédito */
  readonly tea = computed(() => TEA_POR_TIPO[this.tipoCredito()]);

  readonly esMontoValido = computed(() => this.monto() >= MONTO_MINIMO);

  readonly esDniValido = computed(() => /^\d{8}$/.test(this.dniSesion()));

  readonly formularioValido = computed(
    () => this.esMontoValido() && this.esDniValido() && this.puedeSolicitar(),
  );

  readonly puedeSolicitar = computed(
    () => this.disponibilidad()?.puede_solicitar ?? true,
  );

  readonly mostrarErrorMonto = computed(
    () => this.monto() > 0 && this.monto() < MONTO_MINIMO,
  );

  /** Cuota mensual — amortización francesa; reacciona a monto, plazoMeses y TEA */
  readonly cuotaMensual = computed(() => {
    const meses = this.plazoMeses();
    if (!this.esMontoValido() || meses < 1) {
      return 0;
    }
    return calcularCuotaFrancesa(this.monto(), this.tea(), meses);
  });

  readonly resumen = computed<ResumenSimulacion>(() => ({
    monto: this.monto(),
    plazo: this.plazoMeses(),
    tipoCredito: this.tipoCredito(),
    tea: this.tea(),
    cuotaMensual: this.cuotaMensual(),
  }));

  readonly solicitudCredito = output<ResumenSimulacion>();
  readonly solicitudEnviada = output<SolicitudResponse>();
  readonly errorSolicitud = output<string>();

  readonly enviando = signal(false);
  readonly mensajeExito = signal<string | null>(null);
  readonly errorSolicitudMsg = signal<string | null>(null);
  readonly disponibilidad = signal<DisponibilidadSolicitud | null>(null);

  readonly cuotaFormateada = computed(() => formatearSoles(this.cuotaMensual()));
  readonly teaFormateada = computed(() => formatearPorcentaje(this.tea()));
  readonly montoFormateado = computed(() => formatearSoles(this.monto()));

  readonly slotsPendientes = computed(() =>
    Array.from({ length: this.disponibilidad()?.maximo_pendientes ?? MAX_SOLICITUDES_PENDIENTES }),
  );

  readonly cupoRestante = computed(() => {
    const disp = this.disponibilidad();
    if (!disp) {
      return MAX_SOLICITUDES_PENDIENTES;
    }
    return Math.max(0, disp.maximo_pendientes - disp.pendientes);
  });

  ngOnInit(): void {
    if (this.esDniValido()) {
      this.cargarDisponibilidad();
    }
  }

  private cargarDisponibilidad(): void {
    const dni = this.dniSesion();
    if (!/^\d{8}$/.test(dni)) {
      this.disponibilidad.set(null);
      return;
    }

    this.creditService.obtenerDisponibilidad(dni).subscribe({
      next: (data) => this.disponibilidad.set(data),
    });
  }

  actualizarMonto(valor: string): void {
    const parsed = Number.parseFloat(valor);
    this.monto.set(Number.isFinite(parsed) ? Math.max(0, parsed) : 0);
  }

  actualizarPlazo(valor: number | string): void {
    const meses = typeof valor === 'number' ? valor : Number.parseInt(valor, 10);
    if (Number.isFinite(meses) && meses >= 12 && meses <= 48) {
      this.plazoMeses.set(meses);
    }
  }

  actualizarTipoCredito(valor: string): void {
    this.tipoCredito.set(valor as TipoCredito);
  }

  solicitarCredito(): void {
    if (!this.formularioValido() || this.enviando()) {
      return;
    }

    const resumen = this.resumen();
    this.solicitudCredito.emit(resumen);
    this.enviando.set(true);
    this.mensajeExito.set(null);
    this.errorSolicitudMsg.set(null);

    this.creditService
      .enviarSolicitud(resumenASolicitudRequest(resumen, this.dniSesion()))
      .subscribe({
        next: (respuesta) => {
          this.enviando.set(false);
          this.mensajeExito.set(respuesta.mensaje);
          this.cargarDisponibilidad();
          this.solicitudEnviada.emit(respuesta);
        },
        error: (err: unknown) => {
          this.enviando.set(false);
          const mensaje = this.extraerMensajeError(err);
          this.errorSolicitudMsg.set(mensaje);
          this.cargarDisponibilidad();
          this.errorSolicitud.emit(mensaje);
        },
      });
  }

  private extraerMensajeError(err: unknown): string {
    if (err instanceof HttpErrorResponse) {
      const detalle = err.error?.detail ?? err.error?.mensaje;
      if (typeof detalle === 'string') {
        return detalle;
      }
      if (err.status === 0) {
        return 'No hay conexión con el servidor. Verifique que el backend esté activo.';
      }
    }
    return 'No se pudo registrar la solicitud. Verifique que el servidor esté activo.';
  }
}
