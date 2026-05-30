from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from app.database import init_db
from app.repository import (
    actualizar_aportacion,
    guardar_lote,
    listar_con_estado,
    obtener_aportacion,
    resumen_aportaciones,
)
from app.schemas import AportacionResponse, LoteAportaciones, ResumenAportaciones


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
def aportaciones_internas(dni: str | None = None) -> list[dict]:
    return listar_con_estado(dni)


@app.get("/internal/aportaciones/resumen")
def resumen_interno() -> dict:
    return resumen_aportaciones()


@app.get("/api/v1/admin/aportaciones", response_model=list[AportacionResponse])
def obtener_aportaciones() -> list[AportacionResponse]:
    return [_map(a) for a in listar_con_estado()]


@app.get("/api/v1/admin/aportaciones/resumen", response_model=ResumenAportaciones)
def obtener_resumen() -> ResumenAportaciones:
    return ResumenAportaciones(**resumen_aportaciones())


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


def _map(a: dict) -> AportacionResponse:
    from app.repository import _estado

    return AportacionResponse(
        id_aportacion=a["id_aportacion"],
        id_solicitud=a["id_solicitud"],
        dni_socio=a["dni_socio"],
        nombre_socio=a.get("nombre_socio", ""),
        numero_cuota=a["numero_cuota"],
        monto_cuota=a["monto_cuota"],
        fecha_vencimiento=a["fecha_vencimiento"],
        estado=a.get("estado") or _estado(a),
        fecha_pago=a.get("fecha_pago"),
    )
