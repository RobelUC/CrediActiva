import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, delay, map, of } from 'rxjs';
import { environment } from '../../../environments/environment';
import type {
  AporteHistorial,
  AportesHistorialFiltro,
  AportesHistorialPaginados,
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

  obtenerCreditoDetalle(dni: string, idSolicitud: string): Observable<CreditoSocio> {
    if (environment.modoSoloFrontend) {
      const credito =
        MOCK_CREDITOS_SOCIO.find((c) => c.id_solicitud === idSolicitud) ?? MOCK_CREDITOS_SOCIO[0];
      return of({ ...credito }).pipe(delay(200));
    }
    return this.http.get<CreditoSocio>(`${API}/${dni}/creditos/${idSolicitud}`);
  }

  obtenerHistorialAportes(
    dni: string,
    filtro: AportesHistorialFiltro = {},
  ): Observable<AportesHistorialPaginados> {
    const page = filtro.page ?? 1;
    const pageSize = filtro.page_size ?? 15;

    if (environment.modoSoloFrontend) {
      let items = [...MOCK_APORTES_SOCIO];
      if (filtro.estado) {
        items = items.filter((a) => a.estado === filtro.estado);
      }
      const total = items.length;
      const totalPages = total ? Math.ceil(total / pageSize) : 0;
      const inicio = (page - 1) * pageSize;
      return of({
        items: items.slice(inicio, inicio + pageSize),
        total,
        page,
        page_size: pageSize,
        total_pages: totalPages,
      }).pipe(delay(300));
    }

    const params: Record<string, string | number | boolean> = {
      page,
      page_size: pageSize,
    };
    if (filtro.estado) {
      params['estado'] = filtro.estado;
    }
    if (filtro.refrescar) {
      params['refrescar'] = true;
    }
    return this.http.get<AportesHistorialPaginados | AporteHistorial[]>(
      `${API}/${dni}/aportaciones`,
      { params },
    ).pipe(
      map((data) => this.normalizarAportesPaginados(data, page, pageSize)),
    );
  }

  private normalizarAportesPaginados(
    data: AportesHistorialPaginados | AporteHistorial[],
    page: number,
    pageSize: number,
  ): AportesHistorialPaginados {
    if (Array.isArray(data)) {
      const total = data.length;
      const totalPages = total ? Math.ceil(total / pageSize) : 0;
      const inicio = (page - 1) * pageSize;
      return {
        items: data.slice(inicio, inicio + pageSize),
        total,
        page,
        page_size: pageSize,
        total_pages: totalPages,
      };
    }
    return data;
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
        email: datos.email,
        telefono: datos.telefono,
      };
      return of(actualizado).pipe(delay(400));
    }
    return this.http.patch<PerfilSocio>(`${API}/${dni}/perfil`, datos);
  }

  eliminarCuenta(dni: string): Observable<{ mensaje: string; dni: string }> {
    if (environment.modoSoloFrontend) {
      return of({
        mensaje: 'Su cuenta ha sido desactivada. Ya no podrá iniciar sesión.',
        dni,
      }).pipe(delay(400));
    }
    return this.http.delete<{ mensaje: string; dni: string }>(`${API}/${dni}/cuenta`);
  }
}
