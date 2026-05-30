# CrediActiva — Sistema de estilos

Cooperativa de crédito (Huancayo). Identidad visual:

| Rol | Color | Hex |
|-----|-------|-----|
| Principal (seguridad) | Azul marino | `#002855` |
| Secundario (crecimiento) | Verde bosque | `#00703C` |
| Tipografía | Poppins / Roboto | Google Fonts |

## Uso rápido (CDN Bootstrap)

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="assets/css/crediactiva.css" rel="stylesheet">
```

- `.btn-primary` → azul marino  
- `.btn-success` → verde bosque  
- `.btn-crediactiva-primary` / `.btn-crediactiva-success` → alias de marca  

## Compilación SCSS (recomendado)

```bash
npm install
npm run build:css
```

Genera `assets/css/crediactiva.bundle.css` con variables Bootstrap sobrescritas desde el inicio.
