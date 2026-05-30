import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const socioGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.sesionActiva()) {
    return router.createUrlTree(['/login']);
  }

  if (auth.esAdministrador()) {
    return router.createUrlTree(['/admin']);
  }

  return true;
};
