import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException, Query

from app.database import init_db
from app.repository import (
    actualizar_aportacion,
    eliminar_por_dni,
    guardar_lote,
    listar_aportaciones_paginado,
    listar_con_estado,
    obtener_aportacion,
    resumen_aportaciones,
)
from app.schemas import (
    AportacionResponse,
    AportacionesPaginadasResponse,
    LoteAportaciones,
    ResumenAportaciones,
)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
_cache_nombres: dict[str, str] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Payment Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "servicio": "payment-service"}


@app.post("/internal/aportaciones/lote")
def crear_lote(payload: LoteAportaciones) -> dict[str, int]:
    guardar_lote([item.model_dump() for item in payload.items])
    return {"creadas": len(payload.items)}


@app.get("/internal/aportaciones")
def aportaciones_internas(
    dni: str | None = None,
    enriquecer: bool = Query(default=True),
) -> list[dict]:
    items = listar_con_estado(dni)
    if not enriquecer:
        return items
    return [_enriquecer(a) for a in items]


@app.get("/internal/aportaciones/resumen")
def resumen_interno() -> dict:
    return resumen_aportaciones()


@app.delete("/internal/datos-socio/{dni}")
def eliminar_datos_socio(dni: str) -> dict[str, int]:
    return {"aportaciones_eliminadas": eliminar_por_dni(dni)}


@app.get("/api/v1/admin/aportaciones", response_model=AportacionesPaginadasResponse)
def obtener_aportaciones(
    dni: str | None = Query(default=None, min_length=8, max_length=8),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
) -> AportacionesPaginadasResponse:
    items, total = listar_aportaciones_paginado(dni=dni, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total else 0
    return AportacionesPaginadasResponse(
        items=[_map(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/api/v1/admin/aportaciones/resumen", response_model=ResumenAportaciones)
def obtener_resumen(dni: str | None = Query(default=None, min_length=8, max_length=8)) -> ResumenAportaciones:
    return ResumenAportaciones(**resumen_aportaciones(dni))


@app.post("/api/v1/admin/aportaciones/{id_aportacion}/pagar", response_model=AportacionResponse)
def registrar_pago(id_aportacion: str) -> AportacionResponse:
    aportacion = obtener_aportacion(id_aportacion)
    if not aportacion:
        raise HTTPException(status_code=404, detail="Aportación no encontrada.")
    if aportacion.get("fecha_pago"):
        raise HTTPException(status_code=400, detail="La cuota ya fue pagada.")

    actualizada = actualizar_aportacion(
        id_aportacion,
        {"fecha_pago": datetime.now(timezone.utc).date().isoformat()},
    )
    copia = {**actualizada, "estado": "PAGADO"}  # type: ignore[dict-item]
    return _map(copia)  # type: ignore[arg-type]


def _nombre_socio(dni: str) -> str:
    if dni in _cache_nombres:
        return _cache_nombres[dni]
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{AUTH_SERVICE_URL}/internal/socios/{dni}")
            if resp.status_code == 200:
                data = resp.json()
                nombre = f"{data['nombres']} {data['apellidos']}"
                _cache_nombres[dni] = nombre
                return nombre
    except httpx.HTTPError:
        pass
    return f"Socio {dni}"


def _enriquecer(a: dict) -> dict:
    return {**a, "nombre_socio": _nombre_socio(a["dni_socio"])}


def _map(a: dict) -> AportacionResponse:
    from app.repository import _estado

    enriquecida = _enriquecer(a)
    return AportacionResponse(
        id_aportacion=enriquecida["id_aportacion"],
        id_solicitud=enriquecida["id_solicitud"],
        dni_socio=enriquecida["dni_socio"],
        nombre_socio=enriquecida["nombre_socio"],
        numero_cuota=enriquecida["numero_cuota"],
        monto_cuota=enriquecida["monto_cuota"],
        fecha_vencimiento=enriquecida["fecha_vencimiento"],
        estado=enriquecida.get("estado") or _estado(enriquecida),
        fecha_pago=enriquecida.get("fecha_pago"),
    )
