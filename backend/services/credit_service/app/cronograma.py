"""Generación de cronograma de pagos."""

from datetime import datetime, timezone

from app.calculadora import TEA_POR_TIPO, _cuota_francesa, _tasa_mensual_desde_tea
from app.schemas import TipoCredito


def _sumar_meses(fecha_base: datetime, meses: int) -> str:
    mes_total = fecha_base.month - 1 + meses
    year = fecha_base.year + mes_total // 12
    month = mes_total % 12 + 1
    day = min(fecha_base.day, 28)
    return f"{year}-{month:02d}-{day:02d}"


def generar_cronograma(
    monto: float,
    plazo_meses: int,
    tipo_credito: TipoCredito,
    fecha_inicio: datetime | None = None,
) -> list[dict]:
    base = fecha_inicio or datetime.now(timezone.utc)
    tea = TEA_POR_TIPO[tipo_credito]
    tasa = _tasa_mensual_desde_tea(tea)
    cuota_fija = _cuota_francesa(monto, tasa, plazo_meses)
    saldo = round(monto, 2)
    filas: list[dict] = []

    for numero in range(1, plazo_meses + 1):
        interes = round(saldo * tasa, 2)
        capital = round(cuota_fija - interes, 2)

        if numero == plazo_meses:
            capital = saldo
            cuota = round(capital + interes, 2)
        else:
            cuota = cuota_fija

        saldo = round(saldo - capital, 2)
        filas.append(
            {
                "numero_cuota": numero,
                "fecha_vencimiento": _sumar_meses(base, numero),
                "cuota": cuota,
                "capital": capital,
                "interes": interes,
                "saldo_restante": max(saldo, 0),
            }
        )

    return filas
