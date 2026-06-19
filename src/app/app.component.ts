import { Component, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { AuthService } from './core/services/auth.service';

@Component({
  selector: 'ca-root',
  standalone: true,
  imports: [RouterOutlet],
  template: '<router-outlet />',
  styles: `:host { display: block; }`,
})
export class AppComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  constructor() {
    this.auth.restaurarSesion();
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe(() => this.auth.restaurarSesion());
  }
}
