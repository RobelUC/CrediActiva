-- CrediActiva — Esquema relacional normalizado (3FN)
-- Referencia académica. En producción cada servicio crea su BD vía SQLAlchemy.

-- ========== AUTH SERVICE ==========
CREATE TABLE IF NOT EXISTS socios (
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

-- ========== CREDIT SERVICE ==========
CREATE TABLE IF NOT EXISTS tipos_credito (
    codigo    VARCHAR(20) PRIMARY KEY,
    nombre    VARCHAR(50) NOT NULL,
    tea_anual FLOAT       NOT NULL
);

INSERT OR IGNORE INTO tipos_credito (codigo, nombre, tea_anual) VALUES
    ('Emprendedor', 'Crédito Emprendedor', 14.5),
    ('Vivienda',    'Crédito Vivienda',    10.5),
    ('Agrícola',    'Crédito Agrícola',    12.0);

CREATE TABLE IF NOT EXISTS solicitudes (
    id_solicitud          VARCHAR(36) PRIMARY KEY,
    dni_usuario           VARCHAR(8)  NOT NULL,
    id_tipo_credito       VARCHAR(20) NOT NULL,
    monto                 FLOAT       NOT NULL,
    plazo_meses           INTEGER     NOT NULL,
    estado_preaprobacion  VARCHAR(30) NOT NULL,
    estado_evaluacion     VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    mensaje               TEXT        NOT NULL DEFAULT '',
    observaciones         TEXT        NOT NULL DEFAULT '',
    fecha_registro        DATETIME    NOT NULL,
    FOREIGN KEY (id_tipo_credito) REFERENCES tipos_credito(codigo)
);

CREATE TABLE IF NOT EXISTS evaluaciones_financieras (
    id_evaluacion           VARCHAR(36) PRIMARY KEY,
    id_solicitud            VARCHAR(36) NOT NULL UNIQUE,
    tea_aplicada            FLOAT NOT NULL,
    tasa_mensual_efectiva   FLOAT NOT NULL,
    cuota_mensual           FLOAT NOT NULL,
    interes_total           FLOAT NOT NULL,
    monto_total_a_pagar     FLOAT NOT NULL,
    FOREIGN KEY (id_solicitud) REFERENCES solicitudes(id_solicitud)
);

CREATE TABLE IF NOT EXISTS cuotas_credito (
    id_cuota           VARCHAR(36) PRIMARY KEY,
    id_solicitud       VARCHAR(36) NOT NULL,
    numero_cuota       INTEGER     NOT NULL,
    fecha_vencimiento  DATE        NOT NULL,
    cuota              FLOAT       NOT NULL,
    capital            FLOAT       NOT NULL,
    interes            FLOAT       NOT NULL,
    saldo_restante     FLOAT       NOT NULL,
    FOREIGN KEY (id_solicitud) REFERENCES solicitudes(id_solicitud),
    UNIQUE (id_solicitud, numero_cuota)
);

-- ========== PAYMENT SERVICE ==========
CREATE TABLE IF NOT EXISTS aportaciones (
    id_aportacion      VARCHAR(36) PRIMARY KEY,
    id_solicitud       VARCHAR(36) NOT NULL,
    id_cuota           VARCHAR(36),
    dni_socio          VARCHAR(8)  NOT NULL,
    numero_cuota       INTEGER     NOT NULL,
    monto_cuota        FLOAT       NOT NULL,
    fecha_vencimiento  DATE        NOT NULL,
    fecha_pago         DATE,
    estado_pago        VARCHAR(10) NOT NULL DEFAULT 'PENDIENTE',
    UNIQUE (id_solicitud, numero_cuota)
);
