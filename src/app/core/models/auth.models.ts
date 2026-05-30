export type RolUsuario = 'socio' | 'admin';

export interface UsuarioSesion {
  id: string;
  dni: string;
  nombres: string;
  apellidos: string;
  email: string;
  rol: RolUsuario;
}

export interface LoginRequest {
  dni: string;
  password: string;
}

export interface RegistroRequest {
  nombres: string;
  apellidos: string;
  dni: string;
  email: string;
  telefono: string;
  password: string;
}

export interface AuthResponse {
  exito: boolean;
  mensaje: string;
  usuario?: UsuarioSesion;
}

export interface ConsultaDniResponse {
  dni: string;
  nombres: string;
  apellidos: string;
}
