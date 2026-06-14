-- CrediActiva — Esquema PostgreSQL para Supabase (3FN, base única)
-- Ejecutar en: Supabase → SQL Editor → New query → Run

-- ========== AUTH ==========
CREATE TABLE IF NOT EXISTS socios (
    id_socio        VARCHAR(36) PRIMARY KEY,
    dni             VARCHAR(8)  NOT NULL,
    nombres         VARCHAR(100) NOT NULL,
    apellidos       VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    telefono        VARCHAR(20)  NOT NULL DEFAULT '',
    aporte_mensual  DOUBLE PRECISION NOT NULL DEFAULT 50.0,
    fecha_registro  TIMESTAMPTZ  NOT NULL,
    activo          BOOLEAN      NOT NULL DEFAULT TRUE,
    password_hash   VARCHAR(255),
    rol             VARCHAR(10)  NOT NULL DEFAULT 'socio',
    CONSTRAINT uq_socios_dni   UNIQUE (dni),
    CONSTRAINT uq_socios_email UNIQUE (email)
);

-- ========== CREDIT ==========
CREATE TABLE IF NOT EXISTS tipos_credito (
    codigo    VARCHAR(20) PRIMARY KEY,
    nombre    VARCHAR(50) NOT NULL,
    tea_anual DOUBLE PRECISION NOT NULL
);

INSERT INTO tipos_credito (codigo, nombre, tea_anual) VALUES
    ('Emprendedor', 'Crédito Emprendedor', 14.5),
    ('Vivienda',    'Crédito Vivienda',    10.5),
    ('Agrícola',    'Crédito Agrícola',    12.0)
ON CONFLICT (codigo) DO NOTHING;

CREATE TABLE IF NOT EXISTS solicitudes (
    id_solicitud          VARCHAR(36) PRIMARY KEY,
    dni_usuario           VARCHAR(8)  NOT NULL,
    id_tipo_credito       VARCHAR(20) NOT NULL REFERENCES tipos_credito(codigo),
    monto                 DOUBLE PRECISION NOT NULL,
    plazo_meses           INTEGER     NOT NULL,
    estado_preaprobacion  VARCHAR(30) NOT NULL,
    estado_evaluacion     VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    mensaje               TEXT        NOT NULL DEFAULT '',
    observaciones         TEXT        NOT NULL DEFAULT '',
    fecha_registro        TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluaciones_financieras (
    id_evaluacion           VARCHAR(36) PRIMARY KEY,
    id_solicitud            VARCHAR(36) NOT NULL UNIQUE REFERENCES solicitudes(id_solicitud),
    tea_aplicada            DOUBLE PRECISION NOT NULL,
    tasa_mensual_efectiva   DOUBLE PRECISION NOT NULL,
    cuota_mensual           DOUBLE PRECISION NOT NULL,
    interes_total           DOUBLE PRECISION NOT NULL,
    monto_total_a_pagar     DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS cuotas_credito (
    id_cuota           VARCHAR(36) PRIMARY KEY,
    id_solicitud       VARCHAR(36) NOT NULL REFERENCES solicitudes(id_solicitud),
    numero_cuota       INTEGER     NOT NULL,
    fecha_vencimiento  DATE        NOT NULL,
    cuota              DOUBLE PRECISION NOT NULL,
    capital            DOUBLE PRECISION NOT NULL,
    interes            DOUBLE PRECISION NOT NULL,
    saldo_restante     DOUBLE PRECISION NOT NULL,
    UNIQUE (id_solicitud, numero_cuota)
);

-- ========== PAYMENT ==========
CREATE TABLE IF NOT EXISTS aportaciones (
    id_aportacion      VARCHAR(36) PRIMARY KEY,
    id_solicitud       VARCHAR(36) NOT NULL,
    id_cuota           VARCHAR(36),
    dni_socio          VARCHAR(8)  NOT NULL,
    numero_cuota       INTEGER     NOT NULL,
    monto_cuota        DOUBLE PRECISION NOT NULL,
    fecha_vencimiento  DATE        NOT NULL,
    fecha_pago         DATE,
    estado_pago        VARCHAR(10) NOT NULL DEFAULT 'PENDIENTE',
    UNIQUE (id_solicitud, numero_cuota)
);
