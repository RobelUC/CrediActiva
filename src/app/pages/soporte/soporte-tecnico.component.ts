import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

interface CanalSoporte {
  icono: string;
  titulo: string;
  detalle: string;
  enlace?: string;
  tipoEnlace?: 'tel' | 'mailto' | 'url';
}

interface FaqSoporte {
  pregunta: string;
  respuesta: string;
}

@Component({
  selector: 'ca-soporte-tecnico',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './soporte-tecnico.component.html',
  styleUrl: './soporte-tecnico.component.scss',
})
export class SoporteTecnicoComponent {
  private readonly route = inject(ActivatedRoute);

  readonly audiencia = this.route.snapshot.data['audiencia'] as 'socio' | 'admin';

  readonly titulo = this.audiencia === 'admin' ? 'Soporte técnico' : 'Soporte técnico';
  readonly subtitulo =
    this.audiencia === 'admin'
      ? 'Asistencia para el panel administrativo y operación del sistema'
      : 'Ayuda con el portal digital, acceso y uso de la plataforma';

  readonly correoSoporte = 'robelcortez13@gmail.co';
  readonly telefonoSoporte = '976 866 622';
  readonly telefonoSoporteEnlace = 'tel:+51976866622';
  readonly whatsappEnlace = 'https://wa.me/51976866622';

  readonly canales: readonly CanalSoporte[] = [
    {
      icono: 'bi-envelope-fill',
      titulo: 'Correo de soporte',
      detalle: this.correoSoporte,
      enlace: `mailto:${this.correoSoporte}`,
      tipoEnlace: 'mailto',
    },
    {
      icono: 'bi-telephone-fill',
      titulo: 'Mesa de ayuda TI',
      detalle: this.telefonoSoporte,
      enlace: this.telefonoSoporteEnlace,
      tipoEnlace: 'tel',
    },
    {
      icono: 'bi-whatsapp',
      titulo: 'WhatsApp Soporte',
      detalle: this.telefonoSoporte,
      enlace: this.whatsappEnlace,
      tipoEnlace: 'url',
    },
    {
      icono: 'bi-clock-history',
      titulo: 'Horario de atención',
      detalle: 'Lun–Vie 8:00 a.m. – 6:00 p.m. · Sáb 9:00 a.m. – 1:00 p.m.',
    },
  ];

  readonly faqsSocio: readonly FaqSoporte[] = [
    {
      pregunta: 'No puedo iniciar sesión',
      respuesta:
        'Verifique su DNI (8 dígitos) y contraseña. Si olvidó su clave, acérquese a una oficina en Huancayo con su documento para restablecerla.',
    },
    {
      pregunta: 'El simulador no carga',
      respuesta:
        'Cierre sesión, limpie la caché del navegador y vuelva a ingresar. Si persiste, escriba a robelcortez13@gmail.co indicando su DNI y navegador.',
    },
    {
      pregunta: 'No veo mis créditos actualizados',
      respuesta:
        'Los pagos registrados por la cooperativa pueden tardar unos minutos en reflejarse. Actualice la página o vuelva a entrar al portal.',
    },
  ];

  readonly faqsAdmin: readonly FaqSoporte[] = [
    {
      pregunta: 'Un socio no aparece en el listado',
      respuesta:
        'Confirme que el crédito esté aprobado (aportaciones) o que el filtro de socios no esté en «Solo inactivos». Use la búsqueda por DNI.',
    },
    {
      pregunta: 'Error al generar o aprobar un crédito',
      respuesta:
        'Revise que el socio esté activo y que no exceda el límite de solicitudes pendientes. Si el error continúa, capture pantalla y envíe a robelcortez13@gmail.co.',
    },
    {
      pregunta: 'Reportes no muestran datos recientes',
      respuesta:
        'Pulse «Generar reporte» para refrescar. En horas pico el proceso puede demorar unos segundos.',
    },
  ];

  readonly faqs = this.audiencia === 'admin' ? this.faqsAdmin : this.faqsSocio;

  enlaceExterno(canal: CanalSoporte): string {
    return canal.enlace ?? '#';
  }

  esExterno(canal: CanalSoporte): boolean {
    return canal.tipoEnlace === 'url';
  }
}
