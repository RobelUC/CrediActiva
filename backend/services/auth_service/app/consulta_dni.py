"""Consulta de DNI — API ApisPeru (RENIEC)."""

import os
import re

import httpx
from fastapi import APIRouter, HTTPException, status

from app.schemas import ConsultaDniResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])

APISPERU_BASE = os.getenv("APISPERU_URL", "https://dniruc.apisperu.com/api/v1/dni")
APISPERU_TOKEN = os.getenv(
    "APISPERU_TOKEN",
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImpmY2M5NTAxMjMwOUBnbWFpbC5jb20ifQ.UaK6eecpbt-mVnF9hI-BYSHtl6QQ5hCLU1MNItWe9P8",
)


@router.get("/consultar-dni/{dni}", response_model=ConsultaDniResponse)
def consultar_dni_reniec(dni: str) -> ConsultaDniResponse:
    if not re.match(r"^\d{8}$", dni):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DNI inválido.")

    if not APISPERU_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Consulta RENIEC no configurada.",
        )

    url = f"{APISPERU_BASE}/{dni}"
    try:
        with httpx.Client(timeout=12.0) as client:
            resp = client.get(url, params={"token": APISPERU_TOKEN})
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo consultar el DNI. Intente más tarde.",
        ) from exc

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
