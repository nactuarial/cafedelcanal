# Flat infographic-style illustrations for the site (no outlines, pastel palette,
# geometric people). Writes SVG files to img/ilustra/.
#   python3 tools/ilustra.py
import math, os

C = dict(
    sky='#a9d6de', sky2='#8fc9d9', teal='#5ba3a6', teal2='#3e7c82', teal3='#2f5f66', navy='#2f4858',
    mint='#9ed3b5', green='#6db37d', green2='#4f9a63', grass='#88c057', leaf='#3f8a5a', leaf2='#2f6e48',
    mustard='#e8c35a', yellow='#f2d06b', salmon='#f4b7a0', pink='#f6c9b8', red='#e2553b', cherry='#c8352b',
    orange='#f08a4b', brown='#8b5a3c', brown2='#6b4430', dbrown='#4a3328', cream='#f7efdf', kraft='#d9b98c',
    kraft2='#c9a674', lav='#b9b3cf', gray='#a7aeb3', gray2='#7d878d', steel='#c5ccd0', white='#fbf8f1',
    skin1='#e9b48f', skin2='#c98b62', skin3='#a86b48', hair='#2b211c',
)

class S:
    def __init__(s, w, h, bg=None):
        s.w, s.h, s.o = w, h, []
        if bg: s.rect(0, 0, w, h, bg)
    def add(s, x): s.o.append(x); return s
    def rect(s, x, y, w, h, f, rx=0, **k): return s.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{f}"{at(k)}/>')
    def circ(s, x, y, r, f, **k): return s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{f}"{at(k)}/>')
    def ell(s, x, y, rx, ry, f, rot=0, **k): return s.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{f}" transform="rotate({rot:.1f} {x:.1f} {y:.1f})"{at(k)}/>')
    def poly(s, pts, f, **k): return s.add(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{f}"{at(k)}/>')
    def path(s, d, f, **k): return s.add(f'<path d="{d}" fill="{f}"{at(k)}/>')
    def line(s, x1, y1, x2, y2, c, w=2, **k): return s.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"{at(k)}/>')
    def svg(s, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s.w} {s.h}" preserveAspectRatio="xMidYMid slice" role="img">'
                f'<title>{title}</title>' + ''.join(s.o) + '</svg>\n')

def at(k): return ''.join(f' {a.replace("_", "-")}="{v}"' for a, v in k.items())

# ---------- building blocks ----------
def zig(s, x0, x1, y, h, f, step=14, up=True):
    """Row of small triangles (grass / torn edge) sitting on y."""
    pts, x = [(x0, y)], x0
    while x < x1:
        pts += [(x + step/2, y - h if up else y + h), (min(x + step, x1), y)]
        x += step
    s.poly(pts + [(x1, y + (2 if up else -2)), (x0, y + (2 if up else -2))], f)

def scallop(s, x0, x1, y, r, f):
    d, x = f'M{x0},{y + r} ', x0
    while x < x1:
        d += f'A{r},{r} 0 0 1 {x + 2*r},{y + r} '
        x += 2*r
    s.path(d + f'L{x1},{y + r + 2} L{x0},{y + r + 2}Z', f)

def hill(s, pts, base, f):
    d = f'M{pts[0][0]},{base} L{pts[0][0]},{pts[0][1]} '
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx = (x0 + x1)/2
        d += f'C{mx},{y0} {mx},{y1} {x1},{y1} '
    s.path(d + f'L{pts[-1][0]},{base}Z', f)

def tree(s, x, y, h, f, trunk='#6b4430', kind='round'):
    s.rect(x - h*.04, y - h*.35, h*.08, h*.35, trunk)
    if kind == 'round':
        s.ell(x, y - h*.62, h*.26, h*.34, f)
    else:
        s.poly([(x - h*.24, y - h*.3), (x, y - h), (x + h*.24, y - h*.3)], f)

def coffee_bush(s, x, y, h, leaf=C['leaf'], leaf2=C['leaf2'], cherries=True, seed=0):
    s.rect(x - 2, y - h*.9, 4, h*.9, C['brown2'])
    n = 6
    for i in range(n):
        yy = y - h*(.18 + .13*i)
        span = h*(.42 - .045*i)
        for side in (-1, 1):
            s.ell(x + side*span*.55, yy, span*.5, span*.2, leaf if (i + side) % 2 else leaf2, rot=side*(18 + 4*i))
        if cherries and i in (1, 2, 4):
            for j, dx in enumerate((-.35, -.2, .25, .4)):
                if (i + j + seed) % 3 == 0: continue
                s.circ(x + dx*span, yy + h*.05, h*.035, C['cherry'] if (j + seed) % 2 else C['red'])
    s.ell(x, y - h*.95, h*.09, h*.05, leaf2)

def seedling(s, x, y, h, bag=C['dbrown']):
    s.poly([(x - h*.32, y - h*.42), (x + h*.32, y - h*.42), (x + h*.27, y), (x - h*.27, y)], bag)
    s.rect(x - 1.5, y - h, 3, h*.6, C['green2'])
    for i, (dy, sp) in enumerate(((.95, .3), (.78, .36), (.62, .3))):
        s.ell(x - h*sp*.55, y - h*dy, h*sp*.55, h*.1, C['green'] if i % 2 else C['leaf'], rot=-20)
        s.ell(x + h*sp*.55, y - h*dy, h*sp*.55, h*.1, C['leaf'] if i % 2 else C['green'], rot=20)

def person(s, x, y, h, skin, shirt, pants, hair=C['hair'], hat=None, apron=None, arms='down', long_hair=False, cap=None, face=1):
    """Flat standing figure, feet at (x, y), total height h. face: 1 right, -1 left, 0 front."""
    u = h/10
    # legs
    s.rect(x - u*.75, y - u*4.2, u*.65, u*4.0, pants, rx=u*.2)
    s.rect(x + u*.1, y - u*4.2, u*.65, u*4.0, pants, rx=u*.2)
    s.ell(x - u*.45 + face*u*.2, y - u*.15, u*.55, u*.25, C['dbrown'])
    s.ell(x + u*.45 + face*u*.2, y - u*.15, u*.55, u*.25, C['dbrown'])
    # body
    s.path(f'M{x - u*1.2},{y - u*4} L{x - u*1.05},{y - u*7.1} Q{x},{y - u*7.6} {x + u*1.05},{y - u*7.1} L{x + u*1.2},{y - u*4} Z', shirt)
    if apron: s.rect(x - u*.9, y - u*6, u*1.8, u*2.6, apron, rx=u*.15)
    # arms
    if arms == 'down':
        for side in (-1, 1):
            s.rect(x + side*u*1.15 - u*.3, y - u*7, u*.6, u*2.9, shirt, rx=u*.3)
            s.circ(x + side*u*1.15, y - u*4, u*.36, skin)
    elif arms == 'front':
        s.rect(x - u*1.45, y - u*7, u*.6, u*2.2, shirt, rx=u*.3)
        s.circ(x - u*1.15, y - u*4.9, u*.36, skin)
        s.add(f'<rect x="{x + u*.6:.1f}" y="{y - u*7:.1f}" width="{u*.6:.1f}" height="{u*2.6:.1f}" rx="{u*.3:.1f}" fill="{shirt}" transform="rotate(-55 {x + u*.9:.1f} {y - u*6.8:.1f})"/>')
        s.circ(x + u*3.0, y - u*5.6, u*.36, skin)
    # neck + head
    s.rect(x - u*.25, y - u*7.6, u*.5, u*.5, skin)
    hx, hy = x + face*u*.1, y - u*8.35
    if long_hair:
        if face: s.ell(hx - face*u*.75, hy + u*.45, u*.42, u*.95, hair)
        else:
            for side in (-1, 1): s.ell(hx + side*u*.72, hy + u*.35, u*.32, u*.85, hair)
    s.circ(hx, hy, u*.85, skin)
    s.path(f'M{hx - u*.85},{hy} A{u*.85},{u*.85} 0 0 1 {hx + u*.85},{hy} Q{hx},{hy - u*.35} {hx - u*.85},{hy}Z', hair)
    if face: s.circ(hx + face*u*.42, hy + u*.08, u*.09, C['hair'])
    else:
        s.circ(hx - u*.3, hy + u*.08, u*.09, C['hair']); s.circ(hx + u*.3, hy + u*.08, u*.09, C['hair'])
    if face: s.path(f'M{hx + face*u*.15},{hy + u*.4} q{face*u*.25},{u*.15} {face*u*.45},{-u*.05}', 'none', stroke=C['skin3'], stroke_width=u*.09, stroke_linecap='round')
    if hat:
        s.ell(hx, hy - u*.45, u*1.6, u*.32, hat)
        s.path(f'M{hx - u*.8},{hy - u*.45} Q{hx - u*.75},{hy - u*1.55} {hx},{hy - u*1.6} Q{hx + u*.75},{hy - u*1.55} {hx + u*.8},{hy - u*.45}Z', hat)
        s.rect(hx - u*.8, hy - u*.8, u*1.6, u*.22, C['dbrown'])
    if cap:
        s.path(f'M{hx - u*.88},{hy - u*.1} A{u*.9},{u*.9} 0 0 1 {hx + u*.88},{hy - u*.1}Z', cap)
        s.ell(hx + face*u*.9, hy - u*.12, u*.7, u*.16, cap)

def basket(s, x, y, w, f=C['kraft2'], full=True):
    if full:
        for i in range(6):
            s.circ(x - w*.3 + i*w*.12, y - w*.05 - (i % 2)*w*.05, w*.09, C['cherry'] if i % 2 else C['red'])
    s.path(f'M{x - w/2},{y - w*.08} L{x + w/2},{y - w*.08} L{x + w*.38},{y + w*.42} L{x - w*.38},{y + w*.42}Z', f)
    for i in range(3): s.rect(x - w*.42, y + w*(.02 + i*.13), w*.84, w*.03, C['brown'], opacity='.35')

def coffee_bag(s, x, y, w, f=C['kraft']):
    h = w*1.35
    s.path(f'M{x - w/2},{y} L{x - w*.44},{y - h} L{x + w*.44},{y - h} L{x + w/2},{y} Z', f)
    s.rect(x - w*.44, y - h - w*.12, w*.88, w*.14, C['kraft2'])
    s.rect(x - w*.3, y - h*.68, w*.6, w*.55, C['white'], rx=w*.04)
    for dx, dy, c in ((-.08, .02, C['cherry']), (.08, .02, C['red']), (0, .14, C['cherry'])):
        s.circ(x + dx*w, y - h*.42 + dy*w - w*.05, w*.065, c)
    s.ell(x - w*.08, y - h*.58, w*.1, w*.04, C['leaf'], rot=-30)
    s.ell(x + w*.08, y - h*.58, w*.1, w*.04, C['leaf2'], rot=30)

def wheel(s, x, y, r):
    s.circ(x, y, r, C['navy']); s.circ(x, y, r*.55, C['gray']); s.circ(x, y, r*.2, C['navy'])

def sun_rays(s, x, y, r, f):
    s.circ(x, y, r, f)

def dots(s, x, y, n, gap, f, r=3, vertical=True):
    for i in range(n): s.circ(x if vertical else x + i*gap, y + i*gap if vertical else y, r, f)

# ---------- scenes ----------
def hero():
    s = S(1600, 640, C['sky'])
    s.circ(1170, 150, 70, C['yellow'])
    dots(s, 1170, 250, 0, 0, C['white'])
    for cx, cy in ((300, 120), (820, 90), (1420, 120)):
        s.ell(cx, cy, 70, 18, C['white'], opacity='.75'); s.ell(cx + 40, cy - 12, 40, 16, C['white'], opacity='.75')
    hill(s, [(0, 300), (260, 230), (560, 270), (860, 210), (1180, 260), (1440, 220), (1600, 250)], 640, '#8cc0ba')
    hill(s, [(0, 330), (300, 290), (640, 320), (980, 280), (1300, 310), (1600, 285)], 640, C['teal'])
    # canal
    s.path('M0,370 C300,350 520,395 800,372 C1080,350 1300,385 1600,365 L1600,430 C1300,445 1080,415 800,438 C520,458 300,420 0,440Z', C['sky2'])
    for i in range(9): s.rect(150 + i*160, 395 + (i % 2)*12, 60, 4, C['white'], rx=2, opacity='.7')
    # container ship
    sx, sy = 930, 392
    s.path(f'M{sx - 210},{sy - 26} L{sx + 220},{sy - 26} L{sx + 190},{sy + 14} L{sx - 190},{sy + 14}Z', C['navy'])
    s.rect(sx - 210, sy - 30, 430, 6, C['red'])
    cols = [C['red'], C['orange'], C['teal2'], C['mustard'], C['salmon'], C['teal'], C['red'], C['mustard']]
    for i in range(8):
        for j in range(2):
            s.rect(sx - 170 + i*40, sy - 56 - j*24, 36, 22, cols[(i + j*3) % 8], rx=2)
    s.rect(sx + 160, sy - 92, 40, 62, C['white']); s.rect(sx + 166, sy - 84, 28, 8, C['navy'])
    s.rect(sx + 175, sy - 112, 10, 20, C['red'])
    # tug
    s.path('M560,402 L640,402 L630,420 L570,420Z', C['red']); s.rect(585, 388, 26, 14, C['white'])
    # near hills: dark on the left, behind the headline
    hill(s, [(0, 360), (220, 330), (520, 400), (760, 470)], 640, C['teal2'])
    hill(s, [(820, 470), (1100, 420), (1600, 400)], 640, C['green'])
    for x in range(40, 700, 70): tree(s, x, 470 + (x % 3)*12, 70 + (x % 4)*10, C['teal3'] if x % 140 else '#356e6f', kind='round' if x % 3 else 'cone')
    # coffee rows on the right slope
    s.path('M700,640 L760,500 C900,460 1200,440 1600,430 L1600,640Z', C['grass'])
    zig(s, 760, 1600, 470, 10, C['green2'], step=16)
    for row, (yb, sc) in enumerate(((520, 46), (575, 58), (640, 74))):
        for i in range(12):
            x = 800 + i*70 + (row % 2)*35
            if x > 1580: continue
            coffee_bush(s, x, yb, sc, seed=i + row)
    # farmer with a sombrero pintao, looking at the canal
    fx, fy = 1360, 640
    person(s, fx, fy + 60, 300, C['skin2'], C['white'], C['navy'], hat=C['cream'], face=-1)
    u, hx = 30, fx - 3
    for i in range(6): s.rect(hx - 22 + i*8, 449.5 - u*.8 - 3, 4, 13, C['dbrown'])
    basket(s, fx + 70, fy - 128, 70)
    zig(s, 0, 1600, 640, 12, C['cream'], step=24)
    return s.svg('Ilustración: el Canal de Panamá con un barco, colinas verdes, cafetales y un caficultor con sombrero')

def vivero():
    s = S(400, 276, C['mint'])
    s.rect(0, 0, 400, 60, '#b6dfc8')
    for i in range(9): s.line(20 + i*45, 0, 20 + i*45, 60, C['green2'], 1.2, opacity='.35')
    s.rect(0, 58, 400, 6, C['green2'])
    s.rect(0, 200, 400, 76, C['brown'])
    zig(s, 0, 400, 200, 7, C['brown'], step=12)
    for row, (yb, h) in enumerate(((150, 40), (178, 46), (212, 54))):
        for i in range(9):
            x = 22 + i*46 + (row % 2)*20
            if x < 395: seedling(s, x, yb, h)
    person(s, 300, 270, 190, C['skin2'], C['orange'], C['navy'], cap=C['teal2'], arms='front', face=-1)
    seedling(s, 255, 214, 50, bag=C['dbrown'])
    s.circ(350, 34, 16, C['yellow'])
    dots(s, 40, 80, 4, 12, C['white'], r=2.5)
    return s.svg('Ilustración: vivero con plantones de café en bolsas y un trabajador sembrando')

def cosecha():
    s = S(400, 276, C['mustard'])
    s.circ(330, 60, 34, C['yellow'])
    hill(s, [(0, 170), (140, 140), (300, 170), (400, 150)], 276, C['green'])
    for i in range(6): coffee_bush(s, 20 + i*75, 236, 120, seed=i)
    s.rect(0, 236, 400, 40, C['green2'])
    zig(s, 0, 400, 236, 7, C['green2'], step=12)
    person(s, 205, 276, 200, C['skin3'], C['red'], C['teal2'], long_hair=True, cap=C['navy'], arms='front', face=1)
    basket(s, 160, 196, 62)
    for i, (x, y) in enumerate(((330, 140), (345, 152), (338, 128), (355, 138))):
        s.circ(x, y, 7, C['cherry'] if i % 2 else C['red'])
    return s.svg('Ilustración: caficultora cosechando cerezas rojas de café en un cafetal')

def proceso():
    s = S(400, 276, C['salmon'])
    s.rect(0, 220, 400, 56, C['pink'])
    # roaster
    s.rect(110, 150, 170, 70, C['gray2'], rx=6)
    s.circ(195, 120, 70, C['steel']); s.circ(195, 120, 52, C['gray']); s.circ(195, 120, 22, C['steel'])
    for a in range(0, 360, 45):
        r = math.radians(a); s.line(195 + 26*math.cos(r), 120 + 26*math.sin(r), 195 + 48*math.cos(r), 120 + 48*math.sin(r), C['gray2'], 4)
    s.poly([(165, 18), (225, 18), (210, 52), (180, 52)], C['red'])
    s.rect(180, 52, 30, 14, C['gray2'])
    # cooling tray with beans
    s.ell(320, 214, 66, 16, C['gray2']); s.ell(320, 208, 62, 13, C['steel'])
    for i in range(22):
        s.ell(272 + (i*17) % 96, 204 + (i*7) % 10, 4.5, 3, C['dbrown'] if i % 3 else C['brown'], rot=(i*40) % 180)
    for i in range(8): s.ell(262 - i*3, 150 + i*7, 4, 2.6, C['dbrown'], rot=30 + i*20)
    s.poly([(255, 140), (275, 140), (268, 152)], C['gray2'])
    # gears
    for gx, gy, r, c in ((60, 70, 26, C['teal2']), (95, 40, 16, C['mustard'])):
        for a in range(0, 360, 45):
            rr = math.radians(a); s.circ(gx + r*math.cos(rr), gy + r*math.sin(rr), r*.24, c)
        s.circ(gx, gy, r, c); s.circ(gx, gy, r*.38, C['salmon'])
    dots(s, 360, 30, 5, 14, C['white'], r=3)
    s.rect(30, 236, 70, 6, C['white'], opacity='.6'); s.rect(300, 248, 60, 6, C['white'], opacity='.6')
    return s.svg('Ilustración: tostadora de café con granos tostados enfriándose y engranajes')

def empaque():
    s = S(400, 276, C['sky'])
    s.rect(0, 0, 400, 70, C['lav'])
    for i in range(5): s.rect(30 + i*75, 18, 44, 34, C['white'], rx=3, opacity='.55')
    # conveyor
    s.rect(0, 200, 400, 18, C['navy'], rx=9)
    for i in range(10): wheel(s, 20 + i*40, 209, 7)
    s.rect(0, 218, 400, 58, C['sky2'])
    for i, x in enumerate((60, 150, 240, 330)):
        coffee_bag(s, x, 200, 62 if i != 2 else 70, f=C['kraft'] if i % 2 else C['kraft2'])
    # filler nozzle
    s.rect(225, 70, 30, 40, C['gray2']); s.poly([(225, 110), (255, 110), (244, 124), (236, 124)], C['gray2'])
    dots(s, 240, 128, 3, 9, C['dbrown'], r=2.5)
    s.circ(370, 100, 18, C['yellow']); s.rect(362, 92, 16, 16, C['red'], rx=2)
    return s.svg('Ilustración: bolsas kraft de Café del Canal avanzando por una banda de empaque')

def productores():
    s = S(764, 361, C['teal'])
    hill(s, [(0, 160), (200, 120), (420, 160), (620, 110), (764, 140)], 361, C['green'])
    scallop(s, 0, 764, 0, 12, C['teal2'])
    s.circ(660, 60, 30, C['yellow'])
    for i in range(10): coffee_bush(s, 30 + i*80, 250, 150, seed=i)
    people = (
        (190, C['skin2'], C['white'], C['navy'], dict(hat=C['cream'], face=1)),
        (380, C['skin3'], C['red'], C['teal3'], dict(long_hair=True, cap=C['navy'], face=0, arms='front')),
        (580, C['skin2'], C['sky2'], C['navy'], dict(cap=C['navy'], face=-1)),
    )
    for x, sk, sh, pa, kw in people: person(s, x, 361 + 20, 300, sk, sh, pa, **kw)
    basket(s, 420, 250, 80)
    s.rect(0, 300, 764, 61, C['leaf'])
    zig(s, 0, 764, 300, 10, C['leaf'], step=16)
    for i in range(8): coffee_bush(s, 20 + i*105, 361, 90, leaf=C['green'], leaf2=C['green2'], seed=i + 3)
    return s.svg('Ilustración: tres productores de café sonrientes entre los cafetales, con una canasta de cerezas')

def distribuidores():
    s = S(764, 361, C['sky'])
    # buildings
    for i, (x, w, h, c) in enumerate(((0, 120, 210, C['lav']), (130, 90, 250, C['salmon']), (230, 140, 190, C['mint']), (520, 110, 240, C['pink']), (640, 124, 200, C['lav']))):
        s.rect(x, 300 - h, w, h, c)
        for r in range(int(h/45)):
            for q in range(int(w/38)):
                s.rect(x + 14 + q*38, 300 - h + 18 + r*45, 20, 26, C['white'], opacity='.7')
    tree(s, 440, 300, 140, C['green']); tree(s, 490, 300, 110, C['green2'])
    s.rect(0, 300, 764, 61, C['gray2'])
    for i in range(8): s.rect(20 + i*100, 330, 50, 6, C['white'], opacity='.8')
    s.rect(0, 296, 764, 8, C['steel'])
    # taxi
    tx = 40
    s.path(f'M{tx},{318} L{tx},{268} Q{tx + 4},{252} {tx + 30},{250} L{tx + 80},{218} L{tx + 200},{218} L{tx + 250},{252} Q{tx + 290},{256} {tx + 292},{278} L{tx + 292},{318}Z', C['mustard'])
    s.path(f'M{tx + 90},{228} L{tx + 140},{228} L{tx + 140},{256} L{tx + 66},{256}Z', C['sky2'])
    s.path(f'M{tx + 150},{228} L{tx + 196},{228} L{tx + 232},{256} L{tx + 150},{256}Z', C['sky2'])
    for i in range(12): s.rect(tx + 20 + i*20, 284 + (i % 2)*8, 10, 8, C['navy'])
    s.rect(tx + 120, 206, 44, 12, C['white'], rx=3)
    wheel(s, tx + 62, 318, 24); wheel(s, tx + 232, 318, 24)
    # driver in the window, thumbs up
    s.circ(tx + 116, 238, 13, C['skin2']); s.path(f'M{tx + 103},{236} A13,13 0 0 1 {tx + 129},{236}Z', C['hair'])
    s.circ(tx + 140, 248, 7, C['skin2']); s.rect(tx + 138, 236, 5, 10, C['skin2'], rx=2)
    # person in wheelchair holding a box of coffee
    wx = 430
    wheel(s, wx, 330, 30); s.circ(wx, 330, 22, C['gray'])
    s.rect(wx - 34, 270, 60, 12, C['navy'], rx=4); s.rect(wx - 40, 230, 10, 50, C['navy'], rx=4)
    wheel(s, wx + 40, 348, 9)
    s.rect(wx - 20, 270, 50, 14, C['navy']); s.rect(wx + 22, 270, 14, 60, C['navy'], rx=6)
    s.path(f'M{wx - 32},{278} L{wx - 28},{205} Q{wx - 4},{195} {wx + 14},{205} L{wx + 14},{278}Z', C['teal2'])
    s.rect(wx - 14, 186, 10, 12, C['skin2']); s.circ(wx - 9, 172, 20, C['skin2'])
    s.path(f'M{wx - 29},{172} A20,20 0 0 1 {wx + 11},{172} Q{wx - 9},{164} {wx - 29},{172}Z', C['hair'])
    s.circ(wx + 1, 172, 2.2, C['hair'])
    s.rect(wx + 4, 222, 62, 46, C['kraft'], rx=3)
    s.circ(wx + 30, 248, 6, C['cherry']); s.circ(wx + 40, 248, 6, C['red']); s.circ(wx + 35, 257, 6, C['cherry'])
    s.ell(wx + 30, 236, 8, 3.5, C['leaf'], rot=-30); s.ell(wx + 40, 236, 8, 3.5, C['leaf2'], rot=30)
    s.circ(wx + 4, 244, 7, C['skin2']); s.circ(wx + 66, 244, 7, C['skin2'])
    # older man with a white cane
    person(s, 640, 361, 260, C['skin2'], C['white'], C['navy'], hair=C['gray'], face=-1)
    hy = 361 - 26*8.35
    s.rect(637.4 - 24, hy - 5, 24, 9, C['navy'], rx=4)
    s.line(670, 257, 684, 358, C['white'], 5); s.line(680, 330, 684, 358, C['red'], 5)
    return s.svg('Ilustración: un taxista, una persona en silla de ruedas con una caja de Café del Canal y un señor con bastón en la calle')

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'img', 'ilustra')
    os.makedirs(out, exist_ok=True)
    for name, fn in (('hero-canal', hero), ('proceso-vivero', vivero), ('proceso-cosecha', cosecha), ('proceso-tostado', proceso),
                     ('proceso-empaque', empaque), ('red-productores', productores), ('red-distribuidores', distribuidores)):
        open(os.path.join(out, name + '.svg'), 'w').write(fn())
        print(name)
