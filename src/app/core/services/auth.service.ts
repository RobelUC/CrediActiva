import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, catchError, delay, of, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import type {
  AuthResponse,
  ConsultaDniResponse,
  LoginRequest,
  RegistroRequest,
  UsuarioSesion,
} from '../models/auth.models';
import {
  DEMO_ADMIN_DNI,
  DEMO_ADMIN_PASSWORD,
  DEMO_DNI,
  DEMO_PASSWORD,
  MOCK_CONSULTA_DNI,
} from '../mock/frontend-demo.mock';

const STORAGE_KEY = 'ca_sesion';
const API_AUTH = `${environment.apiUrl}/auth`;

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly usuarioActual = signal<UsuarioSesion | null>(this.cargarSesion());

  readonly sesionActiva = computed(() => this.usuarioActual() !== null);
  readonly usuario = this.usuarioActual.asReadonly();
  readonly esAdministrador = computed(
    () => this.usuarioActual()?.rol === 'admin',
  );
  readonly modoSoloFrontend = environment.modoSoloFrontend;

  iniciarSesion(credenciales: LoginRequest): Observable<AuthResponse> {
    if (environment.modoSoloFrontend) {
      return of(this.demoLogin(credenciales)).pipe(
        delay(300),
        tap((resp) => {
          if (resp.exito && resp.usuario) {
            this.persistirSesion(resp.usuario);
          }
        }),
      );
    }

    return this.http.post<AuthResponse>(`${API_AUTH}/login`, credenciales).pipe(
      tap((resp) => {
        if (resp.exito && resp.usuario) {
          this.persistirSesion(resp.usuario);
        }
      }),
      catchError((err) => of(this.mapearError(err, 'No se pudo iniciar sesión.'))),
    );
  }

  registrar(datos: RegistroRequest): Observable<AuthResponse> {
    if (environment.modoSoloFrontend) {
      const usuario: UsuarioSesion = {
        id: 'demo-' + datos.dni,
        dni: datos.dni,
        nombres: datos.nombres,
        apellidos: datos.apellidos,
        email: datos.email,
        rol: 'socio',
      };
      const resp: AuthResponse = {
        exito: true,
        mensaje: 'Registro demo completado (sin backend).',
        usuario,
      };
      return of(resp).pipe(
        delay(400),
        tap((r) => {
          if (r.usuario) {
            this.persistirSesion(r.usuario);
          }
        }),
      );
    }

    return this.http.post<AuthResponse>(`${API_AUTH}/registro`, datos).pipe(
      tap((resp) => {
        if (resp.exito && resp.usuario) {
          this.persistirSesion(resp.usuario);
        }
      }),
      catchError((err) => of(this.mapearError(err, 'No se pudo completar el registro.'))),
    );
  }

  consultarDni(dni: string): Observable<ConsultaDniResponse | null> {
    if (environment.modoSoloFrontend) {
      const datos: ConsultaDniResponse =
        dni === DEMO_DNI
          ? MOCK_CONSULTA_DNI
          : {
              dni,
              nombres: 'JUAN CARLOS',
              apellidos: 'PÉREZ GARCÍA',
            };
      return of(datos).pipe(delay(500));
    }

    return this.http.get<ConsultaDniResponse>(`${API_AUTH}/consultar-dni/${dni}`).pipe(
      catchError((err) => {
        const msg = this.mapearError(err, 'No se pudo consultar el DNI.');
        throw new Error(msg.mensaje);
      }),
    );
  }

  cerrarSesion(): void {
    this.usuarioActual.set(null);
    sessionStorage.removeItem(STORAGE_KEY);
  }

  actualizarDatosSesion(
    datos: Pick<UsuarioSesion, 'nombres' | 'apellidos' | 'email'>,
  ): void {
    const actual = this.usuarioActual();
    if (!actual) {
      return;
    }
    const actualizado = { ...actual, ...datos };
    this.persistirSesion(actualizado);
  }

  private demoLogin(credenciales: LoginRequest): AuthResponse {
    if (
      credenciales.dni === DEMO_ADMIN_DNI &&
      credenciales.password === DEMO_ADMIN_PASSWORD
    ) {
      return {
        exito: true,
        mensaje: 'Sesión demo (administrador).',
        usuario: {
          id: 'demo-admin',
          dni: DEMO_ADMIN_DNI,
          nombres: 'Administrador',
          apellidos: 'CrediActiva',
          email: 'admin@crediactiva.pe',
          rol: 'admin',
        },
      };
    }

    if (
      credenciales.dni === DEMO_DNI &&
      credenciales.password === DEMO_PASSWORD
    ) {
      return {
        exito: true,
        mensaje: 'Sesión demo (socio).',
        usuario: {
          id: 'demo-1',
          dni: DEMO_DNI,
          nombres: MOCK_CONSULTA_DNI.nombres,
          apellidos: MOCK_CONSULTA_DNI.apellidos,
          email: 'demo.socio@crediactiva.pe',
          rol: 'socio',
        },
      };
    }

    return {
      exito: false,
      mensaje:
        'Credenciales incorrectas. Use las cuentas demo o regístrese en modo demo.',
    };
  }

  private mapearError(err: unknown, fallback: string): AuthResponse {
    if (!(err instanceof HttpErrorResponse)) {
      return { exito: false, mensaje: fallback };
    }
    if (err.status === 0) {
      return {
        exito: false,
        mensaje: 'No hay conexión con el servidor. Verifique que el backend esté activo.',
      };
    }
    const detalle = err.error?.detail ?? err.error?.mensaje;
    if (typeof detalle === 'string') {
      return { exito: false, mensaje: detalle };
    }
    if (Array.isArray(detalle)) {
      const primero = detalle[0];
      const msg = primero?.msg ?? primero?.message ?? JSON.stringify(primero);
      return { exito: false, mensaje: String(msg) };
    }
    return { exito: false, mensaje: fallback };
  }

  private persistirSesion(usuario: UsuarioSesion): void {
    this.usuarioActual.set(usuario);
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(usuario));
  }

  private cargarSesion(): UsuarioSesion | null {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return null;
      }
      const usuario = JSON.parse(raw) as UsuarioSesion;
      return { ...usuario, rol: usuario.rol ?? 'socio' };
    } catch {
      return null;
    }
  }
}
