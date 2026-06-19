import { DecimalPipe } from '@angular/common';
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
import { ActivatedRoute, RouterLink } from '@angular/router';
import type { Socio } from '../../core/models/admin.models';
import type { TipoCredito } from '../../core/models/credito.types';
import { AdminService } from '../../core/services/admin.service';
import {
  MONTO_MINIMO,
  PLAZOS_MESES,
  TEA_POR_TIPO,
} from '../../components/credit-simulator/credit-simulator.types';
import {
  calcularCuotaFrancesa,
  formatearPorcentaje,
  formatearSoles,
} from '../../components/credit-simulator/credit-simulator.utils';

@Component({
  selector: 'ca-admin-generar-credito',
  standalone: true,
  imports: [FormsModule, DecimalPipe, SolesPipe, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-generar-credito.component.html',
  styleUrl: './admin-shared.scss',
})
export class AdminGenerarCreditoComponent implements OnInit {
  private readonly admin = inject(AdminService);
  private readonly route = inject(ActivatedRoute);

  readonly MONTO_MINIMO = MONTO_MINIMO;
  readonly plazosDisponibles = PLAZOS_MESES;
  readonly tiposCredito: readonly TipoCredito[] = ['Emprendedor', 'Vivienda', 'Agrícola'];

  readonly socios = signal<Socio[]>([]);
  readonly busquedaDni = signal('');
  readonly resultadosBusqueda = signal<Socio[]>([]);
  readonly socioSeleccionado = signal<Socio | null>(null);
  readonly buscando = signal(false);
  readonly busquedaRealizada = signal(false);

  readonly generandoCredito = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);

  readonly montoCredito = signal(5_000);
  readonly plazoCredito = signal(24);
  readonly tipoCredito = signal<TipoCredito>('Emprendedor');
  readonly observacionesCredito = signal('');

  readonly dniCredito = computed(() => this.socioSeleccionado()?.dni ?? '');

  readonly teaCredito = computed(() => TEA_POR_TIPO[this.tipoCredito()]);

  readonly cuotaCredito = computed(() => {
    const monto = this.montoCredito();
    const plazo = this.plazoCredito();
    if (monto < MONTO_MINIMO || plazo < 1) {
      return 0;
    }
    return calcularCuotaFrancesa(monto, this.teaCredito(), plazo);
  });

  readonly cuotaCreditoFormateada = computed(() => formatearSoles(this.cuotaCredito()));
  readonly teaCreditoFormateada = computed(() => formatearPorcentaje(this.teaCredito()));

  readonly formularioCreditoValido = computed(
    () =>
      !!this.socioSeleccionado()?.activo &&
      /^\d{8}$/.test(this.dniCredito()) &&
      this.montoCredito() >= MONTO_MINIMO &&
      this.plazoCredito() >= 12 &&
      this.plazoCredito() <= 48,
  );

  ngOnInit(): void {
    const dniQuery = this.route.snapshot.queryParamMap.get('dni');
    if (dniQuery && /^\d{8}$/.test(dniQuery)) {
      this.busquedaDni.set(dniQuery);
    }
    this.cargarSocios();
  }

  cargarSocios(): void {
    this.admin.listarSocios().subscribe({
      next: (data) => {
        this.socios.set(data);
        if (this.busquedaDni().length >= 1) {
          this.buscarSocioPorDni();
        }
      },
      error: () => this.notificar('No se pudo cargar el listado de socios.', true),
    });
  }

  actualizarBusquedaDni(valor: string): void {
    this.busquedaDni.set(valor.replace(/\D/g, '').slice(0, 8));
    this.busquedaRealizada.set(false);
    this.resultadosBusqueda.set([]);
  }

  buscarSocioPorDni(): void {
    const termino = this.busquedaDni().trim();
    if (!termino) {
      this.notificar('Ingrese un DNI para buscar.', true);
      return;
    }

    this.buscando.set(true);
    this.busquedaRealizada.set(true);
    this.socioSeleccionado.set(null);

    const coincidencias = this.socios().filter((socio) => socio.dni.includes(termino));
    this.resultadosBusqueda.set(coincidencias);
    this.buscando.set(false);

    if (coincidencias.length === 1 && coincidencias[0].dni === termino) {
      this.seleccionarSocio(coincidencias[0]);
    }
  }

  seleccionarSocio(socio: Socio): void {
    this.socioSeleccionado.set(socio);
    this.busquedaDni.set(socio.dni);
    this.resultadosBusqueda.set([]);
    this.busquedaRealizada.set(false);
    this.limpiarMensaje();

    if (!socio.activo) {
      this.notificar('El socio está inactivo. Reactívelo antes de generar un crédito.', true);
    }
  }

  limpiarSeleccion(): void {
    this.socioSeleccionado.set(null);
    this.busquedaDni.set('');
    this.resultadosBusqueda.set([]);
    this.busquedaRealizada.set(false);
  }

  actualizarMontoCredito(valor: string): void {
    const parsed = Number.parseFloat(valor);
    this.montoCredito.set(Number.isFinite(parsed) ? Math.max(0, parsed) : 0);
  }

  actualizarPlazoCredito(valor: number | string): void {
    const meses = typeof valor === 'number' ? valor : Number.parseInt(valor, 10);
    if (Number.isFinite(meses) && meses >= 12 && meses <= 48) {
      this.plazoCredito.set(meses);
    }
  }

  actualizarTipoCredito(valor: string): void {
    this.tipoCredito.set(valor as TipoCredito);
  }

  generarCreditoAdmin(): void {
    if (!this.formularioCreditoValido() || this.generandoCredito()) {
      return;
    }

    this.generandoCredito.set(true);
    this.admin
      .crearCreditoAdmin({
        dni_usuario: this.dniCredito(),
        monto: this.montoCredito(),
        plazo_meses: this.plazoCredito(),
        tipo_credito: this.tipoCredito(),
        observaciones:
          this.observacionesCredito().trim() ||
          'Crédito generado y aprobado desde el panel administrativo.',
      })
      .subscribe({
        next: () => {
          this.generandoCredito.set(false);
          this.notificar(
            'Crédito generado y aprobado. Cronograma y cuotas creados automáticamente.',
            false,
          );
        },
        error: (err) => {
          this.generandoCredito.set(false);
          this.notificar(err?.error?.detail ?? 'No se pudo generar el crédito.', true);
        },
      });
  }

  private notificar(texto: string, error: boolean): void {
    this.mensaje.set(texto);
    this.esError.set(error);
  }

  private limpiarMensaje(): void {
    this.mensaje.set(null);
    this.esError.set(false);
  }
}
