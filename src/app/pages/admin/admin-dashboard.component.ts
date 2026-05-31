import { DatePipe } from '@angular/common';
import { SolesPipe } from '../../core/pipes/soles.pipe';
import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import type { DashboardAdmin } from '../../core/models/admin.models';
import { AdminService } from '../../core/services/admin.service';

@Component({
  selector: 'ca-admin-dashboard',
  standalone: true,
  imports: [DatePipe, RouterLink, SolesPipe],
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
