import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'ca-register',
  standalone: true,
  imports: [FormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class RegisterComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  private ultimoDniConsultado = '';

  readonly nombres = signal('');
  readonly apellidos = signal('');
  readonly dni = signal('');
  readonly email = signal('');
  readonly telefono = signal('');
  readonly password = signal('');
  readonly confirmarPassword = signal('');
  readonly aceptaTerminos = signal(false);
  readonly mostrarPassword = signal(false);
  readonly enviando = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);

  readonly consultandoDni = signal(false);
  readonly dniValidadoReniec = signal(false);
  readonly avisoDni = signal<string | null>(null);

  readonly dniFormatoInvalido = computed(
    () => this.dni().length > 0 && !/^\d{8}$/.test(this.dni()),
  );

  readonly dniInvalido = computed(
    () =>
      /^\d{8}$/.test(this.dni()) &&
      !this.consultandoDni() &&
      !this.dniValidadoReniec() &&
      !!this.avisoDni(),
  );

  readonly emailInvalido = computed(() => {
    const e = this.email().trim();
    return e.length > 0 && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
  });

  readonly telefonoInvalido = computed(
    () => this.telefono().length > 0 && !/^\d{9}$/.test(this.telefono()),
  );

  readonly passwordInvalida = computed(
    () => this.password().length > 0 && this.password().length < 6,
  );

  readonly confirmacionInvalida = computed(
    () =>
      this.confirmarPassword().length > 0 &&
      this.confirmarPassword() !== this.password(),
  );

  readonly formularioValido = computed(() => {
    const nombres = this.nombres().trim().length >= 2;
    const apellidos = this.apellidos().trim().length >= 2;
    return (
      nombres &&
      apellidos &&
      this.dniValidadoReniec() &&
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email().trim()) &&
      /^\d{9}$/.test(this.telefono()) &&
      this.password().length >= 6 &&
      this.confirmarPassword() === this.password() &&
      this.aceptaTerminos()
    );
  });

  actualizarDni(valor: string): void {
    const dni = valor.replace(/\D/g, '').slice(0, 8);
    this.dni.set(dni);
    this.limpiarMensaje();

    if (dni.length < 8) {
      this.dniValidadoReniec.set(false);
      this.avisoDni.set(null);
      this.ultimoDniConsultado = '';
      return;
    }

    if (dni !== this.ultimoDniConsultado) {
      this.consultarDniReniec(dni);
    }
  }

  private consultarDniReniec(dni: string): void {
    this.ultimoDniConsultado = dni;
    this.consultandoDni.set(true);
    this.dniValidadoReniec.set(false);
    this.avisoDni.set(null);

    this.auth.consultarDni(dni).subscribe({
      next: (datos) => {
        this.consultandoDni.set(false);
        if (!datos) {
          return;
        }
        this.nombres.set(datos.nombres);
        this.apellidos.set(datos.apellidos);
        this.dniValidadoReniec.set(true);
        this.avisoDni.set('Datos obtenidos de RENIEC.');
        this.esError.set(false);
      },
      error: (err: Error) => {
        this.consultandoDni.set(false);
        this.dniValidadoReniec.set(false);
        this.nombres.set('');
        this.apellidos.set('');
        this.avisoDni.set(err.message);
        this.esError.set(true);
      },
    });
  }

  actualizarTelefono(valor: string): void {
    this.telefono.set(valor.replace(/\D/g, '').slice(0, 9));
    this.limpiarMensaje();
  }

  registrar(): void {
    if (!this.formularioValido() || this.enviando()) {
      return;
    }

    this.enviando.set(true);
    this.limpiarMensaje();

    this.auth
      .registrar({
        nombres: this.nombres().trim(),
        apellidos: this.apellidos().trim(),
        dni: this.dni(),
        email: this.email().trim(),
        telefono: this.telefono(),
        password: this.password(),
      })
      .subscribe({
        next: (resp) => {
          this.enviando.set(false);
          if (resp.exito) {
            this.esError.set(false);
            this.mensaje.set(resp.mensaje);
            void this.router.navigate(['/portal']);
            return;
          }
          this.esError.set(true);
          this.mensaje.set(resp.mensaje);
        },
        error: () => {
          this.enviando.set(false);
          this.esError.set(true);
          this.mensaje.set('No se pudo completar el registro. Intente nuevamente.');
        },
      });
  }

  limpiarMensaje(): void {
    this.mensaje.set(null);
    if (!this.avisoDni() || this.dniValidadoReniec()) {
      this.esError.set(false);
    }
  }

  actualizarNombres(valor: string): void {
    this.nombres.set(valor);
    this.limpiarMensaje();
  }

  actualizarApellidos(valor: string): void {
    this.apellidos.set(valor);
    this.limpiarMensaje();
  }

  actualizarEmail(valor: string): void {
    this.email.set(valor);
    this.limpiarMensaje();
  }

  actualizarPassword(valor: string): void {
    this.password.set(valor);
    this.limpiarMensaje();
  }

  actualizarConfirmar(valor: string): void {
    this.confirmarPassword.set(valor);
    this.limpiarMensaje();
  }
}
