import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'ca-socio-portal-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './socio-portal-layout.component.html',
  styleUrl: './socio-portal-layout.component.scss',
})
export class SocioPortalLayoutComponent {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly menuAbierto = signal(false);

  toggleMenu(): void {
    this.menuAbierto.update((abierto) => !abierto);
  }

  cerrarMenu(): void {
    this.menuAbierto.set(false);
  }

  cerrarSesion(): void {
    this.cerrarMenu();
    this.auth.cerrarSesion();
    void this.router.navigate(['/']);
  }
}
