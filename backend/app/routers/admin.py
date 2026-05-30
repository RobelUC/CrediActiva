from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas.admin import (
    AportacionResponse,
    EvaluarSolicitudRequest,
    ResumenAportaciones,
    SolicitudAdminResponse,
)
from app.schemas.reportes import DashboardAdmin, ReporteAuditoria
from app.schemas.socio import SocioCreate, SocioResponse
from app.services.admin_reportes import construir_dashboard, construir_reporte_auditoria
from app.services.almacen import (
    actualizar_aportacion,
    actualizar_solicitud,
    guardar_aportaciones,
    guardar_socio,
    listar_aportaciones_con_estado,
    listar_socios,
    listar_solicitudes,
    obtener_aportacion,
    obtener_socio_por_dni,
    obtener_solicitud,
    resumen_aportaciones,
)
from app.services.cronograma import generar_cronograma

router = APIRouter(prefix="/api/v1/admin", tags=["Administración"])


def _nombre_socio(dni: str) -> str:
    socio = obtener_socio_por_dni(dni)
    if socio:
        return f"{socio['nombres']} {socio['apellidos']}"
    return f"Socio {dni}"


@router.get("/dashboard", response_model=DashboardAdmin)
def dashboard_general() -> DashboardAdmin:
    return DashboardAdmin(**construir_dashboard())


@router.get("/reportes/auditoria", response_model=ReporteAuditoria)
def reportes_auditoria() -> ReporteAuditoria:
    return ReporteAuditoria(**construir_reporte_auditoria())


@router.post("/socios", response_model=SocioResponse, status_code=status.HTTP_201_CREATED)
def registrar_socio(payload: SocioCreate) -> SocioResponse:
    if obtener_socio_por_dni(payload.dni):
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
    guardar_socio(registro)
    return SocioResponse(**registro)


@router.get("/socios", response_model=list[SocioResponse])
def obtener_socios() -> list[SocioResponse]:
    return [SocioResponse(**s) for s in listar_socios()]


@router.get("/solicitudes", response_model=list[SolicitudAdminResponse])
def obtener_solicitudes_admin() -> list[SolicitudAdminResponse]:
    return [_map_solicitud_admin(s) for s in listar_solicitudes()]


@router.get("/solicitudes/{id_solicitud}", response_model=SolicitudAdminResponse)
def obtener_solicitud_admin(id_solicitud: str) -> SolicitudAdminResponse:
    solicitud = obtener_solicitud(id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    return _map_solicitud_admin(solicitud)


@router.post(
    "/solicitudes/{id_solicitud}/evaluar",
    response_model=SolicitudAdminResponse,
)
def evaluar_solicitud(
    id_solicitud: str,
    payload: EvaluarSolicitudRequest,
) -> SolicitudAdminResponse:
    solicitud = obtener_solicitud(id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")

    if solicitud.get("estado_evaluacion") != "PENDIENTE":
        raise HTTPException(status_code=400, detail="La solicitud ya fue evaluada.")

    cronograma: list[dict] = []
    if payload.decision == "APROBADO":
        cronograma = generar_cronograma(
            solicitud["monto"],
            solicitud["plazo_meses"],
            solicitud["tipo_credito"],
        )
        _crear_aportaciones_desde_cronograma(solicitud, cronograma)

    actualizada = actualizar_solicitud(
        id_solicitud,
        {
            "estado_evaluacion": payload.decision,
            "observaciones": payload.observaciones,
            "cronograma": cronograma,
        },
    )
    return _map_solicitud_admin(actualizada)  # type: ignore[arg-type]


@router.get("/aportaciones", response_model=list[AportacionResponse])
def obtener_aportaciones() -> list[AportacionResponse]:
    return [_map_aportacion(a) for a in listar_aportaciones_con_estado()]


@router.get("/aportaciones/resumen", response_model=ResumenAportaciones)
def obtener_resumen_aportaciones() -> ResumenAportaciones:
    return ResumenAportaciones(**resumen_aportaciones())


@router.post("/aportaciones/{id_aportacion}/pagar", response_model=AportacionResponse)
def registrar_pago_aportacion(id_aportacion: str) -> AportacionResponse:
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
    return _map_aportacion(copia)  # type: ignore[arg-type]


def _crear_aportaciones_desde_cronograma(
    solicitud: dict,
    cronograma: list[dict],
) -> None:
    dni = solicitud["dni_usuario"]
    nombre = _nombre_socio(dni)
    lote = [
        {
            "id_aportacion": str(uuid4()),
            "id_solicitud": solicitud["id_solicitud"],
            "dni_socio": dni,
            "nombre_socio": nombre,
            "numero_cuota": cuota["numero_cuota"],
            "monto_cuota": cuota["cuota"],
            "fecha_vencimiento": cuota["fecha_vencimiento"],
            "fecha_pago": None,
        }
        for cuota in cronograma
    ]
    guardar_aportaciones(lote)


def _map_solicitud_admin(s: dict) -> SolicitudAdminResponse:
    return SolicitudAdminResponse(
        id_solicitud=s["id_solicitud"],
        dni_usuario=s.get("dni_usuario", ""),
        monto=s.get("monto", 0),
        plazo_meses=s.get("plazo_meses", 0),
        tipo_credito=s.get("tipo_credito", "Emprendedor"),
        estado_preaprobacion=s.get("estado", "EN_REVISION"),
        estado_evaluacion=s.get("estado_evaluacion", "PENDIENTE"),
        fecha_registro=s.get("fecha_registro", datetime.now(timezone.utc)),
        observaciones=s.get("observaciones", ""),
        cronograma=s.get("cronograma", []),
    )


def _map_aportacion(a: dict) -> AportacionResponse:
    return AportacionResponse(
        id_aportacion=a["id_aportacion"],
        id_solicitud=a["id_solicitud"],
        dni_socio=a["dni_socio"],
        nombre_socio=a.get("nombre_socio", ""),
        numero_cuota=a["numero_cuota"],
        monto_cuota=a["monto_cuota"],
        fecha_vencimiento=a["fecha_vencimiento"],
        estado=a.get("estado", "PENDIENTE"),
        fecha_pago=a.get("fecha_pago"),
    )
