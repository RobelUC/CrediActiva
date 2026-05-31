"""
Genera diagrama ER de CrediActiva en PNG y PDF.
Uso: python generar_diagrama_er.py
Salida: backend/docs/diagrama_er_crediactiva.png
        backend/docs/diagrama_er_crediactiva.pdf
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = Path(__file__).resolve().parent / "docs"
NAVY = "#002855"
FOREST = "#00703c"
GOLD = "#c5a572"
AUTH_BG = "#eef4fb"
CREDIT_BG = "#eef8f2"
PAY_BG = "#fdf6ee"
LINE = "#334155"
MUTED = "#64748b"


def _entity_box(ax, x, y, w, h, title: str, attrs: list[str], header_color: str) -> None:
    body_h = h - 0.55
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.4,
        edgecolor=header_color,
        facecolor="white",
        zorder=3,
    )
    ax.add_patch(box)

    header = FancyBboxPatch(
        (x, y + body_h),
        w,
        0.55,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=0,
        facecolor=header_color,
        zorder=4,
    )
    ax.add_patch(header)
    ax.text(x + w / 2, y + body_h + 0.275, title, ha="center", va="center", fontsize=10, fontweight="bold", color="white", zorder=5)

    for i, attr in enumerate(attrs):
        ax.text(x + 0.12, y + body_h - 0.22 - i * 0.28, attr, ha="left", va="center", fontsize=8.2, color="#1e293b", zorder=5)


def _service_zone(ax, x, y, w, h, label: str, color: str) -> None:
    zone = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.03,rounding_size=0.15",
        linewidth=1.2,
        edgecolor=color,
        facecolor=color,
        alpha=0.18,
        zorder=1,
    )
    ax.add_patch(zone)
    ax.text(x + 0.2, y + h - 0.35, label, ha="left", va="center", fontsize=11, fontweight="bold", color=color, zorder=2)


def _rel(
    ax,
    start,
    end,
    label: str,
    style: str = "-",
    color: str = LINE,
    rad: float = 0.0,
    dashed: bool = False,
) -> None:
    ls = (0, (4, 3)) if dashed else style
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.3,
        color=color,
        linestyle=ls,
        connectionstyle=f"arc3,rad={rad}",
        zorder=2,
    )
    ax.add_patch(arrow)
    mx = (start[0] + end[0]) / 2
    my = (start[1] + end[1]) / 2 + 0.15
    ax.text(mx, my, label, ha="center", va="bottom", fontsize=7.5, color=MUTED, style="italic", zorder=6)


def generar() -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    png_path = OUT_DIR / "diagrama_er_crediactiva.png"
    pdf_path = OUT_DIR / "diagrama_er_crediactiva.pdf"

    fig, ax = plt.subplots(figsize=(16, 11), dpi=150)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    ax.text(
        8,
        10.55,
        "CrediActiva — Modelo Entidad-Relación (3FN)",
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        color=NAVY,
    )
    ax.text(
        8,
        10.15,
        "Microservicios con base de datos por servicio  |  SQLite  |  Normalización hasta Tercera Forma Normal",
        ha="center",
        va="center",
        fontsize=10,
        color=MUTED,
    )

    _service_zone(ax, 0.3, 0.4, 4.6, 9.6, "AUTH-SERVICE  (auth.db)", NAVY)
    _service_zone(ax, 5.2, 0.4, 6.8, 9.6, "CREDIT-SERVICE  (credit.db)", FOREST)
    _service_zone(ax, 12.2, 0.4, 3.5, 9.6, "PAYMENT-SERVICE  (payment.db)", GOLD)

    _entity_box(
        ax, 0.7, 4.2, 3.8, 3.4, "SOCIOS",
        [
            "id_socio  PK",
            "dni  UK",
            "nombres, apellidos",
            "email  UK",
            "telefono, aporte_mensual",
            "fecha_registro, activo",
            "password_hash",
        ],
        NAVY,
    )

    _entity_box(
        ax, 5.5, 7.5, 2.8, 1.9, "TIPOS_CREDITO",
        ["codigo  PK", "nombre", "tea_anual"],
        FOREST,
    )

    _entity_box(
        ax, 5.5, 4.0, 3.4, 3.0, "SOLICITUDES",
        [
            "id_solicitud  PK",
            "dni_usuario  FK*",
            "id_tipo_credito  FK",
            "monto, plazo_meses",
            "estado_preaprobacion",
            "estado_evaluacion",
            "fecha_registro",
        ],
        FOREST,
    )

    _entity_box(
        ax, 9.2, 4.3, 2.5, 2.5, "EVALUACIONES_FINANCIERAS",
        [
            "id_evaluacion  PK",
            "id_solicitud  FK UK",
            "tea_aplicada",
            "cuota_mensual",
            "interes_total",
        ],
        FOREST,
    )

    _entity_box(
        ax, 5.8, 0.8, 3.0, 2.5, "CUOTAS_CREDITO",
        [
            "id_cuota  PK",
            "id_solicitud  FK",
            "numero_cuota",
            "fecha_vencimiento",
            "cuota, capital, interes",
            "saldo_restante",
        ],
        FOREST,
    )

    _entity_box(
        ax, 12.4, 3.5, 3.1, 3.2, "APORTACIONES",
        [
            "id_aportacion  PK",
            "id_solicitud  FK*",
            "id_cuota  FK*",
            "dni_socio  FK*",
            "monto_cuota",
            "fecha_vencimiento",
            "fecha_pago, estado_pago",
        ],
        "#b45309",
    )

    # Relaciones internas credit-service
    _rel(ax, (7.2, 7.5), (7.2, 7.0), "1 : N", color=FOREST)
    _rel(ax, (8.9, 5.5), (9.2, 5.5), "1 : 1", color=FOREST)
    _rel(ax, (7.2, 4.0), (7.2, 3.3), "1 : N", color=FOREST)

    # Relaciones cross-service (lógicas)
    _rel(ax, (4.5, 5.8), (5.5, 5.5), "1 : N  (dni_usuario)", dashed=True, color=NAVY, rad=0.08)
    _rel(ax, (4.5, 5.2), (12.4, 5.0), "1 : N  (dni_socio)", dashed=True, color=NAVY, rad=-0.15)
    _rel(ax, (8.9, 4.5), (12.4, 4.8), "1 : N  (id_solicitud)", dashed=True, color=FOREST, rad=0.1)
    _rel(ax, (8.5, 1.5), (12.4, 4.0), "1 : 0..1  (id_cuota)", dashed=True, color=FOREST, rad=-0.12)

    legend_items = [
        mpatches.Patch(facecolor="white", edgecolor=NAVY, label="PK = Clave primaria"),
        mpatches.Patch(facecolor="white", edgecolor=FOREST, label="FK = Clave foránea (mismo servicio)"),
        mpatches.Patch(facecolor="white", edgecolor=MUTED, linestyle="--", label="FK* = Referencia lógica entre microservicios"),
    ]
    ax.legend(handles=legend_items, loc="lower left", fontsize=9, frameon=True, framealpha=0.95)

    ax.text(
        8,
        0.15,
        "Cooperativa de Crédito CrediActiva — Huancayo, Perú  |  Proyecto Final Web",
        ha="center",
        va="center",
        fontsize=9,
        color=MUTED,
    )

    plt.tight_layout(pad=0.5)
    fig.savefig(png_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(pdf_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    return png_path, pdf_path


if __name__ == "__main__":
    png, pdf = generar()
    print(f"PNG: {png}")
    print(f"PDF: {pdf}")
