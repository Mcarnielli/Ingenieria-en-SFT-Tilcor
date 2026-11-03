"""Umbrales de alerta por variable (Tesis, cap. 10.4)."""

# tipo: (min_ok, max_ok, crit_bajo, crit_alto)
UMBRALES = {
    'temperatura':  (15, 30, 13.5, 33),
    'humedad':      (45, 75, 40, 82),
    'calidad_aire': (None, 3000, None, 3300),
    'temp_agua':    (10, 30, 9, 33),
    'flujo_agua':   (5, 200, None, None),   # el cero sostenido >2 h se evalúa aparte
}

RANGOS_FISICOS = {   # fuera de estos valores la lectura se descarta como falla del sensor
    'temperatura': (-20, 80), 'humedad': (0, 100), 'calidad_aire': (0, 10000),
    'temp_agua': (-5, 80), 'flujo_agua': (0, 5000),
}


def evaluar(tipo: str, valor: float) -> str:
    """Devuelve 'ok', 'warning' o 'critico'."""
    mn, mx, cb, ca = UMBRALES[tipo]
    if ca is not None and valor > ca:
        return 'critico'
    if cb is not None and valor < cb:
        return 'critico'
    if mx is not None and valor > mx:
        return 'warning'
    if mn is not None and valor < mn:
        return 'warning'
    return 'ok'
