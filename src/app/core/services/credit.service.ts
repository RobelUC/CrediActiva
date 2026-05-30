import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, delay, of } from 'rxjs';
import { environment } from '../../../environments/environment';
import { mockSolicitudResponse } from '../mock/frontend-demo.mock';
import type {
  SolicitudRequest,
  SolicitudResponse,
} from '../models/solicitud.models';

const SOLICITUDES_ENDPOINT = `${environment.apiUrl}/solicitudes`;

@Injectable({ providedIn: 'root' })
export class CreditService {
  private readonly http = inject(HttpClient);

  enviarSolicitud(datos: SolicitudRequest): Observable<SolicitudResponse> {
    if (environment.modoSoloFrontend) {
      return of(
        mockSolicitudResponse(
          datos.dni_usuario,
          datos.monto,
          datos.plazo_meses,
          datos.tipo_credito,
        ),
      ).pipe(delay(500));
    }
    return this.http.post<SolicitudResponse>(SOLICITUDES_ENDPOINT, datos);
  }
}
