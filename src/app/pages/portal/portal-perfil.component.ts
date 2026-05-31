import { DatePipe } from '@angular/common';
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
import type { PerfilSocio, PerfilSocioUpdate } from '../../core/models/portal.models';
import { AuthService } from '../../core/services/auth.service';
import { PortalSocioService } from '../../core/services/portal-socio.service';

@Component({
  selector: 'ca-portal-perfil',
  standalone: true,
  imports: [FormsModule, DatePipe, SoloNumerosDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './portal-perfil.component.html',
  styleUrl: './portal-shared.scss',
})
export class PortalPerfilComponent implements OnInit {
  private readonly portal = inject(PortalSocioService);
  private readonly auth = inject(AuthService);

  readonly perfil = signal<PerfilSocio | null>(null);
  readonly editando = signal<PerfilSocioUpdate>({
    nombres: '',
    apellidos: '',
    email: '',
    telefono: '',
    aporte_mensual: 50,
  });
  readonly guardando = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);

  readonly telefonoInvalido = computed(
    () =>
      this.editando().telefono.length > 0 &&
      !/^\d{9}$/.test(this.editando().telefono),
  );

  readonly formularioValido = computed(() => {
    const e = this.editando();
    return (
      e.nombres.trim().length >= 2 &&
      e.apellidos.trim().length >= 2 &&
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.email) &&
      /^\d{9}$/.test(e.telefono)
    );
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
          nombres: p.nombres,
          apellidos: p.apellidos,
          email: p.email,
          telefono: p.telefono,
          aporte_mensual: p.aporte_mensual,
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
        this.mensaje.set('Perfil actualizado correctamente.');
        this.esError.set(false);
        this.auth.actualizarDatosSesion({
          nombres: p.nombres,
          apellidos: p.apellidos,
          email: p.email,
        });
      },
      error: () => {
        this.guardando.set(false);
        this.mensaje.set('No se pudo guardar el perfil.');
        this.esError.set(true);
      },
    });
  }
}
