# CreditSimulatorComponent

Componente standalone Angular 21 para CrediActiva.

## Uso

```html
<ca-credit-simulator (solicitudCredito)="onSolicitud($event)" />
```

```typescript
import { CreditSimulatorComponent } from './components/credit-simulator/credit-simulator.component';
import type { ResumenSimulacion } from './components/credit-simulator/credit-simulator.types';

onSolicitud(resumen: ResumenSimulacion): void {
  console.log(resumen);
}
```

## TEA por tipo

| Tipo | TEA |
|------|-----|
| Emprendedor | 14.5% |
| Agrícola | 12.0% |
| Vivienda | 10.5% (tasa preferencial) |

## Ejecutar

```bash
npm install
npm start
```
