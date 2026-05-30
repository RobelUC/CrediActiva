"""Cuentas de demostración — se crean al iniciar el auth-service."""

from datetime import datetime, timezone

from app.repository import guardar_socio, obtener_por_dni
from app.security import hash_password

DEMO_SOCIO_DNI = "74874853"
DEMO_SOCIO_PASSWORD = "demo1234"
DEMO_SOCIO_ID = "00000000-0000-4000-8000-000000000001"


def sembrar_cuentas_demo() -> None:
    """Garantiza un socio de prueba para portal y simulador."""
    if obtener_por_dni(DEMO_SOCIO_DNI):
        return

    guardar_socio(
        {
            "id_socio": DEMO_SOCIO_ID,
            "nombres": "OLIVER ALE",
            "apellidos": "SILES VIA Y RADA",
            "dni": DEMO_SOCIO_DNI,
            "email": "demo.socio@crediactiva.pe",
            "telefono": "987654321",
            "aporte_mensual": 50.0,
            "fecha_registro": datetime.now(timezone.utc),
            "activo": True,
            "password_hash": hash_password(DEMO_SOCIO_PASSWORD),
        }
    )
