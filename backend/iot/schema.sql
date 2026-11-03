-- Esquema IoT — TILCOR S.A.S. (PostgreSQL 14+; compatible con TimescaleDB)
CREATE TABLE IF NOT EXISTS sensores (
  id          INTEGER PRIMARY KEY,
  galpon      INTEGER NOT NULL,
  tipo        TEXT    NOT NULL,           -- temperatura | humedad | calidad_aire | flujo_agua | temp_agua
  numero      INTEGER NOT NULL,
  unidad      TEXT    NOT NULL,
  UNIQUE (galpon, tipo, numero)
);

CREATE TABLE IF NOT EXISTS lecturas (
  ts          TIMESTAMPTZ      NOT NULL DEFAULT now(),
  sensor_id   INTEGER          NOT NULL REFERENCES sensores(id),
  valor       DOUBLE PRECISION NOT NULL,
  estado      TEXT             NOT NULL CHECK (estado IN ('ok','warning','critico'))
);
CREATE INDEX IF NOT EXISTS ix_lecturas_sensor_ts ON lecturas (sensor_id, ts DESC);
-- Con TimescaleDB instalado (producción):
-- SELECT create_hypertable('lecturas', 'ts', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS alertas_iot (
  id          BIGSERIAL PRIMARY KEY,
  ts          TIMESTAMPTZ NOT NULL DEFAULT now(),
  sensor_id   INTEGER     NOT NULL REFERENCES sensores(id),
  severidad   TEXT        NOT NULL CHECK (severidad IN ('warning','critico')),
  valor       DOUBLE PRECISION NOT NULL,
  mensaje     TEXT        NOT NULL,
  revisada    BOOLEAN     NOT NULL DEFAULT FALSE
);

INSERT INTO sensores (id, galpon, tipo, numero, unidad) VALUES
  (1,1,'temperatura',1,'C'), (2,1,'temperatura',2,'C'),
  (3,1,'humedad',1,'%'),     (4,1,'humedad',2,'%'),
  (5,1,'calidad_aire',1,'ppm'), (6,1,'flujo_agua',1,'L'),
  (7,1,'temp_agua',1,'C')
ON CONFLICT DO NOTHING;
