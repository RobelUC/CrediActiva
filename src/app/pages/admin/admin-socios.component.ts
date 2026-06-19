import { ChangeDetectionStrategy, Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SoloNumerosDirective } from '../../core/directives/solo-numeros.directive';
import { SolesPipe } from '../../core/pipes/soles.pipe';
import type { Socio, SocioCreate, SocioUpdate } from '../../core/models/admin.models';
import { AdminService } from '../../core/services/admin.service';

type FiltroEstado = 'todos' | 'activos' | 'inactivos';

const SOCIO_VACIO: SocioCreate = {
  nombres: '',
  apellidos: '',
  dni: '',
  email: '',
  telefono: '',
  aporte_mensual: 50,
  password: '',
};

@Component({
  selector: 'ca-admin-socios',
  standalone: true,
  imports: [FormsModule, SolesPipe, SoloNumerosDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-socios.component.html',
  styleUrl: './admin-shared.scss',
})
export class AdminSociosComponent implements OnInit {
  private readonly admin = inject(AdminService);
  private readonly router = inject(Router);

  readonly cargando = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);
  readonly socios = signal<Socio[]>([]);
  readonly filtroEstado = signal<FiltroEstado>('todos');
  readonly socioEditando = signal<Socio | null>(null);
  readonly formulario = signal<SocioCreate>({ ...SOCIO_VACIO });

  readonly modoEdicion = computed(() => this.socioEditando() !== null);

  readonly sociosFiltrados = computed(() => {
    const lista = this.socios();
    const filtro = this.filtroEstado();
    if (filtro === 'activos') {
      return lista.filter((s) => s.activo);
    }
    if (filtro === 'inactivos') {
      return lista.filter((s) => !s.activo);
    }
    return lista;
  });

  readonly tituloFormulario = computed(() =>
    this.modoEdicion() ? 'Editar socio' : 'Registrar nuevo socio',
  );

  ngOnInit(): void {
    this.cargarSocios();
  }

  cargarSocios(): void {
    this.admin.listarSocios().subscribe({
      next: (data) => this.socios.set(data),
      error: () => this.notificar('No se pudo cargar socios.', true),
    });
  }

  actualizarCampo<K extends keyof SocioCreate>(campo: K, valor: SocioCreate[K]): void {
    this.formulario.update((s) => ({ ...s, [campo]: valor }));
  }

  actualizarActivo(valor: boolean): void {
    const editando = this.socioEditando();
    if (editando) {
      this.socioEditando.set({ ...editando, activo: valor });
    }
  }

  iniciarEdicion(socio: Socio): void {
    this.socioEditando.set({ ...socio });
    this.formulario.set({
      nombres: socio.nombres,
      apellidos: socio.apellidos,
      dni: socio.dni,
      email: socio.email,
      telefono: socio.telefono,
      aporte_mensual: socio.aporte_mensual,
      password: '',
    });
    this.limpiarMensaje();
  }

  cancelarEdicion(): void {
    this.socioEditando.set(null);
    this.formulario.set({ ...SOCIO_VACIO });
    this.limpiarMensaje();
  }

  guardarSocio(): void {
    const datos = this.formulario();
    if (!this.validarFormulario(datos)) {
      return;
    }

    if (this.modoEdicion()) {
      this.actualizarSocio();
      return;
    }
    this.registrarSocio();
  }

  irAGenerarCredito(dni: string): void {
    void this.router.navigate(['/admin/generar-credito'], { queryParams: { dni } });
  }

  registrarSocio(): void {
    const datos = this.formulario();
    this.cargando.set(true);
    this.admin.registrarSocio(datos).subscribe({
      next: () => {
        this.cargando.set(false);
        this.notificar('Socio registrado correctamente.', false);
        const dniRegistrado = datos.dni;
        this.formulario.set({ ...SOCIO_VACIO });
        this.cargarSocios();
        if (
          confirm(
            '¿Desea generar un crédito para este socio ahora?\n\nSe abrirá Generar crédito con su DNI.',
          )
        ) {
          this.irAGenerarCredito(dniRegistrado);
        }
      },
      error: (err) => {
        this.cargando.set(false);
        this.notificar(this.extraerError(err, 'Error al registrar socio.'), true);
      },
    });
  }

  actualizarSocio(): void {
    const editando = this.socioEditando();
    if (!editando) {
      return;
    }

    const datos = this.formulario();
    const payload: SocioUpdate = {
      nombres: datos.nombres.trim(),
      apellidos: datos.apellidos.trim(),
      email: datos.email.trim(),
      telefono: datos.telefono,
      aporte_mensual: datos.aporte_mensual,
      activo: editando.activo,
    };

    this.cargando.set(true);
    this.admin.actualizarSocio(editando.id_socio, payload).subscribe({
      next: () => {
        this.cargando.set(false);
        this.notificar('Socio actualizado correctamente.', false);
        this.cancelarEdicion();
        this.cargarSocios();
      },
      error: (err) => {
        this.cargando.set(false);
        this.notificar(this.extraerError(err, 'Error al actualizar socio.'), true);
      },
    });
  }

  eliminarSocio(socio: Socio): void {
    if (
      !confirm(
        `¿Eliminar al socio ${socio.nombres} ${socio.apellidos}?\n\nEl socio quedará inactivo y no podrá iniciar sesión.`,
      )
    ) {
      return;
    }

    this.cargando.set(true);
    this.admin.eliminarSocio(socio.id_socio).subscribe({
      next: () => {
        this.cargando.set(false);
        this.notificar('Socio eliminado correctamente.', false);
        if (this.socioEditando()?.id_socio === socio.id_socio) {
          this.cancelarEdicion();
        }
        this.cargarSocios();
      },
      error: (err) => {
        this.cargando.set(false);
        this.notificar(this.extraerError(err, 'Error al eliminar socio.'), true);
      },
    });
  }

  reactivarSocio(socio: Socio): void {
    const payload: SocioUpdate = {
      nombres: socio.nombres,
      apellidos: socio.apellidos,
      email: socio.email,
      telefono: socio.telefono,
      aporte_mensual: socio.aporte_mensual,
      activo: true,
    };

    this.cargando.set(true);
    this.admin.actualizarSocio(socio.id_socio, payload).subscribe({
      next: () => {
        this.cargando.set(false);
        this.notificar('Socio reactivado correctamente.', false);
        this.cargarSocios();
      },
      error: (err) => {
        this.cargando.set(false);
        this.notificar(this.extraerError(err, 'Error al reactivar socio.'), true);
      },
    });
  }

  borrarSocioDefinitivo(socio: Socio): void {
    if (
      !confirm(
        `¿Borrar DEFINITIVAMENTE a ${socio.nombres} ${socio.apellidos} (DNI ${socio.dni})?\n\nSe eliminarán también sus solicitudes y aportaciones. Esta acción no se puede deshacer.`,
      )
    ) {
      return;
    }

    this.cargando.set(true);
    this.admin.eliminarSocioPermanente(socio.id_socio).subscribe({
      next: (resp) => {
        this.cargando.set(false);
        this.notificar(resp.mensaje || 'Socio eliminado definitivamente.', false);
        if (this.socioEditando()?.id_socio === socio.id_socio) {
          this.cancelarEdicion();
        }
        this.cargarSocios();
      },
      error: (err) => {
        this.cargando.set(false);
        this.notificar(this.extraerError(err, 'Error al borrar socio definitivamente.'), true);
      },
    });
  }

  private validarFormulario(datos: SocioCreate): boolean {
    if (datos.nombres.trim().length < 2 || datos.apellidos.trim().length < 2) {
      this.notificar('Nombres y apellidos son obligatorios.', true);
      return false;
    }
    if (!/^\d{8}$/.test(datos.dni)) {
      this.notificar('DNI inválido (8 dígitos).', true);
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(datos.email.trim())) {
      this.notificar('Correo electrónico inválido.', true);
      return false;
    }
    if (!/^\d{9}$/.test(datos.telefono)) {
      this.notificar('Celular inválido (9 dígitos).', true);
      return false;
    }
    if (datos.aporte_mensual < 0) {
      this.notificar('El aporte mensual no puede ser negativo.', true);
      return false;
    }
    if (!this.modoEdicion() && datos.password.length < 6) {
      this.notificar('La contraseña debe tener al menos 6 caracteres.', true);
      return false;
    }
    return true;
  }

  private extraerError(err: unknown, fallback: string): string {
    if (err && typeof err === 'object' && 'error' in err) {
      const detalle = (err as { error?: { detail?: string } }).error?.detail;
      if (typeof detalle === 'string') {
        return detalle;
      }
    }
    return fallback;
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
