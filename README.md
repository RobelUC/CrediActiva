# CrediActiva Web

Sistema web para una **cooperativa de crédito** en Huancayo, Perú. Permite a los socios simular créditos, solicitar préstamos y consultar su portal; y a los administradores gestionar socios, préstamos, aportaciones y reportes.

**Stack:** Angular 21 + Bootstrap (frontend) · FastAPI + microservicios (backend) · SQLite local o Supabase/PostgreSQL (base de datos).

**Repositorio:** https://github.com/RobelUC/CrediActiva

---

## Tabla de contenidos

1. [Descripción del proyecto](#descripción-del-proyecto)
2. [Arquitectura](#arquitectura)
3. [Requisitos](#requisitos)
4. [Guía rápida para evaluación](#guía-rápida-para-evaluación)
5. [Instalación completa](#instalación-completa)
6. [Cuentas de demostración](#cuentas-de-demostración)
7. [Flujo de demostración sugerido](#flujo-de-demostración-sugerido)
8. [Rutas de la aplicación](#rutas-de-la-aplicación)
9. [Base de datos](#base-de-datos)
10. [Solución de problemas](#solución-de-problemas)
11. [Estructura del proyecto](#estructura-del-proyecto)
12. [Documentación adicional](#documentación-adicional)

---

## Descripción del proyecto

CrediActiva es una plataforma integral para cooperativas de ahorro y crédito. Incluye:

| Módulo | Descripción |
|--------|-------------|
| **Landing** | Página institucional con productos, testimonios y FAQ |
| **Autenticación** | Registro e inicio de sesión de socios |
| **Simulador** | Cálculo de cuotas con sistema francés (Angular Signals) |
| **Portal del socio** | Resumen de cuenta, créditos, aportes y perfil |
| **Panel admin** | Dashboard, gestión de socios, préstamos, aportaciones y reportes |

El frontend se comunica con un **API Gateway** que enruta las peticiones a 4 microservicios especializados.

---

## Arquitectura

```
Angular (4200) ──► API Gateway (8000)
                        │
        ┌───────────────┼───────────────┬───────────────┐
        ▼               ▼               ▼               ▼
  auth-service   credit-service  payment-service  portal-service
     (8001)          (8002)          (8003)          (8004)
```

| Servicio | Puerto | Responsabilidad |
|----------|--------|-----------------|
| **api-gateway** | 8000 | Punto de entrada único, CORS, enrutamiento |
| **auth-service** | 8001 | Socios, login, registro, consulta DNI |
| **credit-service** | 8002 | Solicitudes, evaluación, cronograma de cuotas |
| **payment-service** | 8003 | Aportaciones y registro de pagos |
| **portal-service** | 8004 | Agregación de datos para portal y admin |

**Comunicación entre servicios:**
- `credit-service` → `auth-service` (datos del socio al aprobar crédito)
- `credit-service` → `payment-service` (crear cuotas al aprobar)
- `portal-service` → auth, credit, payment (dashboard y reportes)

---

## Requisitos

| Herramienta | Versión mínima |
|-------------|----------------|
| **Node.js** | 20+ (probado con v22) |
| **npm** | 10+ |
| **Python** | 3.11+ |
| **Sistema operativo** | Windows (PowerShell) |
| **Internet** | Requerido para `npm install` y Supabase |

---

## Guía rápida para evaluación

> Pasos mínimos para que un evaluador abra el proyecto y lo ejecute con backend real.

### 1. Clonar o descomprimir el proyecto

```powershell
git clone https://github.com/RobelUC/CrediActiva.git
cd CrediActiva
```

> Si recibes el proyecto en USB o carpeta, asegúrate de que incluya el archivo `backend/.env` (no está en GitHub por seguridad). Sin ese archivo, el backend usará SQLite local automáticamente.

### 2. Terminal 1 — Backend

```powershell
cd backend

# Solo la primera vez:
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r services\requirements.txt

# Si no existe backend/.env (clon desde GitHub):
copy .env.example .env
# Editar .env con la URL de Supabase, o dejar vacío para SQLite local

# Iniciar todos los microservicios:
.\start-all.ps1
```

**Verificar que funciona:** abrir http://localhost:8000/health

Debe mostrar todos los servicios en `"ok"`:

```json
{
  "status": "ok",
  "microservicios": {
    "auth-service": "ok",
    "credit-service": "ok",
    "payment-service": "ok",
    "portal-service": "ok"
  }
}
```

### 3. Terminal 2 — Frontend

```powershell
cd ProyectoFinalWeb   # o cd CrediActiva si clonaste el repo
npm install
npm start
```

Si `npm install` falla con error de certificados SSL:

```powershell
$env:NODE_OPTIONS="--use-system-ca"
npm install
npm start
```

**Abrir la aplicación:** http://localhost:4200

### 4. Confirmar modo backend activo

En `src/environments/environment.ts` debe estar:

```typescript
modoSoloFrontend: false,
apiUrl: 'http://localhost:8000/api/v1',
```

Con `modoSoloFrontend: true` la app usa datos simulados sin llamar al backend.

---

## Instalación completa

### Frontend (Angular)

```powershell
cd ProyectoFinalWeb
npm install
npm start
```

| Comando | Descripción |
|---------|-------------|
| `npm start` | Servidor de desarrollo en http://localhost:4200 |
| `npm run build` | Compilar para producción |
| `npm run build:css` | Compilar estilos Bootstrap personalizados |

### Backend (Microservicios)

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r services\requirements.txt
.\start-all.ps1
```

| URL | Descripción |
|-----|-------------|
| http://localhost:8000 | API Gateway |
| http://localhost:8000/health | Estado de todos los microservicios |
| http://localhost:8000/docs | Documentación Swagger (si está habilitada) |

### Configurar Supabase (opcional)

1. Copiar la plantilla de entorno:

```powershell
cd backend
copy .env.example .env
```

2. Editar `backend/.env` con la connection string desde el panel de Supabase:
   - **Project Settings → Database → Connection string → URI**
   - En Windows, si el puerto `5432` da timeout, usar el **Transaction pooler** (puerto `6543`)

3. Probar la conexión:

```powershell
py backend\test_supabase.py
```

4. Reiniciar el backend:

```powershell
.\start-all.ps1
```

> **Sin `backend/.env`:** el sistema usa **SQLite local** en `backend/services/*/data/`. Funciona sin configuración adicional.

Guía detallada: [`backend/docs/SUPABASE.md`](backend/docs/SUPABASE.md)

---

## Cuentas de demostración

Las cuentas demo se crean automáticamente al iniciar el backend (`start-all.ps1`).

### Socio (portal y simulador)

| Campo | Valor |
|-------|-------|
| DNI | `74874853` |
| Contraseña | `demo1234` |
| Portal | http://localhost:4200/portal |
| Simulador | http://localhost:4200/simulador |

### Administrador (panel admin)

| Campo | Valor |
|-------|-------|
| DNI | `00000000` |
| Contraseña | `admin123` |
| Panel | http://localhost:4200/admin |

---

## Flujo de demostración sugerido

1. **Landing** — Abrir http://localhost:4200 y recorrer la página institucional
2. **Login socio** — Ingresar con `74874853` / `demo1234`
3. **Portal** — Ver resumen, créditos activos y aportes en `/portal`
4. **Simulador** — Ir a `/simulador`, simular un crédito y enviar solicitud
5. **Login admin** — Cerrar sesión e ingresar con `00000000` / `admin123`
6. **Evaluar solicitud** — En `/admin/prestamos`, aprobar o rechazar la solicitud del socio
7. **Registrar pago** — En `/admin/aportaciones`, marcar una cuota como pagada
8. **Volver como socio** — Ver el crédito aprobado y cuotas actualizadas en el portal
9. **Reportes** — En `/admin/reportes`, mostrar el reporte de auditoría

---

## Rutas de la aplicación

| Ruta | Módulo | Acceso |
|------|--------|--------|
| `/` | Landing CrediActiva | Público |
| `/login` | Inicio de sesión | Público |
| `/registro` | Registro de socio | Público |
| `/simulador` | Simulador de crédito | Requiere sesión de socio |
| `/portal` | Resumen de cuenta | Socio autenticado |
| `/portal/creditos` | Créditos del socio | Socio autenticado |
| `/portal/aportes` | Historial de aportes | Socio autenticado |
| `/portal/perfil` | Perfil del socio | Socio autenticado |
| `/admin` | Dashboard administrativo | Administrador |
| `/admin/socios` | Gestión de socios (CRUD) | Administrador |
| `/admin/prestamos` | Solicitudes y evaluación | Administrador |
| `/admin/aportaciones` | Cuotas y pagos | Administrador |
| `/admin/reportes` | Reporte de auditoría | Administrador |

---

## Base de datos

Modelo relacional normalizado hasta **3FN** (Tercera Forma Normal).

| Servicio | Tablas principales |
|----------|-------------------|
| auth-service | `socios` |
| credit-service | `tipos_credito`, `solicitudes`, `evaluaciones_financieras`, `cuotas_credito` |
| payment-service | `aportaciones` |

**Documentación:**
- Modelo de datos: [`backend/docs/MODELO_BASE_DATOS.md`](backend/docs/MODELO_BASE_DATOS.md)
- Esquema SQL (3FN): [`backend/docs/esquema_3fn.sql`](backend/docs/esquema_3fn.sql)
- Esquema Supabase: [`backend/docs/esquema_supabase.sql`](backend/docs/esquema_supabase.sql)
- Diagrama ER (PDF): [`backend/docs/diagrama_er_crediactiva.pdf`](backend/docs/diagrama_er_crediactiva.pdf)
- Diagrama ER (PNG): [`backend/docs/diagrama_er_crediactiva.png`](backend/docs/diagrama_er_crediactiva.png)

---

## Solución de problemas

| Problema | Solución |
|----------|----------|
| `npm install` falla con `UNABLE_TO_VERIFY_LEAF_SIGNATURE` | Ejecutar `$env:NODE_OPTIONS="--use-system-ca"` antes de `npm install` |
| Puerto 4200 ya en uso | Cerrar otras instancias de `ng serve` o aceptar el puerto alternativo |
| `auth-service: offline` en `/health` | Cerrar procesos Python antiguos y volver a ejecutar `.\start-all.ps1` |
| Error de conexión a Supabase | Comentar `SUPABASE_DATABASE_URL` en `backend/.env` y reiniciar (usa SQLite local). O copiar una nueva connection string desde el panel de Supabase |
| Frontend muestra datos falsos | Verificar `modoSoloFrontend: false` en `src/environments/environment.ts` |
| `npm install` falla con Angular 21 | Comprobar versión con `npm view @angular/core version`. Si no existe v21, ajustar `package.json` a `^20.0.0` |
| Login devuelve error de conexión | Confirmar que el backend está activo en http://localhost:8000/health |

### Probar conexión a Supabase manualmente

```powershell
cd backend
.\.venv\Scripts\activate
py test_supabase.py
```

---

## Estructura del proyecto

```
ProyectoFinalWeb/
├── src/                          # Frontend Angular
│   ├── app/
│   │   ├── components/           # Simulador de crédito
│   │   ├── core/                 # Servicios, guards, modelos, pipes
│   │   └── pages/                # Landing, auth, portal, admin
│   └── environments/             # Configuración (API URL, modo demo)
├── assets/scss/                  # Tema Bootstrap CrediActiva
├── backend/
│   ├── gateway/                  # API Gateway (puerto 8000)
│   ├── services/
│   │   ├── auth_service/         # Autenticación y socios (8001)
│   │   ├── credit_service/       # Solicitudes y créditos (8002)
│   │   ├── payment_service/      # Aportaciones y pagos (8003)
│   │   └── portal_service/       # Agregación portal/admin (8004)
│   ├── docs/                     # Modelo BD, esquemas SQL, diagramas
│   ├── start-all.ps1             # Script para iniciar todos los servicios
│   ├── test_supabase.py          # Prueba de conexión a Supabase
│   └── .env.example              # Plantilla de variables de entorno
├── package.json
└── README.md
```

---

## Documentación adicional

| Archivo | Contenido |
|---------|-----------|
| [`backend/README.md`](backend/README.md) | Arquitectura de microservicios y endpoints |
| [`backend/docs/SUPABASE.md`](backend/docs/SUPABASE.md) | Guía de configuración de Supabase |
| [`backend/docs/DESPLIEGUE.md`](backend/docs/DESPLIEGUE.md) | Publicar en Render (sin localhost) |
| [`backend/docs/MODELO_BASE_DATOS.md`](backend/docs/MODELO_BASE_DATOS.md) | Modelo relacional 3FN |
| [`src/app/components/credit-simulator/README.md`](src/app/components/credit-simulator/README.md) | Documentación del simulador |

---

## Endpoints principales (vía Gateway)

| Método | Ruta | Servicio |
|--------|------|----------|
| POST | `/api/v1/auth/login` | auth-service |
| POST | `/api/v1/auth/registro` | auth-service |
| POST | `/api/v1/solicitudes` | credit-service |
| GET/POST/PUT/DELETE | `/api/v1/admin/socios` | auth-service |
| GET/POST | `/api/v1/admin/solicitudes` | credit-service |
| GET/POST | `/api/v1/admin/aportaciones` | payment-service |
| GET | `/api/v1/admin/dashboard` | portal-service |
| GET | `/api/v1/admin/reportes/auditoria` | portal-service |
| GET | `/api/v1/portal/{dni}/*` | portal-service |

---

**CrediActiva** — Cooperativa de Crédito, Huancayo, Perú.
