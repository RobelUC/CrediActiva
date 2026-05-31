# Modelo de Base de Datos — CrediActiva

Diseño relacional normalizado hasta **3FN** (Tercera Forma Normal), alineado con los requerimientos del sistema de cooperativa de crédito.

## Arquitectura de datos

El proyecto usa **microservicios** con esquema normalizado (3FN). En **desarrollo local** cada servicio puede usar su SQLite; en **Supabase** comparten una sola base PostgreSQL (`SUPABASE_DATABASE_URL`). Las referencias entre servicios usan **claves lógicas** (`dni`, `id_solicitud`, `id_cuota`) sin FK entre bounded contexts de auth y payment.

| Servicio | Persistencia | Entidades principales |
|----------|--------------|------------------------|
| auth-service | `socios` | socios |
| credit-service | tablas de crédito | tipos_credito, solicitudes, evaluaciones_financieras, cuotas_credito |
| payment-service | `aportaciones` | aportaciones |

Configuración Supabase: ver `docs/SUPABASE.md` y `docs/esquema_supabase.sql`.

---

## Diagrama entidad-relación (modelo lógico)

```mermaid
erDiagram
    SOCIOS ||--o{ SOLICITUDES : "solicita (dni_usuario)"
    TIPOS_CREDITO ||--o{ SOLICITUDES : "clasifica"
    SOLICITUDES ||--|| EVALUACIONES_FINANCIERAS : "tiene"
    SOLICITUDES ||--o{ CUOTAS_CREDITO : "genera"
    SOLICITUDES ||--o{ APORTACIONES : "registra pagos"
    CUOTAS_CREDITO ||--o| APORTACIONES : "referencia (id_cuota)"

    SOCIOS {
        string id_socio PK
        string dni UK
        string nombres
        string apellidos
        string email UK
        string telefono
        float aporte_mensual
        datetime fecha_registro
        bool activo
        string password_hash
    }

    TIPOS_CREDITO {
        string codigo PK
        string nombre
        float tea_anual
    }

    SOLICITUDES {
        string id_solicitud PK
        string dni_usuario FK_logica
        string id_tipo_credito FK
        float monto
        int plazo_meses
        string estado_preaprobacion
        string estado_evaluacion
        string mensaje
        string observaciones
        datetime fecha_registro
    }

    EVALUACIONES_FINANCIERAS {
        string id_evaluacion PK
        string id_solicitud FK UK
        float tea_aplicada
        float tasa_mensual_efectiva
        float cuota_mensual
        float interes_total
        float monto_total_a_pagar
    }

    CUOTAS_CREDITO {
        string id_cuota PK
        string id_solicitud FK
        int numero_cuota
        date fecha_vencimiento
        float cuota
        float capital
        float interes
        float saldo_restante
    }

    APORTACIONES {
        string id_aportacion PK
        string id_solicitud FK_logica
        string id_cuota FK_logica
        string dni_socio FK_logica
        int numero_cuota
        float monto_cuota
        date fecha_vencimiento
        date fecha_pago
        string estado_pago
    }
```

---

## Normalización (1FN → 3FN)

### Primera Forma Normal (1FN)
- Todos los atributos son **atómicos** (sin listas embebidas).
- Se eliminaron columnas JSON `cronograma` y `auditoria` de `solicitudes`.
- El cronograma vive en `cuotas_credito` (una fila por cuota).
- La auditoría financiera vive en `evaluaciones_financieras`.

### Segunda Forma Normal (2FN)
- Todas las tablas tienen **clave primaria simple** (`id_socio`, `id_solicitud`, `id_cuota`, etc.).
- No existen dependencias parciales: atributos de cuota dependen de `id_cuota`, no solo de `id_solicitud`.

### Tercera Forma Normal (3FN)
- **Catálogo `tipos_credito`**: `tea_anual` y `nombre` dependen del código del producto, no de la solicitud.
- **Eliminado `nombre_socio`** de `aportaciones`: violaba 3FN (nombre dependía de `dni_socio`, no de `id_aportacion`). El nombre se obtiene en tiempo de lectura desde auth-service.
- **`evaluaciones_financieras`**: descompone atributos derivados del cálculo crediticio en tabla 1:1 con la solicitud.
- **`socios`**: cada campo depende únicamente de `id_socio`; `dni` y `email` son claves alternativas (UNIQUE).

---

## DDL de referencia

### auth-service (`socios`)

```sql
CREATE TABLE socios (
    id_socio        VARCHAR(36) PRIMARY KEY,
    dni             VARCHAR(8)  NOT NULL,
    nombres         VARCHAR(100) NOT NULL,
    apellidos       VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    telefono        VARCHAR(20)  NOT NULL DEFAULT '',
    aporte_mensual  FLOAT        NOT NULL DEFAULT 50.0,
    fecha_registro  DATETIME     NOT NULL,
    activo          BOOLEAN      NOT NULL DEFAULT 1,
    password_hash   VARCHAR(255),
    CONSTRAINT uq_socios_dni   UNIQUE (dni),
    CONSTRAINT uq_socios_email UNIQUE (email)
);
```

### credit-service

```sql
CREATE TABLE tipos_credito (
    codigo    VARCHAR(20) PRIMARY KEY,
    nombre    VARCHAR(50) NOT NULL,
    tea_anual FLOAT       NOT NULL
);

CREATE TABLE solicitudes (
    id_solicitud          VARCHAR(36) PRIMARY KEY,
    dni_usuario           VARCHAR(8)  NOT NULL,
    id_tipo_credito       VARCHAR(20) NOT NULL REFERENCES tipos_credito(codigo),
    monto                 FLOAT       NOT NULL,
    plazo_meses           INTEGER     NOT NULL,
    estado_preaprobacion  VARCHAR(30) NOT NULL,
    estado_evaluacion     VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    mensaje               TEXT        NOT NULL DEFAULT '',
    observaciones         TEXT        NOT NULL DEFAULT '',
    fecha_registro        DATETIME    NOT NULL
);

CREATE TABLE evaluaciones_financieras (
    id_evaluacion           VARCHAR(36) PRIMARY KEY,
    id_solicitud            VARCHAR(36) NOT NULL UNIQUE REFERENCES solicitudes(id_solicitud),
    tea_aplicada            FLOAT NOT NULL,
    tasa_mensual_efectiva   FLOAT NOT NULL,
    cuota_mensual           FLOAT NOT NULL,
    interes_total           FLOAT NOT NULL,
    monto_total_a_pagar     FLOAT NOT NULL
);

CREATE TABLE cuotas_credito (
    id_cuota           VARCHAR(36) PRIMARY KEY,
    id_solicitud       VARCHAR(36) NOT NULL REFERENCES solicitudes(id_solicitud),
    numero_cuota       INTEGER     NOT NULL,
    fecha_vencimiento  DATE        NOT NULL,
    cuota              FLOAT       NOT NULL,
    capital            FLOAT       NOT NULL,
    interes            FLOAT       NOT NULL,
    saldo_restante     FLOAT       NOT NULL,
    CONSTRAINT uq_solicitud_cuota UNIQUE (id_solicitud, numero_cuota)
);
```

### payment-service

```sql
CREATE TABLE aportaciones (
    id_aportacion      VARCHAR(36) PRIMARY KEY,
    id_solicitud       VARCHAR(36) NOT NULL,
    id_cuota           VARCHAR(36),
    dni_socio          VARCHAR(8)  NOT NULL,
    numero_cuota       INTEGER     NOT NULL,
    monto_cuota        FLOAT       NOT NULL,
    fecha_vencimiento  DATE        NOT NULL,
    fecha_pago         DATE,
    estado_pago        VARCHAR(10) NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT uq_aportacion_cuota UNIQUE (id_solicitud, numero_cuota)
);
```

---

## Catálogo inicial (`tipos_credito`)

| codigo | nombre | tea_anual |
|--------|--------|-----------|
| Emprendedor | Crédito Emprendedor | 14.5 % |
| Vivienda | Crédito Vivienda | 10.5 % |
| Agrícola | Crédito Agrícola | 12.0 % |

---

## Correspondencia con requerimientos funcionales

| Requerimiento | Tablas |
|---------------|--------|
| Registro y gestión de socios | `socios` |
| Autenticación | `socios.password_hash` |
| Simulación y solicitud de crédito | `solicitudes`, `tipos_credito`, `evaluaciones_financieras` |
| Evaluación admin de préstamos | `solicitudes.estado_evaluacion`, `cuotas_credito` |
| Cronograma de pagos | `cuotas_credito` |
| Control de aportaciones/cuotas | `aportaciones` |
| Reportes de cartera | JOIN lógico entre servicios vía `portal-service` |

---

## Migración desde esquema anterior

Al reiniciar los microservicios, `init_db()` detecta columnas legacy (`cronograma`, `auditoria`, `nombre_socio`) y migra automáticamente al esquema 3FN.

Si prefieres empezar limpio, elimina las bases SQLite en:

- `backend/services/auth_service/data/auth.db`
- `backend/services/credit_service/data/credit.db`
- `backend/services/payment_service/data/payment.db`

y ejecuta `backend/start-all.ps1`.

---

## Archivos de implementación

| Archivo | Descripción |
|---------|-------------|
| `backend/services/auth_service/app/models.py` | Entidad Socio |
| `backend/services/credit_service/app/models.py` | Catálogo, solicitudes, evaluación, cuotas |
| `backend/services/payment_service/app/models.py` | Aportaciones |
| `backend/docs/esquema_3fn.sql` | Script DDL consolidado |
| `backend/docs/diagrama_er_crediactiva.png` | Diagrama ER (PNG, 200 dpi) |
| `backend/docs/diagrama_er_crediactiva.pdf` | Diagrama ER (PDF vectorial) |
| `backend/generar_diagrama_er.py` | Regenerar diagrama ER |
