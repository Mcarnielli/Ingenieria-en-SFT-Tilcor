"""Ingesta MQTT -> PostgreSQL con motor de alertas.

Topic esperado:  gallinero/<galpon>/sensores/<tipo>/<n>
Payload JSON:    {"sensor_id": 1, "valor": 25.6, "unidad": "C"}

Variables de entorno: MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS, MQTT_TLS=1, DATABASE_URL
"""
import json, logging, os, re
import paho.mqtt.client as mqtt
import psycopg
from umbrales import evaluar, RANGOS_FISICOS

log = logging.getLogger('tilcor.iot')
TOPIC_RE = re.compile(r'^gallinero/(\d+)/sensores/([a-z_]+)/(\d+)$')
TOPIC_SUB = 'gallinero/+/sensores/+/+'


class Ingesta:
    def __init__(self, dsn: str):
        self.conn = psycopg.connect(dsn, autocommit=True)
        self.estado_previo = {}          # sensor_id -> último estado (para no repetir alertas)
        self.descartadas = 0

    def procesar(self, topic: str, payload: bytes) -> str | None:
        """Valida, guarda y evalúa una lectura. Devuelve el estado o None si se descartó."""
        m = TOPIC_RE.match(topic)
        if not m:
            return self._descartar(f'topic inválido: {topic}')
        galpon, tipo, numero = int(m[1]), m[2], int(m[3])
        if tipo not in RANGOS_FISICOS:
            return self._descartar(f'tipo desconocido: {tipo}')
        try:
            d = json.loads(payload)
            valor = float(d['valor'])
        except (ValueError, KeyError, TypeError):
            return self._descartar(f'payload inválido en {topic}')
        lo, hi = RANGOS_FISICOS[tipo]
        if not (lo <= valor <= hi) or valor != valor:
            return self._descartar(f'valor fuera de rango físico ({valor}) en {topic}')

        row = self.conn.execute(
            'SELECT id FROM sensores WHERE galpon=%s AND tipo=%s AND numero=%s',
            (galpon, tipo, numero)).fetchone()
        if not row:
            return self._descartar(f'sensor no registrado: {topic}')
        sid = row[0]

        estado = evaluar(tipo, valor)
        self.conn.execute('INSERT INTO lecturas (sensor_id, valor, estado) VALUES (%s,%s,%s)',
                          (sid, valor, estado))
        previo = self.estado_previo.get(sid, 'ok')
        if estado != 'ok' and estado != previo:      # alerta solo al cambiar de estado
            msg = f'{tipo} {numero} (galpón {galpon}): {valor} — nivel {estado}'
            self.conn.execute(
                'INSERT INTO alertas_iot (sensor_id, severidad, valor, mensaje) VALUES (%s,%s,%s,%s)',
                (sid, estado, valor, msg))
            log.warning('ALERTA %s', msg)
        self.estado_previo[sid] = estado
        return estado

    def _descartar(self, motivo):
        self.descartadas += 1
        log.error('Lectura descartada: %s', motivo)
        return None


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    ing = Ingesta(os.environ['DATABASE_URL'])
    cli = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if os.getenv('MQTT_USER'):
        cli.username_pw_set(os.environ['MQTT_USER'], os.getenv('MQTT_PASS', ''))
    if os.getenv('MQTT_TLS') == '1':
        cli.tls_set()
    cli.on_connect = lambda c, u, f, rc, p=None: (log.info('Conectado al broker (rc=%s)', rc), c.subscribe(TOPIC_SUB, qos=1))
    cli.on_message = lambda c, u, msg: ing.procesar(msg.topic, msg.payload)
    cli.connect(os.getenv('MQTT_HOST', 'localhost'), int(os.getenv('MQTT_PORT', '1883')), keepalive=60)
    cli.loop_forever(retry_first_connection=True)


if __name__ == '__main__':
    main()
