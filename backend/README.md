# CrediActiva — Arquitectura de Microservicios

Backend dividido en **4 microservicios + API Gateway**. Por defecto usa **SQLite local**; opcionalmente **Supabase (PostgreSQL)** con una sola base compartida. Ver `docs/SUPABASE.md`.

## Arquitectura

```
Angular (4200) ──► API Gateway (8000)
                        │
        ┌───────────────┼───────────────┬───────────────┐
        ▼               ▼               ▼               ▼
  auth-service   credit-service  payment-service  portal-service
     (8001)          (8002)          (8003)          (8004)
   auth + credit + payment (Supabase o SQLite)   (sin BD)
```

| Servicio | Puerto | Responsabilidad | Base de datos |
|----------|--------|-----------------|---------------|
| **auth-service** | 8001 | Socios, perfil | Tabla `socios` (Supabase o `data/auth.db`) |
| **credit-service** | 8002 | Solicitudes, evaluación, cronograma | Tablas crédito (Supabase o `data/credit.db`) |
| **payment-service** | 8003 | Cuotas y pagos | Tabla `aportaciones` (Supabase o `data/payment.db`) |
| **portal-service** | 8004 | Portal del socio, dashboard, reportes | Agrega vía HTTP |
| **api-gateway** | 8000 | Punto de entrada único, CORS | — |

## Requisitos

- Python 3.11+
- Node.js 20+ (frontend)

## Instalación

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r services\requirements.txt
```

### Supabase (opcional)

```powershell
copy .env.example .env
# Edita .env con SUPABASE_DATABASE_URL desde el panel de Supabase
# Opcional: ejecuta docs/esquema_supabase.sql en SQL Editor
```

Guía completa: **`docs/SUPABASE.md`**.

## Ejecutar (todos los servicios)

```powershell
cd backend
.\start-all.ps1
```

O manualmente (5 terminales):

```powershell
cd backend\services\auth_service
..\..\..\.venv\Scripts\uvicorn app.main:app --port 8001

cd backend\services\credit_service
..\..\..\.venv\Scripts\uvicorn app.main:app --port 8002

cd backend\services\payment_service
..\..\..\.venv\Scripts\uvicorn app.main:app --port 8003

cd backend\services\portal_service
..\..\..\.venv\Scripts\uvicorn app.main:app --port 8004

cd backend\gateway
..\..\.venv\Scripts\uvicorn app.main:app --port 8000
```

## Endpoints (vía Gateway)

El frontend sigue usando `http://localhost:8000` — el gateway enruta automáticamente:

- `POST /api/v1/solicitudes` → credit-service
- `/api/v1/admin/socios` → auth-service
- `/api/v1/admin/solicitudes` → credit-service
- `/api/v1/admin/aportaciones` → payment-service
- `/api/v1/admin/dashboard` → portal-service
- `/api/v1/portal/{dni}/*` → portal-service o auth-service (perfil)

Health check de todos: `GET http://localhost:8000/health`

## Comunicación entre servicios

- **credit-service** → auth-service (nombre del socio al aprobar crédito)
- **credit-service** → payment-service (crear cuotas al aprobar)
- **portal-service** → auth, credit, payment (agregar datos del portal y admin)
