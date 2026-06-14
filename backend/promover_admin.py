"""Promueve un socio existente a administrador. Uso: py backend\\promover_admin.py 74874853"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "services" / "auth_service"))

from app.database import init_db
from app.repository import asignar_rol_por_dni, obtener_por_dni


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: py backend\\promover_admin.py <DNI>")
        print("Ejemplo: py backend\\promover_admin.py 74874853")
        sys.exit(1)

    dni = sys.argv[1].strip()
    if len(dni) != 8 or not dni.isdigit():
        print("El DNI debe tener 8 dígitos.")
        sys.exit(1)

    init_db()

    if not obtener_por_dni(dni):
        print(f"No existe un socio con DNI {dni}. Regístrelo primero en la web.")
        sys.exit(1)

    socio = asignar_rol_por_dni(dni, "admin")
    if not socio:
        print("No se pudo asignar el rol.")
        sys.exit(1)

    print(f"OK: {socio['nombres']} {socio['apellidos']} ({dni}) ahora es administrador.")
    print("Inicie sesion con su DNI y contrasena habitual en /login; accedera a /admin")


if __name__ == "__main__":
    main()
