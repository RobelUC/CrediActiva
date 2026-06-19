import { ChangeDetectionStrategy, Component } from '@angular/core';

interface CanalContacto {
  icono: string;
  titulo: string;
  detalle: string;
  enlace?: string;
  tipoEnlace?: 'tel' | 'mailto' | 'url';
}

interface Oficina {
  nombre: string;
  direccion: string;
  referencia: string;
  horario: string;
}

interface AreaAtencion {
  icono: string;
  area: string;
  responsable: string;
  correo: string;
  telefono: string;
  descripcion: string;
}

@Component({
  selector: 'ca-portal-contactos',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './portal-contactos.component.html',
  styleUrl: './portal-shared.scss',
})
export class PortalContactosComponent {
  readonly empresa = {
    nombre: 'CrediActiva Cooperativa de Ahorro y Crédito',
    ruc: '20123456789',
    slogan: 'Finanzas solidarias para emprender, crecer y vivir mejor.',
    mision:
      'Brindamos soluciones financieras accesibles y transparentes a nuestros socios, con acompañamiento cercano y compromiso con el desarrollo de las familias peruanas.',
  };

  readonly canalesPrincipales: readonly CanalContacto[] = [
    {
      icono: 'bi-telephone-fill',
      titulo: 'Central telefónica',
      detalle: '(01) 612-4500',
      enlace: 'tel:+516124500',
      tipoEnlace: 'tel',
    },
    {
      icono: 'bi-whatsapp',
      titulo: 'WhatsApp Socios',
      detalle: '+51 987 654 321',
      enlace: 'https://wa.me/51987654321',
      tipoEnlace: 'url',
    },
    {
      icono: 'bi-envelope-fill',
      titulo: 'Correo general',
      detalle: 'atencion@crediactiva.pe',
      enlace: 'mailto:atencion@crediactiva.pe',
      tipoEnlace: 'mailto',
    },
    {
      icono: 'bi-globe2',
      titulo: 'Sitio web',
      detalle: 'www.crediactiva.pe',
      enlace: 'https://www.crediactiva.pe',
      tipoEnlace: 'url',
    },
  ];

  readonly oficinas: readonly Oficina[] = [
    {
      nombre: 'Oficina principal — Lima',
      direccion: 'Av. Javier Prado Este 4200, San Borja',
      referencia: 'A dos cuadras del Óvalo Monitor',
      horario: 'Lun–Vie 9:00 a.m. – 6:00 p.m. · Sáb 9:00 a.m. – 1:00 p.m.',
    },
    {
      nombre: 'Agencia Norte — Los Olivos',
      direccion: 'Av. Alfredo Mendiola 3520, Urb. El Pacífico',
      referencia: 'Frente al centro comercial Plaza Norte',
      horario: 'Lun–Vie 9:00 a.m. – 5:30 p.m.',
    },
  ];

  readonly areas: readonly AreaAtencion[] = [
    {
      icono: 'bi-people-fill',
      area: 'Atención al socio',
      responsable: 'Lic. María Fernández',
      correo: 'socios@crediactiva.pe',
      telefono: 'Anexo 101',
      descripcion: 'Consultas sobre membresía, aportes y actualización de datos.',
    },
    {
      icono: 'bi-cash-coin',
      area: 'Créditos y evaluación',
      responsable: 'Econ. Carlos Ruiz',
      correo: 'creditos@crediactiva.pe',
      telefono: 'Anexo 205',
      descripcion: 'Estado de solicitudes, documentación y cronogramas de pago.',
    },
    {
      icono: 'bi-shield-check',
      area: 'Cobranzas y regularización',
      responsable: 'Lic. Ana Torres',
      correo: 'cobranzas@crediactiva.pe',
      telefono: 'Anexo 308',
      descripcion: 'Acuerdos de pago, refinanciamiento y orientación financiera.',
    },
  ];

  readonly redes = [
    { icono: 'bi-facebook', nombre: 'Facebook', usuario: '@CrediActivaPE' },
    { icono: 'bi-instagram', nombre: 'Instagram', usuario: '@crediactiva' },
    { icono: 'bi-linkedin', nombre: 'LinkedIn', usuario: 'CrediActiva Cooperativa' },
  ];

  enlaceExterno(canal: CanalContacto): string {
    return canal.enlace ?? '#';
  }

  esExterno(canal: CanalContacto): boolean {
    return canal.tipoEnlace === 'url';
  }
}
