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
    ciudad: 'Huancayo, Junín',
    slogan: 'Finanzas solidarias para emprender, crecer y vivir mejor en la sierra central.',
    mision:
      'Democratizamos el acceso al crédito responsable en Huancayo y la región Junín, con tasas transparentes y acompañamiento humano en cada solicitud.',
    direccionMapa: 'Av. Huancavelica 450, Huancayo',
    telefonoUrgente: '(064) 381-200',
    telefonoUrgenteEnlace: 'tel:+5164381200',
  };

  readonly canalesPrincipales: readonly CanalContacto[] = [
    {
      icono: 'bi-telephone-fill',
      titulo: 'Central telefónica',
      detalle: '(064) 381-200',
      enlace: 'tel:+5164381200',
      tipoEnlace: 'tel',
    },
    {
      icono: 'bi-whatsapp',
      titulo: 'WhatsApp Socios',
      detalle: '+51 964 381 200',
      enlace: 'https://wa.me/51964381200',
      tipoEnlace: 'url',
    },
    {
      icono: 'bi-envelope-fill',
      titulo: 'Correo general',
      detalle: 'contacto@crediactiva.pe',
      enlace: 'mailto:contacto@crediactiva.pe',
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
      nombre: 'Oficina principal — Huancayo',
      direccion: 'Av. Huancavelica 450, Huancayo',
      referencia: 'A tres cuadras de la Plaza de la Constitución',
      horario: 'Lun–Vie 9:00 a.m. – 6:00 p.m. · Sáb 9:00 a.m. – 1:00 p.m.',
    },
    {
      nombre: 'Agencia El Tambo',
      direccion: 'Jr. Lima 218, El Tambo',
      referencia: 'Frente al mercado central de El Tambo',
      horario: 'Lun–Vie 9:00 a.m. – 5:30 p.m. · Sáb 9:00 a.m. – 12:30 p.m.',
    },
  ];

  readonly areas: readonly AreaAtencion[] = [
    {
      icono: 'bi-people-fill',
      area: 'Atención al socio',
      responsable: 'Lic. Rosa Quispe',
      correo: 'socios@crediactiva.pe',
      telefono: 'Anexo 101',
      descripcion: 'Consultas sobre membresía, aportes y actualización de datos en sede Huancayo.',
    },
    {
      icono: 'bi-cash-coin',
      area: 'Créditos y evaluación',
      responsable: 'Econ. Miguel Rojas',
      correo: 'creditos@crediactiva.pe',
      telefono: 'Anexo 205',
      descripcion: 'Estado de solicitudes, documentación y cronogramas de pago.',
    },
    {
      icono: 'bi-shield-check',
      area: 'Cobranzas y regularización',
      responsable: 'Lic. Patricia Vargas',
      correo: 'cobranzas@crediactiva.pe',
      telefono: 'Anexo 308',
      descripcion: 'Acuerdos de pago, refinanciamiento y orientación financiera.',
    },
  ];

  readonly redes = [
    { icono: 'bi-facebook', nombre: 'Facebook', usuario: '@CrediActivaHuancayo' },
    { icono: 'bi-instagram', nombre: 'Instagram', usuario: '@crediactiva_junin' },
    { icono: 'bi-linkedin', nombre: 'LinkedIn', usuario: 'CrediActiva Cooperativa' },
  ];

  enlaceExterno(canal: CanalContacto): string {
    return canal.enlace ?? '#';
  }

  esExterno(canal: CanalContacto): boolean {
    return canal.tipoEnlace === 'url';
  }
}
