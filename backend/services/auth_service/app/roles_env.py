"""Asigna rol admin a socios indicados en ADMIN_SOCIO_DNI al iniciar el servicio."""

import os

from app.repository import asignar_rol_por_dni, obtener_por_dni


def aplicar_roles_desde_env() -> None:
    """
    ADMIN_SOCIO_DNI puede listar uno o varios DNI separados por coma.
    Ejemplo: ADMIN_SOCIO_DNI=74874853,12345678
    """
    raw = os.getenv("ADMIN_SOCIO_DNI", "").strip()
    if not raw:
        return

    for dni in (parte.strip() for parte in raw.split(",")):
        if not dni or len(dni) != 8 or not dni.isdigit():
            continue
        if not obtener_por_dni(dni):
            continue
        asignar_rol_por_dni(dni, "admin")
