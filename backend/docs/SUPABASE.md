# Migración a Supabase (PostgreSQL)

Los microservicios usan **una sola base PostgreSQL** en Supabase por defecto. Cada servicio crea solo sus tablas al arrancar (`init_db()`). Si no configuras `.env`, sigue funcionando con SQLite local.

## 1. Crear proyecto en Supabase

1. Entra en [supabase.com](https://supabase.com) y crea un proyecto.
2. Guarda la contraseña de la base de datos.

## 2. Crear tablas (opcional pero recomendado)

En **SQL Editor**, pega y ejecuta el archivo:

`backend/docs/esquema_supabase.sql`

Si omites este paso, las tablas se crearán al iniciar los servicios (SQLAlchemy `create_all`).

## 3. Configurar conexión

```powershell
cd backend
copy .env.example .env
```

Edita `backend/.env` y pega la **Connection string** (URI):

- **Project Settings → Database → Connection string → URI**
- Si ves **`connection timeout expired`** en Windows, usa la URL del **Transaction pooler** (puerto **6543**, host `*.pooler.supabase.com`), no la directa `:5432`.
- La conexión directa `db.xxx.supabase.co:5432` a veces queda bloqueada por red/firewall.

Ejemplo:

```env
SUPABASE_DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

La app convierte automáticamente `postgresql://` y `postgres://` a `postgresql+psycopg://`.

## 4. Instalar dependencias

```powershell
cd backend
.\.venv\Scripts\activate
pip install -r services\requirements.txt
```

## 5. Arrancar servicios

```powershell
.\start-all.ps1
```

Al iniciar, cada microservicio conecta a Supabase y crea/actualiza su esquema.

## 6. Ver datos

- Panel de Supabase: **Table Editor**
- O desde el repo: `py backend\ver_tablas.py` (lee `SUPABASE_DATABASE_URL` si existe)

## Variables de entorno

| Variable | Uso |
|----------|-----|
| `SUPABASE_DATABASE_URL` | URL compartida para auth, credit y payment |
| `DATABASE_URL` | Alternativa genérica |
| `AUTH_DATABASE_URL` | Sobrescribe solo auth-service |
| `CREDIT_DATABASE_URL` | Sobrescribe solo credit-service |
| `PAYMENT_DATABASE_URL` | Sobrescribe solo payment-service |

## Notas

- **No subas** `backend/.env` a Git (ya está en `.gitignore`).
- Los datos antiguos en `services/*/data/*.db` no se migran solos; exporta/importa manualmente si los necesitas.
