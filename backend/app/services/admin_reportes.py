"""Métricas para dashboard y reportes de auditoría."""

from datetime import datetime, timezone

from app.services.almacen import listar_aportaciones_con_estado, listar_socios, listar_solicitudes, resumen_aportaciones
from app.services.calculadora import TEA_POR_TIPO


def construir_dashboard() -> dict:
    socios = listar_socios()
    solicitudes = listar_solicitudes()
    aportes_resumen = resumen_aportaciones()

    pendientes = [s for s in solicitudes if s.get("estado_evaluacion") == "PENDIENTE"]
    aprobadas = [s for s in solicitudes if s.get("estado_evaluacion") == "APROBADO"]
    rechazadas = [s for s in solicitudes if s.get("estado_evaluacion") == "RECHAZADO"]

    monto_colocado = round(sum(s.get("monto", 0) for s in aprobadas), 2)
    evaluadas = len(aprobadas) + len(rechazadas)
    tasa_aprobacion = round(len(aprobadas) / evaluadas * 100, 1) if evaluadas else 0.0

    return {
        "total_socios": len(socios),
        "total_solicitudes": len(solicitudes),
        "solicitudes_pendientes": len(pendientes),
        "solicitudes_aprobadas": len(aprobadas),
        "solicitudes_rechazadas": len(rechazadas),
        "monto_colocado": monto_colocado,
        "monto_por_cobrar": aportes_resumen["monto_pendiente"],
        "tasa_aprobacion": tasa_aprobacion,
        "aportaciones": aportes_resumen,
        "actualizado_en": datetime.now(timezone.utc),
    }


def construir_reporte_auditoria() -> dict:
    solicitudes = listar_solicitudes()
    aportes = listar_aportaciones_con_estado()

    cartera: dict[str, dict] = {}
    auditoria = []
    interes_total_sistema = 0.0

    for s in solicitudes:
        tipo = s.get("tipo_credito", "Emprendedor")
        monto = s.get("monto", 0)
        if tipo not in cartera:
            cartera[tipo] = {"cantidad": 0, "monto_total": 0.0}
        cartera[tipo]["cantidad"] += 1
        if s.get("estado_evaluacion") == "APROBADO":
            cartera[tipo]["monto_total"] += monto

        cronograma = s.get("cronograma", [])
        cuota = cronograma[0]["cuota"] if cronograma else None
        tea = TEA_POR_TIPO.get(tipo, 0)
        interes = 0.0
        if cronograma:
            interes = round(sum(c["cuota"] for c in cronograma) - monto, 2)
            interes_total_sistema += interes

        auditoria.append(
            {
                "id_solicitud": s["id_solicitud"],
                "dni_usuario": s.get("dni_usuario", ""),
                "monto": monto,
                "tipo_credito": tipo,
                "estado_evaluacion": s.get("estado_evaluacion", "PENDIENTE"),
                "tea_aplicada": tea if s.get("estado_evaluacion") == "APROBADO" else None,
                "cuota_mensual": cuota,
                "interes_total": interes if interes else None,
                "observaciones": s.get("observaciones", ""),
            }
        )

    pagadas = sum(1 for a in aportes if a["estado"] == "PAGADO")
    vencidas = sum(1 for a in aportes if a["estado"] == "VENCIDO")

    return {
        "actualizado_en": datetime.now(timezone.utc),
        "cartera_por_producto": [
            {"tipo_credito": k, "cantidad": v["cantidad"], "monto_total": round(v["monto_total"], 2)}
            for k, v in cartera.items()
        ],
        "solicitudes": auditoria,
        "resumen_financiero": {
            "monto_colocado": round(sum(s.get("monto", 0) for s in solicitudes if s.get("estado_evaluacion") == "APROBADO"), 2),
            "interes_generado": round(interes_total_sistema, 2),
            "cuotas_pagadas": pagadas,
            "cuotas_vencidas": vencidas,
            "indice_morosidad": round(vencidas / len(aportes) * 100, 2) if aportes else 0.0,
        },
    }
