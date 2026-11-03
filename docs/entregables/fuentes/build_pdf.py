import re, subprocess, io, sys
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas

U = '/tmp/uni/'; O = '/mnt/user-data/outputs/'
BLUE = colors.HexColor('#1A5276'); LIGHT = colors.HexColor('#EAF2F8'); GRAY = colors.HexColor('#555555')
OUT = O + 'TILCOR_Desarrollo_Completo_PPIII.pdf'

# (clave, parte, título de parte, pdf, páginas a descartar, títulos de capítulo (None = leer del docx))
SRC = [
  ('p1', 'PARTE I', 'Informe de relevamiento y diagnóstico', U + 'Informe_Parte1_Final_fix.pdf', {1}),
  ('p2', 'PARTE II', 'Cursogramas, diagnóstico y propuesta', U + 'Cursograma_Diagnostico_Propuesta_v2_fix.pdf', {1, 2}),
  ('p3', 'PARTE III', 'Especificación del sistema y casos de uso', U + 'Informe_Parte2_Completo_fix.pdf', {1, 2}),
  ('p4', 'PARTE IV', 'Diseño y desarrollo del sistema', U + 'Tesis_Parte2_Desarrollo_fix.pdf', {1, 2}),
  ('p5', 'PARTE V', 'Integración, testing y especificaciones del sistema', O + 'Cap8_9_Integracion_Especificaciones_TILCOR.pdf', set()),
]
ANEX = []
HEAD = {  # capítulos por parte (nivel 1), tal como figuran en cada documento
 'p1': ['RESUMEN EJECUTIVO', '1. INTRODUCCION', '2. PEDIDO DEL USUARIO', '3. RELEVAMIENTO ORGANIZACIONAL', '4. RELEVAMIENTO ESTRUCTURAL', '5. RELEVAMIENTO FUNCIONAL', '6. RELEVAMIENTO TECNOLOGICO', '7. RELEVAMIENTO DEL NEGOCIO', '8. DIAGNOSTICO DE LA SITUACION ACTUAL', '9. ANALISIS DE REQUERIMIENTOS', '10. PROPUESTA DEL SISTEMA', '11. CONCLUSIONES', 'REFERENCIAS BIBLIOGRAFICAS'],
 'p2': ['1. SIMBOLOGIA UTILIZADA', '2. CURSOGRAMA 1 — REGISTRO DIARIO DE PRODUCCION', '3. CURSOGRAMA 2 — GESTION DE VENTA Y FACTURACION', '4. CURSOGRAMA 3 — MONITOREO AMBIENTAL IoT DEL GALPON', '5. CURSOGRAMA 4 — CONTROL DE MORTALIDAD Y VIABILIDAD', '6. DIAGNOSTICO DE PROPUESTA'],
 'p3': ['1. OBJETIVO DEL SISTEMA', '2. LÍMITE DEL SISTEMA', '3. ALCANCE DEL SISTEMA', '4. ESPECIFICACIONES DE REQUERIMIENTOS', '5. DIAGRAMA DE CASO DE USO AMBIENTAL', '6. RELACIONES ENTRE CASOS DE USO', '7. ARTICULACIÓN CON EL INFORME PARTE I', 'REFERENCIAS BIBLIOGRÁFICAS', '8. FICHAS DE CASOS DE USO — CATÁLOGO COMPLETO'],
 'p4': ['6. ARQUITECTURA GENERAL DEL SISTEMA', '7. DISENO E IMPLEMENTACION DE LA BASE DE DATOS', '8. MODULO DE GESTION DE CLIENTES', '9. MODULO DE REGISTRO DE PRODUCCION AVICOLA', '10. MODULO DE MONITOREO IoT', '11. MODULO DE FACTURACION Y CUENTA CORRIENTE', '12. MODULO DE REPORTES Y DASHBOARDS', '13. SEGURIDAD, AUTENTICACION Y ROLES', '14. PLAN DE PRUEBAS', '15. DESPLIEGUE E INFRAESTRUCTURA', '16. CONCLUSIONES DEL DESARROLLO', 'GLOSARIO TECNICO', 'REFERENCIAS BIBLIOGRAFICAS'],
 'p5': ['8. Integración y Testing', '8.1 Alcance y entorno de prueba', '8.2 Estrategia de integración', '8.3 Pruebas unitarias y de integración del módulo IoT', '8.4 Pruebas de la interfaz (demo funcional)', '8.5 Defectos detectados y corregidos', '8.6 Pruebas de aceptación con el cliente', '8.7 Pruebas con hardware real en TILCOR', '8.8 Limitaciones y trabajo futuro', '9. Especificaciones del Sistema', '9.1 Despliegue', '9.2 Hardware mínimo y óptimo', '9.3 Software de base y aplicación', '9.4 Seguridad y auditoría'],
}

def norm(t): return re.sub(r'\s+', ' ', t).strip()
def page_texts(path):
    n = len(PdfReader(path).pages); out = []
    for i in range(1, n + 1):
        t = subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), '-layout', path, '-'], capture_output=True, text=True).stdout
        out.append([norm(l) for l in t.splitlines() if l.strip()])
    return out

def find_page(pages, title, drop, start=0):
    t = norm(title)
    for i, lines in enumerate(pages):
        if (i + 1) in drop or i < start: continue
        for l in lines:
            if l == t or (len(t) > 28 and l.startswith(t[:28])) or (l.startswith(t) and len(l) < len(t) + 3): return i
    return None

# ---------- estilos ----------
def S(name, **k): return ParagraphStyle(name, fontName=k.pop('fn', 'Helvetica'), **k)
sTitle = S('t', fontSize=24, leading=30, alignment=1, textColor=BLUE, fn='Helvetica-Bold')
sSub = S('s', fontSize=13, leading=18, alignment=1, textColor=GRAY)
sH = S('h', fontSize=16, leading=20, textColor=BLUE, fn='Helvetica-Bold', spaceAfter=8)
sP = S('p', fontSize=9.5, leading=13.5, spaceAfter=5)
sC = S('c', fontSize=8.7, leading=11)
sCB = S('cb', fontSize=8.7, leading=11, fn='Helvetica-Bold', textColor=colors.white)

def front_pdf(entries, total_pages, front_len):
    """entries: [(nivel, texto, pagina_global)]; nivel 0 = parte"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm, topMargin=20 * mm, bottomMargin=20 * mm)
    f = []
    # --- portada
    f += [Spacer(1, 38 * mm), Paragraph('COLEGIO UNIVERSITARIO IES', S('x1', fontSize=12, alignment=1, textColor=GRAY, fn='Helvetica-Bold')),
          Paragraph('Analista en Sistemas de Información · Córdoba', sSub), Spacer(1, 22 * mm),
          Paragraph('SISTEMA DE GESTIÓN INTEGRAL<br/>PARA EMPRESA AVÍCOLA', sTitle), Spacer(1, 6 * mm),
          Paragraph('TILCOR S.A.S. — Colonia Tirolesa, Córdoba', S('x2', fontSize=14, leading=18, alignment=1, fn='Helvetica-Bold')), Spacer(1, 12 * mm)]
    box = Table([[Paragraph('DESARROLLO COMPLETO DEL PROYECTO', S('x3', fontSize=13, alignment=1, textColor=colors.white, fn='Helvetica-Bold'))],
                 [Paragraph('PPIII · Instancia Evaluativa 2', S('x4', fontSize=10.5, alignment=1, textColor=colors.white))]], colWidths=[150 * mm])
    box.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BLUE), ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
    f += [box, Spacer(1, 18 * mm)]
    au = Table([[Paragraph('<b>AUTORES</b>', sC), Paragraph('<b>REFERENCIAS</b>', sC)],
                [Paragraph('Carnielli, Matías<br/>Bacari, Fernando', S('x5', fontSize=10.5, leading=15)),
                 Paragraph('Demo: tilcorvercel.vercel.app<br/>Código: github.com/Mcarnielli/Ingenieria-en-SFT-Tilcor', S('x6', fontSize=9.5, leading=14))]],
               colWidths=[70 * mm, 100 * mm])
    au.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.8, BLUE), ('BACKGROUND', (0, 0), (-1, 0), LIGHT), ('LINEBELOW', (0, 0), (-1, 0), 0.5, BLUE),
                            ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    f += [au, Spacer(1, 14 * mm), Paragraph('Córdoba, noviembre de 2026', sSub), PageBreak()]
    # --- índice
    f.append(Paragraph('ÍNDICE GENERAL', sH))
    rows = []
    for lvl, txt, pg in entries:
        if lvl == 0: rows.append([Paragraph('<b>%s</b>' % txt, S('i0', fontSize=9.6, leading=13, textColor=BLUE, fn='Helvetica-Bold')), str(pg)])
        else: rows.append([Paragraph(txt, S('i%d' % lvl, fontSize=8.8, leading=11.2, leftIndent=10 + 12 * (lvl - 1))), str(pg)])
    t = Table(rows, colWidths=[150 * mm, 20 * mm])
    ts = [('ALIGN', (1, 0), (1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'), ('TOPPADDING', (0, 0), (-1, -1), 1.6), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.6), ('FONTSIZE', (1, 0), (1, -1), 8.8)]
    for i, (lvl, _, _) in enumerate(entries):
        if lvl == 0: ts += [('LINEABOVE', (0, i), (-1, i), 0.4, BLUE), ('TOPPADDING', (0, i), (-1, i), 6)]
    t.setStyle(TableStyle(ts)); f += [t, PageBreak()]
    # --- guía de lectura y estado
    f.append(Paragraph('GUÍA DE LECTURA Y ESTADO DE IMPLEMENTACIÓN', sH))
    f.append(Paragraph('Este documento reúne todo el desarrollo del proyecto en un único archivo. Está organizado en cinco partes. <b>Cada parte conserva su propia numeración de capítulos</b> (por ejemplo, el capítulo 8 de la Parte I, el de la Parte III y el de la Parte V son distintos); las referencias cruzadas indican siempre de qué parte se trata. Las menciones internas a «Informe Parte I», «Informe Parte II» y «Parte II: Desarrollo» corresponden, respectivamente, a las Partes I, III y IV de este documento.', sP))
    mp = [[Paragraph('<b>Parte</b>', sCB), Paragraph('<b>Contenido</b>', sCB)],
          [Paragraph('I', sC), Paragraph('Pedido del cliente, relevamiento organizacional, estructural, funcional, tecnológico y del negocio; diagnóstico y propuesta.', sC)],
          [Paragraph('II', sC), Paragraph('Cursogramas de la situación actual y propuesta para los cuatro procesos; diagnóstico comparativo.', sC)],
          [Paragraph('III', sC), Paragraph('Objetivo, límite y alcance del sistema; requerimientos; casos de uso y catálogo de fichas.', sC)],
          [Paragraph('IV', sC), Paragraph('Arquitectura, base de datos, módulos, seguridad, plan de pruebas y despliegue (diseño y código de referencia).', sC)],
          [Paragraph('V', sC), Paragraph('<b>Capítulo 8 — Integración y Testing</b> y <b>capítulo 9 — Especificaciones del Sistema</b>, con resultados de pruebas reales.', sC)]]
    t1 = Table(mp, colWidths=[22 * mm, 148 * mm]); t1.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), BLUE), ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#BFC5CA')), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
    f += [t1, Spacer(1, 8)]
    f.append(Paragraph('Estado de implementación (a la fecha de entrega)', S('h2', fontSize=11.5, leading=15, textColor=BLUE, fn='Helvetica-Bold', spaceAfter=5)))
    G, A, Rr = colors.HexColor('#D5F5E3'), colors.HexColor('#FEF9E7'), colors.HexColor('#FADBD8')
    es = [[Paragraph('<b>Componente</b>', sCB), Paragraph('<b>Estado</b>', sCB), Paragraph('<b>Detalle</b>', sCB)],
          [Paragraph('Demo funcional (PWA)', sC), Paragraph('Implementado', sC), Paragraph('En línea en tilcorvercel.vercel.app. Perfiles Administrador y Empleado; inicio, producción, IoT, sanidad y ventas (Don Gestión por iframe). Datos de ejemplo en el navegador.', sC)],
          [Paragraph('Módulo IoT (MQTT → PostgreSQL)', sC), Paragraph('Implementado y probado', sC), Paragraph('Ingesta, validación, motor de alertas, simulador de sensores y auditoría por triggers. 29 pruebas automáticas aprobadas (cap. 8).', sC)],
          [Paragraph('Prueba con sensores reales', sC), Paragraph('Pendiente', sC), Paragraph('Se realiza en una visita a TILCOR; resultados a completar en la tabla 8.4.', sC)],
          [Paragraph('Backend completo (API REST, JWT, clientes, facturación AFIP, reportes)', sC), Paragraph('Diseñado', sC), Paragraph('Especificado en las Partes III y IV; su construcción corresponde a las Fases 3 a 5 del Contrato de alcance (documento aparte).', sC)]]
    t2 = Table(es, colWidths=[44 * mm, 28 * mm, 98 * mm]); t2.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), BLUE), ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#BFC5CA')), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (1, 1), (1, 2), G), ('BACKGROUND', (1, 3), (1, 3), A), ('BACKGROUND', (1, 4), (1, 4), Rr), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
    f += [t2]
    doc.build(f)
    return PdfReader(io.BytesIO(buf.getvalue()))

def divider(code, title, items):
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=A4); w, h = A4
    c.setFillColor(BLUE); c.rect(0, h / 2 - 20, w, 110, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 30); c.drawCentredString(w / 2, h / 2 + 50, code)
    c.setFont('Helvetica', 15); c.drawCentredString(w / 2, h / 2 + 15, title)
    c.setFillColor(GRAY); c.setFont('Helvetica', 10)
    y = h / 2 - 60
    for it in items: c.drawCentredString(w / 2, y, it); y -= 15
    c.showPage(); c.save(); return PdfReader(io.BytesIO(buf.getvalue())).pages[0]

def build():
    parts = []  # dict(code,title,pdf,drop,heads,reader)
    for k, code, title, path, drop in SRC:
        parts.append(dict(k=k, code=code, title=title, path=path, drop=drop, texts=page_texts(path), reader=PdfReader(path)))
    # páginas por capítulo dentro de cada fuente (índice 0-based dentro del PDF fuente)
    for p in parts:
        last = 0; p['found'] = []
        for h in HEAD[p['k']]:
            i = find_page(p['texts'], h, p['drop'], last)
            if i is None: print('NO ENCONTRADO', p['k'], h); continue
            p['found'].append((h, i)); last = i
        p['pages'] = [i for i in range(len(p['reader'].pages)) if (i + 1) not in p['drop']]
    anex = [dict(code=c, title=t, path=pa, reader=PdfReader(pa)) for _, c, t, pa in ANEX]
    items_div = {p['k']: [h for h, _ in p['found'] if re.match(r'^(\d+\.|RESUMEN)', h) or p['k'] == 'p5' and re.match(r'^\d\. ', h)] for p in parts}

    def layout(front_len):
        pos = front_len; entries = []; plan = []
        for p in parts:
            entries.append((0, '%s — %s' % (p['code'], p['title']), pos + 1)); plan.append(('div', p)); start = pos + 1  # divisor ocupa 1
            pos += 1
            idx = {pg: pos + n for n, pg in enumerate(p['pages'])}
            for h, i in p['found']:
                lvl = 1
                if p['k'] == 'p5' and re.match(r'^\d\.\d', h): lvl = 2
                disp = h if p['k'] == 'p5' else (h.title() if h.isupper() and False else h)
                entries.append((lvl, disp, idx[i] + 1))
            plan.append(('src', p)); pos += len(p['pages'])
        if anex:
            entries.append((0, 'ANEXOS', pos + 1)); plan.append(('adiv', None)); pos += 1
        for a in anex:
            entries.append((1, '%s — %s' % (a['code'], a['title']), pos + 1)); plan.append(('anx', a)); pos += len(a['reader'].pages)
        return entries, plan, pos

    # pasada 1: cantidad de páginas del frente (portada + índice + guía)
    fl = 3
    for _ in range(4):
        entries, plan, total = layout(fl)
        fr = front_pdf(entries, total, fl)
        if len(fr.pages) == fl: break
        fl = len(fr.pages)
    entries, plan, total = layout(fl); fr = front_pdf(entries, total, fl)
    assert len(fr.pages) == fl

    w = PdfWriter(); outline = []
    for pg in fr.pages: w.add_page(pg)
    def stamp(page, num):
        pw, ph = float(page.mediabox.width), float(page.mediabox.height)
        b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(pw, ph))
        c.setFont('Helvetica', 8); c.setFillColor(GRAY)
        c.drawCentredString(pw / 2, 20, 'TILCOR S.A.S. · Desarrollo completo del proyecto PPIII · Página %d de %d' % (num, total))
        c.showPage(); c.save(); page.merge_page(PdfReader(io.BytesIO(b.getvalue())).pages[0])
    def cover_old_footer(page, label, hb=62, ht=58):
        pw, ph = float(page.mediabox.width), float(page.mediabox.height)
        b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(pw, ph))
        c.setFillColor(colors.white); c.rect(0, 0, pw, hb, fill=1, stroke=0); c.rect(0, ph - ht, pw, ht, fill=1, stroke=0)
        c.setFillColor(GRAY); c.setFont('Helvetica', 8); c.drawString(62, ph - 36, 'Sistema de Gestión Integral Avícola — TILCOR S.A.S.')
        c.drawRightString(pw - 62, ph - 36, label)
        c.setStrokeColor(BLUE); c.setLineWidth(0.6); c.line(62, ph - 42, pw - 62, ph - 42)
        c.showPage(); c.save(); page.merge_page(PdfReader(io.BytesIO(b.getvalue())).pages[0])

    n = fl
    w.add_outline_item('Portada', 0); w.add_outline_item('Índice general', 1); w.add_outline_item('Guía de lectura y estado', fl - 1)
    cur_parent = None
    for kind, obj in plan:
        if kind == 'div':
            pg = divider(obj['code'], obj['title'], items_div[obj['k']] if obj['k'] != 'p5' else ['8. Integración y Testing', '9. Especificaciones del Sistema'])
            w.add_page(pg); n += 1; cur_parent = w.add_outline_item('%s — %s' % (obj['code'], obj['title']), n - 1)
        elif kind == 'src':
            base = n
            for j, i in enumerate(obj['pages']):
                page = obj['reader'].pages[i]
                if obj['k'] != 'p5': cover_old_footer(page, '%s · %s' % (obj['code'].title().replace('Parte','Parte'), obj['title']))
                w.add_page(page); n += 1
            idx = {pg: base + k for k, pg in enumerate(obj['pages'])}
            for h, i in obj['found']:
                if obj['k'] == 'p5' and re.match(r'^\d\.\d', h): continue
                w.add_outline_item(h, idx[i], parent=cur_parent)
        elif kind == 'adiv':
            w.add_page(divider('ANEXOS', 'Documentos complementarios', ['A. Contrato de alcance y presupuesto', 'B. Manual de usuario'])); n += 1; cur_parent = w.add_outline_item('ANEXOS', n - 1)
        elif kind == 'anx':
            w.add_outline_item('%s — %s' % (obj['code'], obj['title']), n, parent=cur_parent)
            for page in obj['reader'].pages: w.add_page(page); n += 1
    assert n == total, (n, total)
    for i, page in enumerate(w.pages):
        if i == 0: continue
        stamp(page, i + 1)
    w.add_metadata({'/Title': 'Sistema de Gestión Integral para Empresa Avícola — TILCOR S.A.S. — Desarrollo completo PPIII', '/Author': 'Carnielli, Matías; Bacari, Fernando'})
    w.page_mode = '/UseOutlines'
    with open(OUT, 'wb') as fh: w.write(fh)
    print('OK', total, 'páginas; frente', fl)
    return entries

if __name__ == '__main__':
    e = build()
    for x in e[:14]: print(x)
