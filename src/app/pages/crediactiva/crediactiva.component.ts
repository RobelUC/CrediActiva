import { DecimalPipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  HostListener,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import type { TipoCredito } from '../../core/models/credito.types';
import {
  PREGUNTAS_FRECUENTES,
  TESTIMONIOS,
  VALORES_CREDIACTIVA,
} from './crediactiva.data';

const MONTO_MINIMO = 1000;

interface StatCard {
  valor: string;
  etiqueta: string;
  icono: string;
}

@Component({
  selector: 'ca-crediactiva',
  standalone: true,
  imports: [FormsModule, RouterLink, DecimalPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './crediactiva.component.html',
  styleUrl: './crediactiva.component.scss',
})
export class CrediactivaComponent {
  readonly auth = inject(AuthService);
  readonly anioActual = new Date().getFullYear();

  /** Navbar sticky: fondo sólido al hacer scroll */
  readonly navScrolled = signal(false);

  /** Simulador solo con cuenta de socio */
  readonly puedeUsarSimulador = computed(
    () => this.auth.sesionActiva() && !this.auth.esAdministrador(),
  );

  readonly rutaSimulador = computed(() =>
    this.puedeUsarSimulador() ? '/simulador' : '/login',
  );

  readonly queryParamsSimulador = computed(() =>
    this.puedeUsarSimulador() ? {} : { returnUrl: '/simulador' },
  );
  readonly MONTO_MINIMO = MONTO_MINIMO;

  readonly tiposCredito: readonly TipoCredito[] = [
    'Emprendedor',
    'Vivienda',
    'Agrícola',
  ];

  readonly valores = VALORES_CREDIACTIVA;
  readonly testimonios = TESTIMONIOS;
  readonly faqs = PREGUNTAS_FRECUENTES;

  /** FAQ: índice del ítem abierto (null = todos cerrados) */
  readonly faqAbierto = signal<number | null>(0);

  readonly estadisticas: readonly StatCard[] = [
    { valor: '12+', etiqueta: 'Años de experiencia', icono: 'bi-calendar-check' },
    { valor: '18,000+', etiqueta: 'Socios atendidos', icono: 'bi-people' },
    { valor: 'S/ 48M', etiqueta: 'Créditos colocados', icono: 'bi-cash-stack' },
    { valor: '96%', etiqueta: 'Satisfacción del socio', icono: 'bi-emoji-smile' },
  ];

  /** Señales del formulario hero */
  readonly monto = signal(5_000);
  readonly tipoCredito = signal<TipoCredito>('Emprendedor');
  readonly dni = signal('');

  readonly montoInvalido = computed(
    () => this.monto() > 0 && this.monto() < MONTO_MINIMO,
  );

  readonly dniInvalido = computed(
    () => this.dni().length > 0 && !/^\d{8}$/.test(this.dni()),
  );

  readonly formularioListo = computed(
    () =>
      this.monto() >= MONTO_MINIMO &&
      /^\d{8}$/.test(this.dni()),
  );

  actualizarMonto(valor: string): void {
    const parsed = Number.parseFloat(valor);
    this.monto.set(Number.isFinite(parsed) ? Math.max(0, parsed) : 0);
  }

  actualizarDni(valor: string): void {
    this.dni.set(valor.replace(/\D/g, '').slice(0, 8));
  }

  alternarFaq(id: number): void {
    this.faqAbierto.update((actual) => (actual === id ? null : id));
  }

  faqEstaAbierto(id: number): boolean {
    return this.faqAbierto() === id;
  }

  estrellasArray(cantidad: number): number[] {
    return Array.from({ length: cantidad }, (_, i) => i);
  }

  @HostListener('window:scroll')
  onVentanaScroll(): void {
    this.navScrolled.set(window.scrollY > 20);
  }
}
