# Minimal pop illustrations with Panamanian wildlife, in the manner of Malika Favre's travel
# posters: few flat colors per scene, big silhouettes, negative space, hard-edged shadows and
# op-art stripes/rings. Writes SVG files to img/v5/.
#   python3 tools/favre.py
import math, os

P = dict(
    navy='#14213d', ink='#0d0d12', emerald='#0e6b4f', jungle='#0a4a37', lime='#8cc63f', coral='#ff6b57',
    red='#e8382f', gold='#f4b63a', cream='#f5ecd8', sand='#e9d3ae', kraft='#d8a76a', morpho='#1f6bff',
    sky='#2bb3e6', orange='#ff8a1f', blue='#2a5bd7', white='#fffaf0', brown='#5a3424', yellow='#ffd23f',
)

class S:
    def __init__(s, w, h, bg):
        s.w, s.h, s.o, s.defs, s.n = w, h, [], [], 0
        s.rect(0, 0, w, h, bg)
    def add(s, x): s.o.append(x)
    def uid(s, p): s.n += 1; return f'{p}{s.n}'
    def rect(s, x, y, w, h, f, rx=0, **k): s.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{f}"{at(k)}/>')
    def circ(s, x, y, r, f, **k): s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{f}"{at(k)}/>')
    def ell(s, x, y, rx, ry, f, rot=0, **k): s.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{f}" transform="rotate({rot:.1f} {x:.1f} {y:.1f})"{at(k)}/>')
    def path(s, d, f, **k): s.add(f'<path d="{d}" fill="{f}"{at(k)}/>')
    def poly(s, pts, f, **k): s.add(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{f}"{at(k)}/>')
    def line(s, x1, y1, x2, y2, c, w, **k): s.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"{at(k)}/>')
    def group(s, tr): s.add(f'<g transform="{tr}">')
    def end(s): s.add('</g>')
    def clip(s, inner):
        i = s.uid('c'); s.defs.append(f'<clipPath id="{i}">{inner}</clipPath>'); return f'url(#{i})'
    def svg(s, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s.w} {s.h}" preserveAspectRatio="xMidYMid slice" role="img">'
                f'<title>{title}</title><defs>{"".join(s.defs)}</defs>' + ''.join(s.o) + '</svg>\n')

def at(k): return ''.join(f' {a.replace("_", "-")}="{v}"' for a, v in k.items())

# ---------- motifs ----------
def leaf(s, x, y, L, ang, f, vein=None):
    """Pointed leaf from (x, y) along angle ang (deg), length L."""
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    tx, ty = x + ux*L, y + uy*L; w = L*.32
    c1 = (x + ux*L*.35 + nx*w, y + uy*L*.35 + ny*w); c2 = (x + ux*L*.35 - nx*w, y + uy*L*.35 - ny*w)
    s.path(f'M{x:.1f},{y:.1f} Q{c1[0]:.1f},{c1[1]:.1f} {tx:.1f},{ty:.1f} Q{c2[0]:.1f},{c2[1]:.1f} {x:.1f},{y:.1f}Z', f)
    if vein: s.line(x, y, x + ux*L*.85, y + uy*L*.85, vein, max(1, L*.02))

def cherries(s, x, y, r, n=5, f=P['red'], hi=None):
    pts = [(0, 0), (1.7, .4), (.8, 1.5), (-.9, 1.3), (2.4, 1.8), (-.2, 2.8)][:n]
    for dx, dy in pts:
        s.circ(x + dx*r, y + dy*r, r, f)
        if hi: s.circ(x + dx*r - r*.35, y + dy*r - r*.35, r*.28, hi)

def rings(s, x, y, r, n, c1, c2):
    for i in range(n):
        s.circ(x, y, r*(1 - i/n), c1 if i % 2 == 0 else c2)

def stripes(s, x, y, w, h, n, c, vertical=False):
    for i in range(n):
        if vertical: s.rect(x + i*w/n, y, w/n/2, h, c)
        else: s.rect(x, y + i*h/n, w, h/n/2, c)

def toucan(s, x, y, k=1.0, face=-1):
    """Keel-billed toucan perched, eye at (x, y), facing left (face=-1)."""
    s.group(f'translate({x} {y}) scale({k*-face} {k})') if face == 1 else s.group(f'translate({x} {y}) scale({k})')
    # tail
    s.path('M95,215 L150,345 L118,352 L70,235Z', P['ink'])
    # body
    s.path('M-22,-32 C18,-74 92,-62 112,0 C138,78 146,170 112,232 C70,262 10,230 -12,150 C-32,80 -50,8 -22,-32Z', P['ink'])
    # yellow bib
    s.path('M-34,4 C-46,58 -30,112 8,146 C30,104 30,46 18,6 C2,-6 -18,-6 -34,4Z', P['gold'])
    s.path('M-8,146 C10,150 26,144 36,132 C30,150 14,160 -8,146Z', P['red'])
    # beak (rainbow), clipped bands
    up = 'M-22,-30 C-118,-46 -224,-14 -266,30 C-204,18 -112,6 -22,6Z'
    lo = 'M-22,6 C-112,8 -204,20 -266,30 C-206,42 -112,40 -22,30Z'
    s.path(up, P['lime']); s.path(lo, P['blue'])
    cp = s.clip(f'<path d="{up}"/>')
    s.add(f'<g clip-path="{cp}"><rect x="-150" y="-60" width="36" height="120" fill="{P["orange"]}"/><rect x="-280" y="-60" width="64" height="120" fill="{P["red"]}"/></g>')
    cl = s.clip(f'<path d="{lo}"/>')
    s.add(f'<g clip-path="{cl}"><rect x="-280" y="-10" width="64" height="80" fill="{P["red"]}"/></g>')
    s.path('M-22,6 C-112,8 -204,20 -266,30', 'none', stroke=P['ink'], stroke_width=3)
    # eye
    s.circ(-2, -6, 17, P['lime']); s.circ(-2, -6, 7, P['ink']); s.circ(-5, -9, 2.4, P['white'])
    # feet
    s.path('M40,226 l-6,22 M58,228 l2,22', 'none', stroke=P['blue'], stroke_width=8, stroke_linecap='round')
    s.end()

def golden_frog(s, x, y, k=1.0):
    """Panamanian golden frog, sitting, seen in 3/4 from the front."""
    s.group(f'translate({x} {y}) scale({k})')
    g, d = P['gold'], P['ink']
    # back legs
    s.path('M-70,40 C-110,30 -120,70 -80,78 L-20,78 C-40,66 -50,52 -70,40Z', g)
    s.path('M70,40 C110,30 120,70 80,78 L20,78 C40,66 50,52 70,40Z', g)
    # body + head
    s.path('M-52,60 C-66,10 -40,-40 0,-44 C40,-40 66,10 52,60 C30,80 -30,80 -52,60Z', g)
    s.path('M-40,-28 C-34,-62 34,-62 40,-28 C24,-14 -24,-14 -40,-28Z', g)
    # eyes
    for sx in (-1, 1):
        s.circ(sx*30, -44, 13, g); s.circ(sx*31, -45, 7, d); s.circ(sx*29, -48, 2, P['white'])
    # front legs (long and thin, as on the real frog)
    s.path('M-30,20 C-48,40 -50,62 -40,80 L-30,80 C-38,60 -30,40 -18,30Z', g)
    s.path('M30,20 C48,40 50,62 40,80 L30,80 C38,60 30,40 18,30Z', g)
    # black spots
    for px, py, r in ((-20, 4, 7), (16, -6, 6), (28, 30, 8), (-30, 40, 6), (0, 32, 5), (-6, -24, 4), (86, 60, 6), (-90, 56, 6)):
        s.circ(px, py, r, d)
    s.end()

def hummingbird(s, x, y, k=1.0):
    """Hovering hummingbird facing left."""
    s.group(f'translate({x} {y}) scale({k})')
    s.path('M-30,0 L-118,10 L-30,6Z', P['ink'])  # bill
    s.path('M-34,-4 C-30,-26 6,-30 22,-8 C44,4 70,10 96,34 C64,30 40,26 22,24 C0,30 -26,22 -34,-4Z', P['emerald'])
    s.path('M-30,4 C-20,22 2,26 16,20 C2,12 -12,8 -30,4Z', P['coral'])  # gorget
    s.path('M96,34 L130,26 L118,50Z', P['jungle'])  # tail
    s.circ(-16, -10, 4, P['ink']); s.circ(-17, -11, 1.2, P['white'])
    # wings as a fan of thin blades (motion)
    for i, a in enumerate((-120, -105, -90, -75)):
        r = math.radians(a)
        s.path(f'M10,-8 L{10 + 120*math.cos(r - .06):.1f},{-8 + 120*math.sin(r - .06):.1f} L{10 + 120*math.cos(r + .06):.1f},{-8 + 120*math.sin(r + .06):.1f}Z',
               P['cream'], opacity=f'{.95 - i*.18:.2f}')
    s.end()

def morpho(s, x, y, k=1.0, rot=0):
    """Blue morpho butterfly, wings open, seen from above."""
    s.group(f'translate({x} {y}) rotate({rot}) scale({k})')
    for sx in (-1, 1):
        s.path(f'M0,-6 C{sx*40},-80 {sx*120},-96 {sx*132},-50 C{sx*140},-10 {sx*90},6 0,6Z', P['ink'])
        s.path(f'M0,-4 C{sx*36},-66 {sx*104},-80 {sx*116},-46 C{sx*120},-16 {sx*80},0 0,4Z', P['morpho'])
        s.path(f'M0,6 C{sx*80},6 {sx*112},40 {sx*92},84 C{sx*70},104 {sx*24},80 0,14Z', P['ink'])
        s.path(f'M0,8 C{sx*70},10 {sx*98},40 {sx*82},74 C{sx*62},90 {sx*24},70 0,16Z', P['morpho'])
        for cx, cy in ((112, -52), (96, -36), (80, 64)): s.circ(sx*cx, cy, 4, P['white'])
    s.ell(0, 8, 6, 44, P['ink'])
    s.path('M-2,-34 C-10,-60 -20,-72 -28,-76 M2,-34 C10,-60 20,-72 28,-76', 'none', stroke=P['ink'], stroke_width=2.5, stroke_linecap='round')
    s.end()

def redeye_frog(s, x, y, k=1.0):
    """Red-eyed tree frog peeking over an edge at y (chin on the edge)."""
    s.group(f'translate({x} {y}) scale({k})')
    s.path('M-70,10 C-74,-40 -40,-70 0,-70 C40,-70 74,-40 70,10Z', P['lime'])
    for sx in (-1, 1):
        s.circ(sx*40, -58, 24, P['lime']); s.circ(sx*40, -58, 17, P['red']); s.ell(sx*40, -58, 4, 13, P['ink'])
        s.circ(sx*36, -64, 3, P['white'])
        # orange toes gripping the edge
        for i in range(4):
            s.circ(sx*(76 + i*14), 6 + (i % 2)*4, 8, P['orange'])
        s.path(f'M{sx*58},0 C{sx*70},-20 {sx*90},-6 {sx*112},4 L{sx*58},12Z', P['lime'])
        s.path(f'M{sx*60},-8 C{sx*72},-24 {sx*86},-12 {sx*96},-4', 'none', stroke=P['blue'], stroke_width=5)
    s.path('M-30,-24 Q0,-14 30,-24', 'none', stroke=P['jungle'], stroke_width=3, stroke_linecap='round')
    s.end()

def macaw(s, x, y, k=1.0, rot=0):
    """Scarlet macaw in flight, seen from below/side, heading left."""
    s.group(f'translate({x} {y}) rotate({rot}) scale({k})')
    s.path('M40,0 L230,-14 L234,0 L230,14Z', P['red'])          # long tail
    s.path('M90,0 L230,-6 L230,6Z', P['blue'])
    # wings: red -> yellow -> blue bands
    for sy in (-1, 1):
        s.path(f'M10,0 C20,{sy*-60} 60,{sy*-120} 110,{sy*-150} C90,{sy*-90} 70,{sy*-40} 50,0Z', P['red'])
        s.path(f'M30,{sy*-40} C50,{sy*-80} 80,{sy*-120} 110,{sy*-150} C96,{sy*-110} 84,{sy*-80} 70,{sy*-40}Z', P['yellow'])
        s.path(f'M60,{sy*-70} C80,{sy*-110} 96,{sy*-134} 110,{sy*-150} C104,{sy*-120} 96,{sy*-96} 86,{sy*-70}Z', P['blue'])
    s.path('M-40,0 C-30,-24 20,-26 60,-8 C70,0 70,0 60,8 C20,26 -30,24 -40,0Z', P['red'])
    s.circ(-34, -4, 14, P['white']); s.circ(-34, -4, 4, P['ink'])
    s.path('M-46,-8 C-66,-8 -70,10 -58,18 C-56,8 -50,4 -44,4Z', P['cream'])
    s.path('M-46,4 C-56,6 -58,14 -52,18 L-44,8Z', P['ink'])
    s.end()

def sloth(s, x, y, k=1.0):
    """Three-toed sloth hanging from a cable at y, belly up, face toward the viewer."""
    s.group(f'translate({x} {y}) scale({k})')
    fur, dark = P['sand'], P['brown']
    for sx in (-1, 1):
        s.path(f'M{sx*30},0 C{sx*34},20 {sx*40},40 {sx*44},60 L{sx*24},62 C{sx*22},40 {sx*18},20 {sx*14},0Z', fur)
        for i in range(3): s.path(f'M{sx*(14 + i*6)},0 q{sx*-2},-10 {sx*4},-14', 'none', stroke=dark, stroke_width=3, stroke_linecap='round')
    s.ell(0, 92, 62, 46, fur)
    s.circ(0, 70, 34, fur)
    s.ell(0, 72, 28, 22, P['cream'])
    for sx in (-1, 1):
        s.ell(sx*13, 68, 9, 6, dark, rot=sx*-20); s.circ(sx*12, 68, 3, P['ink'])
    s.ell(0, 80, 6, 4, P['ink'])
    s.path('M-8,88 Q0,94 8,88', 'none', stroke=dark, stroke_width=2.5, stroke_linecap='round')
    s.end()

def sombrero_top(s, x, y, r):
    """Panama 'sombrero pintao' seen from above: cream with black concentric bands."""
    s.circ(x + r*.12, y + r*.14, r, P['ink'], opacity='.18')      # hard shadow
    for i, (rr, c) in enumerate(((1, P['cream']), (.86, P['ink']), (.8, P['cream']), (.7, P['ink']), (.64, P['cream']),
                                 (.5, P['ink']), (.44, P['cream']), (.3, P['ink']), (.24, P['cream']))):
        s.circ(x, y, r*rr, c)

def coffee_bag(s, x, y, w, f=P['kraft']):
    h = w*1.3
    s.path(f'M{x - w/2},{y} L{x - w*.46},{y - h} L{x + w*.46},{y - h} L{x + w/2},{y}Z', f)
    s.rect(x - w*.46, y - h - w*.1, w*.92, w*.12, P['sand'])
    s.circ(x, y - h*.48, w*.2, P['cream'])
    cherries(s, x - w*.07, y - h*.52, w*.05, n=3, f=P['red'])
    leaf(s, x - w*.02, y - h*.56, w*.12, -130, P['emerald']); leaf(s, x + w*.02, y - h*.56, w*.12, -50, P['jungle'])

# ---------- scenes ----------
def hero():
    s = S(1600, 700, P['coral'])
    s.circ(1050, 360, 230, P['gold'])
    # canal: navy water with op-art reflection stripes
    s.rect(0, 470, 1600, 230, P['navy'])
    for i in range(9):
        y = 486 + i*24; w = 300 - i*18
        s.rect(1050 - w/2, y, w, 6 + i*.6, P['gold'], opacity=f'{.85 - i*.07:.2f}')
    # far shore and a ship on the horizon
    s.path('M640,470 C760,446 860,452 960,470Z', P['jungle'])
    s.path('M1250,470 C1340,440 1480,436 1600,452 L1600,470Z', P['jungle'])
    s.path('M820,470 L1010,470 L996,486 L834,486Z', P['ink'])
    for i, c in enumerate((P['cream'], P['red'], P['cream'], P['gold'], P['cream'], P['red'])):
        s.rect(846 + i*22, 448, 20, 22, c)
    s.rect(978, 432, 18, 38, P['cream'])
    # big monstera / jungle mass on the left: the quiet field behind the headline
    s.path('M0,0 L680,0 C740,120 720,260 640,360 C580,440 540,560 500,700 L0,700Z', P['jungle'])
    for i in range(6):
        leaf(s, 640 + i*8 - max(0, i - 3)*40, 120 + i*90, 170 - i*6, 10 + i*14, P['emerald'], vein=P['jungle'])
    # coffee branch from the right edge with leaves and cherries
    s.path('M1600,560 C1460,548 1330,560 1180,600 L1184,612 C1330,576 1460,566 1600,578Z', P['brown'])
    for x, a, L in ((1560, -120, 120), (1500, 70, 110), (1430, -110, 130), (1360, 80, 100), (1300, -130, 110), (1230, 60, 90)):
        leaf(s, x, 566 + (1560 - x)*.06, L, a, P['emerald'] if a < 0 else P['jungle'], vein=P['lime'])
    cherries(s, 1470, 586, 13, n=6, f=P['red'], hi=P['coral'])
    cherries(s, 1290, 612, 12, n=5, f=P['red'], hi=P['coral'])
    toucan(s, 1290, 368, k=.95)
    return s.svg('Ilustración: un tucán pico iris sobre una rama de café frente a un gran sol y el Canal de Panamá con un barco')

def vivero():
    s = S(400, 276, P['cream'])
    # seedlings in rows, seen from above
    for r in range(3):
        for c in range(6):
            x, y = 34 + c*66 + (r % 2)*33, 40 + r*62
            if x > 390: continue
            s.circ(x + 5, y + 6, 20, P['sand'])
            s.circ(x, y, 20, P['ink'])
            leaf(s, x, y, 26, -150 + c*9, P['emerald']); leaf(s, x, y, 26, 30 + c*9, P['lime'])
    s.rect(0, 210, 400, 66, P['emerald'])
    golden_frog(s, 300, 200, k=.95)
    return s.svg('Ilustración: una rana dorada de Panamá entre plantones de café vistos desde arriba')

def cosecha():
    s = S(400, 276, P['navy'])
    s.circ(330, 70, 46, P['gold'])
    s.path('M-10,240 C90,200 200,170 410,150 L410,158 C200,180 90,210 -6,250Z', P['brown'])
    for x, a, L in ((40, -120, 80), (80, 50, 70), (140, -110, 90), (190, 70, 70), (250, -120, 80), (310, 60, 64), (360, -100, 70)):
        leaf(s, x, 236 - x*.22, L, a, P['emerald'] if a < 0 else P['jungle'], vein=P['lime'])
    cherries(s, 112, 218, 10, n=6, hi=P['coral']); cherries(s, 230, 196, 10, n=5, hi=P['coral']); cherries(s, 330, 178, 9, n=4, hi=P['coral'])
    hummingbird(s, 250, 104, k=1.25)
    return s.svg('Ilustración: un colibrí junto a una rama de café con cerezas rojas, de noche con luna dorada')

def proceso():
    s = S(400, 276, P['gold'])
    # roasting drum as op-art rings of beans
    s.circ(214, 150, 150, P['ink'], opacity='.15')
    rings(s, 200, 138, 150, 12, P['brown'], P['cream'])
    for i in range(14):
        a = math.radians(i*360/14)
        s.ell(200 + 70*math.cos(a), 138 + 70*math.sin(a), 9, 6, P['ink'], rot=i*360/14)
    s.circ(200, 138, 22, P['ink'])
    morpho(s, 120, 70, k=.62, rot=-18)
    return s.svg('Ilustración: una mariposa morfo azul sobre un tambor de tostado de café dibujado como anillos')

def empaque():
    s = S(400, 276, P['coral'])
    s.path('M0,276 L0,210 L400,150 L400,276Z', P['red'], opacity='.35')    # hard shadow plane
    coffee_bag(s, 200, 276, 170, f=P['kraft'])
    redeye_frog(s, 200, 54, k=.62)
    return s.svg('Ilustración: una rana de ojos rojos asomándose sobre una bolsa de Café del Canal')

def productores():
    s = S(764, 361, P['emerald'])
    # coffee leaves pattern seen from above
    for r in range(5):
        for c in range(10):
            x, y = c*84 + (r % 2)*42, r*84 + 10
            leaf(s, x, y, 70, 35 + (c*37 + r*53) % 100, P['jungle'] if (r + c) % 2 else P['lime'], vein=None)
            if (r*3 + c) % 4 == 0: cherries(s, x + 20, y + 30, 8, n=5)
    # three farmers from above: shoulders + sombrero, with a basket of cherries
    for x, y, shirt in ((200, 190, P['cream']), (390, 230, P['coral']), (560, 170, P['white'])):
        s.ell(x + 10, y + 12, 78, 46, P['ink'], opacity='.2')
        s.ell(x, y, 74, 40, shirt)
        sombrero_top(s, x, y - 6, 56)
    s.circ(470, 290, 34, P['kraft']); cherries(s, 452, 274, 10, n=6, hi=P['coral'])
    macaw(s, 620, 70, k=.55, rot=-12)
    return s.svg('Ilustración: tres productores vistos desde arriba con sombreros pintaos entre cafetales y una guacamaya volando')

def distribuidores():
    s = S(764, 361, P['navy'])
    # sidewalks and a zebra crossing (op-art stripes)
    s.rect(0, 0, 764, 70, P['sand']); s.rect(0, 300, 764, 61, P['sand'])
    s.rect(0, 70, 764, 6, P['cream']); s.rect(0, 294, 764, 6, P['cream'])
    for i in range(10): s.rect(470, 86 + i*21, 120, 11, P['cream'])
    for i in range(7): s.rect(40 + i*60, 182, 30, 6, P['gold'])
    # taxi from above with a long hard shadow
    tx, ty = 150, 210
    s.rect(tx + 14, ty - 38, 210, 98, P['ink'], rx=26, opacity='.3')
    s.rect(tx, ty - 50, 210, 96, P['yellow'], rx=24)
    s.rect(tx + 48, ty - 38, 46, 72, P['sky'], rx=8); s.rect(tx + 132, ty - 38, 36, 72, P['sky'], rx=8)
    s.rect(tx + 96, ty - 40, 34, 76, P['yellow'])
    s.rect(tx + 102, ty - 12, 22, 20, P['ink'], rx=3)
    for i in range(10): s.rect(tx + 6 + i*20, ty + 30, 10, 8, P['ink'])
    # person in a wheelchair carrying a box, from above
    wx, wy = 530, 236
    s.rect(wx - 38, wy - 46, 76, 64, P['ink'], rx=10)
    s.rect(wx - 46, wy - 40, 10, 54, P['sky'], rx=4); s.rect(wx + 36, wy - 40, 10, 54, P['sky'], rx=4)
    s.ell(wx, wy - 20, 30, 20, P['coral']); s.circ(wx, wy - 22, 16, P['brown'])
    s.rect(wx - 22, wy - 4, 44, 26, P['kraft'], rx=3); cherries(s, wx - 6, wy + 4, 4, n=3)
    # cable and sloth
    s.path('M0,40 Q382,120 764,30', 'none', stroke=P['ink'], stroke_width=5)
    sloth(s, 300, 84, k=.9)
    return s.svg('Ilustración: una calle vista desde arriba con un taxi amarillo, una persona en silla de ruedas con una caja de café y un perezoso colgado del cable')

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'img', 'v5')
    os.makedirs(out, exist_ok=True)
    for name, fn in (('hero', hero), ('vivero', vivero), ('cosecha', cosecha), ('proceso', proceso),
                     ('empaque', empaque), ('productores', productores), ('distribuidores', distribuidores)):
        open(os.path.join(out, name + '.svg'), 'w').write(fn())
        print(name)
