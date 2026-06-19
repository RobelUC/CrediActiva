# Despliegue en producción (Render + Supabase)

Guía para publicar CrediActiva **sin localhost**, usando:

| Componente | Servicio |
|------------|----------|
| Base de datos | **Supabase** (ya configurado) |
| Backend (API + microservicios) | **Render** — Docker |
| Frontend (Angular) | **Render** — sitio estático |

---

## Resumen rápido

1. Subir el código a **GitHub**.
2. Crear cuenta en [render.com](https://render.com).
3. **New → Blueprint** → conectar repo → usa el archivo `render.yaml`.
4. Configurar variables de entorno (Supabase, CORS, API URL).
5. Entregar al profesor las dos URLs públicas.

---

## Paso 1 — Preparar Supabase

Ya tienes `SUPABASE_DATABASE_URL` en `backend/.env`. Para producción en la nube:

1. En Supabase → **Project Settings → Database**.
2. Copia la URI del **Transaction pooler** (puerto **6543**), más estable que `:5432`.
3. Esa URL la pegarás en Render como `SUPABASE_DATABASE_URL`.

**No subas** `backend/.env` a GitHub.

---

## Paso 2 — Subir a GitHub

```powershell
git add .
git commit -m "Configuración de despliegue en Render"
git push origin feature/backend
```

(Ajusta la rama si usas `main`.)

---

## Paso 3 — Desplegar con Render Blueprint

1. Entra a [dashboard.render.com](https://dashboard.render.com).
2. **New +** → **Blueprint**.
3. Conecta tu repositorio de GitHub.
4. Render detectará `render.yaml` y creará:
   - **crediactiva-api** — backend Docker (gateway + 4 microservicios)
   - **crediactiva-web** — frontend Angular estático

---

## Paso 4 — Variables de entorno en Render

### Servicio `crediactiva-api`

| Variable | Valor |
|----------|--------|
| `SUPABASE_DATABASE_URL` | URI del pooler Supabase (6543) |
| `CORS_ORIGINS` | URL del frontend (ver paso 5) |
| `ADMIN_PASSWORD` | Contraseña admin (`admin123` o la que uses) |
| `APISPERU_TOKEN` | Token ApisPeru (consulta DNI) |

Opcional: `ADMIN_SOCIO_DNI`, `APISPERU_SSL_VERIFY=false`

### Servicio `crediactiva-web`

| Variable | Valor |
|----------|--------|
| `API_URL` | URL pública del API **sin** `/api/v1` |

Ejemplo:

```text
API_URL=https://crediactiva-api.onrender.com
```

Tras cambiar `API_URL`, haz **Manual Deploy** del frontend para recompilar Angular con la URL correcta.

---

## Paso 5 — Orden recomendado

1. Despliega primero **crediactiva-api**.
2. Espera a que quede **Live** y prueba:  
   `https://TU-API.onrender.com/health`  
   Debe responder `"status": "ok"`.
3. Copia la URL del API (ej. `https://crediactiva-api.onrender.com`).
4. En **crediactiva-web**, configura:
   - `API_URL` = esa URL
   - Redeploy del frontend.
5. Copia la URL del frontend (ej. `https://crediactiva-web.onrender.com`).
6. Vuelve al API y configura:
   - `CORS_ORIGINS` = URL del frontend
   - Redeploy del API.

---

## Paso 6 — Verificación

| Prueba | URL |
|--------|-----|
| Health API | `https://TU-API.onrender.com/health` |
| App web | `https://TU-FRONT.onrender.com` |
| Login socio | DNI `74874853` / `demo1234` |
| Login admin | DNI `00000000` / `admin123` |

---

## Notas importantes

- **Plan free de Render:** el API se “duerme” tras ~15 min sin uso. La primera carga puede tardar **30–60 s** (cold start). El frontend estático no lleva `plan` en `render.yaml` (los static sites son gratis por defecto).
- **HTTPS:** Render incluye certificado SSL automático.
- **Microservicios:** en producción corren **dentro de un solo contenedor Docker** (`backend/Dockerfile` + `start-all.sh`); el gateway sigue siendo el único punto de entrada público.
- **Local sigue igual:** `npm start` + `backend/start-all.ps1` con `environment.ts` en localhost.

---

## Build local de producción (opcional)

```powershell
$env:API_URL="https://crediactiva-api.onrender.com"
node scripts/set-api-url.js
npm run build -- --configuration production
```

Los archivos quedan en `dist/crediactiva-web/browser`.

---

## Alternativas

| Frontend | Backend |
|----------|---------|
| Vercel / Netlify | Render (Docker) |
| Render Static | Railway / Fly.io |

La lógica es la misma: frontend apunta a `API_URL` y el gateway permite `CORS_ORIGINS`.

---

## Qué entregar al profesor

```text
Frontend: https://crediactiva-web.onrender.com
API:      https://crediactiva-api.onrender.com
Health:   https://crediactiva-api.onrender.com/health
BD:       Supabase (PostgreSQL en la nube)
```

Credenciales demo: ver README principal.
