"""Simulador de sensores del galpón: publica lecturas MQTT con el formato real.
Uso:  python simulador.py --host localhost --intervalo 5 [--anomalia humedad]
Sirve para probar todo el flujo sin hardware y como plan B en la defensa."""
import argparse, json, os, random, time
import paho.mqtt.client as mqtt

SENSORES = [  # (tipo, n, id, base, ruido, unidad)
    ('temperatura', 1, 1, 26.0, 0.6, 'C'), ('temperatura', 2, 2, 27.0, 0.6, 'C'),
    ('humedad', 1, 3, 62.0, 2.0, '%'), ('humedad', 2, 4, 64.0, 2.0, '%'),
    ('calidad_aire', 1, 5, 800.0, 60.0, 'ppm'), ('flujo_agua', 1, 6, 55.0, 4.0, 'L'),
    ('temp_agua', 1, 7, 24.0, 0.5, 'C'),
]
ANOMALIAS = {'humedad': 38.0, 'temperatura': 34.0, 'calidad_aire': 3400.0}


def lectura(s, anomalia=None):
    tipo, n, sid, base, ruido, u = s
    v = ANOMALIAS[tipo] if anomalia == tipo else base + random.uniform(-ruido, ruido)
    return f'gallinero/1/sensores/{tipo}/{n}', json.dumps({'sensor_id': sid, 'valor': round(v, 1), 'unidad': u})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='localhost'); ap.add_argument('--port', type=int, default=1883)
    ap.add_argument('--intervalo', type=float, default=5); ap.add_argument('--anomalia', choices=ANOMALIAS)
    ap.add_argument('--ciclos', type=int, default=0, help='0 = infinito')
    a = ap.parse_args()
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if os.getenv('MQTT_USER'): c.username_pw_set(os.environ['MQTT_USER'], os.getenv('MQTT_PASS', ''))
    c.connect(a.host, a.port); c.loop_start()
    i = 0
    while a.ciclos == 0 or i < a.ciclos:
        for s in SENSORES:
            t, p = lectura(s, a.anomalia); c.publish(t, p, qos=1)
        i += 1; time.sleep(a.intervalo)
    c.loop_stop(); c.disconnect()


if __name__ == '__main__':
    main()
