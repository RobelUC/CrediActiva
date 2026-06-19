import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException, status

from app.auth_routes import router as auth_router
from app.consulta_dni import router as consulta_dni_router
from app.database import init_db
from app.demo_data import sembrar_cuentas_demo
from app.roles_env import aplicar_roles_desde_env
from app.repository import (
    actualizar_password_socio,
    actualizar_socio,
    borrar_socio_permanente,
    eliminar_socio,
    guardar_socio,
    listar_socios,
    obtener_por_dni,
    obtener_por_email,
    obtener_por_id,
)
from app.schemas import PerfilSocioUpdate, SocioCreate, SocioPasswordUpdate, SocioResponse, SocioUpdate
from app.security import hash_password

CREDIT_SERVICE_URL = os.getenv("CREDIT_SERVICE_URL", "http://localhost:8002")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8003")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    sembrar_cuentas_demo()
    aplicar_roles_desde_env()
    yield


app = FastAPI(title="Auth Service", version="1.0.0", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(consulta_dni_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "servicio": "auth-service"}


@app.post("/api/v1/admin/socios", response_model=SocioResponse, status_code=status.HTTP_201_CREATED)
def registrar_socio(payload: SocioCreate) -> SocioResponse:
    if obtener_por_dni(payload.dni):
        raise HTTPException(status_code=409, detail="El DNI ya está registrado como socio.")

    registro = {
        "id_socio": str(uuid4()),
        "nombres": payload.nombres.strip(),
        "apellidos": payload.apellidos.strip(),
        "dni": payload.dni,
        "email": payload.email.strip().lower(),
        "telefono": payload.telefono,
        "aporte_mensual": round(payload.aporte_mensual, 2),
        "fecha_registro": datetime.now(timezone.utc),
        "activo": True,
        "password_hash": hash_password(payload.password),
    }
    return SocioResponse(**guardar_socio(registro))


@app.get("/api/v1/admin/socios", response_model=list[SocioResponse])
def obtener_socios() -> list[SocioResponse]:
    return [SocioResponse(**s) for s in listar_socios()]


@app.get("/api/v1/admin/socios/{id_socio}", response_model=SocioResponse)
def obtener_socio(id_socio: str) -> SocioResponse:
    socio = obtener_por_id(id_socio)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    return SocioResponse(**socio)


@app.put("/api/v1/admin/socios/{id_socio}", response_model=SocioResponse)
def editar_socio(id_socio: str, payload: SocioUpdate) -> SocioResponse:
    if not obtener_por_id(id_socio):
        raise HTTPException(status_code=404, detail="Socio no encontrado.")

    existente = obtener_por_email(payload.email.strip().lower())
    if existente and existente["id_socio"] != id_socio:
        raise HTTPException(status_code=409, detail="El correo ya está registrado en otro socio.")

    try:
        actualizado = actualizar_socio(
            id_socio,
            {
                "nombres": payload.nombres,
                "apellidos": payload.apellidos,
                "email": payload.email,
                "telefono": payload.telefono,
                "aporte_mensual": payload.aporte_mensual,
                "activo": payload.activo,
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if not actualizado:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    return SocioResponse(**actualizado)


@app.patch("/api/v1/admin/socios/{id_socio}/password", response_model=SocioResponse)
def cambiar_password_socio(id_socio: str, payload: SocioPasswordUpdate) -> SocioResponse:
    socio = obtener_por_id(id_socio)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    if socio.get("rol") == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La contraseña del administrador se gestiona por configuración del sistema.",
        )

    actualizado = actualizar_password_socio(id_socio, hash_password(payload.password))
    if not actualizado:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    return SocioResponse(**actualizado)


@app.delete("/api/v1/admin/socios/{id_socio}", response_model=SocioResponse)
def desactivar_socio(id_socio: str) -> SocioResponse:
    socio = eliminar_socio(id_socio)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    return SocioResponse(**socio)


@app.delete("/api/v1/admin/socios/{id_socio}/permanente")
def eliminar_socio_permanente(id_socio: str) -> dict:
    socio = obtener_por_id(id_socio)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")

    if socio.get("rol") == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede eliminar definitivamente una cuenta administrador.",
        )

    dni = socio["dni"]
    try:
        with httpx.Client(timeout=15.0) as client:
            resp_pago = client.delete(f"{PAYMENT_SERVICE_URL}/internal/datos-socio/{dni}")
            resp_credito = client.delete(f"{CREDIT_SERVICE_URL}/internal/datos-socio/{dni}")
            if resp_pago.status_code >= 400 or resp_credito.status_code >= 400:
                raise HTTPException(
                    status_code=502,
                    detail="No se pudieron eliminar los datos relacionados del socio.",
                )
            datos_pago = resp_pago.json()
            datos_credito = resp_credito.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Error de comunicación con microservicios al eliminar datos del socio.",
        ) from exc

    eliminado = borrar_socio_permanente(id_socio)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")

    return {
        "mensaje": "Socio eliminado definitivamente.",
        "socio": SocioResponse(**eliminado),
        "aportaciones_eliminadas": datos_pago.get("aportaciones_eliminadas", 0),
        "solicitudes_eliminadas": datos_credito.get("solicitudes_eliminadas", 0),
    }


@app.get("/internal/socios", response_model=list[SocioResponse])
def socios_internos() -> list[SocioResponse]:
    return [SocioResponse(**s) for s in listar_socios()]


@app.get("/internal/socios/{dni}", response_model=SocioResponse)
def socio_interno(dni: str) -> SocioResponse:
    socio = obtener_por_dni(dni)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    return SocioResponse(**socio)


@app.get("/api/v1/portal/{dni}/perfil")
def perfil_socio(dni: str) -> dict:
    socio = obtener_por_dni(dni)
    if socio:
        return {
            "id_socio": socio["id_socio"],
            "nombres": socio["nombres"],
            "apellidos": socio["apellidos"],
            "dni": socio["dni"],
            "email": socio["email"],
            "telefono": socio.get("telefono", ""),
            "aporte_mensual": socio.get("aporte_mensual", 50.0),
            "fecha_registro": socio.get("fecha_registro"),
        }
    return {
        "id_socio": None,
        "nombres": "Socio",
        "apellidos": "CrediActiva",
        "dni": dni,
        "email": f"socio{dni}@crediactiva.pe",
        "telefono": "",
        "aporte_mensual": 50.0,
        "fecha_registro": None,
    }


@app.patch("/api/v1/portal/{dni}/perfil")
def actualizar_perfil(dni: str, payload: PerfilSocioUpdate) -> dict:
    socio = obtener_por_dni(dni)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    if not socio.get("activo", True):
        raise HTTPException(status_code=403, detail="La cuenta está inactiva.")

    email = payload.email.strip().lower()
    existente = obtener_por_email(email)
    if existente and existente["dni"] != dni:
        raise HTTPException(status_code=409, detail="El correo ya está registrado en otro socio.")

    try:
        actualizado = actualizar_socio(
            socio["id_socio"],
            {
                "nombres": socio["nombres"],
                "apellidos": socio["apellidos"],
                "email": email,
                "telefono": payload.telefono,
                "aporte_mensual": socio.get("aporte_mensual", 50.0),
                "activo": True,
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if not actualizado:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")

    return {
        "id_socio": actualizado["id_socio"],
        "nombres": actualizado["nombres"],
        "apellidos": actualizado["apellidos"],
        "dni": actualizado["dni"],
        "email": actualizado["email"],
        "telefono": actualizado.get("telefono", ""),
        "aporte_mensual": actualizado.get("aporte_mensual", 50.0),
        "fecha_registro": actualizado.get("fecha_registro"),
    }


@app.delete("/api/v1/portal/{dni}/cuenta")
def eliminar_cuenta_socio(dni: str) -> dict:
    socio = obtener_por_dni(dni)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    if socio.get("rol") == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede eliminar una cuenta administrador desde el portal.",
        )
    if not socio.get("activo", True):
        raise HTTPException(status_code=400, detail="La cuenta ya está inactiva.")

    resultado = eliminar_socio(socio["id_socio"])
    if not resultado:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")

    return {
        "mensaje": "Su cuenta ha sido desactivada. Ya no podrá iniciar sesión.",
        "dni": dni,
    }
