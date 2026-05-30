import { CurrencyPipe, DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import type { DashboardAdmin } from '../../core/models/admin.models';
import { AdminService } from '../../core/services/admin.service';

@Component({
  selector: 'ca-admin-dashboard',
  standalone: true,
  imports: [CurrencyPipe, DatePipe, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-shared.scss',
})
export class AdminDashboardComponent implements OnInit {
  private readonly admin = inject(AdminService);
  readonly dashboard = signal<DashboardAdmin | null>(null);

  ngOnInit(): void {
    this.admin.obtenerDashboard().subscribe({
      next: (d) => this.dashboard.set(d),
    });
  }
}
