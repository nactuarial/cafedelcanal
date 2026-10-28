# Street-stencil illustrations in the style of Banksy: flat black silhouettes sprayed on a concrete
# wall, a single red accent, overspray haze and paint drips. Writes SVG files to img/v7/.
#   python3 tools/banksy.py
import math, os, random

INK, RED, WALL = '#151413', '#d42a20', '#d3cec5'

class S:
    def __init__(s, w, h, seed=1):
        s.w, s.h, s.o = w, h, []
        s.r = random.Random(seed)
    def add(s, x): s.o.append(x)
    def p(s, d, fill=INK, **k): s.add(f'<path d="{d}" fill="{fill}"{at(k)}/>')
    def limb(s, pts, w, col=INK):
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        s.add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    def curve(s, pts, w, col=INK): s.add(f'<path d="{catmull(pts)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
    def blob(s, pts, col=INK): s.p(catmull(pts, True), col)
    def circ(s, x, y, r, col=INK): s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/>')
    def ell(s, x, y, rx, ry, rot=0, col=INK):
        s.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" transform="rotate({rot:.1f} {x:.1f} {y:.1f})" fill="{col}"/>')
    def rect(s, x, y, w, h, col=INK, rot=0, cx=None, cy=None):
        t = f' transform="rotate({rot} {cx} {cy})"' if rot else ''
        s.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}"{t}/>')
    def drip(s, x, y, n=None, col=INK):
        """Run of paint from the bottom edge of a shape at (x, y)."""
        n = n if n is not None else s.r.uniform(12, 46)
        w = s.r.uniform(1.6, 3.2)
        s.add(f'<path d="M{x - w:.1f},{y - 2:.1f} L{x - w*.7:.1f},{y + n:.1f} A{w*.9:.1f},{w*1.1:.1f} 0 1 0 {x + w*.7:.1f},{y + n:.1f} L{x + w:.1f},{y - 2:.1f} Z" fill="{col}"/>')
    def text(s, x, y, txt, size, col=INK, anchor='start', rot=0, ls=2):
        """Stencil lettering: heavy sans with the bridges a cut stencil leaves."""
        t = f' transform="rotate({rot} {x} {y})"' if rot else ''
        s.add(f'<g{t}><text x="{x}" y="{y}" font-family="Impact,\'Arial Black\',\'Helvetica Neue\',sans-serif" font-weight="900" '
              f'font-size="{size}" letter-spacing="{ls}" text-anchor="{anchor}" fill="{col}" filter="url(#rough)">{txt}</text>'
              f'<rect x="{x - (len(txt)*size*.62 if anchor == "end" else len(txt)*size*.31 if anchor == "middle" else 0):.0f}" y="{y - size*.42:.1f}" '
              f'width="{len(txt)*size*.62:.0f}" height="{max(1.5, size*.06):.1f}" fill="{WALL}" opacity=".9"/></g>')
    def svg(s, title):
        w, h = s.w, s.h
        defs = (f'<defs>'
                # concrete: fine grit plus large damp stains
                f'<filter id="grit" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="{s.r.randint(1, 99)}"/>'
                f'<feColorMatrix values="0 0 0 0 .2  0 0 0 0 .19  0 0 0 0 .17  0 0 0 -1.3 .85"/></filter>'
                f'<filter id="stain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".006 .012" numOctaves="3" seed="{s.r.randint(1, 99)}"/>'
                f'<feColorMatrix values="0 0 0 0 .32  0 0 0 0 .3  0 0 0 0 .26  0 0 0 -2.2 1.25"/></filter>'
                # spray paint: edge slightly eaten by the wall texture, plus a soft overspray halo
                f'<filter id="rough" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="1" seed="3" result="n"/>'
                f'<feDisplacementMap in="SourceGraphic" in2="n" scale="2.2" xChannelSelector="R" yChannelSelector="G"/></filter>'
                f'<filter id="spray" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur in="SourceGraphic" stdDeviation="3.2" result="b"/>'
                f'<feComponentTransfer in="b" result="halo"><feFuncA type="linear" slope=".28"/></feComponentTransfer>'
                f'<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="1" seed="5" result="n"/>'
                f'<feDisplacementMap in="SourceGraphic" in2="n" scale="2.4" xChannelSelector="R" yChannelSelector="G" result="e"/>'
                f'<feMerge><feMergeNode in="halo"/><feMergeNode in="e"/></feMerge></filter></defs>')
        wall = (f'<rect width="{w}" height="{h}" fill="{WALL}"/>'
                f'<rect width="{w}" height="{h}" filter="url(#stain)" opacity=".4"/>'
                f'<rect width="{w}" height="{h}" filter="url(#grit)" opacity=".55"/>')
        # formwork joints and tie holes of a poured-concrete wall
        panel = 200 if w > 500 else 140
        for x in range(panel, w, panel):
            wall += f'<rect x="{x}" y="0" width="1.4" height="{h}" fill="#9d978c" opacity=".55"/>'
        for x in range(panel//2, w, panel):
            for y in (h*.22, h*.74):
                wall += f'<circle cx="{x}" cy="{y:.0f}" r="3.2" fill="#8f897e" opacity=".6"/>'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" role="img">'
                f'<title>{title}</title>{defs}{wall}<g filter="url(#spray)">' + ''.join(s.o) + '</g></svg>\n')

def at(k): return ''.join(f' {a.replace("_", "-")}="{v}"' for a, v in k.items())

def catmull(pts, close=False):
    """Smooth path through points (Catmull-Rom -> cubic Bezier)."""
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if close else [P[0]] + P + [P[-1]]
    d = f'M{P[1][0]:.1f},{P[1][1]:.1f}'
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0])/6, p1[1] + (p2[1] - p0[1])/6)
        c2 = (p2[0] - (p3[0] - p1[0])/6, p2[1] - (p3[1] - p1[1])/6)
        d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d + (' Z' if close else '')

# ---------- motifs ----------
def heart(s, x, y, r, col=RED, leaf=True):
    """Heart-shaped coffee cherry: the balloon of the series, with a small leaf and stalk on top."""
    s.p(f'M{x},{y + r*1.05} C{x - r*.35},{y + r*.7} {x - r*1.15},{y + r*.2} {x - r*1.1},{y - r*.3} '
        f'C{x - r*1.05},{y - r*.95} {x - r*.25},{y - r*1.05} {x},{y - r*.5} '
        f'C{x + r*.25},{y - r*1.05} {x + r*1.05},{y - r*.95} {x + r*1.1},{y - r*.3} '
        f'C{x + r*1.15},{y + r*.2} {x + r*.35},{y + r*.7} {x},{y + r*1.05} Z', col)
    s.ell(x - r*.5, y - r*.42, r*.16, r*.26, -35, '#f0e9dd')          # highlight
    if leaf:
        s.limb([(x, y - r*.5), (x + r*.05, y - r*.82)], max(2, r*.07))
        s.blob([(x + r*.05, y - r*.8), (x + r*.4, y - r*1.12), (x + r*.85, y - r*1.12), (x + r*.45, y - r*.82)])

def cherry(s, x, y, r, col=RED):
    s.circ(x, y, r, col); s.circ(x - r*.35, y - r*.35, r*.22, '#f0e9dd')

def cleaf(s, x, y, L, ang, col=INK):
    """Coffee leaf as a stencil cut: solid with the midrib left open."""
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    W = L*.3
    pts = []
    for i in range(13):
        t = i/12; hw = W*math.sin(math.pi*t)**.8*(1 - .2*t)
        pts.append((x + ux*L*t + nx*hw, y + uy*L*t + ny*hw))
    for i in range(11, 0, -1):
        t = i/12; hw = W*math.sin(math.pi*t)**.8*(1 - .2*t)
        pts.append((x + ux*L*t - nx*hw, y + uy*L*t - ny*hw))
    s.blob(pts, col)
    s.limb([(x + ux*L*.12, y + uy*L*.12), (x + ux*L*.85, y + uy*L*.85)], max(1.4, L*.035), WALL)

def girl(s, x, g, H, reach=(1, -1)):
    """Girl in a short dress, hair blown back, one arm stretched toward (x + reach)."""
    k = H/300
    hy = g - 262*k
    s.blob([(x - 4*k, hy - 30*k), (x + 22*k, hy - 20*k), (x + 26*k, hy + 4*k), (x + 16*k, hy + 26*k), (x - 8*k, hy + 30*k),
            (x - 26*k, hy + 14*k), (x - 26*k, hy - 14*k)])                                                       # head
    s.blob([(x - 6*k, hy - 32*k), (x + 20*k, hy - 26*k), (x + 6*k, hy - 12*k), (x - 18*k, hy + 4*k), (x - 30*k, hy + 22*k),
            (x - 44*k, hy + 2*k), (x - 62*k, hy + 4*k), (x - 84*k, hy - 6*k), (x - 60*k, hy - 18*k), (x - 30*k, hy - 28*k)])  # hair, blown back
    s.limb([(x - 2*k, hy + 24*k), (x - 2*k, hy + 40*k)], 13*k)                                                    # neck
    s.blob([(x - 18*k, hy + 40*k), (x + 14*k, hy + 40*k), (x + 22*k, hy + 90*k), (x + 30*k, hy + 150*k), (x + 6*k, hy + 160*k),
            (x - 40*k, hy + 162*k), (x - 72*k, hy + 156*k), (x - 44*k, hy + 112*k), (x - 26*k, hy + 72*k)])                        # dress, skirt in the wind
    sx, sy = x + 8*k, hy + 50*k
    ex, ey = sx + reach[0]*52*k, sy + reach[1]*52*k
    s.limb([(sx, sy), (ex, ey), (ex + reach[0]*48*k, ey + reach[1]*48*k)], 15*k)                                  # reaching arm
    s.ell(ex + reach[0]*54*k, ey + reach[1]*54*k, 10*k, 8*k, -40)
    s.limb([(x - 14*k, hy + 54*k), (x - 30*k, hy + 96*k), (x - 40*k, hy + 128*k)], 14*k)                         # other arm
    s.limb([(x - 14*k, hy + 150*k), (x - 16*k, g - 12*k)], 17*k)                                                  # legs
    s.limb([(x + 10*k, hy + 150*k), (x + 18*k, hy + 192*k), (x + 30*k, g - 26*k)], 17*k)
    s.ell(x - 8*k, g - 8*k, 19*k, 9*k); s.ell(x + 40*k, g - 22*k, 18*k, 9*k, -25)                               # shoes
    return ex + reach[0]*54*k, ey + reach[1]*54*k

def rat(s, x, g, k=1, face=1):
    """Upright rat, two-legged, as in the stencil rats."""
    f = face
    s.ell(x, g - 46*k, 20*k, 34*k, f*-8)                                             # body
    s.blob([(x + f*6*k, g - 98*k), (x + f*20*k, g - 92*k), (x + f*44*k, g - 82*k), (x + f*18*k, g - 70*k), (x - f*12*k, g - 74*k)])  # head + snout
    s.ell(x - f*2*k, g - 98*k, 9*k, 11*k, f*-20); s.ell(x - f*1*k, g - 97*k, 5*k, 6*k, f*-20, WALL)  # ear
    s.circ(x + f*20*k, g - 86*k, 2.2*k, WALL)                                         # eye
    for i in (-1, 1):
        s.limb([(x + f*44*k, g - 82*k), (x + f*58*k, g - 84*k + i*5*k)], 1.1*k)       # whiskers
    s.limb([(x - 6*k, g - 16*k), (x - 12*k, g)], 7*k); s.limb([(x + 8*k, g - 16*k), (x + 12*k, g)], 7*k)  # legs
    s.ell(x - 15*k, g, 9*k, 3.5*k); s.ell(x + 16*k, g, 9*k, 3.5*k)
    s.curve([(x - f*16*k, g - 24*k), (x - f*44*k, g - 14*k), (x - f*60*k, g - 2*k), (x - f*86*k, g + 2*k), (x - f*100*k, g - 12*k)], 4*k)  # tail

def campesino(s, x, g, H, face=1, arm=None):
    """Farmer silhouette in a wide-brimmed sombrero."""
    k = H/300; f = face
    hy = g - 262*k
    s.ell(x, hy, 19*k, 23*k)
    s.ell(x, hy - 16*k, 46*k, 8*k); s.blob([(x - 20*k, hy - 18*k), (x - 16*k, hy - 40*k), (x + 16*k, hy - 40*k), (x + 20*k, hy - 18*k)])  # sombrero
    s.limb([(x, hy + 18*k), (x, hy + 34*k)], 13*k)
    s.blob([(x - 30*k, hy + 34*k), (x + 30*k, hy + 34*k), (x + 34*k, hy + 70*k), (x + 26*k, hy + 140*k), (x - 26*k, hy + 140*k), (x - 34*k, hy + 70*k)])  # shirt
    s.blob([(x - 27*k, hy + 134*k), (x + 27*k, hy + 134*k), (x + 22*k, g - 8*k), (x + 4*k, g - 8*k), (x, hy + 180*k), (x - 4*k, g - 8*k), (x - 24*k, g - 8*k)])  # trousers
    s.ell(x - 16*k, g - 5*k, 16*k, 6*k); s.ell(x + 16*k, g - 5*k, 16*k, 6*k)       # boots
    s.limb([(x - f*28*k, hy + 42*k), (x - f*36*k, hy + 96*k), (x - f*34*k, hy + 140*k)], 13*k)
    if arm: s.limb([(x + f*28*k, hy + 42*k)] + arm, 13*k)
    else: s.limb([(x + f*28*k, hy + 42*k), (x + f*36*k, hy + 96*k), (x + f*34*k, hy + 140*k)], 13*k)

def bag(s, x, y, w, h, col=INK):
    """Coffee bag with a folded top and a cut-out label."""
    s.blob([(x, y + 14), (x + w*.5, y + 6), (x + w, y + 14), (x + w + 4, y + h*.6), (x + w, y + h), (x + w*.5, y + h + 3), (x, y + h), (x - 4, y + h*.6)], col)
    s.rect(x - 2, y, w + 4, 16, col)
    s.rect(x + 2, y + 18, w - 4, 3, WALL)
    s.rect(x + w*.14, y + h*.38, w*.72, h*.36, WALL)

# ---------- scenes ----------
def hero():
    s = S(1600, 640, 1)
    # the girl reaching for a heart-shaped coffee cherry that floats away over the Canal
    hx, hy = girl(s, 1050, 612, 340, reach=(.8, -.6))
    s.curve([(hx + 4, hy - 6), (hx + 50, hy - 50), (hx + 70, hy - 100), (hx + 110, hy - 150), (1300, 230)], 2.4)  # string
    heart(s, 1312, 168, 64)
    for x, y in ((1006, 512), (1030, 515), (1062, 505), (1078, 497), (1316, 236)):
        s.drip(x, y)
    # container ship on the horizon line of the Canal, stenciled small
    sx, sy = 1340, 560
    s.p(f'M{sx},{sy} L{sx + 210},{sy} L{sx + 196},{sy + 26} L{sx + 14},{sy + 26} Z')
    for i in range(6):
        s.rect(sx + 24 + i*26, sy - 18 - (i % 3)*10, 22, 18 + (i % 3)*10, INK)
        s.rect(sx + 24 + i*26, sy - 10 - (i % 3)*10, 22, 2.2, WALL)
    s.rect(sx + 182, sy - 44, 16, 44); s.rect(sx + 186, sy - 36, 8, 4, WALL)
    s.limb([(1300, 588), (1580, 588)], 3)
    s.drip(1420, 588, 30); s.drip(1530, 588, 18)
    s.text(1560, 430, 'DEL VIVERO', 34, INK, 'end', -4)
    s.text(1560, 472, 'A LA TAZA', 34, RED, 'end', -4)
    return s.svg('Estarcido estilo Banksy en un muro de concreto: una niña alcanza un globo rojo con forma de cereza de café en corazón; al fondo, un barco portacontenedores en el Canal')

def vivero():
    s = S(400, 276, 2)
    # a crack in the wall with a seedling growing out of it, watered by a child
    s.limb([(250, 276), (262, 246), (254, 226), (270, 204), (264, 188)], 3)
    s.limb([(262, 246), (284, 238)], 2); s.limb([(254, 226), (240, 214)], 1.6)
    s.curve([(264, 196), (262, 160), (268, 128), (272, 100)], 4)                       # stem
    cleaf(s, 266, 168, 52, -150); cleaf(s, 266, 150, 56, -28); cleaf(s, 270, 122, 44, -160); cleaf(s, 271, 106, 40, -40)
    cherry(s, 279, 86, 9); cherry(s, 290, 98, 8)
    k = .62; x, g = 120, 262                                                          # child, smaller girl figure
    s.ell(x, g - 186, 15, 17); s.blob([(x - 14, g - 196), (x - 6, g - 208), (x + 14, g - 204), (x + 16, g - 190), (x + 6, g - 196)])
    s.limb([(x, g - 170), (x, g - 160)], 9)
    s.blob([(x - 14, g - 160), (x + 14, g - 160), (x + 22, g - 96), (x - 22, g - 96)])
    s.limb([(x - 8, g - 98), (x - 10, g - 8)], 9); s.limb([(x + 8, g - 98), (x + 10, g - 8)], 9)
    s.ell(x - 14, g - 4, 11, 5); s.ell(x + 14, g - 4, 11, 5)
    s.limb([(x + 10, g - 154), (x + 36, g - 136), (x + 52, g - 140)], 8)
    # red watering can tipped toward the seedling, with the water as a sprayed dotted arc
    cx, cy = 176, 120
    s.add(f'<g transform="rotate(22 {cx} {cy})">')
    s.rect(cx - 30, cy - 18, 60, 40, RED); s.p(f'M{cx + 26},{cy + 10} L{cx + 70},{cy - 22} L{cx + 74},{cy - 16} L{cx + 32},{cy + 18} Z', RED)
    s.ell(cx + 74, cy - 20, 8, 5, -35, RED)
    s.add(f'<path d="M{cx - 28},{cy - 10} Q{cx - 52},{cy - 20} {cx - 42},{cy + 14}" fill="none" stroke="{RED}" stroke-width="5"/>')
    s.add('</g>')
    for i, (dx, dy) in enumerate(((236, 92), (244, 104), (250, 116), (246, 128), (256, 132), (252, 146))):
        s.circ(dx, dy, 2.6 - i*.2, INK)
    for x in (112, 124, 252): s.drip(x, 262 if x < 200 else 200, 10)
    return s.svg('Estarcido estilo Banksy: un niño riega con una regadera roja un plantón de café que crece de una grieta en el muro')

def cosecha():
    s = S(400, 276, 3)
    # a stencil rat carrying a branch of red coffee cherries over its shoulder like a bindle
    rat(s, 190, 246, 1.55, 1)
    s.limb([(196, 120), (154, 70), (120, 40)], 5)
    for (lx, ly, L, a) in ((150, 66, 40, -120), (132, 50, 38, 160), (142, 60, 36, 40)):
        cleaf(s, lx, ly, L, a)
    for (cx, cy) in ((126, 58), (114, 46), (138, 76), (122, 74), (108, 62), (150, 88), (134, 92)):
        cherry(s, cx, cy, 8.5)
    s.limb([(206, 128), (198, 112)], 10)                                              # paw on the branch
    s.limb([(40, 248), (370, 248)], 2.5)
    for x in (172, 214, 300): s.drip(x, 248)
    s.text(372, 52, 'COSECHA', 26, INK, 'end', 0)
    s.text(372, 80, 'A MANO', 26, RED, 'end', 0)
    return s.svg('Estarcido estilo Banksy: una rata de pie carga al hombro una rama con cerezas de café rojas')

def proceso():
    s = S(400, 276, 4)
    # homage to the flower thrower: a masked figure, mid-swing, hurling a bouquet of coffee cherries
    x, g = 214, 262
    s.blob([(x - 24, 92), (x + 18, 84), (x + 40, 112), (x + 38, 160), (x + 22, 176), (x - 18, 176), (x - 30, 140)])  # jacket, torso leaning back
    s.blob([(x - 20, 168), (x + 24, 166), (x + 30, 182), (x - 22, 184)])                                       # belt line
    s.ell(x + 2, 62, 21, 24, 12)                                                                                # head
    s.blob([(x - 20, 48), (x - 4, 34), (x + 18, 38), (x + 24, 50), (x + 2, 52)]); s.rect(x + 18, 44, 20, 6)    # cap, peak back
    s.rect(x - 20, 58, 30, 5, WALL)                                                                             # eye slit above the bandana
    s.limb([(x - 10, 178), (x - 40, 214), (x - 74, 252)], 22)                                                   # front leg, lunging
    s.limb([(x + 18, 178), (x + 46, 214), (x + 70, 252)], 22)
    s.ell(x - 82, 256, 22, 8); s.ell(x + 78, 256, 22, 8)
    s.limb([(x + 26, 98), (x + 62, 120), (x + 90, 104)], 17)                                                    # back arm, balance
    s.limb([(x - 18, 100), (x - 56, 86), (x - 84, 58)], 18)                                                     # throwing arm
    s.ell(x - 88, 52, 11, 11)
    for (L, a) in ((40, -160), (36, -120), (40, -80), (32, -40)):
        cleaf(s, x - 92, 48, L, a)
    for (cx, cy) in ((x - 120, 26), (x - 104, 14), (x - 88, 20), (x - 134, 42), (x - 114, 36), (x - 98, 30), (x - 76, 26)):
        cherry(s, cx, cy, 8.5, RED)
    for xx, yy in ((x - 12, 184), (x + 20, 184), (x - 82, 262)): s.drip(xx, yy, 14)
    s.text(388, 156, 'BENEFICIO', 22, INK, 'end', 0)
    return s.svg('Estarcido estilo Banksy: una figura con pañuelo, en pleno lanzamiento, arroja un ramo de cerezas de café rojas')

def empaque():
    s = S(400, 276, 5)
    bag(s, 72, 70, 120, 168)
    s.add(f'<text x="132" y="160" font-family="Impact,\'Arial Black\',sans-serif" font-weight="900" font-size="16" text-anchor="middle" fill="{INK}">CAFÉ DEL</text>'
          f'<text x="132" y="184" font-family="Impact,\'Arial Black\',sans-serif" font-weight="900" font-size="16" text-anchor="middle" fill="{INK}">CANAL</text>')
    heart(s, 132, 210, 9, RED, leaf=False)
    # cup with the steam rising into a red heart
    cx, g = 290, 238
    s.p(f'M{cx - 54},{g - 92} L{cx + 54},{g - 92} L{cx + 46},{g - 30} Q{cx + 40},{g - 4} {cx},{g - 4} Q{cx - 40},{g - 4} {cx - 46},{g - 30} Z')
    s.add(f'<path d="M{cx + 50},{g - 76} q30,0 26,24 q-4,18 -30,18" fill="none" stroke="{INK}" stroke-width="9"/>')
    s.ell(cx, g + 4, 74, 9)
    s.rect(cx - 34, g - 66, 68, 3, WALL)
    for i, dx in enumerate((-18, 0, 18)):
        s.curve([(cx + dx, g - 104), (cx + dx + 8, g - 120), (cx + dx - 6, g - 136), (cx + dx + 4, g - 150)], 5)
    heart(s, cx, g - 182, 26, RED, leaf=False)
    for x in (100, 168, 262, 318): s.drip(x, 238 if x < 200 else g + 10)
    return s.svg('Estarcido estilo Banksy: una bolsa de Café del Canal y una taza cuyo vapor sube en forma de corazón rojo')

def productores():
    s = S(764, 361, 6)
    # two farmers handing over a heart-shaped red cherry, among stenciled coffee shrubs
    campesino(s, 300, 340, 280, 1, [(352, 150), (382, 140)])
    campesino(s, 470, 340, 270, -1, [(418, 150), (392, 146)])
    heart(s, 387, 112, 26)
    for bx in (90, 680):
        s.limb([(bx, 340), (bx, 160)], 6)
        for j in range(6):
            y = 170 + j*28
            cleaf(s, bx, y, 54 - j*2, -20 - j*4); cleaf(s, bx, y + 10, 54 - j*2, -160 + j*4)
            if j % 2: cherry(s, bx + 8, y + 18, 6); cherry(s, bx - 6, y + 22, 6)
    s.limb([(20, 342), (744, 342)], 3)
    for x in (282, 318, 452, 488, 90, 680): s.drip(x, 342)
    s.text(42, 70, 'PRODUCTORES', 30, INK, 'start', -3)
    s.text(42, 104, 'DEL CANAL', 30, RED, 'start', -3)
    return s.svg('Estarcido estilo Banksy: dos productores con sombrero se pasan un corazón rojo de café entre cafetales')

def distribuidores():
    s = S(764, 361, 7)
    # the placard monkey, Panamanian howler edition, with the brand slogan
    x, g = 330, 340
    s.blob([(x - 30, g - 170), (x + 18, g - 176), (x + 36, g - 120), (x + 28, g - 60), (x - 32, g - 60), (x - 42, g - 120)])  # body
    s.ell(x - 4, g - 196, 30, 28); s.ell(x - 4, g - 188, 20, 18, 0, WALL); s.ell(x - 4, g - 184, 13, 11)  # head, face mask, muzzle
    s.circ(x - 12, g - 196, 3, INK); s.circ(x + 4, g - 196, 3, INK)
    s.ell(x - 34, g - 196, 8, 10); s.ell(x + 26, g - 196, 8, 10)                   # ears
    s.limb([(x - 22, g - 60), (x - 30, g - 20), (x - 26, g)], 16); s.limb([(x + 20, g - 60), (x + 30, g - 20), (x + 26, g)], 16)
    s.ell(x - 34, g, 16, 6); s.ell(x + 34, g, 16, 6)
    s.curve([(x + 30, g - 70), (x + 80, g - 60), (x + 100, g - 110), (x + 82, g - 140), (x + 66, g - 126)], 9)  # prehensile tail
    # sandwich board
    bx, by, bw, bh = x - 120, g - 148, 240, 92
    s.rect(bx, by, bw, bh, INK); s.rect(bx + 8, by + 8, bw - 16, bh - 16, WALL)
    s.limb([(x - 30, g - 160), (bx + 24, by + 4)], 4); s.limb([(x + 22, g - 164), (bx + bw - 24, by + 4)], 4)
    s.add(f'<text x="{x}" y="{by + 44}" font-family="Impact,\'Arial Black\',sans-serif" font-weight="900" font-size="25" text-anchor="middle" fill="{INK}">RÍETE AHORA,</text>'
          f'<text x="{x}" y="{by + 72}" font-family="Impact,\'Arial Black\',sans-serif" font-weight="900" font-size="19" text-anchor="middle" fill="{RED}">QUE EL CAFÉ YA VIENE</text>')
    # delivery bicycle loaded with bags
    cx, cy = 580, 300
    for wx in (cx - 60, cx + 70):
        s.add(f'<circle cx="{wx}" cy="{cy}" r="36" fill="none" stroke="{INK}" stroke-width="7"/>')
        s.circ(wx, cy, 5)
    s.limb([(cx - 60, cy), (cx - 6, cy - 4), (cx + 30, cy - 58), (cx - 30, cy - 58), (cx - 6, cy - 4)], 6)
    s.limb([(cx + 30, cy - 58), (cx + 70, cy), (cx + 52, cy - 88), (cx + 70, cy - 92)], 6)
    s.limb([(cx - 42, cy - 64), (cx - 18, cy - 64)], 8)
    s.rect(cx + 14, cy - 76, 76, 10)
    bag(s, cx + 18, cy - 136, 30, 58, RED); bag(s, cx + 54, cy - 128, 30, 50)
    s.limb([(20, 342), (744, 342)], 3)
    for x in (300, 352, 520, 660): s.drip(x, 342)
    return s.svg('Estarcido estilo Banksy: un mono aullador con un cartel que dice «Ríete ahora, que el café ya viene» y una bicicleta de reparto cargada con bolsas de café')

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'img', 'v7')
    os.makedirs(out, exist_ok=True)
    for name, fn in (('hero', hero), ('vivero', vivero), ('cosecha', cosecha), ('proceso', proceso),
                     ('empaque', empaque), ('productores', productores), ('distribuidores', distribuidores)):
        open(os.path.join(out, name + '.svg'), 'w').write(fn())
        print(name)
