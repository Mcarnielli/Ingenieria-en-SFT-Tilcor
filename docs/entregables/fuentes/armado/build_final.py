# -*- coding: utf-8 -*-
import io, json, re, subprocess, sys
sys.path.insert(0, '.')
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas

SP = '/tmp/claude-0/-home-claude/b7d7bd27-8074-546c-95cb-7723bd4ca75c/scratchpad/'
OUT = '/mnt/user-data/outputs/TILCOR_Desarrollo_Completo_PPIII.pdf'
BLUE = colors.HexColor('#1A5276'); LIGHT = colors.HexColor('#EAF2F8'); GRAY = colors.HexColor('#555555')
CH = json.load(open(SP + 'chunks.json', encoding='utf8'))
PARTS = {1: ('PARTE 1', 'Relevamiento y propuesta (PP2)', ['1 Introducción', '2 Relevamiento', '3 Propuesta']),
         2: ('PARTE 2', 'Modelado y desarrollo del sistema (PP3)', ['4 Objetivos, límites y alcance', '5 Especificación de requerimientos', '6 Análisis y diseño del producto', '7 Implementación del software', '8 Integración y testing', '9 Especificaciones del sistema']),
         3: ('CIERRE', 'Conclusiones, glosario y referencias', [])}

def norm(t): return re.sub(r'\s+', ' ', t).strip()
def page_lines(path):
    n = len(PdfReader(path).pages); out = []
    for i in range(1, n + 1):
        t = subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), '-layout', path, '-'], capture_output=True, text=True).stdout
        out.append([norm(l) for l in t.splitlines() if l.strip()])
    return out

def S(name, **k): return ParagraphStyle(name, fontName=k.pop('fn', 'Helvetica'), **k)
sTitle = S('t', fontSize=24, leading=30, alignment=1, textColor=BLUE, fn='Helvetica-Bold'); sSub = S('s', fontSize=13, leading=18, alignment=1, textColor=GRAY)
sH = S('h', fontSize=16, leading=20, textColor=BLUE, fn='Helvetica-Bold', spaceAfter=8); sP = S('p', fontSize=9.5, leading=13.5, spaceAfter=5)
sC = S('c', fontSize=8.7, leading=11); sCB = S('cb', fontSize=8.7, leading=11, fn='Helvetica-Bold', textColor=colors.white)

def esc(t): return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def front_pdf(entries):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm, topMargin=20 * mm, bottomMargin=20 * mm)
    f = [Spacer(1, 38 * mm), Paragraph('COLEGIO UNIVERSITARIO IES', S('x1', fontSize=12, alignment=1, textColor=GRAY, fn='Helvetica-Bold')),
         Paragraph('Analista en Sistemas de Información · Córdoba', sSub), Spacer(1, 22 * mm),
         Paragraph('SISTEMA DE GESTIÓN INTEGRAL<br/>PARA EMPRESA AVÍCOLA', sTitle), Spacer(1, 6 * mm),
         Paragraph('TILCOR S.A.S. — Colonia Tirolesa, Córdoba', S('x2', fontSize=14, leading=18, alignment=1, fn='Helvetica-Bold')), Spacer(1, 12 * mm)]
    box = Table([[Paragraph('DESARROLLO COMPLETO DEL PROYECTO', S('x3', fontSize=13, alignment=1, textColor=colors.white, fn='Helvetica-Bold'))],
                 [Paragraph('PPIII · Instancia Evaluativa 2', S('x4', fontSize=10.5, alignment=1, textColor=colors.white))]], colWidths=[150 * mm])
    box.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BLUE), ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
    f += [box, Spacer(1, 18 * mm)]
    au = Table([[Paragraph('<b>AUTORES</b>', sC), Paragraph('<b>REFERENCIAS</b>', sC)],
                [Paragraph('Carnielli, Matías<br/>Bacari, Fernando', S('x5', fontSize=10.5, leading=15)),
                 Paragraph('Demo: tilcorvercel.vercel.app<br/>Código: github.com/Mcarnielli/Ingenieria-en-SFT-Tilcor', S('x6', fontSize=9.5, leading=14))]], colWidths=[70 * mm, 100 * mm])
    au.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.8, BLUE), ('BACKGROUND', (0, 0), (-1, 0), LIGHT), ('LINEBELOW', (0, 0), (-1, 0), 0.5, BLUE), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    f += [au, Spacer(1, 14 * mm), Paragraph('Córdoba, noviembre de 2026', sSub), PageBreak(), Paragraph('ÍNDICE GENERAL', sH)]
    rows = []
    for lvl, txt, pg in entries:
        if lvl == 0: rows.append([Paragraph('<b>%s</b>' % esc(txt), S('i0', fontSize=9.6, leading=13, textColor=BLUE, fn='Helvetica-Bold')), str(pg)])
        elif lvl == 1: rows.append([Paragraph('<b>%s</b>' % esc(txt), S('i1', fontSize=9, leading=11.4, leftIndent=4, fn='Helvetica-Bold')), str(pg)])
        else: rows.append([Paragraph(esc(txt), S('i%d' % lvl, fontSize=8.3, leading=10.4, leftIndent=8 + 11 * (lvl - 1))), str(pg)])
    t = Table(rows, colWidths=[150 * mm, 20 * mm])
    ts = [('ALIGN', (1, 0), (1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'), ('TOPPADDING', (0, 0), (-1, -1), 1.1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.1), ('FONTSIZE', (1, 0), (1, -1), 8.3)]
    for i, (lvl, _, _) in enumerate(entries):
        if lvl == 0: ts += [('LINEABOVE', (0, i), (-1, i), 0.4, BLUE), ('TOPPADDING', (0, i), (-1, i), 6)]
    t.setStyle(TableStyle(ts)); f += [t, PageBreak()]
    # guía
    f.append(Paragraph('GUÍA DE LECTURA Y ESTADO DE IMPLEMENTACIÓN', sH))
    f.append(Paragraph('Este documento reúne todo el desarrollo del proyecto en un único archivo, organizado según el <b>Checklist de Avances</b> de la materia, en dos partes con numeración continua de capítulos del 1 al 9.', sP))
    mp = [[Paragraph('<b>Parte</b>', sCB), Paragraph('<b>Capítulos</b>', sCB), Paragraph('<b>Contenido</b>', sCB)],
          [Paragraph('1 · PP2', sC), Paragraph('1 a 3', sC), Paragraph('Introducción (carta y pedido del usuario), relevamiento (contexto, estructura, procesos con cursogramas, tecnología existente y de mercado) y propuesta (diagnóstico y propuesta general).', sC)],
          [Paragraph('2 · PP3', sC), Paragraph('4 a 6', sC), Paragraph('Objetivos, límites y alcance; especificación de requerimientos; análisis y diseño: modelado ambiental, de paquetes y de los 24 casos de uso por módulo (requerimientos, prototipos, ficha, vista estática y dinámica).', sC)],
          [Paragraph('2 · PP3', sC), Paragraph('7 a 9', sC), Paragraph('Implementación por módulo y caso de uso (código real del repositorio y de la demo); integración y testing con resultados reales; especificaciones del sistema (despliegue, hardware, software, seguridad y auditoría).', sC)],
          [Paragraph('Cierre', sC), Paragraph('—', sC), Paragraph('Conclusiones, glosario técnico y referencias bibliográficas.', sC)]]
    t1 = Table(mp, colWidths=[20 * mm, 20 * mm, 130 * mm]); t1.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), BLUE), ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#BFC5CA')), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
    f += [t1, Spacer(1, 8), Paragraph('Estado de implementación (a la fecha de entrega)', S('h2', fontSize=11.5, leading=15, textColor=BLUE, fn='Helvetica-Bold', spaceAfter=5))]
    G, A, Rr = colors.HexColor('#D5F5E3'), colors.HexColor('#FEF9E7'), colors.HexColor('#FADBD8')
    es = [[Paragraph('<b>Componente</b>', sCB), Paragraph('<b>Estado</b>', sCB), Paragraph('<b>Detalle</b>', sCB)],
          [Paragraph('Demo funcional (PWA)', sC), Paragraph('Implementado', sC), Paragraph('En línea en tilcorvercel.vercel.app. Perfiles Administrador y Empleado; inicio, producción, IoT, sanidad y ventas (Don Gestión por iframe). Datos de ejemplo en el navegador.', sC)],
          [Paragraph('Módulo IoT (MQTT → PostgreSQL)', sC), Paragraph('Implementado y probado', sC), Paragraph('Ingesta, validación, motor de alertas, simulador de sensores y auditoría por triggers. 29 pruebas automáticas aprobadas (cap. 8).', sC)],
          [Paragraph('Prueba con sensores reales', sC), Paragraph('Pendiente', sC), Paragraph('Se realiza en una visita a TILCOR; resultados a completar en la tabla de la sección 8.7.', sC)],
          [Paragraph('Backend completo (API REST, JWT, clientes, facturación AFIP, reportes)', sC), Paragraph('Diseñado', sC), Paragraph('Especificado en los capítulos 4 a 7; su construcción corresponde a las fases 3 a 5 del plan de implementación (sección 3.2.5).', sC)],
          [Paragraph('Prototipos de CU05, CU11, CU13, CU16 y CU23', sC), Paragraph('Bocetos', sC), Paragraph('Las pantallas de estos casos de uso no están en la demo; se presentan como bocetos rotulados en la sección 6.3.', sC)]]
    t2 = Table(es, colWidths=[44 * mm, 28 * mm, 98 * mm]); t2.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), BLUE), ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#BFC5CA')), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (1, 1), (1, 2), G), ('BACKGROUND', (1, 3), (1, 3), A), ('BACKGROUND', (1, 4), (1, 4), Rr), ('BACKGROUND', (1, 5), (1, 5), A), ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
    f += [t2, Spacer(1, 6), Paragraph('Nota: los capítulos 1 a 3 conservan el texto del relevamiento original, redactado antes de la demo; las cifras y el estado de los sensores allí descriptos corresponden a la fecha del relevamiento.', S('n', fontSize=8.3, leading=11, textColor=GRAY))]
    doc.build(f); return PdfReader(io.BytesIO(buf.getvalue()))

def divider(code, title, items):
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=A4); w, h = A4
    c.setFillColor(BLUE); c.rect(0, h / 2 - 20, w, 110, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 30); c.drawCentredString(w / 2, h / 2 + 50, code)
    c.setFont('Helvetica', 15); c.drawCentredString(w / 2, h / 2 + 15, title)
    c.setFillColor(GRAY); c.setFont('Helvetica', 10.5); y = h / 2 - 60
    for it in items: c.drawCentredString(w / 2, y, it); y -= 16
    c.showPage(); c.save(); return PdfReader(io.BytesIO(buf.getvalue())).pages[0]

def build():
    # 1) lectura de capítulos
    chunks = []
    for name, parte, heads in CH:
        path = SP + 'chunks/%s.pdf' % name
        chunks.append(dict(name=name, parte=parte, heads=heads, path=path, reader=PdfReader(path), lines=page_lines(path)))
    # 2) página de cada encabezado dentro de su capítulo
    for c in chunks:
        last = 0; c['found'] = []
        for lvl, text in c['heads']:
            t = norm(text); pg = None
            for i in range(last, len(c['lines'])):
                for l in c['lines'][i]:
                    if l == t or (len(t) > 30 and l.startswith(t[:30])) or (l.startswith(t[:25]) and len(t) <= 30 and len(l) < len(t) + 3): pg = i; break
                if pg is not None: break
            if pg is None: print('NO ENCONTRADO', c['name'], text); pg = last
            c['found'].append((lvl, text, pg)); last = pg

    def layout(fl):
        pos = fl; entries = []; plan = []
        for parte in (1, 2, 3):
            code, title, items = PARTS[parte]
            if parte != 3:
                entries.append((0, '%s — %s' % (code, title), pos + 1)); plan.append(('div', parte)); pos += 1
            else:
                entries.append((0, '%s — %s' % (code, title), pos + 1))
            for c in [x for x in chunks if x['parte'] == parte]:
                base = pos
                for lvl, text, pg in c['found']:
                    if lvl <= 3 or text.startswith('6.3.'): entries.append((lvl, text, base + pg + 1))
                plan.append(('src', c)); pos += len(c['reader'].pages)
        return entries, plan, pos
    fl = 4
    for _ in range(5):
        entries, plan, total = layout(fl)
        fr = front_pdf(entries)
        if len(fr.pages) == fl: break
        fl = len(fr.pages)
    entries, plan, total = layout(fl); fr = front_pdf(entries); assert len(fr.pages) == fl

    w = PdfWriter()
    for pg in fr.pages: w.add_page(pg)
    n = fl
    w.add_outline_item('Portada', 0); w.add_outline_item('Índice general', 1); w.add_outline_item('Guía de lectura y estado', fl - 1)
    def stamp(page, num, label):
        pw, ph = float(page.mediabox.width), float(page.mediabox.height)
        b = io.BytesIO(); c = canvas.Canvas(b, pagesize=(pw, ph)); c.setFont('Helvetica', 8); c.setFillColor(GRAY)
        c.drawCentredString(pw / 2, 20, 'TILCOR S.A.S. · Desarrollo completo del proyecto PPIII · Página %d de %d' % (num, total))
        if label:
            c.drawString(40, ph - 28, 'Sistema de Gestión Integral Avícola — TILCOR S.A.S.'); c.drawRightString(pw - 40, ph - 28, label)
            c.setStrokeColor(BLUE); c.setLineWidth(0.5); c.line(40, ph - 33, pw - 40, ph - 33)
        c.showPage(); c.save(); page.merge_page(PdfReader(io.BytesIO(b.getvalue())).pages[0])
    labels = {}
    stack = {}  # nivel -> item de outline
    parent0 = None
    cur_part = None
    for kind, obj in plan:
        if kind == 'div':
            code, title, items = PARTS[obj]
            w.add_page(divider(code, title, items)); n += 1; labels[n - 1] = None
            parent0 = w.add_outline_item('%s — %s' % (code, title), n - 1); stack = {0: parent0}; cur_part = '%s · %s' % (code.title(), title)
        else:
            c = obj
            if cur_part and c['parte'] == 3 and 'Cierre' not in cur_part:
                code, title, _ = PARTS[3]; parent0 = w.add_outline_item('%s — %s' % (code, title), n); stack = {0: parent0}; cur_part = 'Cierre · ' + title
            base = n
            for pg in c['reader'].pages: w.add_page(pg); labels[n] = cur_part; n += 1
            for lvl, text, pg in c['found']:
                if lvl > 4: continue
                parent = stack.get(lvl - 1) or stack.get(max(k for k in stack if k < lvl))
                it = w.add_outline_item(text, base + pg, parent=parent); stack[lvl] = it
                for k in [k for k in stack if k > lvl]: del stack[k]
    assert n == total, (n, total)
    for i, page in enumerate(w.pages):
        if i == 0: continue
        stamp(page, i + 1, labels.get(i))
    w.add_metadata({'/Title': 'Sistema de Gestión Integral para Empresa Avícola — TILCOR S.A.S. — Desarrollo completo PPIII', '/Author': 'Carnielli, Matías; Bacari, Fernando'})
    w.page_mode = '/UseOutlines'
    with open(OUT, 'wb') as fh: w.write(fh)
    print('OK', total, 'páginas; frente', fl, 'entradas índice', len(entries))
    json.dump(entries, open(SP + 'entries.json', 'w'), ensure_ascii=False)

build()
