-- Auditoría por triggers (Tesis 13.3): quién, cuándo, tabla, operación y snapshot antes/después.
CREATE TABLE IF NOT EXISTS auditoria (
  id        BIGSERIAL PRIMARY KEY,
  ts        TIMESTAMPTZ NOT NULL DEFAULT now(),
  usuario   TEXT        NOT NULL DEFAULT coalesce(nullif(current_setting('app.usuario', true), ''), current_user),
  tabla     TEXT        NOT NULL,
  operacion TEXT        NOT NULL CHECK (operacion IN ('INSERT','UPDATE','DELETE')),
  antes     JSONB,
  despues   JSONB
);
CREATE INDEX IF NOT EXISTS ix_auditoria_tabla_ts ON auditoria (tabla, ts DESC);

CREATE OR REPLACE FUNCTION fn_auditar() RETURNS trigger AS $$
BEGIN
  INSERT INTO auditoria (tabla, operacion, antes, despues)
  VALUES (TG_TABLE_NAME, TG_OP,
          CASE WHEN TG_OP IN ('UPDATE','DELETE') THEN to_jsonb(OLD) END,
          CASE WHEN TG_OP IN ('INSERT','UPDATE') THEN to_jsonb(NEW) END);
  RETURN COALESCE(NEW, OLD);
END; $$ LANGUAGE plpgsql;

-- Ejemplo de uso sobre una tabla (repetir por cada tabla auditada):
-- CREATE TRIGGER trg_aud_alertas AFTER INSERT OR UPDATE OR DELETE ON alertas_iot
--   FOR EACH ROW EXECUTE FUNCTION fn_auditar();
-- La aplicación fija el usuario por transacción:  SET LOCAL app.usuario = 'mcarnielli';
