# CrediActiva Web

Cooperativa de crédito — Huancayo, Perú. Frontend Angular + estilos Bootstrap.

## Requisitos

- Node.js 20+ (probado con v22)
- npm 10+

## Instalación

En PowerShell (si npm falla con `UNABLE_TO_VERIFY_LEAF_SIGNATURE`):

```powershell
cd ProyectoFinalWeb
$env:NODE_OPTIONS="--use-system-ca"
npm install
npm start
```

Sin error de certificados:

```bash
npm install
npm start
```

La app queda en `http://localhost:4200`.

### Backend — Microservicios

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r services\requirements.txt
.\start-all.ps1
```

API Gateway: `http://localhost:8000` · Health: `http://localhost:8000/health`

Arquitectura: **4 microservicios + API Gateway**, cada uno con SQLite propia. Ver `backend/README.md`.

### Panel de administración

- URL: `http://localhost:4200/admin`
- Credenciales demo: DNI `00000000` · contraseña `admin123`

### Portal del socio y simulador (cuenta demo)

- Login: DNI `74874853` · contraseña `demo1234`
- Portal: `http://localhost:4200/portal`
- Simulador: `http://localhost:4200/simulador`
- La cuenta demo se crea automáticamente al iniciar el backend (`start-all.ps1`)

## Estructura principal

| Ruta | Descripción |
|------|-------------|
| `src/app/components/credit-simulator/` | Simulador con Signals |
| `src/app/core/services/credit.service.ts` | POST de solicitudes |
| `assets/scss/` | Variables y tema CrediActiva |

## Si `npm install` falla con Angular 21

Comprueba la versión publicada:

```bash
npm view @angular/core version
```

Si aún no existe v21 en el registro, ajusta en `package.json` a la última estable (p. ej. `^20.0.0`) y vuelve a instalar.
