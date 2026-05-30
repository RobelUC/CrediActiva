"""Cálculo financiero servidor — TEA y amortización francesa (auditoría)."""

from app.schemas.solicitud import AuditoriaInteres, EstadoPreaprobacion, TipoCredito

TEA_POR_TIPO: dict[TipoCredito, float] = {
    "Emprendedor": 14.5,
    "Vivienda": 10.5,
    "Agrícola": 12.0,
}

MONTO_PREAPROBACION_AUTOMATICA = 20_000


def _tasa_mensual_desde_tea(tea_porcentaje: float) -> float:
    """TEA → tasa mensual efectiva: (1 + TEA)^(1/12) - 1"""
    tea = tea_porcentaje / 100.0
    return (1.0 + tea) ** (1.0 / 12.0) - 1.0


def _cuota_francesa(capital: float, tasa_mensual: float, plazo_meses: int) -> float:
    if plazo_meses <= 0 or capital <= 0:
        return 0.0
    if tasa_mensual == 0:
        return round(capital / plazo_meses, 2)
    factor = (1.0 + tasa_mensual) ** plazo_meses
    cuota = capital * tasa_mensual * factor / (factor - 1.0)
    return round(cuota, 2)


def calcular_auditoria_credito(
    monto: float,
    plazo_meses: int,
    tipo_credito: TipoCredito,
) -> AuditoriaInteres:
    """
    Cuota por sistema francés e interés total en el plazo:
    interés_total = (cuota × plazo) − capital.
    """
    tea = TEA_POR_TIPO[tipo_credito]
    tasa_mensual = _tasa_mensual_desde_tea(tea)
    cuota = _cuota_francesa(monto, tasa_mensual, plazo_meses)
    monto_total = round(cuota * plazo_meses, 2)
    interes_total = round(monto_total - monto, 2)

    return AuditoriaInteres(
        tea_aplicada=tea,
        tasa_mensual_efectiva=round(tasa_mensual * 100, 6),
        cuota_mensual=cuota,
        interes_total=interes_total,
        monto_total_a_pagar=monto_total,
    )


def determinar_estado_preaprobacion(monto: float) -> EstadoPreaprobacion:
    if monto < MONTO_PREAPROBACION_AUTOMATICA:
        return "APROBADO_PRELIMINAR"
    return "EN_REVISION"


def construir_mensaje_exito(
    estado: EstadoPreaprobacion,
    dni_usuario: str,
    tipo_credito: str,
    monto: float,
) -> str:
    monto_fmt = f"S/. {monto:,.2f}"
    if estado == "APROBADO_PRELIMINAR":
        return (
            f"¡Felicitaciones! Su solicitud {tipo_credito} por {monto_fmt} "
            f"para el DNI {dni_usuario} fue pre-aprobada. Puede acercarse a "
            f"cualquier agencia CrediActiva en Huancayo para formalizar su crédito."
        )
    return (
        f"Solicitud {tipo_credito} por {monto_fmt} registrada para el DNI {dni_usuario}. "
        f"Por el monto solicitado, un asesor de la sede Huancayo revisará su expediente "
        f"y se comunicará con usted en un plazo máximo de 48 horas hábiles."
    )
