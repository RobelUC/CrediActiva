import { Directive, HostListener } from '@angular/core';

/** Solo permite dígitos 0-9 (DNI, celular, etc.). */
@Directive({
  selector: 'input[caSoloNumeros]',
  standalone: true,
})
export class SoloNumerosDirective {
  private readonly teclasPermitidas = new Set([
    'Backspace',
    'Delete',
    'Tab',
    'Escape',
    'Enter',
    'ArrowLeft',
    'ArrowRight',
    'ArrowUp',
    'ArrowDown',
    'Home',
    'End',
  ]);

  @HostListener('keydown', ['$event'])
  onKeydown(event: KeyboardEvent): void {
    if (
      this.teclasPermitidas.has(event.key) ||
      event.ctrlKey ||
      event.metaKey ||
      event.altKey
    ) {
      return;
    }
    if (!/^\d$/.test(event.key)) {
      event.preventDefault();
    }
  }

  @HostListener('paste', ['$event'])
  onPaste(event: ClipboardEvent): void {
    const texto = event.clipboardData?.getData('text') ?? '';
    if (!/^\d*$/.test(texto)) {
      event.preventDefault();
    }
  }
}
