import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, delay, of } from 'rxjs';
import { environment } from '../../../environments/environment';
import type {
  AporteHistorial,
  CreditoSocio,
  PerfilSocio,
  PerfilSocioUpdate,
  ResumenCuenta,
} from '../models/portal.models';
import {
  MOCK_APORTES_SOCIO,
  MOCK_CREDITOS_SOCIO,
  MOCK_PERFIL,
  MOCK_RESUMEN_CUENTA,
} from '../mock/frontend-demo.mock';

const API = `${environment.apiUrl}/portal`;

@Injectable({ providedIn: 'root' })
export class PortalSocioService {
  private readonly http = inject(HttpClient);

  obtenerResumen(dni: string): Observable<ResumenCuenta> {
    if (environment.modoSoloFrontend) {
      return of({ ...MOCK_RESUMEN_CUENTA, dni }).pipe(delay(300));
    }
    return this.http.get<ResumenCuenta>(`${API}/${dni}/resumen`);
  }

  obtenerCreditos(dni: string): Observable<CreditoSocio[]> {
    if (environment.modoSoloFrontend) {
      return of([...MOCK_CREDITOS_SOCIO]).pipe(delay(300));
    }
    return this.http.get<CreditoSocio[]>(`${API}/${dni}/creditos`);
  }

  obtenerHistorialAportes(dni: string): Observable<AporteHistorial[]> {
    if (environment.modoSoloFrontend) {
      return of([...MOCK_APORTES_SOCIO]).pipe(delay(300));
    }
    return this.http.get<AporteHistorial[]>(`${API}/${dni}/aportaciones`);
  }

  obtenerPerfil(dni: string): Observable<PerfilSocio> {
    if (environment.modoSoloFrontend) {
      return of({ ...MOCK_PERFIL, dni }).pipe(delay(300));
    }
    return this.http.get<PerfilSocio>(`${API}/${dni}/perfil`);
  }

  actualizarPerfil(dni: string, datos: PerfilSocioUpdate): Observable<PerfilSocio> {
    if (environment.modoSoloFrontend) {
      const actualizado: PerfilSocio = {
        ...MOCK_PERFIL,
        dni,
        ...datos,
      };
      return of(actualizado).pipe(delay(400));
    }
    return this.http.patch<PerfilSocio>(`${API}/${dni}/perfil`, datos);
  }
}
