#!/usr/bin/env python3
"""PixelMordor - Fondo de Mordor en Pixel Art (Python puro).
Genera Barad-dûr con el Ojo de Sauron ardiente, el Monte del Destino (Orodruin)
en erupción con ríos de lava, la llanura de Gorgoroth con grietas incandescentes,
cenizas flotantes y bestias aladas. Sin dependencias externas.
Lienzo 640x400 escalado x3 = 1920x1200."""
import json, math, os, random, struct, sys, zlib

W, H, S = 640, 400, 3
FASE = os.environ.get('PM_FASE', 'noche')
out_dir = sys.argv[1] if len(sys.argv) > 1 else '/tmp/test_mordor'
os.makedirs(out_dir, exist_ok=True)

# Paletas de color según la fase
PALETAS = {
    'dia': {
        'sky': ['#180f1e', '#26142c', '#3c1836', '#591f38', '#782633', '#96302e', '#b84226', '#d65d24'],
        'nubes_humo': ('#2c1a24', '#1f131a', '#44222b'),
        'montana_mordor': ('#2b1820', '#1c1016', '#120a0e'),
        'baraddur': ('#1e141d', '#130c12', '#2a1b28'),
        'baraddur_filo': '#4d2a3d',
        'gorgoroth': ('#22161b', '#160d11', '#2f1e24'),
        'lava': ('#ff3700', '#ff7b00', '#ffcc00'),
        'ojo': ('#ff2200', '#ff8800', '#ffee55'),
        'sol_sangre': '#d6301a',
        'cenizas': ['#ff6600', '#ffaa33', '#883322']
    },
    'dorado': {
        'sky': ['#1a0820', '#2e0e2e', '#4f143a', '#78193a', '#a62432', '#cf3824', '#e66020', '#f59828'],
        'nubes_humo': ('#361426', '#250c1b', '#571c2b'),
        'montana_mordor': ('#2d121c', '#1e0a13', '#14060c'),
        'baraddur': ('#1a0c16', '#0f060d', '#281322'),
        'baraddur_filo': '#591e38',
        'gorgoroth': ('#240e17', '#18080f', '#331320'),
        'lava': ('#ff2a00', '#ff6a00', '#ffc400'),
        'ojo': ('#ff1a00', '#ff7700', '#ffe640'),
        'sol_sangre': '#e63312',
        'cenizas': ['#ff7700', '#ffbb33', '#993311']
    },
    'noche': {
        'sky': ['#050208', '#0a040e', '#120718', '#1b0922', '#240c2c', '#300f36', '#3e123d', '#4d1440'],
        'nubes_humo': ('#18081a', '#0f0410', '#250b28'),
        'montana_mordor': ('#140810', '#0c040a', '#060205'),
        'baraddur': ('#0e0710', '#060207', '#160a18'),
        'baraddur_filo': '#2f1532',
        'gorgoroth': ('#12060b', '#0a0306', '#1a0810'),
        'lava': ('#ff2200', '#ff6600', '#ffcc00'),
        'ojo': ('#ff1500', '#ff7700', '#ffffff'),
        'sol_sangre': '#8a180c',
        'cenizas': ['#ff5500', '#ff9900', '#ffdd44']
    }
}

PAL = PALETAS[FASE]

# Bayer dithering
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dith(x, y, t): return (BAYER[y % 4][x % 4] + 0.5) / 16.0 < t

def hx(c):
    if isinstance(c, tuple): return c
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

def mix(a, b, t):
    a, b = hx(a), hx(b)
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] * (1.0 - t) + b[i] * t) for i in range(3))

px = [[(0, 0, 0)] * W for _ in range(H)]

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H: px[y][x] = hx(c)

def over(x, y, c, a):
    if 0 <= x < W and 0 <= y < H: px[y][x] = mix(px[y][x], c, a)

def disc(cx, cy, r, c, plot=put):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r + r // 2: plot(cx + x, cy + y, c)

def glow(cx, cy, r, c, fuerza=0.7):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            d = math.hypot(x, y)
            if d < r and dith(cx + x, cy + y, ((1.0 - d / r) ** 2) * fuerza):
                over(cx + x, cy + y, c, 0.75)

# Zona HUD
ZX0, ZX1, ZY0, ZY1 = 478, 632, 10, 215

# 1. CIELO VOLCÁNICO Y CENIZAS
HORIZONTE = 275
SKY = PAL['sky']
for y in range(HORIZONTE):
    t = (y / float(HORIZONTE)) ** 1.35 * (len(SKY) - 1)
    i = int(t); f = t - i
    c1 = SKY[min(i, len(SKY) - 1)]
    c2 = SKY[min(i + 1, len(SKY) - 1)]
    for x in range(W):
        put(x, y, c2 if dith(x, y, f) else c1)

# Sol velado de sangre (tapado por el humo perenne de Mordor)
if FASE in ('dia', 'dorado'):
    disc(130, 80, 24, PAL['sol_sangre'])
    glow(130, 80, 55, PAL['sol_sangre'], 0.5)

# Nubes de ceniza y humo volcánico denso
def nube_ceniza(cx, cy, w, h, col):
    for dy in range(-h, h + 1):
        for dx in range(-w, w + 1):
            if (dx * dx) / float(w * w) + (dy * dy) / float(h * h) <= 1.0:
                nx, ny = cx + dx, cy + dy
                if dith(nx, ny, 0.75):
                    over(nx, ny, col, 0.8)

nube_ceniza(100, 110, 70, 24, PAL['nubes_humo'][0])
nube_ceniza(250, 70, 90, 28, PAL['nubes_humo'][1])
nube_ceniza(380, 100, 110, 32, PAL['nubes_humo'][2])
nube_ceniza(520, 140, 80, 26, PAL['nubes_humo'][0])

# Relámpagos rojos/morados en las nubes de tormenta de Mordor
random.seed(88)
for _ in range(4):
    rx = random.randint(280, 460)
    ry = random.randint(30, 90)
    for seg in range(12):
        put(rx, ry + seg, '#fca5a5' if seg % 2 == 0 else '#e11d48')
        rx += random.choice([-1, 0, 1, 2])

# 2. MONTE DEL DESTINO (ORODRUIN / MOUNT DOOM)
# Cono volcánico a la derecha (centro x=400)
OX, OY = 395, 150
for y in range(OY, HORIZONTE + 10):
    dy = y - OY
    w_volc = int(14 + dy * 0.9 + 5 * math.sin(dy * 0.1))
    for dx in range(-w_volc, w_volc + 1):
        x = OX + dx
        t_prof = abs(dx) / float(w_volc + 1)
        c_v = PAL['montana_mordor'][0] if t_prof < 0.6 else PAL['montana_mordor'][1]
        put(x, y, c_v)

# Cráter del volcán con magma hirviendo
for dx in range(-16, 17):
    put(OX + dx, OY, PAL['lava'][0])
    put(OX + dx, OY + 1, PAL['lava'][1])
glow(OX, OY, 20, PAL['lava'][0], 0.8)

# Columna colosal de humo negro que brota de Orodruin hacia las nubes
for sh_y in range(15, OY):
    prog = (OY - sh_y) / float(OY)
    w_humo = int(18 + prog * 45)
    for hw in range(-w_humo, w_humo + 1):
        hx_ = OX + hw + int(math.sin(sh_y * 0.08) * 12)
        if dith(hx_, sh_y, (1.0 - abs(hw) / float(w_humo + 1)) * 0.85):
            over(hx_, sh_y, PAL['nubes_humo'][1], 0.8)

# Ríos de lava descendiendo por las laderas del Monte del Destino
random.seed(42)
for rama in range(3):
    lx, ly = float(OX + (rama - 1) * 8), float(OY + 2)
    for paso in range(65):
        ly += 1.8
        lx += math.sin(paso * 0.25 + rama) * 2.2 + (rama - 1) * 0.8
        put(int(lx), int(ly), PAL['lava'][2] if paso % 3 == 0 else PAL['lava'][1])
        put(int(lx) + 1, int(ly), PAL['lava'][0])
        if paso % 8 == 0:
            glow(int(lx), int(ly), 6, PAL['lava'][1], 0.5)

# 3. BARAD-DÛR - LA TORRE OSCURA (THE DARK TOWER)
# Situada imponente en la izquierda/centro (X=195)
BX = 195
# Base colosal de hierro negro y contrafuertes (Y=140 a 280)
TIERS_BD = [
    (52, 245, 275),  # Base
    (42, 215, 246),  # Nivel 2
    (32, 185, 216),  # Nivel 3
    (24, 155, 186),  # Nivel 4
    (18, 125, 156),  # Nivel 5
    (14, 98,  126),  # Nivel 6
]
for w_b, y0, y1 in TIERS_BD:
    for y in range(y0, y1 + 1):
        for x in range(BX - w_b, BX + w_b + 1):
            dx = x - BX
            # Relieve gótico/puntiagudo
            c_b = PAL['baraddur'][0] if abs(dx) < w_b - 3 else PAL['baraddur'][1]
            if y == y0 and abs(dx) % 4 == 0:
                c_b = PAL['baraddur_filo']  # púas de hierro
            put(x, y, c_b)
    # Contrafuertes exteriores
    for dy in range(y0, y1 + 1):
        put(BX - w_b - 1, dy, PAL['baraddur_filo'])
        put(BX + w_b + 1, dy, PAL['baraddur'][1])

# Las Dos Grandes Cornamentas de Hierro en la cima (Cuernos de Barad-dûr)
for cy in range(54, 98):
    prog_c = (98 - cy) / 44.0
    w_c = max(1, int(3 - prog_c * 2))
    # Cuerno izquierdo
    c_izq = BX - int(14 + prog_c * 10)
    for dx in range(-w_c, w_c + 1):
        put(c_izq + dx, cy, PAL['baraddur'][0])
    # Cuerno derecho
    c_der = BX + int(14 + prog_c * 10)
    for dx in range(-w_c, w_c + 1):
        put(c_der + dx, cy, PAL['baraddur_filo'])

# ==============================================================
# EL OJO DE SAURON (THE EYE OF SAURON)
# Ardiendo entre las dos astas de la corona de Barad-dûr
EYE_X, EYE_Y = BX, 74
# Gran resplandor de fuego que envuelve la torre
glow(EYE_X, EYE_Y, 32, PAL['ojo'][0], 0.9)
glow(EYE_X, EYE_Y, 18, PAL['ojo'][1], 0.95)

# Forma almendrada del ojo de fuego
for dy in range(-12, 13):
    w_eye = int(18 * math.cos(dy * math.pi / 26.0))
    for dx in range(-w_eye, w_eye + 1):
        d_norm = math.hypot(dx / 1.5, dy)
        if d_norm <= 8:
            c_e = PAL['ojo'][2] if d_norm < 3.5 else PAL['ojo'][1]
            put(EYE_X + dx, EYE_Y + dy, c_e)
        elif d_norm <= 11:
            if dith(EYE_X + dx, EYE_Y + dy, 0.7):
                put(EYE_X + dx, EYE_Y + dy, PAL['ojo'][0])

# Pupila rasgada vertical (la hendidura negra felina)
for py in range(-8, 9):
    w_pup = 1 if abs(py) > 4 else 2
    for pw in range(-w_pup, w_pup + 1):
        put(EYE_X + pw, EYE_Y + py, '#050102')

# Corona de llamas parpadeantes alrededor del ojo
random.seed(17)
for fl in range(24):
    ang = fl / 24.0 * 2 * math.pi
    dist = 11 + random.randint(2, 6)
    fx = int(EYE_X + math.cos(ang) * dist * 1.3)
    fy = int(EYE_Y + math.sin(ang) * dist)
    put(fx, fy, PAL['ojo'][1] if fl % 2 else PAL['ojo'][0])

# Bestia Alada de los Nazgûl (Fell Beast) en vuelo sobre el cielo
NX, NY = 110, 115
# Cuerpo y cabeza
put(NX, NY, '#070308'); put(NX - 1, NY, '#070308'); put(NX + 1, NY, '#070308')
put(NX - 3, NY - 1, '#070308') # cuello extendido
# Enormes alas membranosas
for w_s in range(1, 9):
    put(NX - w_s, NY - w_s // 2, '#070308')
    put(NX - w_s, NY - w_s // 2 - 1, '#120716')
    put(NX + w_s, NY - w_s // 2, '#070308')
    put(NX + w_s, NY - w_s // 2 - 1, '#120716')
# Cola larga
for t_s in range(1, 7):
    put(NX + t_s, NY + t_s // 2, '#070308')

# 4. LA MESETA DE GORGOROTH (GORGOROTH PLATEAU)
# Suelo de basalto quebrado con grietas de lava incandescente
for y in range(HORIZONTE, H):
    for x in range(W):
        c_g = PAL['gorgoroth'][0] if (x + y) % 3 == 0 else PAL['gorgoroth'][1]
        put(x, y, c_g)

# Grietas de lava hirviente por todo Gorgoroth
random.seed(55)
for grieta in range(6):
    gx = random.randint(30, W - 40)
    gy = random.randint(HORIZONTE + 8, H - 30)
    for paso in range(40):
        gy += 1
        gx += random.choice([-2, -1, 0, 1, 2])
        put(gx, gy, PAL['lava'][1])
        put(gx + 1, gy, PAL['lava'][0])
        if paso % 10 == 0:
            glow(gx, gy, 5, PAL['lava'][0], 0.6)

# Cenizas y chispas incandescentes flotando en el aire
random.seed(99)
for _ in range(140):
    cx = random.randrange(W)
    cy = random.randrange(H)
    if not (ZX0 - 10 <= cx <= ZX1 + 10 and ZY0 <= cy <= ZY1):
        col_c = random.choice(PAL['cenizas'])
        put(cx, cy, col_c)
        if random.random() < 0.2:
            over(cx + 1, cy, col_c, 0.6)

# 5. EXPORTAR PNG EN ALTA RESOLUCIÓN (x3)
def write_png(ruta, buf):
    raw = bytearray()
    for y in range(H):
        fila = b''.join(bytes(buf[y][x]) * S for x in range(W))
        raw += (b'\x00' + fila) * S
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(ruta, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n'
                + chunk(b'IHDR', struct.pack('>IIBBBBB', W * S, H * S, 8, 2, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
                + chunk(b'IEND', b''))

write_png(os.path.join(out_dir, f'mordor-{FASE}.png'), px)

# 6. VISTA PREVIA CON EL HUD DE MORDOR
pv = [list(r) for r in px]

F = {'A': '010101111101101', 'B': '110101110101110', 'C': '011100100100011', 'D': '110101101101110',
     'E': '111100110100111', 'F': '111100110100100', 'G': '011100101101011', 'H': '101101111101101',
     'I': '111010010010111', 'K': '101101110101101', 'L': '100100100100111', 'M': '101111111101101',
     'N': '110101101101101', 'O': '010101101101010', 'P': '110101110100100', 'R': '110101110101101',
     'S': '011100010001110', 'T': '111010010010010', 'U': '101101101101111', 'V': '101101101101010',
     'W': '101101111111101', 'X': '101101010101101', 'Y': '101101010010010', 'Z': '111001010100111',
     '0': '111101101101111', '1': '010110010010111', '2': '110001010100111', '3': '110001010001110',
     '4': '101101111001001', '5': '111100110001110', '6': '011100111101111', '7': '111001010010010',
     '8': '111101111101111', '9': '111101111001110', ':': '000010000010000', '.': '000000000000010',
     '%': '101001010100101', '-': '000000111000000', '+': '000010111010000', ' ': '000000000000000',
     "'": '010010000000000', '!': '010010010000010', ',': '000000000010010'}

def texto(buf, x, y, s, col, esc=1):
    for ch in s.upper():
        g = F.get(ch, F[' '])
        for i, bit in enumerate(g):
            if bit == '1':
                for a in range(esc):
                    for b in range(esc):
                        xx, yy = x + (i % 3) * esc + a, y + (i // 3) * esc + b
                        if 0 <= xx < W and 0 <= yy < H: buf[yy][xx] = hx(col)
        x += 4 * esc

def rect(buf, x0, y0, x1, y1, col, a=1.0):
    for y in range(y0, y1):
        for x in range(x0, x1):
            if 0 <= x < W and 0 <= y < H: buf[y][x] = mix(buf[y][x], col, a)

def panel_mordor(buf, x0, y0, x1, y1):
    # Fondo obsidiana / hierro forjado
    rect(buf, x0, y0, x1, y1, '#0e0608', 0.90)
    # Borde de hierro oscuro y óxido
    for a, b, c, d in ((x0, y0, x1, y0 + 1), (x0, y1 - 1, x1, y1), (x0, y0, x0 + 1, y1), (x1 - 1, y0, x1, y1)):
        rect(buf, a, b, c, d, '#5e2320')
    # Acento de fuego vivo en las esquinas
    rect(buf, x0, y0, x0 + 5, y0 + 1, '#ff3b00')
    rect(buf, x0, y0, x0 + 1, y0 + 5, '#ff3b00')

FUEGO_VIVO = '#ff4400'
ORO_ANILLO = '#ffaa00'
CENIZA_CLARA = '#e0d2ce'
SULFUR = '#ffd940'

X0, X1 = 488, 628
# Tarjeta 1: Reloj y Era del Ojo
panel_mordor(pv, X0, 14, X1, 74)
texto(pv, X0 + 10, 22, '14:32', CENIZA_CLARA, 4)
texto(pv, X0 + 10, 52, 'ERA DEL OJO', FUEGO_VIVO, 2)
rect(pv, X1 - 22, 22, X1 - 12, 32, '#ff3b00')

# Tarjeta 2: Sistema (Forjas de Mordor)
panel_mordor(pv, X0, 80, X1, 144)
for i, (n, v, c) in enumerate((('CPU', 45, '#ff3b00'), ('RAM', 62, '#ff8800'), ('TMP', 78, '#ff2200'))):
    yy = 88 + i * 17
    texto(pv, X0 + 8, yy, n, ORO_ANILLO, 2)
    rect(pv, X0 + 44, yy + 2, X0 + 104, yy + 8, '#261012')
    rect(pv, X0 + 44, yy + 2, X0 + 44 + 60 * v // 100, yy + 8, c)
    texto(pv, X0 + 108, yy, f'{v}%', CENIZA_CLARA, 2)

# Tarjeta 3: Red y Huestes
panel_mordor(pv, X0, 150, X1, 214)
for i, (a, b) in enumerate((('NET', 'CIRITH UNGOL'), ('DEV', 'SAMMATH NAUR'), ('GIT', 'BARAD-DUR'), ('NAZ', '9 ACTIVOS'))):
    yy = 156 + i * 13
    texto(pv, X0 + 8, yy, a, ORO_ANILLO, 2)
    texto(pv, X0 + 48, yy, b, CENIZA_CLARA, 2)

# Tarjeta 4: Cita de la Lengua Negra / Sauron
panel_mordor(pv, X0, 220, X1, 276)
texto(pv, X0 + 8, 226, 'UN ANILLO PARA', FUEGO_VIVO, 2)
texto(pv, X0 + 8, 240, 'GOBERNARLOS...', ORO_ANILLO, 2)
texto(pv, X0 + 8, 254, 'Y ATARLOS EN...', CENIZA_CLARA, 2)
texto(pv, X1 - 44, 264, 'SAURON', FUEGO_VIVO, 1)

write_png(os.path.join(out_dir, 'mordor-preview.png'), pv)
print(f'Mordor {FASE} generada con éxito en {out_dir}')
