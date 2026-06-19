import { DatePipe } from '@angular/common';
import { SolesPipe } from '../../core/pipes/soles.pipe';
import { SoloNumerosDirective } from '../../core/directives/solo-numeros.directive';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import type { PerfilSocio, PerfilSocioUpdate } from '../../core/models/portal.models';
import { AuthService } from '../../core/services/auth.service';
import { PortalSocioService } from '../../core/services/portal-socio.service';

@Component({
  selector: 'ca-portal-perfil',
  standalone: true,
  imports: [FormsModule, DatePipe, SolesPipe, SoloNumerosDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './portal-perfil.component.html',
  styleUrl: './portal-shared.scss',
})
export class PortalPerfilComponent implements OnInit {
  private readonly portal = inject(PortalSocioService);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly perfil = signal<PerfilSocio | null>(null);
  readonly editando = signal<PerfilSocioUpdate>({
    email: '',
    telefono: '',
  });
  readonly guardando = signal(false);
  readonly eliminando = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);

  readonly telefonoInvalido = computed(
    () =>
      this.editando().telefono.length > 0 &&
      !/^\d{9}$/.test(this.editando().telefono),
  );

  readonly formularioValido = computed(() => {
    const e = this.editando();
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.email.trim()) && /^\d{9}$/.test(e.telefono);
  });

  ngOnInit(): void {
    this.cargarPerfil();
  }

  cargarPerfil(): void {
    const dni = this.auth.usuario()?.dni;
    if (!dni) {
      return;
    }
    this.portal.obtenerPerfil(dni).subscribe({
      next: (p) => {
        this.perfil.set(p);
        this.editando.set({
          email: p.email,
          telefono: p.telefono,
        });
      },
    });
  }

  actualizarCampo<K extends keyof PerfilSocioUpdate>(
    campo: K,
    valor: PerfilSocioUpdate[K],
  ): void {
    this.editando.update((e) => ({ ...e, [campo]: valor }));
    this.mensaje.set(null);
  }

  guardar(): void {
    const dni = this.auth.usuario()?.dni;
    if (!dni || !this.formularioValido()) {
      return;
    }
    this.guardando.set(true);
    this.portal.actualizarPerfil(dni, this.editando()).subscribe({
      next: (p) => {
        this.guardando.set(false);
        this.perfil.set(p);
        this.mensaje.set('Datos de contacto actualizados correctamente.');
        this.esError.set(false);
        this.auth.actualizarDatosSesion({
          nombres: p.nombres,
          apellidos: p.apellidos,
          email: p.email,
        });
      },
      error: (err) => {
        this.guardando.set(false);
        const detalle = err?.error?.detail;
        this.mensaje.set(
          typeof detalle === 'string' ? detalle : 'No se pudo guardar el perfil.',
        );
        this.esError.set(true);
      },
    });
  }

  eliminarCuenta(): void {
    const dni = this.auth.usuario()?.dni;
    if (!dni || this.eliminando()) {
      return;
    }

    const confirmado = confirm(
      '¿Desea eliminar su cuenta de socio?\n\n' +
        'Su acceso al portal se desactivará y no podrá iniciar sesión. ' +
        'Si necesita reactivarla, deberá contactar a la cooperativa.\n\n' +
        'Esta acción no se puede deshacer desde el portal.',
    );
    if (!confirmado) {
      return;
    }

    this.eliminando.set(true);
    this.mensaje.set(null);
    this.portal.eliminarCuenta(dni).subscribe({
      next: (resp) => {
        this.eliminando.set(false);
        this.auth.cerrarSesion();
        void this.router.navigate(['/'], {
          state: { mensajeCuentaEliminada: resp.mensaje },
        });
      },
      error: (err) => {
        this.eliminando.set(false);
        const detalle = err?.error?.detail;
        this.mensaje.set(
          typeof detalle === 'string' ? detalle : 'No se pudo eliminar la cuenta.',
        );
        this.esError.set(true);
      },
    });
  }
}
