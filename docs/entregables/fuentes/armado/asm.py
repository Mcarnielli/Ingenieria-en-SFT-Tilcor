# -*- coding: utf-8 -*-
"""Motor de ensamblado: recorta fuentes docx por rangos de elementos, renumera encabezados y agrega contenido nuevo."""
import copy, os, re, shutil, zipfile, subprocess
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PIC = 'http://schemas.openxmlformats.org/drawingml/2006/picture'
NS = {'w': W}
def q(t): return '{%s}%s' % (W, t)

SRC = {'p1': 'Informe_Parte1_Final', 'cur': 'Cursograma_Diagnostico_Propuesta_v2', 'p3': 'Informe_Parte2_Completo',
       'p4': 'Tesis_Parte2_Desarrollo', 'c89': 'cap89'}
UNI = '/tmp/uni/'
WORK = '/tmp/claude-0/-home-claude/b7d7bd27-8074-546c-95cb-7723bd4ca75c/scratchpad/chunks/'
os.makedirs(WORK, exist_ok=True)

FIX = [(r'cion\b', 'ción'), (r'ciones\b', 'ciones'), (r'sion\b', 'sión'), (r'Diseno', 'Diseño'), (r'DISENO', 'DISEÑO'), (r'\bModulo', 'Módulo'), (r'\bMODULO', 'MÓDULO'),
       (r'Tecnologic', 'Tecnológic'), (r'Fisicas', 'Físicas'), (r'Analisis', 'Análisis'), (r'Diagnostico', 'Diagnóstico'), (r'Mision', 'Misión'), (r'Vision', 'Visión'),
       (r'Produccion', 'Producción'), (r'Facturacion', 'Facturación'), (r'Gestion', 'Gestión'), (r'Descripcion', 'Descripción'), (r'Justificacion', 'Justificación'),
       (r'Especificos', 'Específicos'), (r'Indices', 'Índices'), (r'Tecnologico', 'Tecnológico'), (r'Metodologia', 'Metodología'), (r'Autenticacion', 'Autenticación'),
       (r'Auditoria', 'Auditoría'), (r'Bibliografic', 'Bibliográfic'), (r'Glosario Tecnico', 'Glosario técnico'), (r'TECNICO', 'TÉCNICO'), (r'Tecnico', 'Técnico'),
       (r'Organizacion', 'Organización'), (r'Infraestructura Tecnol', 'Infraestructura Tecnol'), (r'Dia\b', 'Día'), (r'Maquinas', 'Máquinas'), (r'Ambiental', 'Ambiental'),
       (r'Sanitario', 'Sanitario'), (r'Pedido', 'Pedido'), (r'Opera\b', 'Opera'), (r'Calculo', 'Cálculo'), (r'Estrategia', 'Estrategia'), (r'Cobertura', 'Cobertura'),
       (r'Unitarias e Integracion', 'Unitarias e Integración'), (r'Pruebas', 'Pruebas'), (r'Indices y', 'Índices y'), (r'Patrones de Diseño', 'Patrones de Diseño'),
       (r'Desafios', 'Desafíos'), (r'Tecnicos', 'Técnicos'), (r'Logros', 'Logros'), (r'Mision y Vision', 'Misión y Visión'), (r'Historia y Contexto', 'Historia y Contexto'),
       (r'Estructura Organizacional', 'Estructura Organizacional'), (r'Cultura', 'Cultura'), (r'Equipamiento', 'Equipamiento'), (r'Identificacion', 'Identificación'),
       (r'Necesidades', 'Necesidades'), (r'Restricciones', 'Restricciones'), (r'Instalaciones Fisicas', 'Instalaciones Físicas'), (r'Planillas de Produccion', 'Planillas de Producción'),
       (r'Raza\b', 'Raza'), (r'Curvas', 'Curvas'), (r'Variables', 'Variables'), (r'Cuadro Comparativo', 'Cuadro Comparativo'), (r'Conclusion\b', 'Conclusión'),
       (r'Problemas Criticos', 'Problemas Críticos'), (r'Analisis de Requerimientos', 'Análisis de Requerimientos'), (r'Roles', 'Roles'), (r'Tecnologias', 'Tecnologías'),
       (r'Plan de Implementacion', 'Plan de Implementación'), (r'Funcionalidades', 'Funcionalidades'), (r'Integracion', 'Integración'), (r'Cuenta Corriente', 'Cuenta Corriente'),
       (r'Dominio — Codigo', 'Dominio — Código'), (r'Codigo', 'Código'), (r'Ciclo', 'Ciclo'), (r'Despliegue', 'Despliegue'), (r'Configuracion', 'Configuración'), (r'Variables de Entorno', 'Variables de Entorno'),
       (r'Catalogo', 'Catálogo'), (r'Funcion', 'Función'), (r'Mortalidad', 'Mortalidad'), (r'Relevamiento del 4 de Diciembre', 'Relevamiento del 4 de diciembre'), (r'Diciembre', 'diciembre')]

def fixhead(t):
    for a, b in FIX: t = re.sub(a, b, t)
    return t

def sentence(t):
    if t.isupper() and len(t) > 3:
        t = t.capitalize()
        t = re.sub(r'\b(iot|afip|arca|cu\d*)\b', lambda m: m.group(1).upper() if m.group(1) != 'iot' else 'IoT', t)
    return t

def run(rpr_sz=None, bold=False, color=None, italic=False, font=None):
    rp = ''
    if font: rp += '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>' % (font, font, font)
    if bold: rp += '<w:b/>'
    if italic: rp += '<w:i/>'
    if color: rp += '<w:color w:val="%s"/>' % color
    if rpr_sz: rp += '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (rpr_sz, rpr_sz)
    return '<w:rPr>%s</w:rPr>' % rp if rp else ''

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def X(xml):
    return etree.fromstring('<w:root xmlns:w="%s" xmlns:r="%s" xmlns:wp="%s" xmlns:a="%s" xmlns:pic="%s">%s</w:root>' % (W, R, WP, A, PIC, xml))

def P(text, sz=21, bold=False, color=None, italic=False, align=None, before=0, after=100, keep=False, ind=None, hang=None, font=None, shade=None, pagebreak_before=False):
    ppr = ''
    if keep: ppr += '<w:keepNext/>'
    if pagebreak_before: ppr += '<w:pageBreakBefore/>'
    if shade: ppr += '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % shade
    ppr += '<w:spacing w:before="%d" w:after="%d"/>' % (before, after)
    if ind is not None: ppr += '<w:ind w:left="%d"%s/>' % (ind, (' w:hanging="%d"' % hang) if hang else '')
    if align: ppr += '<w:jc w:val="%s"/>' % align
    runs = ''
    # **negrita** inline
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for p_ in parts:
        if not p_: continue
        b = bold
        if p_.startswith('**') and p_.endswith('**'): p_ = p_[2:-2]; b = True
        runs += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (run(sz, b, color, italic, font), esc(p_))
    return '<w:p><w:pPr>%s</w:pPr>%s</w:p>' % (ppr, runs)

def BUL(text, sz=21): return P('•\t' + text, sz=sz, ind=500, hang=300, after=60)

def CODE(text, sz=15):
    out = ''
    for ln in text.split('\n'):
        out += '<w:p><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="F2F3F4"/><w:spacing w:before="0" w:after="0"/></w:pPr><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % (run(sz, font='Courier New'), esc(ln) if ln else ' ')
    return out

def TABLE(rows, widths, header=True, sz=18, fills=None, hfill='1A5276'):
    tw = sum(widths)
    x = '<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:tblBorders>' % tw
    for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'): x += '<w:%s w:val="single" w:sz="4" w:space="0" w:color="BFC5CA"/>' % s
    x += '</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'
    for w_ in widths: x += '<w:gridCol w:w="%d"/>' % w_
    x += '</w:tblGrid>'
    for ri, row in enumerate(rows):
        x += '<w:tr>' + ('<w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' if header and ri == 0 else '<w:trPr><w:cantSplit/></w:trPr>')
        for ci, cell in enumerate(row):
            fill = None
            if header and ri == 0: fill = hfill
            elif fills and (ri, ci) in fills: fill = fills[(ri, ci)]
            tc = '<w:tcW w:w="%d" w:type="dxa"/>' % widths[ci]
            if fill: tc += '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill
            hdr = header and ri == 0
            paras = ''
            for ln in str(cell).split('\n'):
                paras += P(ln, sz=sz, bold=hdr, color='FFFFFF' if hdr else None, after=20)
            x += '<w:tc><w:tcPr>%s</w:tcPr>%s</w:tc>' % (tc, paras)
        x += '</w:tr>'
    return x + '</w:tbl>' + P('', after=60)

class Chunk:
    def __init__(self, src, name):
        self.src, self.name = src, name
        self.dir = WORK + name
        if os.path.exists(self.dir): shutil.rmtree(self.dir)
        shutil.copytree(UNI + 'x_' + SRC[src], self.dir)
        self.tree = etree.parse(self.dir + '/word/document.xml')
        self.body = self.tree.getroot().find('w:body', NS)
        self.orig = list(self.body)
        self.sect = self.orig[-1]
        for e in list(self.body): self.body.remove(e)
        self.heads = []   # (nivel, texto)
        self.imgn = 0
        self.rels = etree.parse(self.dir + '/word/_rels/document.xml.rels')
        self.first = True
        self.reps = []

    def rep(self, old, new): self.reps.append((old, new))

    # ---- encabezados
    def hxml(self, level, text, new_page=False):
        st = 'Heading%d' % min(level, 3)
        sz = {1: 34, 2: 28, 3: 24}.get(level, 22)
        col = {1: '1A5276', 2: '2E74B5', 3: '1F4D78'}.get(level, '1F4D78')
        before = {1: 0, 2: 300, 3: 240}.get(level, 200)
        ppr = '<w:pStyle w:val="%s"/><w:keepNext/><w:keepLines/>' % st
        if new_page: ppr += '<w:pageBreakBefore/>'
        ppr += '<w:spacing w:before="%d" w:after="120"/><w:outlineLvl w:val="%d"/>' % (before, min(level, 9) - 1)
        if level == 1: ppr += '<w:pBdr><w:bottom w:val="single" w:sz="8" w:space="4" w:color="1A5276"/></w:pBdr>'
        return '<w:p><w:pPr>%s</w:pPr><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % (ppr, run(sz, True, col), esc(text))

    def h(self, level, text, new_page=False):
        self.heads.append((level, text))
        self.body.append(X(self.hxml(level, text, new_page))[0])

    def sub(self, text, size=22):   # subtítulo sin entrada de índice (no numerado)
        self.body.append(X(P(text, sz=size, bold=True, color='1A5276', before=200, after=80, keep=True))[0])

    def add(self, xml):
        for e in X(xml): self.body.append(e)

    # ---- rangos de la fuente
    def rng(self, a, b, mapping=None, titles=None, base_level=None, skip_first_heading=False):
        """copia orig[a:b]; mapping: {viejo_prefijo: nuevo_prefijo}; titles: {num_nuevo: titulo_nuevo}; headings sin número: nivel = ult+1"""
        last_level = base_level or 3
        for e in self.orig[a:b]:
            if e.tag == q('sectPr'): continue
            st = e.find('w:pPr/w:pStyle', NS)
            if st is not None and st.get(q('val')).startswith('Heading'):
                txt = ''.join(e.itertext()).strip()
                m = re.match(r'^(\d+(?:\.\d+)*)\.?\s+(.*)$', txt)
                if m and mapping is not None:
                    comps = m.group(1).split('.'); new = None
                    for k in sorted(mapping, key=lambda s: -len(s.split('.'))):
                        kc = k.split('.')
                        if comps[:len(kc)] == kc:
                            new = '.'.join([mapping[k]] + comps[len(kc):]); break
                    if new is None: new = m.group(1)
                    title = sentence(fixhead(m.group(2)))
                    if titles and new in titles: title = titles[new]
                    if new.startswith('~'):
                        lvl = int(new[1]); self.h(lvl, title); last_level = lvl
                    else:
                        lvl = len(new.split('.'))
                        self.h(lvl, '%s %s' % (new, title)); last_level = lvl
                else:
                    lvl = last_level + 1
                    t = sentence(fixhead(txt))
                    self.heads.append((lvl, t))
                    self.body.append(X(self.hxml(min(lvl, 5), t))[0])
                continue
            self.body.append(copy.deepcopy(e))

    # ---- imágenes
    def img(self, path, width_cm=15.5, caption=None, align='center'):
        from PIL import Image
        im = Image.open(path); w, h = im.size
        cx = int(width_cm * 360000); cy = int(cx * h / w)
        maxcy = int(21.5 * 360000)
        if cy > maxcy: cy = maxcy; cx = int(cy * w / h)
        self.imgn += 1
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        fn = 'new_%s_%d.%s' % (self.name, self.imgn, ext)
        os.makedirs(self.dir + '/word/media', exist_ok=True)
        shutil.copy(path, self.dir + '/word/media/' + fn)
        rid = 'rIdN%d' % self.imgn
        rel = etree.SubElement(self.rels.getroot(), '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
        rel.set('Id', rid); rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'); rel.set('Target', 'media/' + fn)
        n = 9000 + self.imgn
        xml = ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="80" w:after="60"/><w:jc w:val="%s"/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="%d" cy="%d"/>'
               '<wp:docPr id="%d" name="img%d"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
               '<pic:pic><pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
               '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>') % (align, cx, cy, n, n, n, fn, rid, cx, cy)
        self.add(xml)
        if caption: self.add(P(caption, sz=17, italic=True, color='555555', align='center', after=140))

    def imgs_row(self, paths, width_cm_each=4.6, captions=None):
        """varias capturas en una fila (tabla sin bordes)"""
        from PIL import Image
        cells = ''
        n = len(paths); cw = int(9000 / n)
        for i, p_ in enumerate(paths):
            self.imgn += 1
            ext = os.path.splitext(p_)[1].lower().lstrip('.')
            fn = 'new_%s_%d.%s' % (self.name, self.imgn, ext)
            os.makedirs(self.dir + '/word/media', exist_ok=True); shutil.copy(p_, self.dir + '/word/media/' + fn)
            rid = 'rIdN%d' % self.imgn
            rel = etree.SubElement(self.rels.getroot(), '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
            rel.set('Id', rid); rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'); rel.set('Target', 'media/' + fn)
            im = Image.open(p_); w, h = im.size
            cx = int(width_cm_each * 360000); cy = int(cx * h / w); nn = 9000 + self.imgn
            draw = ('<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="%d" cy="%d"/><wp:docPr id="%d" name="img%d"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
                    '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
                    '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>') % (cx, cy, nn, nn, nn, fn, rid, cx, cy)
            cap = P(captions[i], sz=15, italic=True, color='555555', align='center', after=40) if captions else ''
            cells += '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/></w:tcPr><w:p><w:pPr><w:keepNext/><w:jc w:val="center"/><w:spacing w:after="20"/></w:pPr>%s</w:p>%s</w:tc>' % (cw, draw, cap)
        self.add('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>%s</w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>%s</w:tr></w:tbl>' % (cw * n, '<w:gridCol w:w="%d"/>' % cw * n, cells) + P('', after=60))

    def save(self):
        # sectPr sin encabezado/pie
        s = copy.deepcopy(self.sect)
        for t in ('headerReference', 'footerReference'):
            for e in s.findall('w:' + t, NS): s.remove(e)
        self.body.append(s)
        # limpiar párrafos de salto de página sueltos al principio/final y saltos dentro
        kids = [k for k in self.body if k.tag == q('p')]
        for k in kids:
            brs = k.findall('.//w:br', NS)
            if brs and all(b.get(q('type')) == 'page' for b in brs) and not ''.join(k.itertext()).strip() and k.find('.//w:drawing', NS) is None:
                self.body.remove(k)
        for old, new in self.reps:
            hit = 0
            for tnode in self.body.iter(q('t')):
                if tnode.text and old in tnode.text: tnode.text = tnode.text.replace(old, new); hit += 1
            if not hit: print('  [rep sin coincidencia]', self.name, old)
        self.tree.write(self.dir + '/word/document.xml', xml_declaration=True, encoding='UTF-8', standalone=True)
        self.rels.write(self.dir + '/word/_rels/document.xml.rels', xml_declaration=True, encoding='UTF-8', standalone=True)
        ct = open(self.dir + '/[Content_Types].xml', encoding='utf8').read()
        for ext, mime in (('png', 'image/png'), ('jpg', 'image/jpeg'), ('jpeg', 'image/jpeg')):
            if 'Extension="%s"' % ext not in ct:
                ct = ct.replace('<Override', '<Default Extension="%s" ContentType="%s"/><Override' % (ext, mime), 1)
        open(self.dir + '/[Content_Types].xml', 'w', encoding='utf8').write(ct)
        out = WORK + self.name + '.docx'
        if os.path.exists(out): os.remove(out)
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(self.dir):
                for f in files:
                    full = os.path.join(root, f); z.write(full, os.path.relpath(full, self.dir))
        return out

def convert(docxs):
    soffice = [p for p in subprocess.run('ls /root/.claude/skills/synced/*/docx/scripts/office/soffice.py', shell=True, capture_output=True, text=True).stdout.split()][0]
    subprocess.run(['python3', soffice, '--headless', '--convert-to', 'pdf', '--outdir', WORK] + docxs, capture_output=True, text=True)
