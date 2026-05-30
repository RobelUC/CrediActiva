import { CurrencyPipe, DatePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval } from 'rxjs';
import type { Aportacion, ResumenAportaciones } from '../../core/models/admin.models';
import { AdminService } from '../../core/services/admin.service';
import { badgeAport } from './admin.utils';

@Component({
  selector: 'ca-admin-aportaciones',
  standalone: true,
  imports: [CurrencyPipe, DatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-aportaciones.component.html',
  styleUrl: './admin-shared.scss',
})
export class AdminAportacionesComponent implements OnInit {
  private readonly admin = inject(AdminService);
  private readonly destroyRef = inject(DestroyRef);
  readonly badgeAport = badgeAport;

  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);
  readonly aportaciones = signal<Aportacion[]>([]);
  readonly resumen = signal<ResumenAportaciones | null>(null);

  ngOnInit(): void {
    this.refrescar();
    interval(8_000)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.refrescar());
  }

  refrescar(): void {
    this.admin.listarAportaciones().subscribe({
      next: (data) => this.aportaciones.set(data),
    });
    this.admin.resumenAportaciones().subscribe({
      next: (r) => this.resumen.set(r),
    });
  }

  registrarPago(a: Aportacion): void {
    if (a.estado === 'PAGADO') {
      return;
    }
    this.admin.registrarPago(a.id_aportacion).subscribe({
      next: () => {
        this.mensaje.set('Pago registrado.');
        this.esError.set(false);
        this.refrescar();
      },
      error: () => {
        this.mensaje.set('Error al registrar pago.');
        this.esError.set(true);
      },
    });
  }
}
