"""Endpoints de registro e inicio de sesión."""

import os
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.repository import obtener_por_dni, obtener_por_dni_con_password, obtener_por_email, guardar_socio
from app.schemas import AuthResponse, LoginAuth, RegistroAuth, UsuarioAuth
from app.security import hash_password, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])

ADMIN_DNI = os.getenv("ADMIN_DNI", "00000000")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def _usuario_desde_socio(socio: dict, rol: str = "socio") -> UsuarioAuth:
    return UsuarioAuth(
        id=socio["id_socio"],
        dni=socio["dni"],
        nombres=socio["nombres"],
        apellidos=socio["apellidos"],
        email=socio["email"],
        rol=rol,  # type: ignore[arg-type]
    )


@router.post("/registro", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def registro_publico(payload: RegistroAuth) -> AuthResponse:
    if obtener_por_dni(payload.dni):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta registrada con este DNI.",
        )

    email_norm = str(payload.email).strip().lower()
    existente_email = obtener_por_email(email_norm)
    if existente_email and existente_email["dni"] != payload.dni:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está asociado a otra cuenta.",
        )

    registro = {
        "id_socio": str(uuid4()),
        "nombres": payload.nombres.strip(),
        "apellidos": payload.apellidos.strip(),
        "dni": payload.dni,
        "email": email_norm,
        "telefono": payload.telefono,
        "aporte_mensual": 50.0,
        "fecha_registro": datetime.now(timezone.utc),
        "activo": True,
        "password_hash": hash_password(payload.password),
    }
    socio = guardar_socio(registro)

    return AuthResponse(
        exito=True,
        mensaje="Registro exitoso. Ya puede operar como socio.",
        usuario=_usuario_desde_socio(socio),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginAuth) -> AuthResponse:
    if payload.dni == ADMIN_DNI:
        if payload.password != ADMIN_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="DNI o contraseña incorrectos.",
            )
        return AuthResponse(
            exito=True,
            mensaje="Bienvenido al panel de administración.",
            usuario=UsuarioAuth(
                id=str(uuid4()),
                dni=ADMIN_DNI,
                nombres="Administrador",
                apellidos="CrediActiva",
                email="admin@crediactiva.pe",
                rol="admin",
            ),
        )

    socio = obtener_por_dni_con_password(payload.dni)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DNI o contraseña incorrectos.",
        )

    if not socio.get("activo", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Su cuenta está desactivada. Contacte a la cooperativa.",
        )

    if not socio.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debe completar el registro en la web para activar su acceso.",
        )

    if not verify_password(payload.password, socio.get("password_hash")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DNI o contraseña incorrectos.",
        )

    return AuthResponse(
        exito=True,
        mensaje="Bienvenido a CrediActiva.",
        usuario=_usuario_desde_socio(socio),
    )
