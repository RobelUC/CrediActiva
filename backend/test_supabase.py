"""Prueba rápida de conexión a Supabase. Uso: py backend\\test_supabase.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "services"))
from sqlalchemy import text

from common.db_config import create_db_engine, resolve_database_url

url = resolve_database_url("AUTH_DATABASE_URL", Path("x"))
if not url.startswith("postgresql"):
    print("No se detectó SUPABASE_DATABASE_URL en backend/.env")
    print("Sigues en SQLite local.")
    sys.exit(1)

host = url.split("@")[-1] if "@" in url else url
print(f"Conectando a ...@{host}")

engine = create_db_engine(url)
try:
    with engine.connect() as conn:
        ok = conn.execute(text("SELECT 1")).scalar()
        tablas = conn.execute(
            text(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' ORDER BY tablename"
            )
        ).fetchall()
    print("Conexion OK (SELECT 1 =", ok, ")")
    nombres = [t[0] for t in tablas]
    if nombres:
        print("Tablas en Supabase:", ", ".join(nombres))
    else:
        print("Sin tablas aún. Ejecuta esquema_supabase.sql o inicia los microservicios.")
except Exception as exc:
    print("ERROR de conexion:", exc)
    if "Timeout" in type(exc).__name__ or "timeout" in str(exc).lower():
        if ":5432" in host and "pooler" not in host:
            print()
            print("Solucion habitual:")
            print("  1. Supabase -> Project Settings -> Database -> Connection string")
            print("  2. Elige 'Transaction pooler' (puerto 6543)")
            print("  3. Copia la URI y reemplaza SUPABASE_DATABASE_URL en backend/.env")
            print("  4. Usuario suele ser postgres.TU_PROJECT_REF (no solo 'postgres')")
    sys.exit(1)
