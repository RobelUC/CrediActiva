"""Consulta de DNI — API ApisPeru (RENIEC)."""

import logging
import os
import re

import httpx
from fastapi import APIRouter, HTTPException, status

from app.schemas import ConsultaDniResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])

APISPERU_BASE = os.getenv("APISPERU_URL", "https://dniruc.apisperu.com/api/v1/dni")
APISPERU_TOKEN = os.getenv(
    "APISPERU_TOKEN",
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImpmY2M5NTAxMjMwOUBnbWFpbC5jb20ifQ.UaK6eecpbt-mVnF9hI-BYSHtl6QQ5hCLU1MNItWe9P8",
)


def _ssl_verify_setting() -> bool | str:
    """Certificados SSL para ApisPeru. En Windows a veces hace falta APISPERU_SSL_VERIFY=false."""
    raw = os.getenv("APISPERU_SSL_VERIFY", "").strip().lower()
    if raw in ("0", "false", "no"):
        return False
    if raw in ("1", "true", "yes"):
        return True
    try:
        import certifi

        return certifi.where()
    except ImportError:
        return True


def _consultar_apisperu(dni: str) -> dict:
    url = f"{APISPERU_BASE}/{dni}"
    params = {"token": APISPERU_TOKEN}
    verify_options: list[bool | str] = [_ssl_verify_setting()]
    if verify_options[0] is not False:
        verify_options.append(False)

    last_error: Exception | None = None
    for verify in verify_options:
        try:
            with httpx.Client(timeout=12.0, verify=verify) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Servicio RENIEC no disponible. Intente más tarde.",
            ) from exc
        except httpx.ConnectError as exc:
            last_error = exc
            if "CERTIFICATE" in str(exc).upper() and verify is not False:
                logger.warning("ApisPeru: error SSL, reintentando sin verificar certificado.")
                continue
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Sin conexión al servicio RENIEC. Verifique su internet.",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo consultar el DNI. Intente más tarde.",
            ) from exc

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="No se pudo consultar el DNI (error SSL). Configure APISPERU_SSL_VERIFY=false en backend/.env",
    ) from last_error


@router.get("/consultar-dni/{dni}", response_model=ConsultaDniResponse)
def consultar_dni_reniec(dni: str) -> ConsultaDniResponse:
    if not re.match(r"^\d{8}$", dni):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DNI inválido.")

    if not APISPERU_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Consulta RENIEC no configurada.",
        )

    data = _consultar_apisperu(dni)

    if not data.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNI no encontrado en RENIEC.",
        )

    apellidos = " ".join(
        part
        for part in (data.get("apellidoPaterno", ""), data.get("apellidoMaterno", ""))
        if part
    ).strip()

    return ConsultaDniResponse(
        dni=data.get("dni", dni),
        nombres=(data.get("nombres") or "").strip(),
        apellidos=apellidos,
    )
