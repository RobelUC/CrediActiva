import { CurrencyPipe, DatePipe, DecimalPipe, KeyValuePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import type { ReporteAuditoria } from '../../core/models/admin.models';
import { AdminService } from '../../core/services/admin.service';
import { badgeEval } from './admin.utils';

@Component({
  selector: 'ca-admin-reportes',
  standalone: true,
  imports: [CurrencyPipe, DatePipe, DecimalPipe, KeyValuePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-reportes.component.html',
  styleUrl: './admin-shared.scss',
})
export class AdminReportesComponent implements OnInit {
  private readonly admin = inject(AdminService);
  readonly badgeEval = badgeEval;
  readonly reporte = signal<ReporteAuditoria | null>(null);

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.admin.obtenerReporteAuditoria().subscribe({
      next: (r) => this.reporte.set(r),
    });
  }

  labelResumen(key: string): string {
    const labels: Record<string, string> = {
      monto_colocado: 'Monto colocado',
      interes_generado: 'Interés generado',
      cuotas_pagadas: 'Cuotas pagadas',
      cuotas_vencidas: 'Cuotas vencidas',
      indice_morosidad: 'Índice morosidad (%)',
    };
    return labels[key] ?? key;
  }
}
