# Line-art illustrations in the style of an ink engraving: black contours on paper, veins and
# parallel hatching for shade, terraced hills drawn as nested contour lines. Writes SVG files to
# img/v6/.
#   python3 tools/trazo.py
import math, os, random

INK, PAPER = '#1d1a17', '#fbf8f1'

class S:
    def __init__(s, w, h, seed=1):
        s.w, s.h, s.o = w, h, []
        s.r = random.Random(seed)
    def add(s, x): s.o.append(x)
    def p(s, d, w=1.4, fill='none', **k):
        s.add(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{w}"{at(k)}/>')
    def poly(s, pts, w=1.2, close=False, fill='none'):
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + (' Z' if close else '')
        s.p(d, w, fill)
    def smooth(s, pts, w=1.4, close=False, fill='none'):
        s.p(catmull(pts, close), w, fill)
    def line(s, x1, y1, x2, y2, w=.8): s.p(f'M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}', w)
    def circ(s, x, y, r, w=1.3, fill=PAPER): s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{w}"/>')
    def ell(s, x, y, rx, ry, rot=0, w=1.3, fill=PAPER):
        s.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" transform="rotate({rot:.1f} {x:.1f} {y:.1f})" fill="{fill}" stroke="{INK}" stroke-width="{w}"/>')
    def svg(s, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s.w} {s.h}" preserveAspectRatio="xMidYMid slice" role="img">'
                f'<title>{title}</title><rect width="{s.w}" height="{s.h}" fill="{PAPER}"/>'
                f'<g stroke-linecap="round" stroke-linejoin="round">' + ''.join(s.o) + '</g></svg>\n')

def at(k): return ''.join(f' {a.replace("_", "-")}="{v}"' for a, v in k.items())

def catmull(pts, close=False):
    """Smooth path through points (Catmull-Rom -> cubic Bezier)."""
    P = list(pts)
    if close: P = [P[-1]] + P + [P[0], P[1]]
    else: P = [P[0]] + P + [P[-1]]
    d = f'M{P[1][0]:.1f},{P[1][1]:.1f}'
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0])/6, p1[1] + (p2[1] - p0[1])/6)
        c2 = (p2[0] - (p3[0] - p1[0])/6, p2[1] - (p3[1] - p1[1])/6)
        d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d + (' Z' if close else '')

# ---------- motifs ----------
def leaf(s, x, y, L, ang, bend=.12, shade=1, w=1.5):
    """Coffee leaf from its stalk at (x, y): outline, curved midrib, side veins, hatching on one half."""
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    W = L*.27
    def mid(t):  # point on the (bent) midrib
        b = math.sin(math.pi*t)*L*bend
        return x + ux*L*t + nx*b, y + uy*L*t + ny*b
    def half(t): return W*(math.sin(math.pi*min(1, t*1.05))**.75)*(1 - .25*t)
    T = [i/16 for i in range(17)]
    left = [(mid(t)[0] + nx*half(t), mid(t)[1] + ny*half(t)) for t in T]
    right = [(mid(t)[0] - nx*half(t), mid(t)[1] - ny*half(t)) for t in T]
    s.smooth(left + right[::-1][1:-1], w, close=True, fill=PAPER)
    s.smooth([mid(t) for t in T[:-1]], w*.8)
    for i in range(1, 8):            # side veins, swept toward the tip
        t = i/8.6
        for sd in (1, -1):
            m = mid(t); m2 = mid(min(1, t + .1)); hw = half(t + .06)*.86
            s.p(f'M{m[0]:.1f},{m[1]:.1f} Q{m2[0] + sd*nx*hw*.5:.1f},{m2[1] + sd*ny*hw*.5:.1f} {m2[0] + sd*nx*hw:.1f},{m2[1] + sd*ny*hw:.1f}', .7)
    for i in range(3, 46):           # hatching on the shaded half
        t = i/48
        m = mid(t); hw = half(t)
        if hw < 3: continue
        f = .35 + .5*abs(math.sin(i*1.7))
        s.line(m[0] + shade*nx*hw*.12, m[1] + shade*ny*hw*.12, m[0] + shade*nx*hw*f, m[1] + shade*ny*hw*f, .45)
    s.line(x, y, x - ux*L*.08, y - uy*L*.08, w)

def cherry(s, x, y, r, w=1.2):
    s.circ(x, y, r, w)
    s.circ(x + r*.32, y - r*.32, r*.16, .8)                         # calyx scar
    for i in range(4):                                              # crescent shading
        rr = r*(.86 - i*.12)
        s.p(f'M{x - rr*.95:.1f},{y + rr*.2:.1f} A{rr:.1f},{rr:.1f} 0 0 0 {x + rr*.2:.1f},{y + rr*.95:.1f}', .55)

def cluster(s, x, y, r, n=7, seed=0):
    rnd = random.Random(seed)
    pts = [(0, 0), (1.6, -.6), (-1.5, -.5), (.4, -1.6), (1.1, 1.2), (-1, 1.2), (2.4, .6), (-2.3, .7), (0, 1.9)][:n]
    for dx, dy in sorted(pts, key=lambda p: p[1]):
        cherry(s, x + dx*r + rnd.uniform(-2, 2), y + dy*r + rnd.uniform(-2, 2), r*rnd.uniform(.88, 1.05))

def flower(s, x, y, r):
    for i in range(5):
        a = math.radians(i*72 - 90)
        s.ell(x + math.cos(a)*r*.6, y + math.sin(a)*r*.6, r*.62, r*.24, rot=i*72 - 90, w=.9)
    s.circ(x, y, r*.18, .8)
    for i in range(5):
        a = math.radians(i*72 - 54); s.line(x, y, x + math.cos(a)*r*.5, y + math.sin(a)*r*.5, .6)

def stem(s, pts, w=6):
    d = catmull(pts)
    s.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w}"/><path d="{d}" fill="none" stroke="{PAPER}" stroke-width="{w - 2.6}"/>')
    for i in range(1, len(pts) - 1, 2):
        x, y = pts[i]; s.line(x - w*.2, y - w*.6, x + w*.25, y + w*.5, .6)

def branch(s, x, y, k=1.0, rot=0, seed=3):
    """Upright coffee branch with leaf pairs, cherry clusters at the nodes and a few flowers on top."""
    s.add(f'<g transform="translate({x} {y}) rotate({rot}) scale({k})">')
    stem(s, [(0, 0), (-6, -90), (4, -190), (-4, -290), (6, -390), (0, -470)], 7)
    for i, (ny, L, cl) in enumerate(((-80, 170, True), (-180, 150, True), (-280, 128, True), (-370, 104, False), (-440, 76, False))):
        xm = 3 if i % 2 else -3
        leaf(s, xm, ny, L, 200 + i*6, bend=-.14, shade=-1)
        leaf(s, xm, ny - 6, L*.94, -20 - i*6, bend=.14, shade=1)
        if cl: cluster(s, xm + 4, ny + 18, 13 - i, n=8 - i, seed=seed + i)
    for fx, fy in ((-8, -478), (12, -490), (2, -500)): flower(s, fx, fy, 14)
    s.add('</g>')

def bean(s, x, y, rx, ry, rot=0):
    s.ell(x, y, rx, ry, rot, 1.5)
    a = math.radians(rot); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    pts = [(x + ux*rx*t + nx*ry*.18*math.sin(t*math.pi*1.4), y + uy*rx*t + ny*ry*.18*math.sin(t*math.pi*1.4)) for t in [i/8 - 1 for i in range(17)][1:-1]]
    pts = [(x + ux*rx*.86*t + nx*ry*.16*math.sin(t*4), y + uy*rx*.86*t + ny*ry*.16*math.sin(t*4)) for t in [-1 + i/8 for i in range(17)]]
    s.smooth(pts, 1.3)
    for i in range(-7, 8):          # hatching across one half
        t = i/8.5; hh = ry*math.sqrt(max(0, 1 - t*t))*.9
        cx, cy = x + ux*rx*t + nx*ry*.16*math.sin(t*4), y + uy*rx*t + ny*ry*.16*math.sin(t*4)
        s.line(cx + nx*ry*.12, cy + ny*ry*.12, cx + nx*hh, cy + ny*hh, .55)

def cup(s, x, y, r):
    """Cup of coffee, seen slightly from above, with saucer and steam."""
    s.ell(x, y + r*1.15, r*1.55, r*.32, w=1.4)
    s.p(f'M{x - r},{y} C{x - r},{y + r*1.1} {x - r*.6},{y + r*1.25} {x},{y + r*1.25} C{x + r*.6},{y + r*1.25} {x + r},{y + r*1.1} {x + r},{y}', 1.5, fill=PAPER)
    s.p(f'M{x + r*.95},{y + r*.25} C{x + r*1.6},{y + r*.1} {x + r*1.6},{y + r*.85} {x + r*.82},{y + r*.8}', 1.5)
    s.ell(x, y, r, r*.28, w=1.5)
    s.ell(x, y + r*.03, r*.84, r*.2, w=.8, fill=INK)
    for i in range(14):              # body shading on the right
        t = i/14; yy = y + r*.25 + t*r*.9
        s.line(x + r*.3, yy, x + r*.93*math.sqrt(max(0, 1 - (t*.8)**2)), yy, .5)
    for i, dx in enumerate((-.3, 0, .3)):
        s.p(f'M{x + dx*r},{y - r*.4} c{-r*.18},{-r*.25} {r*.18},{-r*.45} 0,{-r*.7}', .9)

def mountains(s, y0, peaks, x0=0, x1=None, hatch=True):
    x1 = s.w if x1 is None else x1
    pts = [(x0, y0)]
    for px, ph in peaks: pts += [(px, y0 - ph)]
    pts += [(x1, y0)]
    s.poly(pts, 1)
    if hatch:
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if by > ay:  # descending flank: shade it
                n = int(abs(bx - ax)/7)
                for i in range(1, n):
                    t = i/n; px, py = ax + (bx - ax)*t, ay + (by - ay)*t
                    s.line(px, py + 2, px - 5, py + 2 + min(18, (y0 - py)*.4), .5)

def hill_lines(s, cx, base, h, w, n, x0=None, x1=None, skew=0):
    """Terraced hill: outline plus n nested contour lines."""
    x0 = cx - w*1.6 if x0 is None else x0; x1 = cx + w*1.6 if x1 is None else x1
    xs = [x0 + (x1 - x0)*i/60 for i in range(61)]
    def prof(x): return math.exp(-((x - cx)/w)**2)*(1 + skew*(x - cx)/w*.3)
    out = [(x, base - h*prof(x)) for x in xs]
    s.p(catmull(out) + f' L{x1:.1f},{base + 30:.1f} L{x0:.1f},{base + 30:.1f} Z', 0, fill=PAPER, stroke_opacity='0')
    for k in range(n + 1):
        f = 1 - k/(n + 2)
        pts = [(x, base - h*prof(x)*f + k*2.2) for x in xs]
        s.smooth(pts, 1.1 if k == 0 else .55)

def rows(s, vx, vy, y_near, x_from, x_to, n, seed=1):
    """Coffee rows converging to (vx, vy): each row a line of bushy scribbles with dark hatching below."""
    rnd = random.Random(seed)
    for i in range(n):
        xb = x_from + (x_to - x_from)*i/(n - 1)
        steps = 26
        for j in range(steps):
            t0, t1 = j/steps, (j + 1)/steps
            ax, ay = vx + (xb - vx)*t0, vy + (y_near - vy)*t0
            bx, by = vx + (xb - vx)*t1, vy + (y_near - vy)*t1
            sz = 3 + 22*t1
            mx, my = (ax + bx)/2, (ay + by)/2 - sz*.9
            s.p(f'M{ax:.1f},{ay:.1f} Q{mx - sz*.3:.1f},{my - sz*.2:.1f} {mx:.1f},{my:.1f} Q{mx + sz*.3:.1f},{my - sz*.2:.1f} {bx:.1f},{by:.1f}', .6 + .7*t1)
            for q in range(int(2 + 5*t1)):
                hx = ax + (bx - ax)*q/(2 + 5*t1)
                hy = ay + (by - ay)*q/(2 + 5*t1)
                s.line(hx, hy, hx + rnd.uniform(-1, 1), hy + sz*.55, .5 + .4*t1)

def water(s, x0, x1, y0, y1, gap=9, seed=2):
    rnd = random.Random(seed)
    y = y0
    while y < y1:
        x = x0 + rnd.uniform(0, 30)
        while x < x1:
            L = rnd.uniform(14, 46)
            s.line(x, y, min(x + L, x1), y, .5)
            x += L + rnd.uniform(10, 30)
        y += gap

def ship(s, x, y, L):
    h = L*.12
    s.poly([(x - L/2, y - h), (x + L/2, y - h), (x + L*.44, y), (x - L*.42, y)], 1.2, close=True, fill=PAPER)
    for i in range(9):
        s.poly([(x - L*.4 + i*L*.075, y - h), (x - L*.4 + i*L*.075, y - h*2), (x - L*.33 + i*L*.075, y - h*2), (x - L*.33 + i*L*.075, y - h)], .8, close=True, fill=PAPER)
    s.poly([(x + L*.3, y - h), (x + L*.3, y - h*3), (x + L*.42, y - h*3), (x + L*.42, y - h)], 1, close=True, fill=PAPER)

def hat(s, x, y, r):
    s.ell(x, y, r*1.7, r*.42, w=1.4)
    s.p(f'M{x - r*.85},{y - r*.05} C{x - r*.85},{y - r*1.1} {x + r*.85},{y - r*1.1} {x + r*.85},{y - r*.05}', 1.4, fill=PAPER)
    s.p(f'M{x - r*.85},{y - r*.3} Q{x},{y - r*.12} {x + r*.85},{y - r*.3}', 2.4)

def limb(s, pts, w):
    """Outlined tube (arm, leg): an ink stroke with a paper stroke inside."""
    d = catmull(pts)
    s.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w:.1f}"/><path d="{d}" fill="none" stroke="{PAPER}" stroke-width="{w - 2.8:.1f}"/>')

def person(s, x, y, h, hat_on=True, basket=False, face=1, cane=False):
    """Engraved figure, feet at (x, y); face 1 looks right, -1 left."""
    u = h/10; f = face
    # back arm
    limb(s, [(x - f*u*.95, y - u*6.8), (x - f*u*1.35, y - u*5.6), (x - f*u*1.2, y - u*4.4)], u*.62)
    s.circ(x - f*u*1.2, y - u*4.2, u*.28, 1.1)
    # legs + shoes
    limb(s, [(x - u*.42, y - u*4.3), (x - u*.5, y - u*2.2), (x - u*.55, y - u*.3)], u*.8)
    limb(s, [(x + u*.42, y - u*4.3), (x + u*.5, y - u*2.2), (x + u*.55, y - u*.3)], u*.8)
    for sx in (-1, 1):
        s.p(f'M{x + sx*u*.55 - u*.4},{y} Q{x + sx*u*.55 + f*u*.1},{y - u*.45} {x + sx*u*.55 + f*u*.75},{y} Z', 1.2, fill=INK)
    for i in range(5):
        s.line(x - f*u*.2, y - u*(.8 + i*.6), x - f*u*.7, y - u*(1.0 + i*.6), .5)
    # shirt
    s.p(f'M{x - u*1.15},{y - u*4.1} L{x - u*1.05},{y - u*6.9} Q{x},{y - u*7.45} {x + u*1.05},{y - u*6.9} L{x + u*1.15},{y - u*4.1} Q{x},{y - u*3.8} {x - u*1.15},{y - u*4.1} Z', 1.4, fill=PAPER)
    s.p(f'M{x - u*.25},{y - u*7.2} L{x},{y - u*6.6} L{x + u*.25},{y - u*7.2}', 1)
    s.line(x, y - u*6.6, x, y - u*4.0, .7)
    for i in range(9):  # shade on the side away from the light
        s.line(x - f*u*.55, y - u*(4.3 + i*.3), x - f*u*1.05, y - u*(4.4 + i*.3), .45)
    # head, ear, eye, neck
    s.p(f'M{x - u*.22},{y - u*7.3} L{x - u*.2},{y - u*7.65} M{x + u*.22},{y - u*7.3} L{x + u*.2},{y - u*7.65}', 1.2)
    hx, hy = x + f*u*.1, y - u*8.35
    s.ell(hx, hy, u*.72, u*.85, w=1.4)
    s.p(f'M{hx - f*u*.2},{hy - u*.1} a{u*.16},{u*.2} 0 1 0 0.1,{u*.4}', .9)
    s.circ(hx + f*u*.38, hy - u*.05, u*.06, 1, fill=INK)
    s.p(f'M{hx + f*u*.66},{hy + u*.05} l{f*u*.12},{u*.22} l{-f*u*.14},{u*.04}', .9)
    s.p(f'M{hx + f*u*.2},{hy + u*.48} q{f*u*.2},{u*.1} {f*u*.35},{-u*.04}', .8)
    if hat_on: hat(s, hx, hy - u*.62, u*.95)
    else: s.p(f'M{hx - u*.72},{hy - u*.15} Q{hx - u*.6},{hy - u*.95} {hx + u*.1},{hy - u*.88} Q{hx + u*.6},{hy - u*.8} {hx + u*.7},{hy - u*.3}', 1.2)
    # front arm
    if basket:
        limb(s, [(x + f*u*.95, y - u*6.8), (x + f*u*1.6, y - u*5.9), (x + f*u*2.3, y - u*5.4)], u*.62)
        s.circ(x + f*u*2.45, y - u*5.35, u*.28, 1.1)
        bx, by = x + f*u*2.7, y - u*5
        s.p(f'M{bx - u*1.2},{by - u*.3} L{bx + u*1.2},{by - u*.3} L{bx + u*.9},{by + u*1.4} L{bx - u*.9},{by + u*1.4} Z', 1.3, fill=PAPER)
        for i in range(1, 5): s.line(bx - u*1.1 + i*u*.45, by - u*.3, bx - u*.95 + i*u*.4, by + u*1.4, .5)
        for i in range(1, 3): s.line(bx - u*1.1, by - u*.3 + i*u*.55, bx + u*1.1, by - u*.3 + i*u*.55, .5)
        for i in range(5): cherry(s, bx - u*.8 + i*u*.4, by - u*.55 - (i % 2)*u*.25, u*.3)
    elif cane:
        limb(s, [(x + f*u*.95, y - u*6.8), (x + f*u*1.5, y - u*5.8), (x + f*u*1.9, y - u*4.9)], u*.62)
        s.line(x + f*u*2.0, y - u*4.9, x + f*u*2.5, y, 2.2)
        s.circ(x + f*u*1.98, y - u*4.8, u*.28, 1.1)
    else:
        limb(s, [(x + f*u*.95, y - u*6.8), (x + f*u*1.35, y - u*5.6), (x + f*u*1.2, y - u*4.4)], u*.62)
        s.circ(x + f*u*1.2, y - u*4.2, u*.28, 1.1)

def coffee_bag(s, x, y, w):
    h = w*1.35
    s.p(f'M{x - w/2},{y} L{x - w*.45},{y - h} L{x + w*.45},{y - h} L{x + w/2},{y} Z', 1.5, fill=PAPER)
    s.p(f'M{x - w*.45},{y - h} L{x - w*.45},{y - h - w*.1} L{x + w*.45},{y - h - w*.1} L{x + w*.45},{y - h}', 1.3)
    for i in range(6): s.line(x - w*.45 + i*w*.18, y - h - w*.1, x - w*.45 + i*w*.18, y - h, .5)
    s.ell(x, y - h*.5, w*.27, w*.24, w=1)
    cherry(s, x - w*.07, y - h*.45, w*.06); cherry(s, x + w*.07, y - h*.45, w*.06); cherry(s, x, y - h*.36, w*.06)
    leaf(s, x - w*.02, y - h*.56, w*.15, 205, bend=-.1, w=1); leaf(s, x + w*.02, y - h*.56, w*.15, -25, w=1)
    for i in range(16):             # shade on the right side
        t = i/16; yy = y - h + t*h
        s.line(x + w*.3 + t*w*.02, yy, x + w*.45 + t*w*.05, yy, .5)

# ---------- scenes ----------
def hero():
    s = S(1600, 640, 1)
    mountains(s, 250, [(560, 30), (700, 70), (820, 40), (960, 96), (1080, 58), (1200, 84), (1340, 40), (1460, 72)], x0=480)
    hill_lines(s, 1180, 380, 170, 220, 16, x0=820, x1=1600, skew=.4)
    hill_lines(s, 820, 400, 110, 170, 11, x0=560, x1=1080)
    water(s, 560, 1600, 404, 450, gap=8)
    s.p('M560,402 C800,396 1200,398 1600,396', 1.1); s.p('M560,452 C800,456 1200,452 1600,456', 1.1)
    ship(s, 1000, 434, 200)
    rows(s, 1050, 452, 660, 520, 1720, 9)
    branch(s, 1540, 660, k=1.25, rot=-8, seed=5)
    return s.svg('Ilustración a tinta: ramas de café con cerezas, hileras de cafetales, colinas en terrazas, montañas y un barco en el Canal')

def vivero():
    s = S(400, 276, 2)
    s.p('M0,232 C120,226 280,234 400,228', 1.1)
    for i in range(30): s.line(i*14 + 4, 238 + (i % 3)*6, i*14 + 12, 238 + (i % 3)*6, .5)
    for i, (x, h) in enumerate(((80, 120), (200, 150), (320, 110))):
        s.p(f'M{x - 34},{232} L{x - 40},{232 - 60} L{x + 40},{232 - 60} L{x + 34},{232} Z', 1.4, fill=PAPER)
        for q in range(7): s.line(x + 14, 232 - 6 - q*8, x + 37, 232 - 6 - q*8, .5)
        s.p(f'M{x},{172} C{x - 4},{172 - h*.4} {x + 4},{172 - h*.7} {x},{172 - h}', 1.6)
        for j, (t, L) in enumerate(((.35, 46), (.6, 40), (.85, 30))):
            yy = 172 - h*t
            leaf(s, x, yy, L, 200 - j*8, bend=-.12, shade=-1, w=1.1)
            leaf(s, x, yy - 4, L*.95, -20 + j*8, bend=.12, shade=1, w=1.1)
    return s.svg('Ilustración a tinta: tres plantones de café en bolsas de vivero')

def cosecha():
    s = S(400, 276, 3)
    branch(s, 262, 270, k=.55, rot=-30, seed=7)
    return s.svg('Ilustración a tinta: rama de café con hojas, flores y racimos de cerezas')

def proceso():
    s = S(400, 276, 4)
    for x, y, rot in ((110, 90, -20), (250, 80, 15), (120, 196, 10), (262, 196, -12)):
        bean(s, x, y, 62, 42, rot)
    for x, y in ((190, 140), (330, 140), (40, 150)):
        bean(s, x, y, 18, 12, 30)
    return s.svg('Ilustración a tinta: granos de café tostado')

def empaque():
    s = S(400, 276, 5)
    coffee_bag(s, 130, 250, 150)
    cup(s, 300, 170, 56)
    for i in range(3): bean(s, 250 + i*36, 262, 12, 8, 20 + i*30)
    return s.svg('Ilustración a tinta: bolsa de Café del Canal y una taza de café humeante')

def productores():
    s = S(764, 361, 6)
    mountains(s, 120, [(120, 30), (260, 60), (420, 34), (560, 70), (700, 40)], hatch=True)
    hill_lines(s, 560, 200, 90, 200, 9, x0=200, x1=764)
    rows(s, 380, 200, 400, -200, 960, 8, seed=3)
    person(s, 250, 330, 230, basket=True)
    person(s, 470, 340, 250, basket=False, face=-1)
    leaf(s, 520, 230, 60, -40, w=1.1); cluster(s, 540, 256, 9, n=6)
    return s.svg('Ilustración a tinta: dos productores con sombrero cosechando entre hileras de cafetales')

def distribuidores():
    s = S(764, 361, 7)
    # street and buildings in a few lines
    s.line(0, 300, 764, 300, 1.2)
    for i in range(12): s.line(20 + i*66, 330, 50 + i*66, 330, 1)
    for x, w, h in ((10, 120, 170), (140, 90, 220), (240, 130, 150), (560, 100, 200), (670, 90, 160)):
        s.poly([(x, 300), (x, 300 - h), (x + w, 300 - h), (x + w, 300)], 1.1)
        for r in range(int(h/40)):
            for c in range(int(w/34)):
                s.poly([(x + 12 + c*34, 300 - h + 14 + r*40), (x + 12 + c*34, 300 - h + 38 + r*40), (x + 30 + c*34, 300 - h + 38 + r*40), (x + 30 + c*34, 300 - h + 14 + r*40)], .7, close=True)
    # taxi
    tx, ty = 60, 330
    s.p(f'M{tx},{ty - 20} L{tx},{ty - 56} Q{tx + 6},{ty - 70} {tx + 40},{ty - 72} L{tx + 90},{ty - 108} L{tx + 210},{ty - 108} L{tx + 258},{ty - 72} Q{tx + 298},{ty - 68} {tx + 300},{ty - 46} L{tx + 300},{ty - 20} Z', 1.6, fill=PAPER)
    s.p(f'M{tx + 98},{ty - 98} L{tx + 146},{ty - 98} L{tx + 146},{ty - 72} L{tx + 72},{ty - 72} Z M{tx + 156},{ty - 98} L{tx + 204},{ty - 98} L{tx + 240},{ty - 72} L{tx + 156},{ty - 72} Z', 1.1, fill=PAPER)
    s.p(f'M{tx + 128},{ty - 108} L{tx + 128},{ty - 120} L{tx + 172},{ty - 120} L{tx + 172},{ty - 108}', 1.1)
    s.add(f'<text x="{tx + 150}" y="{ty - 111}" font-family="Georgia,serif" font-size="9" text-anchor="middle" fill="{INK}">TAXI</text>')
    for i in range(14): s.line(tx + 12 + i*20, ty - 44, tx + 22 + i*20, ty - 44, 2.5) if i % 2 else None
    for wx in (tx + 66, tx + 238):
        s.circ(wx, ty - 18, 22, 1.6); s.circ(wx, ty - 18, 10, 1)
    # person in a wheelchair holding a box of coffee
    wx, wy = 470, 330
    s.circ(wx, wy - 24, 30, 1.5)
    for a in range(0, 180, 30):
        r = math.radians(a); s.line(wx - 28*math.cos(r), wy - 24 - 28*math.sin(r), wx + 28*math.cos(r), wy - 24 + 28*math.sin(r), .5)
    s.circ(wx + 46, wy - 8, 8, 1.2)
    s.p(f'M{wx - 30},{wy - 66} L{wx + 30},{wy - 66} L{wx + 46},{wy - 16} M{wx - 30},{wy - 66} L{wx - 34},{wy - 130}', 1.5)
    s.p(f'M{wx - 24},{wy - 70} L{wx - 22},{wy - 140} Q{wx},{wy - 150} {wx + 16},{wy - 140} L{wx + 20},{wy - 70} Z', 1.4, fill=PAPER)
    s.p(f'M{wx + 18},{wy - 70} L{wx + 50},{wy - 66} L{wx + 52},{wy - 20}', 1.4)
    s.ell(wx - 2, wy - 162, 15, 18, w=1.4); s.circ(wx + 6, wy - 164, 1.2, 1, fill=INK)
    s.p(f'M{wx - 17},{wy - 168} Q{wx - 12},{wy - 186} {wx + 4},{wy - 182} Q{wx + 14},{wy - 178} {wx + 13},{wy - 168}', 1.2)
    limb(s, [(wx + 10, wy - 136), (wx + 22, wy - 116), (wx + 14, wy - 104)], 10)
    s.poly([(wx + 8, wy - 126), (wx + 70, wy - 126), (wx + 70, wy - 86), (wx + 8, wy - 86)], 1.4, close=True, fill=PAPER)
    cherry(s, wx + 32, wy - 108, 5); cherry(s, wx + 44, wy - 108, 5); cherry(s, wx + 38, wy - 98, 5)
    # older man with a cane
    person(s, 640, 336, 240, hat_on=False, face=-1, cane=True)
    return s.svg('Ilustración a tinta: un taxi, una persona en silla de ruedas con una caja de café y un señor con bastón en la calle')

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), '..', 'img', 'v6')
    os.makedirs(out, exist_ok=True)
    for name, fn in (('hero', hero), ('vivero', vivero), ('cosecha', cosecha), ('proceso', proceso),
                     ('empaque', empaque), ('productores', productores), ('distribuidores', distribuidores)):
        open(os.path.join(out, name + '.svg'), 'w').write(fn())
        print(name)
