import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

/** El simulador requiere sesión de socio (cuenta activa). */
export const simuladorGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.sesionActiva()) {
    return router.createUrlTree(['/login'], {
      queryParams: { returnUrl: '/simulador' },
    });
  }

  if (auth.esAdministrador()) {
    return router.createUrlTree(['/admin']);
  }

  return true;
};
