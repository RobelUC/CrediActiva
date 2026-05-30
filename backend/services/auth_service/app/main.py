from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status

from app.auth_routes import router as auth_router
from app.consulta_dni import router as consulta_dni_router
from app.database import init_db
from app.demo_data import sembrar_cuentas_demo
from app.repository import (
    actualizar_socio,
    eliminar_socio,
    guardar_socio,
    listar_socios,
    obtener_por_dni,
    obtener_por_email,
    obtener_por_id,
)
from app.schemas import PerfilSocioUpdate, SocioCreate, SocioResponse, SocioUpdate


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    sembrar_cuentas_demo()
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


@app.delete("/api/v1/admin/socios/{id_socio}", response_model=SocioResponse)
def desactivar_socio(id_socio: str) -> SocioResponse:
    socio = eliminar_socio(id_socio)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado.")
    return SocioResponse(**socio)


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


@app.patch("/api/v1/portal/{dni}/perfil", response_model=SocioResponse)
def actualizar_perfil(dni: str, payload: PerfilSocioUpdate) -> SocioResponse:
    socio = obtener_por_dni(dni)
    datos = {
        "id_socio": socio["id_socio"] if socio else str(uuid4()),
        "nombres": payload.nombres.strip(),
        "apellidos": payload.apellidos.strip(),
        "dni": dni,
        "email": payload.email.strip().lower(),
        "telefono": payload.telefono,
        "aporte_mensual": round(payload.aporte_mensual, 2),
        "fecha_registro": socio.get("fecha_registro", datetime.now(timezone.utc))
        if socio
        else datetime.now(timezone.utc),
        "activo": True,
    }
    return SocioResponse(**guardar_socio(datos))
