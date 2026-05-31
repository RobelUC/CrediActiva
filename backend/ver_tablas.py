"""Lista tablas y muestra datos de CrediActiva (Supabase/Postgres o SQLite local)."""

import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

sys.path.insert(0, str(BASE / "services"))
from common.db_config import create_db_engine, resolve_database_url  # noqa: E402

SQLITE_BASES = {
    "auth-service": BASE / "services/auth_service/data/auth.db",
    "credit-service": BASE / "services/credit_service/data/credit.db",
    "payment-service": BASE / "services/payment_service/data/payment.db",
}


def _url_remota_configurada() -> str | None:
    url = resolve_database_url("_unused_", BASE / "services/auth_service/data/auth.db")
    return url if url.startswith("postgresql") else None


def mostrar_postgres(limite: int) -> None:
    from sqlalchemy import inspect, text

    engine = create_db_engine(_url_remota_configurada() or "")
    print("=" * 60)
    print(f"Supabase/PostgreSQL -> {engine.url.render_as_string(hide_password=True)}")
    print()

    inspector = inspect(engine)
    for tabla in sorted(inspector.get_table_names()):
        with engine.connect() as conn:
            count = conn.execute(text(f'SELECT COUNT(*) FROM "{tabla}"')).scalar()
            print(f"  [{tabla}] — {count} fila(s)")
            columnas = [c["name"] for c in inspector.get_columns(tabla)]
            print(f"    Columnas: {', '.join(columnas)}")
            if count and count > 0:
                filas = conn.execute(text(f'SELECT * FROM "{tabla}" LIMIT :n'), {"n": limite}).mappings().all()
                for i, fila in enumerate(filas, 1):
                    datos = dict(fila)
                    preview = ", ".join(f"{k}={v!r}" for k, v in list(datos.items())[:6])
                    if len(datos) > 6:
                        preview += ", ..."
                    print(f"    {i}. {preview}")
        print()


def mostrar_sqlite(nombre: str, ruta: Path, limite: int) -> None:
    print("=" * 60)
    print(f"{nombre} -> {ruta}")
    if not ruta.exists():
        print("  (no existe aún — ejecuta backend\\start-all.ps1 primero)\n")
        return

    conn = sqlite3.connect(ruta)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    tablas = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()

    for (tabla,) in tablas:
        count = cur.execute(f"SELECT COUNT(*) FROM [{tabla}]").fetchone()[0]
        print(f"\n  [{tabla}] — {count} fila(s)")

        columnas = [row[1] for row in cur.execute(f"PRAGMA table_info([{tabla}])").fetchall()]
        print(f"    Columnas: {', '.join(columnas)}")

        if count > 0:
            filas = cur.execute(f"SELECT * FROM [{tabla}] LIMIT {limite}").fetchall()
            for i, fila in enumerate(filas, 1):
                datos = dict(fila)
                preview = ", ".join(f"{k}={v!r}" for k, v in list(datos.items())[:6])
                if len(datos) > 6:
                    preview += ", ..."
                print(f"    {i}. {preview}")

    conn.close()
    print()


def main() -> None:
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    remota = _url_remota_configurada()
    if remota:
        mostrar_postgres(limite)
        return
    for nombre, ruta in SQLITE_BASES.items():
        mostrar_sqlite(nombre, ruta, limite)


if __name__ == "__main__":
    main()
