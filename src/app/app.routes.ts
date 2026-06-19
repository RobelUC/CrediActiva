import { Routes } from '@angular/router';
import { CrediactivaComponent } from './pages/crediactiva/crediactiva.component';
import { CreditSimulatorComponent } from './components/credit-simulator/credit-simulator.component';
import { AuthLayoutComponent } from './pages/auth/auth-layout.component';
import { LoginComponent } from './pages/auth/login/login.component';
import { RegisterComponent } from './pages/auth/register/register.component';
import { AdminLayoutComponent } from './pages/admin/admin-layout.component';
import { AdminDashboardComponent } from './pages/admin/admin-dashboard.component';
import { AdminSociosComponent } from './pages/admin/admin-socios.component';
import { AdminPrestamosComponent } from './pages/admin/admin-prestamos.component';
import { AdminGenerarCreditoComponent } from './pages/admin/admin-generar-credito.component';
import { AdminAportacionesComponent } from './pages/admin/admin-aportaciones.component';
import { AdminReportesComponent } from './pages/admin/admin-reportes.component';
import { adminGuard } from './core/guards/admin.guard';
import { SocioPortalLayoutComponent } from './pages/portal/socio-portal-layout.component';
import { PortalResumenComponent } from './pages/portal/portal-resumen.component';
import { PortalCreditosComponent } from './pages/portal/portal-creditos.component';
import { PortalAportesComponent } from './pages/portal/portal-aportes.component';
import { PortalPerfilComponent } from './pages/portal/portal-perfil.component';
import { PortalContactosComponent } from './pages/portal/portal-contactos.component';
import { socioGuard } from './core/guards/socio.guard';
import { simuladorGuard } from './core/guards/simulador.guard';

export const routes: Routes = [
  { path: '', component: CrediactivaComponent },
  {
    path: 'login',
    component: AuthLayoutComponent,
    children: [{ path: '', component: LoginComponent }],
  },
  {
    path: 'registro',
    component: AuthLayoutComponent,
    children: [{ path: '', component: RegisterComponent }],
  },
  {
    path: 'simulador',
    component: CreditSimulatorComponent,
    canActivate: [simuladorGuard],
  },
  {
    path: 'portal',
    component: SocioPortalLayoutComponent,
    canActivate: [socioGuard],
    children: [
      { path: '', component: PortalResumenComponent },
      { path: 'creditos', component: PortalCreditosComponent },
      { path: 'aportes', component: PortalAportesComponent },
      { path: 'contactos', component: PortalContactosComponent },
      { path: 'perfil', component: PortalPerfilComponent },
    ],
  },
  {
    path: 'admin',
    component: AdminLayoutComponent,
    canActivate: [adminGuard],
    children: [
      { path: '', component: AdminDashboardComponent },
      { path: 'socios', component: AdminSociosComponent },
      { path: 'generar-credito', component: AdminGenerarCreditoComponent },
      { path: 'prestamos', component: AdminPrestamosComponent },
      { path: 'aportaciones', component: AdminAportacionesComponent },
      { path: 'reportes', component: AdminReportesComponent },
    ],
  },
  { path: '**', redirectTo: '' },
];
