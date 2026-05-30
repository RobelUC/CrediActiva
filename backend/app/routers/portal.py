from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.schemas.portal import (
    AporteHistorialItem,
    CreditoSocio,
    PerfilSocioResponse,
    PerfilSocioUpdate,
    ResumenCuentaSocio,
)
from app.services.almacen import guardar_socio, obtener_socio_por_dni
from app.services.portal_socio import (
    calcular_resumen_cuenta,
    historial_aportes_socio,
    listar_creditos_socio,
    obtener_perfil_socio,
)

router = APIRouter(prefix="/api/v1/portal", tags=["Portal del socio"])


@router.get("/{dni}/resumen", response_model=ResumenCuentaSocio)
def resumen_cuenta(dni: str) -> ResumenCuentaSocio:
    _validar_dni(dni)
    return ResumenCuentaSocio(**calcular_resumen_cuenta(dni))


@router.get("/{dni}/creditos", response_model=list[CreditoSocio])
def mis_creditos(dni: str) -> list[CreditoSocio]:
    _validar_dni(dni)
    return [CreditoSocio(**c) for c in listar_creditos_socio(dni)]


@router.get("/{dni}/aportaciones", response_model=list[AporteHistorialItem])
def historial_aportes(dni: str) -> list[AporteHistorialItem]:
    _validar_dni(dni)
    return [AporteHistorialItem(**a) for a in historial_aportes_socio(dni)]


@router.get("/{dni}/perfil", response_model=PerfilSocioResponse)
def perfil_socio(dni: str) -> PerfilSocioResponse:
    _validar_dni(dni)
    return PerfilSocioResponse(**obtener_perfil_socio(dni))


@router.patch("/{dni}/perfil", response_model=PerfilSocioResponse)
def actualizar_perfil(dni: str, payload: PerfilSocioUpdate) -> PerfilSocioResponse:
    _validar_dni(dni)
    socio = obtener_socio_por_dni(dni)
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
    guardar_socio(datos)
    return PerfilSocioResponse(
        id_socio=datos["id_socio"],
        nombres=datos["nombres"],
        apellidos=datos["apellidos"],
        dni=datos["dni"],
        email=datos["email"],
        telefono=datos["telefono"],
        aporte_mensual=datos["aporte_mensual"],
        fecha_registro=datos["fecha_registro"],
    )


def _validar_dni(dni: str) -> None:
    if not dni.isdigit() or len(dni) != 8:
        raise HTTPException(status_code=400, detail="DNI inválido.")
