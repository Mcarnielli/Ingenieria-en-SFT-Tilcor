"""Pruebas del módulo IoT. Requieren PostgreSQL (TEST_DATABASE_URL) y, para las de integración,
el broker embebido amqtt (pip install amqtt)."""
import asyncio, json, os, threading, time
import paho.mqtt.client as mqtt
import psycopg, pytest
from umbrales import evaluar
from ingest import Ingesta, TOPIC_SUB
import simulador

DSN = os.getenv('TEST_DATABASE_URL', 'host=/tmp port=5544 user=postgres dbname=tilcor_test')
SCHEMA = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')


@pytest.fixture()
def db():
    c = psycopg.connect(DSN, autocommit=True)
    c.execute('DROP TABLE IF EXISTS alertas_iot, lecturas, sensores CASCADE')
    c.execute(open(SCHEMA, encoding='utf-8').read())
    yield c
    c.close()


def contar(c, tabla, where='TRUE'):
    return c.execute(f'SELECT count(*) FROM {tabla} WHERE {where}').fetchone()[0]


# ---------- Unitarias: umbrales ----------
@pytest.mark.parametrize('tipo,valor,esperado', [
    ('temperatura', 25, 'ok'), ('temperatura', 30, 'ok'), ('temperatura', 31, 'warning'),
    ('temperatura', 33.5, 'critico'), ('temperatura', 14, 'warning'), ('temperatura', 13, 'critico'),
    ('humedad', 60, 'ok'), ('humedad', 44, 'warning'), ('humedad', 39, 'critico'), ('humedad', 83, 'critico'),
    ('calidad_aire', 2000, 'ok'), ('calidad_aire', 3100, 'warning'), ('calidad_aire', 3400, 'critico'),
    ('temp_agua', 25, 'ok'), ('temp_agua', 34, 'critico'), ('flujo_agua', 3, 'warning'), ('flujo_agua', 50, 'ok'),
])
def test_umbrales(tipo, valor, esperado):
    assert evaluar(tipo, valor) == esperado


# ---------- Integración: ingesta -> base de datos ----------
def test_lectura_valida_se_guarda(db):
    ing = Ingesta(DSN)
    est = ing.procesar('gallinero/1/sensores/temperatura/1', json.dumps({'sensor_id': 1, 'valor': 25.6, 'unidad': 'C'}).encode())
    assert est == 'ok' and contar(db, 'lecturas') == 1 and contar(db, 'alertas_iot') == 0


def test_alerta_critica_una_sola_vez_por_episodio(db):
    ing = Ingesta(DSN)
    t = 'gallinero/1/sensores/humedad/1'
    for v in (38, 37, 36):
        ing.procesar(t, json.dumps({'valor': v}).encode())
    assert contar(db, 'lecturas') == 3
    assert contar(db, 'alertas_iot', "severidad='critico'") == 1          # no se repite
    ing.procesar(t, json.dumps({'valor': 60}).encode())                    # se normaliza
    ing.procesar(t, json.dumps({'valor': 38}).encode())                    # nuevo episodio
    assert contar(db, 'alertas_iot') == 2


@pytest.mark.parametrize('topic,payload', [
    ('gallinero/1/sensores/temperatura/1', b'no es json'),
    ('gallinero/1/sensores/temperatura/1', b'{"valor": "abc"}'),
    ('gallinero/1/sensores/temperatura/1', b'{"otro": 1}'),
    ('gallinero/1/sensores/temperatura/1', b'{"valor": 500}'),             # fuera de rango físico
    ('gallinero/1/sensores/humedad/1', b'{"valor": -5}'),
    ('gallinero/1/sensores/radiacion/1', b'{"valor": 1}'),                 # tipo desconocido
    ('gallinero/9/sensores/temperatura/1', b'{"valor": 20}'),              # sensor no registrado
    ('otro/topic', b'{"valor": 1}'),
])
def test_lecturas_invalidas_se_descartan(db, topic, payload):
    ing = Ingesta(DSN)
    assert ing.procesar(topic, payload) is None
    assert contar(db, 'lecturas') == 0 and ing.descartadas == 1


# ---------- Integración extremo a extremo: simulador -> broker MQTT -> ingesta -> base ----------
@pytest.fixture(scope='module')
def broker():
    from amqtt.broker import Broker
    cfg = {'listeners': {'default': {'type': 'tcp', 'bind': '127.0.0.1:18830'}},
           'plugins': {'amqtt.plugins.authentication.AnonymousAuthPlugin': {'allow_anonymous': True}}}
    loop = asyncio.new_event_loop(); b = Broker(cfg, loop=loop) if 'loop' in Broker.__init__.__code__.co_varnames else Broker(cfg)
    ready = threading.Event()

    def run():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(b.start()); ready.set(); loop.run_forever()
    th = threading.Thread(target=run, daemon=True); th.start(); ready.wait(10); time.sleep(0.5)
    yield 18830
    loop.call_soon_threadsafe(loop.stop)


def _suscribir(ing, puerto):
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.on_connect = lambda cl, u, f, rc, p=None: cl.subscribe(TOPIC_SUB, qos=1)
    c.on_message = lambda cl, u, m: ing.procesar(m.topic, m.payload)
    c.connect('127.0.0.1', puerto); c.loop_start(); time.sleep(0.5)
    return c


def test_flujo_completo_mqtt(db, broker):
    ing = Ingesta(DSN); sub = _suscribir(ing, broker)
    pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2); pub.connect('127.0.0.1', broker); pub.loop_start()
    for s in simulador.SENSORES:
        t, p = simulador.lectura(s); pub.publish(t, p, qos=1)
    time.sleep(2)
    assert contar(db, 'lecturas') == 7                                      # 7 sensores del galpón
    assert contar(db, 'alertas_iot') == 0
    t, p = simulador.lectura(simulador.SENSORES[2], anomalia='humedad'); pub.publish(t, p, qos=1)
    time.sleep(1.5)
    assert contar(db, 'alertas_iot', "severidad='critico'") == 1
    pub.loop_stop(); sub.loop_stop()


def test_latencia_lectura_a_base(db, broker):
    ing = Ingesta(DSN); sub = _suscribir(ing, broker)
    pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2); pub.connect('127.0.0.1', broker); pub.loop_start()
    t0 = time.time()
    pub.publish('gallinero/1/sensores/temperatura/1', json.dumps({'valor': 26.0}), qos=1)
    while contar(db, 'lecturas') == 0 and time.time() - t0 < 5:
        time.sleep(0.01)
    lat = time.time() - t0
    print(f'LATENCIA_MS={lat*1000:.0f}')
    assert contar(db, 'lecturas') == 1 and lat < 2.0
    pub.loop_stop(); sub.loop_stop()
