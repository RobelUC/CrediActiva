import { CurrencyPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import type { Socio, SocioCreate } from '../../core/models/admin.models';
import { AdminService } from '../../core/services/admin.service';

@Component({
  selector: 'ca-admin-socios',
  standalone: true,
  imports: [FormsModule, CurrencyPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './admin-socios.component.html',
  styleUrl: './admin-shared.scss',
})
export class AdminSociosComponent implements OnInit {
  private readonly admin = inject(AdminService);

  readonly cargando = signal(false);
  readonly mensaje = signal<string | null>(null);
  readonly esError = signal(false);
  readonly socios = signal<Socio[]>([]);
  readonly nuevoSocio = signal<SocioCreate>({
    nombres: '',
    apellidos: '',
    dni: '',
    email: '',
    telefono: '',
    aporte_mensual: 50,
  });

  ngOnInit(): void {
    this.cargarSocios();
  }

  cargarSocios(): void {
    this.admin.listarSocios().subscribe({
      next: (data) => this.socios.set(data),
      error: () => this.notificar('No se pudo cargar socios.', true),
    });
  }

  registrarSocio(): void {
    const datos = this.nuevoSocio();
    if (!/^\d{8}$/.test(datos.dni)) {
      this.notificar('DNI inválido (8 dígitos).', true);
      return;
    }
    this.cargando.set(true);
    this.admin.registrarSocio(datos).subscribe({
      next: () => {
        this.cargando.set(false);
        this.notificar('Socio registrado correctamente.', false);
        this.nuevoSocio.set({
          nombres: '',
          apellidos: '',
          dni: '',
          email: '',
          telefono: '',
          aporte_mensual: 50,
        });
        this.cargarSocios();
      },
      error: (err) => {
        this.cargando.set(false);
        this.notificar(err?.error?.detail ?? 'Error al registrar socio.', true);
      },
    });
  }

  actualizarCampo<K extends keyof SocioCreate>(campo: K, valor: SocioCreate[K]): void {
    this.nuevoSocio.update((s) => ({ ...s, [campo]: valor }));
  }

  private notificar(texto: string, error: boolean): void {
    this.mensaje.set(texto);
    this.esError.set(error);
  }
}
