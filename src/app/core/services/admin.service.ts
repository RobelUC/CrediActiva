import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, delay, map, of, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import type {
  Aportacion,
  AportacionesFiltro,
  AportacionesPaginadas,
  DashboardAdmin,
  EvaluarSolicitudRequest,
  ReporteAuditoria,
  ResumenAportaciones,
  Socio,
  SocioCreate,
  SocioUpdate,
  SolicitudAdmin,
} from '../models/admin.models';
import {
  MOCK_APORTACIONES,
  MOCK_DASHBOARD,
  MOCK_REPORTE,
  MOCK_SOCIOS,
  MOCK_SOLICITUDES,
} from '../mock/frontend-demo.mock';

const API = `${environment.apiUrl}/admin`;

@Injectable({ providedIn: 'root' })
export class AdminService {
  private readonly http = inject(HttpClient);
  private sociosDemo = [...MOCK_SOCIOS];

  obtenerDashboard(): Observable<DashboardAdmin> {
    if (environment.modoSoloFrontend) {
      return of({ ...MOCK_DASHBOARD }).pipe(delay(300));
    }
    return this.http.get<DashboardAdmin>(`${API}/dashboard`);
  }

  obtenerReporteAuditoria(): Observable<ReporteAuditoria> {
    if (environment.modoSoloFrontend) {
      return of({ ...MOCK_REPORTE }).pipe(delay(300));
    }
    return this.http.get<ReporteAuditoria>(`${API}/reportes/auditoria`);
  }

  listarSocios(): Observable<Socio[]> {
    if (environment.modoSoloFrontend) {
      return of([...this.sociosDemo]).pipe(delay(300));
    }
    return this.http.get<Socio[]>(`${API}/socios`);
  }

  obtenerSocio(idSocio: string): Observable<Socio> {
    if (environment.modoSoloFrontend) {
      const socio = this.sociosDemo.find((s) => s.id_socio === idSocio);
      if (!socio) {
        return throwError(() => ({ error: { detail: 'Socio no encontrado.' } }));
      }
      return of({ ...socio }).pipe(delay(200));
    }
    return this.http.get<Socio>(`${API}/socios/${idSocio}`);
  }

  registrarSocio(datos: SocioCreate): Observable<Socio> {
    if (environment.modoSoloFrontend) {
      if (this.sociosDemo.some((s) => s.dni === datos.dni)) {
        return throwError(() => ({ error: { detail: 'El DNI ya está registrado como socio.' } }));
      }
      const nuevo: Socio = {
        id_socio: 'demo-' + datos.dni,
        ...datos,
        fecha_registro: new Date().toISOString(),
        activo: true,
      };
      this.sociosDemo = [nuevo, ...this.sociosDemo];
      return of(nuevo).pipe(delay(400));
    }
    return this.http.post<Socio>(`${API}/socios`, datos);
  }

  actualizarSocio(idSocio: string, datos: SocioUpdate): Observable<Socio> {
    if (environment.modoSoloFrontend) {
      const idx = this.sociosDemo.findIndex((s) => s.id_socio === idSocio);
      if (idx < 0) {
        return throwError(() => ({ error: { detail: 'Socio no encontrado.' } }));
      }
      const actualizado: Socio = { ...this.sociosDemo[idx], ...datos };
      this.sociosDemo = this.sociosDemo.map((s, i) => (i === idx ? actualizado : s));
      return of(actualizado).pipe(delay(400));
    }
    return this.http.put<Socio>(`${API}/socios/${idSocio}`, datos);
  }

  eliminarSocio(idSocio: string): Observable<Socio> {
    if (environment.modoSoloFrontend) {
      const idx = this.sociosDemo.findIndex((s) => s.id_socio === idSocio);
      if (idx < 0) {
        return throwError(() => ({ error: { detail: 'Socio no encontrado.' } }));
      }
      const desactivado: Socio = { ...this.sociosDemo[idx], activo: false };
      this.sociosDemo = this.sociosDemo.map((s, i) => (i === idx ? desactivado : s));
      return of(desactivado).pipe(delay(400));
    }
    return this.http.delete<Socio>(`${API}/socios/${idSocio}`);
  }

  eliminarSocioPermanente(idSocio: string): Observable<{ mensaje: string }> {
    if (environment.modoSoloFrontend) {
      const idx = this.sociosDemo.findIndex((s) => s.id_socio === idSocio);
      if (idx < 0) {
        return throwError(() => ({ error: { detail: 'Socio no encontrado.' } }));
      }
      this.sociosDemo = this.sociosDemo.filter((s) => s.id_socio !== idSocio);
      return of({ mensaje: 'Socio eliminado definitivamente.' }).pipe(delay(400));
    }
    return this.http.delete<{ mensaje: string }>(`${API}/socios/${idSocio}/permanente`);
  }

  listarSolicitudes(): Observable<SolicitudAdmin[]> {
    if (environment.modoSoloFrontend) {
      return of([...MOCK_SOLICITUDES]).pipe(delay(300));
    }
    return this.http.get<SolicitudAdmin[]>(`${API}/solicitudes`);
  }

  obtenerSolicitud(id: string): Observable<SolicitudAdmin> {
    if (environment.modoSoloFrontend) {
      const sol =
        MOCK_SOLICITUDES.find((s) => s.id_solicitud === id) ?? MOCK_SOLICITUDES[0];
      return of({ ...sol }).pipe(delay(200));
    }
    return this.http.get<SolicitudAdmin>(`${API}/solicitudes/${id}`);
  }

  evaluarSolicitud(
    id: string,
    body: EvaluarSolicitudRequest,
  ): Observable<SolicitudAdmin> {
    if (environment.modoSoloFrontend) {
      const base =
        MOCK_SOLICITUDES.find((s) => s.id_solicitud === id) ?? MOCK_SOLICITUDES[0];
      const actualizada: SolicitudAdmin = {
        ...base,
        estado_evaluacion: body.decision,
        observaciones: body.observaciones || 'Evaluación demo (sin backend).',
      };
      return of(actualizada).pipe(delay(400));
    }
    return this.http.post<SolicitudAdmin>(
      `${API}/solicitudes/${id}/evaluar`,
      body,
    );
  }

  listarAportaciones(filtro: AportacionesFiltro = {}): Observable<AportacionesPaginadas> {
    const page = filtro.page ?? 1;
    const pageSize = filtro.page_size ?? 10;
    const dni = filtro.dni?.trim() || undefined;

    if (environment.modoSoloFrontend) {
      let items = [...MOCK_APORTACIONES];
      if (dni) {
        items = items.filter((a) => a.dni_socio === dni);
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

    const params: Record<string, string | number> = { page, page_size: pageSize };
    if (dni) {
      params['dni'] = dni;
    }
    return this.http
      .get<AportacionesPaginadas | Aportacion[]>(`${API}/aportaciones`, { params })
      .pipe(map((data) => this.normalizarAportacionesPaginadas(data, page, pageSize)));
  }

  private normalizarAportacionesPaginadas(
    data: AportacionesPaginadas | Aportacion[],
    page: number,
    pageSize: number,
  ): AportacionesPaginadas {
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

  resumenAportaciones(dni?: string): Observable<ResumenAportaciones> {
    if (environment.modoSoloFrontend) {
      const items = dni
        ? MOCK_APORTACIONES.filter((a) => a.dni_socio === dni)
        : MOCK_APORTACIONES;
      const pagadas = items.filter((a) => a.estado === 'PAGADO');
      const pendientes = items.filter((a) => a.estado === 'PENDIENTE');
      const vencidas = items.filter((a) => a.estado === 'VENCIDO');
      return of({
        total: items.length,
        pagadas: pagadas.length,
        pendientes: pendientes.length,
        vencidas: vencidas.length,
        monto_pagado: pagadas.reduce((sum, a) => sum + a.monto_cuota, 0),
        monto_pendiente: [...pendientes, ...vencidas].reduce((sum, a) => sum + a.monto_cuota, 0),
        actualizado_en: new Date().toISOString(),
      }).pipe(delay(200));
    }

    const params = dni ? { dni } : undefined;
    return this.http.get<ResumenAportaciones>(`${API}/aportaciones/resumen`, { params });
  }

  registrarPago(idAportacion: string): Observable<Aportacion> {
    if (environment.modoSoloFrontend) {
      const base =
        MOCK_APORTACIONES.find((a) => a.id_aportacion === idAportacion) ??
        MOCK_APORTACIONES[1];
      const pagada: Aportacion = {
        ...base,
        estado: 'PAGADO',
        fecha_pago: new Date().toISOString().slice(0, 10),
      };
      return of(pagada).pipe(delay(400));
    }
    return this.http.post<Aportacion>(
      `${API}/aportaciones/${idAportacion}/pagar`,
      {},
    );
  }
}
