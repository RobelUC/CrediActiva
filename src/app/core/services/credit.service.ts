import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, delay, map, of, Subject, tap, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { MOCK_CREDITOS_SOCIO, mockSolicitudResponse } from '../mock/frontend-demo.mock';
import type {
  DisponibilidadSolicitud,
  SolicitudRequest,
  SolicitudResponse,
} from '../models/solicitud.models';

const SOLICITUDES_ENDPOINT = `${environment.apiUrl}/solicitudes`;
export const MAX_SOLICITUDES_PENDIENTES = 2;

@Injectable({ providedIn: 'root' })
export class CreditService {
  private readonly http = inject(HttpClient);
  private readonly solicitudesActualizadas = new Subject<void>();
  private readonly demoPendientes = new Map<string, number>();

  /** Emite cuando se crea o elimina una solicitud (para refrescar el portal). */
  readonly solicitudCreada$ = this.solicitudesActualizadas.asObservable();

  constructor() {
    this.inicializarDemoPendientes();
  }

  obtenerDisponibilidad(dni: string): Observable<DisponibilidadSolicitud> {
    if (environment.modoSoloFrontend) {
      const pendientes = this.contarPendientesDemo(dni);
      return of(this.buildDisponibilidad(dni, pendientes)).pipe(delay(150));
    }
    return this.http.get<DisponibilidadSolicitud>(
      `${SOLICITUDES_ENDPOINT}/disponibilidad/${dni}`,
    );
  }

  enviarSolicitud(datos: SolicitudRequest): Observable<SolicitudResponse> {
    if (environment.modoSoloFrontend) {
      const pendientes = this.contarPendientesDemo(datos.dni_usuario);
      if (pendientes >= MAX_SOLICITUDES_PENDIENTES) {
        return throwError(
          () =>
            new HttpErrorResponse({
              status: 400,
              error: {
                detail: `Ya tiene ${pendientes} solicitudes pendientes (máximo ${MAX_SOLICITUDES_PENDIENTES}). Espere a que una sea aprobada o rechazada, o elimine una solicitud pendiente.`,
              },
            }),
        );
      }

      this.demoPendientes.set(datos.dni_usuario, pendientes + 1);
      return of(
        mockSolicitudResponse(
          datos.dni_usuario,
          datos.monto,
          datos.plazo_meses,
          datos.tipo_credito,
        ),
      ).pipe(
        delay(500),
        tap(() => this.solicitudesActualizadas.next()),
      );
    }

    return this.http.post<SolicitudResponse>(SOLICITUDES_ENDPOINT, datos).pipe(
      tap(() => this.solicitudesActualizadas.next()),
    );
  }

  eliminarSolicitud(dni: string, idSolicitud: string): Observable<string> {
    if (environment.modoSoloFrontend) {
      const pendientes = this.contarPendientesDemo(dni);
      if (pendientes <= 0) {
        return throwError(
          () =>
            new HttpErrorResponse({
              status: 404,
              error: { detail: 'Solicitud no encontrada.' },
            }),
        );
      }
      this.demoPendientes.set(dni, Math.max(0, pendientes - 1));
      return of('Solicitud eliminada correctamente.').pipe(
        delay(300),
        tap(() => this.solicitudesActualizadas.next()),
      );
    }

    return this.http
      .delete<{ mensaje: string }>(`${SOLICITUDES_ENDPOINT}/${idSolicitud}`, {
        params: { dni_usuario: dni },
      })
      .pipe(
        map((resp) => resp.mensaje),
        tap(() => this.solicitudesActualizadas.next()),
      );
  }

  private inicializarDemoPendientes(): void {
    for (const credito of MOCK_CREDITOS_SOCIO) {
      if (credito.estado_evaluacion !== 'PENDIENTE') {
        continue;
      }
      const dni = '74874853';
      this.demoPendientes.set(dni, (this.demoPendientes.get(dni) ?? 0) + 1);
    }
  }

  private contarPendientesDemo(dni: string): number {
    return this.demoPendientes.get(dni) ?? 0;
  }

  private buildDisponibilidad(
    dni: string,
    pendientes: number,
  ): DisponibilidadSolicitud {
    return {
      dni_usuario: dni,
      pendientes,
      maximo_pendientes: MAX_SOLICITUDES_PENDIENTES,
      puede_solicitar: pendientes < MAX_SOLICITUDES_PENDIENTES,
    };
  }
}
