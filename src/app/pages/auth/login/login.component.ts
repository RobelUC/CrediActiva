import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import {
  DEMO_ADMIN_DNI,
  DEMO_ADMIN_PASSWORD,
  DEMO_DNI,
  DEMO_PASSWORD,
} from '../../../core/mock/frontend-demo.mock';
import { SoloNumerosDirective } from '../../../core/directives/solo-numeros.directive';
import { AuthService } from '../../../core/services/auth.service';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'ca-login',
  standalone: true,
  imports: [FormsModule, RouterLink, SoloNumerosDirective],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  readonly route = inject(ActivatedRoute);

  readonly dni = signal('');
  readonly password = signal('');
  readonly mostrarPassword = signal(false);
  readonly enviando = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);

  readonly dniInvalido = computed(
    () => this.dni().length > 0 && !/^\d{8}$/.test(this.dni()),
  );

  readonly passwordInvalida = computed(
    () => this.password().length > 0 && this.password().length < 6,
  );

  readonly formularioValido = computed(
    () =>
      /^\d{8}$/.test(this.dni()) && this.password().length >= 6,
  );

  readonly requiereSimulador = computed(
    () => this.route.snapshot.queryParamMap.get('returnUrl') === '/simulador',
  );

  readonly modoSoloFrontend = environment.modoSoloFrontend;

  actualizarDni(valor: string): void {
    this.dni.set(valor.replace(/\D/g, '').slice(0, 8));
    this.limpiarMensaje();
  }

  actualizarPassword(valor: string): void {
    this.password.set(valor);
    this.limpiarMensaje();
  }

  alternarVisibilidadPassword(): void {
    this.mostrarPassword.update((v) => !v);
  }

  entrarComoDemo(rol: 'socio' | 'admin'): void {
    if (rol === 'socio') {
      this.dni.set(DEMO_DNI);
      this.password.set(DEMO_PASSWORD);
    } else {
      this.dni.set(DEMO_ADMIN_DNI);
      this.password.set(DEMO_ADMIN_PASSWORD);
    }
    this.iniciarSesion();
  }

  iniciarSesion(): void {
    if (!this.formularioValido() || this.enviando()) {
      return;
    }

    this.enviando.set(true);
    this.limpiarMensaje();

    this.auth
      .iniciarSesion({ dni: this.dni(), password: this.password() })
      .subscribe({
        next: (resp) => {
          this.enviando.set(false);
          if (resp.exito) {
            this.esError.set(false);
            this.mensaje.set(resp.mensaje);
            const destino = this.resolverDestinoTrasLogin(resp.usuario?.rol);
            void this.router.navigateByUrl(destino);
            return;
          }
          this.esError.set(true);
          this.mensaje.set(resp.mensaje);
        },
        error: () => {
          this.enviando.set(false);
          this.esError.set(true);
          this.mensaje.set('No se pudo iniciar sesión. Intente nuevamente.');
        },
      });
  }

  private resolverDestinoTrasLogin(rol?: string): string {
    if (rol === 'admin') {
      return '/admin';
    }

    const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
    if (returnUrl && returnUrl.startsWith('/') && !returnUrl.startsWith('//')) {
      return returnUrl;
    }

    return '/portal';
  }

  private limpiarMensaje(): void {
    this.mensaje.set(null);
    this.esError.set(false);
  }
}
