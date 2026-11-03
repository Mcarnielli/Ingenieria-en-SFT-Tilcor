# -*- coding: utf-8 -*-
import json, re, sys
sys.path.insert(0, '.')
from asm import *

SP = '/tmp/claude-0/-home-claude/b7d7bd27-8074-546c-95cb-7723bd4ca75c/scratchpad/'
SH = SP + 'shots_doc/'; SX = SP + 'shots_extra_j/'; UM = SP + 'uml/'
REPO = '/home/claude/ingenieria-en-sft-tilcor/'
CH = []   # (chunk, parte)

def finish(ch, parte):
    ch.save(); CH.append((ch.name, parte, ch.heads))

# ------------------------------------------------------------------ requerimientos
REQ = json.load(open(SP + 'req.json', encoding='utf8'))
t = etree.parse(UNI + 'x_Informe_Parte1_Final/word/document.xml'); body = t.getroot().find('w:body', NS)
for e in list(body)[182:204]:
    tx = ' '.join(''.join(e.itertext()).split())
    m = re.match(r'^(RF\d\d): (.*)$', tx)
    if m: REQ[m.group(1)] = ['(Relevamiento)', m.group(2), '—']

def req_table(ids):
    rows = [['ID', 'Requerimiento', 'Descripción', 'Prioridad']]
    for i in ids:
        v = REQ[i]
        if i.startswith('RNF-'): rows.append([i, v[0], v[1] + '. Criterio: ' + v[2], '—'])
        else: rows.append([i, v[0], v[1], v[2]])
    return TABLE(rows, [1100, 1800, 5200, 1000], sz=17)

# ------------------------------------------------------------------ módulos y casos de uso
FICHA = {'CU01': (131, 134), 'CU02': (134, 138), 'CU03': (138, 141), 'CU04': (141, 145), 'CU05': (145, 148), 'CU06': (148, 152), 'CU07': (152, 155), 'CU08': (155, 159),
         'CU09': (159, 162), 'CU10': (162, 166), 'CU11': (166, 169), 'CU12': (169, 173), 'CU13': (173, 176), 'CU14': (176, 180), 'CU15': (180, 183), 'CU16': (183, 187),
         'CU17': (187, 190), 'CU18': (190, 194), 'CU19-22': (194, 197), 'CU23': (197, 201), 'CU24': (201, 205)}
TIT = {'CU01': 'Registrar producción diaria de huevos', 'CU02': 'Registrar mortalidad diaria de aves', 'CU03': 'Consultar estado actual de sensores IoT',
       'CU04': 'Ver historial de producción por fecha', 'CU05': 'Configurar umbrales de alerta por sensor', 'CU06': 'Recibir alerta Warning', 'CU07': 'Recibir alerta Crítico',
       'CU08': 'Consultar dashboard IoT en tiempo real', 'CU09': 'Ver curva de postura real vs tabla genética', 'CU10': 'Editar progreso del plan de implementación',
       'CU11': 'Aprobar pedido que supera límite de crédito', 'CU12': 'Ver KPIs generales en dashboard principal', 'CU13': 'Recibir reporte diario automatizado',
       'CU14': 'Ver viabilidad acumulada de los lotes', 'CU15': 'Iniciar sesión con rol diferenciado', 'CU16': 'Recibir informe semanal de mortalidad',
       'CU17': 'Consultar historial sanitario del lote', 'CU18': 'Ver curva de mortalidad histórica', 'CU19-22': 'Flujo automático IoT (CU19 a CU22)',
       'CU23': 'Actualizar datos comerciales (Don Gestión)', 'CU24': 'Emitir factura electrónica ARCA/AFIP'}
MOD = [('Producción avícola', ['CU01', 'CU02', 'CU04', 'CU09']),
       ('Monitoreo IoT y alertas', ['CU03', 'CU05', 'CU06', 'CU07', 'CU08', 'CU19-22']),
       ('Sanidad y mortalidad', ['CU14', 'CU16', 'CU17', 'CU18']),
       ('Dashboard, reportes y plan de implementación', ['CU10', 'CU12', 'CU13']),
       ('Usuarios y roles', ['CU15']),
       ('Gestión comercial (Don Gestión)', ['CU11', 'CU23', 'CU24'])]
REQCU = {'CU01': ['RF-PROD-01', 'RF-PROD-02', 'RF-PROD-03', 'RF-PROD-04', 'RF-PROD-08', 'RF06', 'RF07'], 'CU02': ['RF-PROD-05', 'RF08', 'RF10'], 'CU04': ['RF-PROD-08'],
         'CU09': ['RF-PROD-03', 'RF09'], 'CU03': ['RF-IOT-03', 'RF-IOT-04', 'RF14', 'RNF-02', 'RNF-04'], 'CU05': ['RF-IOT-07'], 'CU06': ['RF-IOT-05', 'RF-IOT-06', 'RF-IOT-09', 'RF12', 'RNF-10'],
         'CU07': ['RF-IOT-05', 'RF-IOT-06', 'RF-IOT-09', 'RF12', 'RNF-10'], 'CU08': ['RF-IOT-03', 'RF-IOT-04', 'RF-IOT-08', 'RF-IOT-09', 'RF13', 'RF14'],
         'CU19-22': ['RF-IOT-01', 'RF-IOT-02', 'RF-IOT-05', 'RF-IOT-06', 'RF-IOT-09', 'RF11', 'RF12', 'RNF-01', 'RNF-10'], 'CU14': ['RF-PROD-06', 'RF08'], 'CU16': ['RF-PROD-07', 'RF16'],
         'CU17': ['RF-PROD-05'], 'CU18': ['RF-PROD-05'], 'CU10': [], 'CU12': ['RF-IOT-04', 'RF-PROD-08', 'RNF-03'], 'CU13': ['RF15', 'RF17'], 'CU15': ['RNF-05', 'RNF-09'],
         'CU11': ['RF01', 'RF05'], 'CU23': ['RF02', 'RF05'], 'CU24': ['RF04']}
PROTO = {'CU01': (['03_produccion', '03b_registro_guardado', '04_alerta_produccion'], ['Formulario de registro', 'Registro guardado', 'Alerta por postura baja'], SH),
         'CU02': (['03_produccion'], ['Campo de aves muertas'], SH), 'CU04': (['03_produccion'], ['Historial de 7 días'], SH), 'CU09': (['02b_inicio_indicadores'], ['Curva real vs tabla'], SH),
         'CU03': (['05_iot'], ['Panel de sensores'], SH), 'CU05': (['wf_cu05'], ['Boceto — no implementado'], SX), 'CU06': (['02_inicio', '05_iot'], ['Banner de alerta', 'Estado de sensores'], SH),
         'CU07': (['02_inicio', '05_iot'], ['Banner de alerta', 'Estado de sensores'], SH), 'CU08': (['05_iot'], ['Dashboard IoT'], SH), 'CU19-22': None,
         'CU14': (['02b_inicio_indicadores', '06_sanidad'], ['Indicadores', 'Sanidad'], SH), 'CU16': (['wf_cu16'], ['Boceto — no implementado'], SX),
         'CU17': (['06_sanidad', '06b_sanidad_protocolo'], ['Sanidad', 'Protocolo de alertas'], SH), 'CU18': (['06_sanidad'], ['Curva de mortalidad'], SH),
         'CU10': (['cu10_plan'], ['Edición del plan'], SX), 'CU12': (['02_inicio', '02b_inicio_indicadores', '02c_inicio_resumen'], ['Inicio', 'Indicadores', 'Resumen'], SH),
         'CU13': (['wf_cu13'], ['Boceto — no implementado'], SX), 'CU15': (['01_login', '01b_login_error', '08_empleado_menu', '08b_empleado_sin_ventas'], ['Login', 'Error de login', 'Perfil empleado', 'Empleado sin Ventas'], SH),
         'CU11': (['wf_cu11'], ['Boceto — no implementado'], SX), 'CU23': (['wf_cu23'], ['Boceto — no implementado'], SX), 'CU24': None}

# ------------------------------------------------------------------ código real
def get_func(name, maxlines=45):
    s = open(SP + 'app_local/index.html', encoding='utf8').read()
    m = re.search(r'(async )?function %s\(' % name, s)
    i = m.start(); j = s.index('{', i); d = 0; k = j
    while True:
        if s[k] == '{': d += 1
        elif s[k] == '}':
            d -= 1
            if d == 0: break
        k += 1
    txt = s[i:k + 1].split('\n'); txt = [l.rstrip() for l in txt]
    if len(txt) > maxlines: txt = txt[:maxlines] + ['  // ... (se omite el resto de la función)']
    return '\n'.join(txt)

def readf(p): return open(REPO + p, encoding='utf8').read().rstrip('\n')

# ================================================================== PARTE 1
c = Chunk('p1', 'c00_resumen'); c.h(1, 'Resumen ejecutivo'); c.rng(14, 19)
c.rep('El presente informe corresponde a la Parte I del Trabajo Final de Tesis de la carrera Analista en', 'El presente documento corresponde al Trabajo Final de Tesis de la carrera Analista en'); finish(c, 1)

c = Chunk('p1', 'c01_intro'); c.h(1, '1 Introducción')
c.h(2, '1.1 Carta de presentación (opcional)')
c.add(P('Córdoba, noviembre de 2026', align='right', after=200))
c.add(P('A la Dirección de **TILCOR S.A.S.**', after=40)); c.add(P('Colonia Tirolesa, Córdoba', after=200))
c.add(P('De nuestra mayor consideración:', after=120))
c.add(P('Nos dirigimos a ustedes, estudiantes de la carrera de Analista en Sistemas de Información del Colegio Universitario IES (Córdoba), para presentarles el trabajo de relevamiento, diseño y desarrollo del **Sistema de Gestión Integral Avícola** que realizamos tomando como caso de estudio a la empresa.', align='both', after=120))
c.add(P('El documento que sigue recoge lo observado en las visitas a los galpones y en las conversaciones con el personal, el diagnóstico de la situación actual, la propuesta de sistema y su especificación, junto con una demostración funcional y un módulo de ingesta de datos de sensores ya probado con datos simulados.', align='both', after=120))
c.add(P('Agradecemos la predisposición del personal de TILCOR para mostrarnos los procesos, las planillas y los sistemas que utilizan (Gallinero y Don Gestión), y quedamos a disposición para revisar este material y ajustarlo a las necesidades reales de la empresa.', align='both', after=220))
c.add(P('Atentamente,', after=500))
c.add(P('______________________________            ______________________________', after=20))
c.add(P('Carnielli, Matías                                                     Bacari, Fernando', after=200))
c.h(2, '1.2 Pedido del usuario'); c.rng(40, 58, {'2': '1.2'})
c.h(2, '1.3 Descripción general del proyecto'); c.rng(20, 39, {'1': '1.3'})
finish(c, 1)

c = Chunk('p1', 'c02_relev'); c.h(1, '2 Relevamiento')
c.h(2, '2.1 Contextual y del negocio')
c.rng(59, 62, {'3.1': '2.1.1'}); c.rng(62, 65, {'3.2': '2.1.2'})
c.rng(137, 162, {'7.1': '2.1.3', '7.2': '2.1.4', '7.3': '2.1.5', '7.4': '2.1.6'})
c.h(2, '2.2 Estructura de la organización')
c.rng(65, 72, {'3.3': '2.2.1'}); c.rng(72, 75, {'3.4': '2.2.2'}); c.rng(75, 78, {'3.5': '2.2.3'})
c.rng(79, 92, {'4.1': '2.2.4', '4.2': '2.2.5', '4.3': '2.2.6'})
finish(c, 1)

c = Chunk('p1', 'c03_proc'); c.h(2, '2.3 Procesos de negocio')
c.add(P('Esta sección describe los cuatro procesos relevados. Para cada uno se presenta la descripción funcional y, a continuación, el cursograma de la situación actual. Los cursogramas de la situación propuesta se encuentran en la sección 3.1.', align='both'))
c.sub('Descripción general de los procesos'); c.rng(94, 95); finish(c, 1)
c = Chunk('cur', 'c03b_simb'); c.sub('Simbología utilizada en los cursogramas', 24); c.rng(19, 24); finish(c, 1)

PROC = [('2.3.1', 'Proceso 1: Producción avícola diaria', (96, 99), (28, 33)),
        ('2.3.2', 'Proceso 2: Gestión comercial y facturación', (100, 103), (43, 48)),
        ('2.3.3', 'Proceso 3: Monitoreo ambiental IoT', (104, 107), (58, 63)),
        ('2.3.4', 'Proceso 4: Control sanitario', (108, 110), (73, 78))]
for i, (num, tit, (a, b), (ca, cb)) in enumerate(PROC):
    c = Chunk('p1', 'c04_%d' % (i + 1)); c.h(3, '%s %s' % (num, tit)); c.rng(a, b); finish(c, 1)
    c = Chunk('cur', 'c04b_%d' % (i + 1)); c.h(4, '%s.1 Cursograma de la situación actual' % num); c.rng(ca, cb); finish(c, 1)

c = Chunk('p1', 'c05_tec'); c.h(2, '2.4 Tecnología'); c.h(3, '2.4.1 Tecnología existente en la empresa')
c.rng(111, 136, {'6.1': '2.4.1.1', '6.2': '2.4.1.2', '6.3': '2.4.1.3'}); finish(c, 1)

c = Chunk('p1', 'c05b_mercado'); c.h(3, '2.4.2 Tecnología existente en el mercado (aplicable)')
c.add(P('Se relevaron soluciones comerciales de gestión avícola que resuelven problemas similares a los de TILCOR, además de las dos herramientas que la empresa ya utiliza. El objetivo es ubicar la propuesta frente a lo que ya existe y justificar el desarrollo a medida.', align='both'))
c.add(TABLE([['Solución', 'Origen', 'Qué ofrece (según el fabricante)', 'Relación con TILCOR'],
             ['BigFarmNet', 'Big Dutchman', 'Software integral de gestión avícola: clima del galpón, datos de producción, resúmenes en gráficos y listas, registro de alarmas e historial. Acceso desde la computadora del galpón, una PC o un dispositivo móvil, y continúa operando si cae la red.', 'Solución de mercado de referencia. Está pensada para integrarse con equipamiento del mismo fabricante.'],
             ['Amino', 'MTech Systems', 'Software de gestión de gallinas ponedoras: seguimiento unificado de costos y producción (de recría a postura), métricas como costo por huevo y conversión alimenticia, tableros de tendencias, predicciones asistidas por IA y registros de salud con datos de sensores IoT.', 'Solución de mercado de referencia. Enfocada en costos y optimización de la producción.'],
             ['Gallinero', 'Plataforma existente en TILCOR', 'Plataforma donde hoy se visualizan las variables ambientales de los sensores instalados (capturas relevadas en 2.4.1.3).', 'Se mantiene como fuente de datos; el nuevo sistema consume el flujo de sensores y agrega alertas y correlación con la producción.'],
             ['Don Gestión', 'Sistema existente en TILCOR', 'Sistema de gestión comercial de la empresa: ventas, clientes, cuentas y facturación.', 'No se reemplaza: se integra por iframe (CU23) y se aprovecha para facturación (CU24).']],
            [1500, 1500, 3700, 2400], sz=17))
c.sub('Análisis y alcance de este relevamiento')
for tx in ['Las soluciones de mercado cubren funciones similares a algunas de las que se proponen (monitoreo, registro de producción, alarmas), pero son productos cerrados de fabricantes de equipamiento o plataformas de gestión de grandes operaciones.',
           'El sistema propuesto se diferencia porque está **hecho a medida del flujo de TILCOR**: carga de producción de 5 campos desde el celular, comparación contra la tabla genética Lohmann, alertas de mortalidad con umbrales propios, integración con Gallinero y Don Gestión y facturación electrónica ARCA/AFIP.',
           'En esta instancia **no se evaluaron costos de licencia ni disponibilidad comercial en Argentina** de las soluciones citadas; queda como trabajo futuro consultar a distribuidores locales y cotizar para completar la comparación.']:
    c.add(BUL(tx))
c.sub('Fuentes consultadas')
c.add(P('Big Dutchman. BigFarmNet — controles y software ambiental. https://www.bigdutchmanusa.com/egg-production/products/environmental/controls-and-software/bigfarmnet/', sz=17, after=40))
c.add(P('MTech Systems. 6 Direct Benefits of Poultry Layer Management Software (Amino). https://test.mtech-systems.com/?p=20248', sz=17, after=40))
finish(c, 1)

c = Chunk('p1', 'c06_prop'); c.h(1, '3 Propuesta'); c.h(2, '3.1 Diagnóstico y propuesta')
c.rng(163, 181, {'8': '3.1'}); finish(c, 1)
c = Chunk('cur', 'c06b_cur')
c.h(3, '3.1.5 Situación propuesta de los procesos')
c.add(P('Cursogramas de cada proceso con el sistema nuevo, a comparar con los cursogramas de la situación actual de la sección 2.3.', align='both'))
for i, (num, tit, _, _) in enumerate(PROC):
    pa = [(34, 39), (49, 54), (64, 69), (79, 84)][i]
    c.h(4, '3.1.5.%d %s — situación propuesta' % (i + 1, tit)); c.rng(*pa)
c.h(3, '3.1.6 Diagnóstico de la propuesta'); c.rng(85, 114, {'6': '3.1.6'}); finish(c, 1)
c = Chunk('p1', 'c07_gral'); c.h(2, '3.2 Propuesta general')
c.rng(209, 224, {'10': '3.2'})
c.h(3, '3.2.6 Requerimientos preliminares del relevamiento'); c.rng(182, 208, {'9': '3.2.6'}); finish(c, 1)

# ================================================================== PARTE 2
c = Chunk('p3', 'c10_obj'); c.h(1, '4 Objetivos, límites y alcance'); c.rng(15, 69, {'1': '4.1', '2': '4.2', '3': '4.3'}); finish(c, 2)
c = Chunk('p3', 'c11_req'); c.h(1, '5 Especificación de requerimientos'); c.rng(70, 79, {'4': '5'}); finish(c, 2)
c = Chunk('p3', 'c12_amb'); c.h(1, '6 Análisis y diseño del producto'); c.h(2, '6.1 Modelado ambiental')
c.rng(80, 115, {'5': '6.1', '6': '6.1.5', '7': '6.1.6'}, titles={'6.1.6': 'Articulación con el relevamiento y la propuesta (Parte 1)'})
for o, n in [('Sección Parte II', 'Sección de la especificación (Parte 2)'), ('Sección Parte I', 'Sección del relevamiento (Parte 1)'),
             ('Cap. 1 — Introducción y objetivos', '1.3 Descripción general del proyecto'), ('Cap. 1 — Objetivo del sistema', '4.1 Objetivo del sistema'),
             ('Cap. 3 — Relevamiento (límites)', '2.1 y 2.2 Relevamiento contextual y estructural'), ('Cap. 2 — Límite del sistema', '4.2 Límite del sistema'),
             ('Cap. 4 — Requerimientos (general)', '3.2.6 Requerimientos preliminares'), ('Cap. 3 — Alcance · Cap. 4 — Especificaciones', '4.3 Alcance · 5 Especificación de requerimientos'),
             ('Cap. 5 — Propuesta del sistema', '3.2 Propuesta general'), ('Cap. 5 — Diagrama de caso de uso', '6.1 Modelado ambiental y 6.3 Casos de uso'),
             ('Cap. 6 — Plan de implementación', '3.2.5 Plan de implementación'), ('Todos los capítulos', 'Capítulos 4 a 9'),
             ('Este documento (Informe Parte II) debe leerse en conjunto con el Informe Parte I', 'La Parte 2 de este documento debe leerse en conjunto con la Parte 1')]: c.rep(o, n)
finish(c, 2)

c = Chunk('p4', 'c13_paq'); c.h(2, '6.2 Modelado de paquetes')
c.add(P('El sistema se organiza en cuatro capas y seis paquetes de aplicación, uno por módulo funcional. Cada paquete agrupa los casos de uso que implementa (sección 6.3) y las tablas que usa. La arquitectura y la base de datos de referencia se detallan a continuación.', align='both'))
c.img(UM + 'paquetes.png', 15.8, 'Figura 6.2-1. Diagrama de paquetes del sistema y casos de uso que contiene cada paquete.')
c.add(TABLE([['Paquete', 'Responsabilidad', 'Casos de uso', 'Tablas principales'],
             ['usuarios', 'Autenticación JWT, roles y auditoría de acceso', 'CU15', 'usuarios, auditoria'],
             ['produccion', 'Registro diario, cálculo de postura y comparación con tabla genética', 'CU01, CU02, CU04, CU09', 'lotes, registros_produccion, tabla_genetica, alertas_productivas'],
             ['sanidad', 'Mortalidad, viabilidad e informes al veterinario', 'CU14, CU16, CU17, CU18', 'lotes, registros_produccion'],
             ['iot', 'Ingesta MQTT, evaluación de umbrales, alertas y dashboard en tiempo real', 'CU03, CU05, CU06, CU07, CU08, CU19–22', 'sensores, registros_sensor, alertas_iot'],
             ['reportes', 'Dashboard principal, reportes programados y plan de implementación', 'CU10, CU12, CU13', 'consultas sobre las tablas anteriores'],
             ['comercial', 'Clientes, pedidos, cuenta corriente y facturación', 'CU11, CU23, CU24', 'clientes, pedidos, cuenta_corriente, facturas']],
            [1300, 3300, 2200, 2400], sz=17))
c.rng(14, 29, {'6.1': '6.2.1', '6.2': '6.2.2', '6.3': '6.2.3'})
c.h(3, '6.2.4 Modelo de datos'); c.rng(30, 52, {'7': '6.2.4'}); finish(c, 2)

# ---- 6.3 casos de uso
c = Chunk('p3', 'c14_cu'); c.h(2, '6.3 Modelado de los casos de uso')
c.add(P('Los 24 casos de uso del sistema se agrupan en seis módulos. Para cada caso de uso se presentan sus requerimientos específicos, los prototipos de interfaz, la ficha de especificación y los diagramas de vista estática (clases) y dinámica (secuencia). Los casos CU19 a CU22 forman un único flujo automático y se modelan en conjunto.', align='both'))
rows = [['Módulo', 'Casos de uso', 'Sección']]
for k, (mn, cus) in enumerate(MOD): rows.append(['%d. %s' % (k + 1, mn), ', '.join(cus), '6.3.%d / 7.%d' % (k + 1, k + 1)])
c.add(TABLE(rows, [3600, 3800, 1800], sz=18))
c.sub('Resumen de relaciones entre casos de uso'); c.rng(206, 207); finish(c, 2)

for k, (mn, cus) in enumerate(MOD):
    c = Chunk('p3', 'c15_m%d' % (k + 1)); c.h(3, '6.3.%d Módulo %d — %s' % (k + 1, k + 1, mn))
    for j, cu in enumerate(cus):
        num = '6.3.%d.%d' % (k + 1, j + 1)
        c.h(4, '%s %s — %s' % (num, cu, TIT[cu]))
        c.sub('Requerimientos específicos', 21)
        if REQCU[cu]: c.add(req_table(REQCU[cu]))
        else: c.add(P('Sin requerimiento funcional numerado: surge de la necesidad del equipo de seguimiento del avance del proyecto (ver plan de implementación, sección 3.2.5).', sz=19))
        c.sub('Prototipos de interfaz', 21)
        pr = PROTO[cu]
        if pr is None: c.add(P('No aplica: es un flujo automático sin pantalla propia (sensores, servidor y servicios externos).' if cu == 'CU19-22' else 'No aplica: la emisión se realiza en Don Gestión y ARCA/AFIP, sin pantalla en esta aplicación.', sz=19, italic=True))
        else:
            files, caps, base = pr; ext = '.jpg'
            n = len(files); wcm = {1: 5.0, 2: 5.0, 3: 4.4, 4: 3.6}[n]
            c.imgs_row([base + f + ext for f in files], wcm, caps)
        c.sub('Ficha de caso de uso', 21); c.rng(FICHA[cu][0] + 1, FICHA[cu][1])
        c.sub('Vista estática (diagrama de clases)', 21); c.img(UM + '%s_est.png' % cu, 15.2, 'Diagrama de clases — %s' % cu)
        c.sub('Vista dinámica (diagrama de secuencia)', 21); c.img(UM + '%s_din.png' % cu, 15.2, 'Diagrama de secuencia — %s' % cu)
    finish(c, 2)

# ---- 7 implementación
IMPL = {
 'CU01': ('Demo (frontend/index.html): sección Producción con cálculo de % de postura y alerta de desvío.', 'Implementado en la demo', ['calcPost', 'guardarReg']),
 'CU02': ('Demo: campo de aves muertas y verificación de mortalidad al guardar.', 'Implementado en la demo', ['checkMort']),
 'CU04': ('Demo: historial de los últimos registros con semáforo de desvío.', 'Implementado en la demo', ['renderProdLog']),
 'CU09': ('Demo: gráfica de postura real vs tabla genética en el inicio.', 'Implementado en la demo (datos de ejemplo)', []),
 'CU03': ('Demo: panel IoT con estado por sensor. Los valores son simulados en el navegador.', 'Demo con datos simulados', ['renderSensors', 'sNivel']),
 'CU05': ('Los umbrales vigentes están definidos en backend/iot/umbrales.py (valores de la sección 7.2.7.4). La pantalla de configuración no está construida.', 'Umbrales implementados; pantalla diseñada', []),
 'CU06': ('backend/iot/umbrales.py (evaluar) y backend/iot/ingest.py: clasifican cada lectura como normal, Warning o Crítico y guardan la alerta. El envío de push/WhatsApp está diseñado.', 'Evaluación implementada y probada; notificación diseñada', []),
 'CU07': ('Misma lógica que CU06 para el nivel Crítico (backend/iot).', 'Evaluación implementada y probada; notificación diseñada', []),
 'CU08': ('Demo: dashboard IoT con semáforo y gráficas (datos simulados). El canal WebSocket de tiempo real está diseñado.', 'Demo con datos simulados', ['simSensors']),
 'CU19-22': ('backend/iot: ingest.py (suscripción MQTT, validación, persistencia, alertas), schema.sql y simulador.py; 29 pruebas automáticas aprobadas (cap. 8). Con sensores reales: pendiente.', 'Implementado y probado con simulador', []),
 'CU14': ('Demo: viabilidad acumulada en el inicio y en Sanidad.', 'Implementado en la demo (datos de ejemplo)', []),
 'CU16': ('Informe semanal por Celery y correo: diseñado, sin construir.', 'Diseñado', []),
 'CU17': ('Demo: sección Sanidad con KPIs y protocolo de alertas.', 'Implementado en la demo (datos de ejemplo)', []),
 'CU18': ('Demo: curva de mortalidad semanal con línea de referencia.', 'Implementado en la demo (datos de ejemplo)', []),
 'CU10': ('Demo: modal de edición del plan con sliders; el progreso se guarda en el navegador.', 'Implementado en la demo', ['guardarPlan']),
 'CU12': ('Demo: pantalla de inicio con KPIs, producción de 7 días, curva y viabilidad. El resumen comercial desde Don Gestión está diseñado.', 'Implementado en la demo (datos de ejemplo)', []),
 'CU13': ('Reporte diario PDF por Celery y correo: diseñado, sin construir.', 'Diseñado', []),
 'CU15': ('Demo: inicio de sesión con dos perfiles; el perfil Empleado no ve Ventas. Los usuarios están en el cliente. JWT en el backend: diseñado. Auditoría por triggers: implementada (backend/db/auditoria.sql).', 'Demo implementada; JWT diseñado; auditoría SQL implementada', ['doLogin', 'aplicarRol']),
 'CU11': ('Aprobación de pedidos sobre el límite de crédito: diseñada, sin construir.', 'Diseñado', []),
 'CU23': ('Demo: sección Ventas con iframe a Don Gestión, visible solo para el rol Administrador.', 'Implementado en la demo', ['setIframe']),
 'CU24': ('Facturación electrónica por Don Gestión y ARCA/AFIP (WSFE): diseñada. El código de referencia está en la sección 7.6.4.', 'Diseñado', []),
}
REALCODE = {'CU19-22': ['backend/iot/schema.sql', 'backend/iot/ingest.py', 'backend/iot/simulador.py'], 'CU06': ['backend/iot/umbrales.py'], 'CU15': ['backend/db/auditoria.sql']}
P4RNG = {1: [(71, 88, {'9.2': '7.1.%d.1', '9.3': '7.1.%d.2', '9.4': '7.1.%d.3', '9.5': '7.1.%d.4'})],
         2: [(89, 109, {'10.1': '7.2.%d.1', '10.2': '7.2.%d.2', '10.3': '7.2.%d.3', '10.4': '7.2.%d.4', '10.5': '7.2.%d.5'})],
         3: [], 4: [(123, 129, {'12.1': '7.4.%d.1', '12.2': '7.4.%d.2'})],
         5: [(130, 141, {'13.1': '7.5.%d.1', '13.2': '7.5.%d.2', '13.3': '7.5.%d.3'})],
         6: [(53, 66, {'8.1': '7.6.%d.1', '8.2': '7.6.%d.2'}), (110, 122, {'11.1': '7.6.%d.3', '11.2': '7.6.%d.4', '11.3': '7.6.%d.5'})]}

c = Chunk('p4', 'c20_impl'); c.h(1, '7 Implementación del software (desarrollo)')
c.add(P('Este capítulo documenta cómo se llevó cada caso de uso a código. Se distinguen tres estados, para que se vea con claridad qué está construido y qué está diseñado:', align='both'))
c.add(BUL('**Implementado y probado:** código real en el repositorio con pruebas automáticas (módulo IoT y auditoría SQL).'))
c.add(BUL('**Implementado en la demo:** funciona en la aplicación publicada (PWA), con datos de ejemplo guardados en el navegador, sin backend.'))
c.add(BUL('**Diseñado:** especificado con su ficha, diagramas y código de referencia, pendiente de construir en las fases 3 a 5 del plan.'))
rows = [['Módulo', 'Caso de uso', 'Estado']]
for k, (mn, cus) in enumerate(MOD):
    for cu in cus: rows.append(['%d. %s' % (k + 1, mn), '%s — %s' % (cu, TIT[cu]), IMPL[cu][1]])
fills = {}
for i, r in enumerate(rows[1:], 1):
    s = r[2]; fills[(i, 2)] = 'D5F5E3' if s.startswith('Implementado') else ('FADBD8' if s.startswith('Diseñado') else 'FEF9E7')
c.add(TABLE(rows, [2900, 4000, 2300], sz=16, fills=fills))
c.add(P('Repositorio: github.com/Mcarnielli/Ingenieria-en-SFT-Tilcor · Demo: tilcorvercel.vercel.app', sz=18, italic=True, color='555555'))
finish(c, 2)

for k, (mn, cus) in enumerate(MOD):
    c = Chunk('p4', 'c21_m%d' % (k + 1)); c.h(2, '7.%d Módulo %d — %s' % (k + 1, k + 1, mn))
    for j, cu in enumerate(cus):
        c.h(3, '7.%d.%d %s — %s' % (k + 1, j + 1, cu, TIT[cu]))
        what, state, funcs = IMPL[cu]
        c.add(P('**Estado:** %s' % state, sz=20, after=40)); c.add(P(what, sz=20, align='both'))
        for f in funcs:
            c.sub('frontend/index.html — función %s' % f, 19); c.add(CODE(get_func(f, 32)))
        for rp in REALCODE.get(cu, []):
            c.sub(rp, 19); c.add(CODE(readf(rp)))
    n = len(cus) + 1
    if P4RNG[k + 1]:
        c.h(3, '7.%d.%d Diseño y código de referencia (Tesis)' % (k + 1, n))
        for a, b, mp in P4RNG[k + 1]: c.rng(a, b, {kk: vv % n for kk, vv in mp.items()})
    finish(c, 2)

c = Chunk('c89', 'c30_test'); c.rng(0, 41, {'8': '8'}); c.rep('plan de pruebas de la Tesis', 'plan de pruebas de la sección 8.9'); c.rep('(Tesis 10.4)', '(sección 7.2.7.4)'); finish(c, 2)
c = Chunk('p4', 'c31_plan'); c.h(2, '8.9 Plan de pruebas del sistema completo (diseño)'); c.rng(142, 152, {'14': '8.9'}); finish(c, 2)
c = Chunk('c89', 'c32_esp'); c.rng(41, 97, {'9': '9'})
for o, n in [('la Tesis (capítulo 15)', 'la sección 9.5'), ('de la Tesis (cap. 6)', 'de la sección 6.2'), ('de la Tesis (13.1)', 'de la sección 7.5.2.1'), ('(Tesis, 13.2)', '(sección 7.5.2.2)')]: c.rep(o, n)
finish(c, 2)
c = Chunk('p4', 'c33_desp'); c.h(2, '9.5 Configuración de despliegue de referencia'); c.rng(153, 164, {'15': '9.5'}); finish(c, 2)

# ---- cierre
c = Chunk('p1', 'c40_concl'); c.h(1, 'Conclusiones'); c.sub('Conclusiones del relevamiento y propuesta', 24); c.rng(225, 228); finish(c, 3)
c = Chunk('p4', 'c41_concl'); c.sub('Conclusiones del desarrollo', 24); c.rng(165, 182, {'16.1': '~2', '16.2': '~2', '16.3': '~2'}); finish(c, 3)
c = Chunk('p4', 'c42_glos'); c.h(1, 'Glosario técnico'); c.rng(183, 185); finish(c, 3)
c = Chunk('p1', 'c43_ref1'); c.h(1, 'Referencias bibliográficas'); c.sub('Relevamiento y propuesta', 22); c.rng(229, 239); finish(c, 3)
c = Chunk('p3', 'c43_ref2'); c.sub('Especificación y casos de uso', 22); c.rng(116, 126); finish(c, 3)
c = Chunk('p4', 'c43_ref3'); c.sub('Diseño y desarrollo', 22); c.rng(186, 196); finish(c, 3)

json.dump([(n, p, h) for n, p, h in CH], open(SP + 'chunks.json', 'w'), ensure_ascii=False)
convert([WORK + n + '.docx' for n, _, _ in CH])
print('chunks', len(CH))
