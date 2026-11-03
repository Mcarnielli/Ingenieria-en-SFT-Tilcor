# Módulo IoT — ingesta MQTT → PostgreSQL

Flujo: sensor (ESP32) → broker MQTT (Mosquitto) → `ingest.py` → PostgreSQL (`lecturas`, `alertas_iot`).

## Uso
```bash
pip install -r requirements.txt
psql "$DATABASE_URL" -f schema.sql
export DATABASE_URL="postgresql://user:pass@host/tilcor"
export MQTT_HOST=broker.ejemplo.com MQTT_PORT=1883 MQTT_USER=... MQTT_PASS=...   # MQTT_TLS=1 y puerto 8883 si hay TLS
python ingest.py                         # suscriptor
python simulador.py --host broker.ejemplo.com --intervalo 5          # sensores simulados
python simulador.py --host ... --anomalia humedad                    # fuerza una alerta crítica
```
Topic: `gallinero/<galpón>/sensores/<tipo>/<n>` · Payload: `{"sensor_id":1,"valor":25.6,"unidad":"C"}`

## Pruebas
```bash
pip install -r requirements-dev.txt
TEST_DATABASE_URL="host=... dbname=tilcor_test" pytest tests -v
```
29 pruebas: umbrales (17), ingesta (10, incluye descarte de datos inválidos y no repetir alertas) y flujo completo con broker real (2).
