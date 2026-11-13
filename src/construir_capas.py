#!/usr/bin/env python3
"""Construye las capas dinámicas de Mordor para GNOME Shell y Plasma.
Genera cielo-*.png, escena-*.png (RGBA con transparencia), sol.png, luna.png y datos.json."""
import json, math, os, struct, sys, zlib

W, H = 640, 400
HORIZONTE = 275

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

PALETAS = {
    'dia': {
        'sky': ['#180f1e', '#26142c', '#3c1836', '#591f38', '#782633', '#96302e', '#b84226', '#d65d24'],
        'nubes_humo': ('#2c1a24', '#1f131a', '#44222b'),
        'montana_mordor': ('#2b1820', '#1c1016', '#120a0e'),
        'baraddur': ('#1e141d', '#130c12', '#2a1b28'),
        'baraddur_filo': '#4d2a3d',
        'gorgoroth': ('#22161b', '#160d11', '#2f1e24'),
        'lava': ('#ff3700', '#ff7b00', '#ffcc00'),
        'ojo': ('#ff2200', '#ff8800', '#ffee55')
    },
    'dorado': {
        'sky': ['#1a0820', '#2e0e2e', '#4f143a', '#78193a', '#a62432', '#cf3824', '#e66020', '#f59828'],
        'nubes_humo': ('#361426', '#250c1b', '#571c2b'),
        'montana_mordor': ('#2d121c', '#1e0a13', '#14060c'),
        'baraddur': ('#1a0c16', '#0f060d', '#281322'),
        'baraddur_filo': '#591e38',
        'gorgoroth': ('#240e17', '#18080f', '#331320'),
        'lava': ('#ff2a00', '#ff6a00', '#ffc400'),
        'ojo': ('#ff1a00', '#ff7700', '#ffe640')
    },
    'noche': {
        'sky': ['#050208', '#0a040e', '#120718', '#1b0922', '#240c2c', '#300f36', '#3e123d', '#4d1440'],
        'nubes_humo': ('#18081a', '#0f0410', '#250b28'),
        'montana_mordor': ('#140810', '#0c040a', '#060205'),
        'baraddur': ('#0e0710', '#060207', '#160a18'),
        'baraddur_filo': '#2f1532',
        'gorgoroth': ('#12060b', '#0a0306', '#1a0810'),
        'lava': ('#ff2200', '#ff6600', '#ffcc00'),
        'ojo': ('#ff1500', '#ff7700', '#ffffff')
    }
}

def png_rgb(ruta, buf, w, h):
    raw = bytearray()
    for y in range(h):
        fila = b''.join(bytes(buf[y][x][:3]) for x in range(w))
        raw += b'\x00' + fila
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(ruta, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))

def png_rgba(ruta, buf, w, h):
    raw = bytearray()
    for y in range(h):
        fila = b''.join(bytes(buf[y][x]) for x in range(w))
        raw += b'\x00' + fila
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(ruta, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))

def genera_cielo(fase):
    buf = [[(0, 0, 0)] * W for _ in range(H)]
    SKY = PALETAS[fase]['sky']
    for y in range(H):
        y_ref = min(y, HORIZONTE)
        t = (y_ref / float(HORIZONTE)) ** 1.35 * (len(SKY) - 1)
        i = int(t); f = t - i
        c1 = SKY[min(i, len(SKY) - 1)]
        c2 = SKY[min(i + 1, len(SKY) - 1)]
        for x in range(W):
            col = c2 if dith(x, y, f) else c1
            buf[y][x] = hx(col)
    return buf

def genera_escena(fase):
    # RGBA con transparencia en el cielo
    buf = [[(0, 0, 0, 0)] * W for _ in range(H)]
    pal = PALETAS[fase]

    def put_rgba(x, y, col, a=255):
        if 0 <= x < W and 0 <= y < H:
            r, g, b = hx(col)
            buf[y][x] = (r, g, b, a)

    def over_rgba(x, y, col, a_f):
        if 0 <= x < W and 0 <= y < H:
            cur_r, cur_g, cur_b, cur_a = buf[y][x]
            r, g, b = hx(col)
            new_a = min(255, int(cur_a + a_f * 255))
            buf[y][x] = (int(cur_r * (1 - a_f) + r * a_f),
                         int(cur_g * (1 - a_f) + g * a_f),
                         int(cur_b * (1 - a_f) + b * a_f), new_a)

    def disc_rgba(cx, cy, r, col, a=255):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r + r // 2:
                    put_rgba(cx + x, cy + y, col, a)

    def glow_rgba(cx, cy, r, col, fuerza=0.7):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                d = math.hypot(x, y)
                if d < r and dith(cx + x, cy + y, ((1.0 - d / r) ** 2) * fuerza):
                    over_rgba(cx + x, cy + y, col, 0.75)

    # 1. MONTE DEL DESTINO
    OX, OY = 395, 150
    for y in range(OY, HORIZONTE + 10):
        dy = y - OY
        w_volc = int(14 + dy * 0.9 + 5 * math.sin(dy * 0.1))
        for dx in range(-w_volc, w_volc + 1):
            x = OX + dx
            t_prof = abs(dx) / float(w_volc + 1)
            c_v = pal['montana_mordor'][0] if t_prof < 0.6 else pal['montana_mordor'][1]
            put_rgba(x, y, c_v, 255)

    # Cráter
    for dx in range(-16, 17):
        put_rgba(OX + dx, OY, pal['lava'][0], 255)
        put_rgba(OX + dx, OY + 1, pal['lava'][1], 255)
    glow_rgba(OX, OY, 20, pal['lava'][0], 0.8)

    # Ríos de lava
    for rama in range(3):
        lx, ly = float(OX + (rama - 1) * 8), float(OY + 2)
        for paso in range(65):
            ly += 1.8
            lx += math.sin(paso * 0.25 + rama) * 2.2 + (rama - 1) * 0.8
            c_l = pal['lava'][2] if paso % 3 == 0 else pal['lava'][1]
            put_rgba(int(lx), int(ly), c_l, 255)
            put_rgba(int(lx) + 1, int(ly), pal['lava'][0], 255)

    # 2. BARAD-DÛR
    BX = 195
    TIERS_BD = [(52, 245, 275), (42, 215, 246), (32, 185, 216), (24, 155, 186), (18, 125, 156), (14, 98, 126)]
    for w_b, y0, y1 in TIERS_BD:
        for y in range(y0, y1 + 1):
            for x in range(BX - w_b, BX + w_b + 1):
                dx = x - BX
                c_b = pal['baraddur'][0] if abs(dx) < w_b - 3 else pal['baraddur'][1]
                if y == y0 and abs(dx) % 4 == 0: c_b = pal['baraddur_filo']
                put_rgba(x, y, c_b, 255)
        for dy in range(y0, y1 + 1):
            put_rgba(BX - w_b - 1, dy, pal['baraddur_filo'], 255)
            put_rgba(BX + w_b + 1, dy, pal['baraddur'][1], 255)

    # Cuernos
    for cy in range(54, 98):
        prog_c = (98 - cy) / 44.0
        w_c = max(1, int(3 - prog_c * 2))
        c_izq = BX - int(14 + prog_c * 10)
        for dx in range(-w_c, w_c + 1): put_rgba(c_izq + dx, cy, pal['baraddur'][0], 255)
        c_der = BX + int(14 + prog_c * 10)
        for dx in range(-w_c, w_c + 1): put_rgba(c_der + dx, cy, pal['baraddur_filo'], 255)

    # EL OJO DE SAURON
    EYE_X, EYE_Y = BX, 74
    glow_rgba(EYE_X, EYE_Y, 26, pal['ojo'][0], 0.9)
    glow_rgba(EYE_X, EYE_Y, 16, pal['ojo'][1], 0.95)
    for dy in range(-11, 12):
        w_eye = int(16 * math.cos(dy * math.pi / 24.0))
        for dx in range(-w_eye, w_eye + 1):
            d_norm = math.hypot(dx / 1.5, dy)
            if d_norm <= 7:
                c_e = pal['ojo'][2] if d_norm < 3.0 else pal['ojo'][1]
                put_rgba(EYE_X + dx, EYE_Y + dy, c_e, 255)
            elif d_norm <= 10:
                if dith(EYE_X + dx, EYE_Y + dy, 0.7):
                    put_rgba(EYE_X + dx, EYE_Y + dy, pal['ojo'][0], 240)
    # Pupila rasgada
    for py in range(-7, 8):
        w_pup = 1 if abs(py) > 3 else 2
        for pw in range(-w_pup, w_pup + 1):
            put_rgba(EYE_X + pw, EYE_Y + py, '#050102', 255)

    # 3. GORGOROTH
    for y in range(HORIZONTE, H):
        for x in range(W):
            c_g = pal['gorgoroth'][0] if (x + y) % 3 == 0 else pal['gorgoroth'][1]
            put_rgba(x, y, c_g, 255)

    # Grietas de lava
    for grieta in range(6):
        gx = 40 + grieta * 95
        gy = HORIZONTE + 8 + (grieta % 3) * 12
        for paso in range(40):
            gy += 1
            gx += ((paso * 7 + grieta) % 5) - 2
            put_rgba(gx, gy, pal['lava'][1], 255)
            put_rgba(gx + 1, gy, pal['lava'][0], 255)

    return buf

def genera_sol():
    # 208x208 con sol de sangre en (104, 104)
    buf = [[(0, 0, 0, 0)] * 208 for _ in range(208)]
    cx, cy, R = 104, 104, 24
    for y in range(-50, 51):
        for x in range(-50, 51):
            d = math.hypot(x, y)
            if d <= R:
                buf[cy + y][cx + x] = (220, 48, 20, 255)
            elif d < 48 and dith(cx + x, cy + y, ((48 - d) / 24.0) ** 1.8 * 0.7):
                buf[cy + y][cx + x] = (240, 80, 20, 210)
    return buf

def genera_luna():
    # 208x208 con luna de ceniza y halo carmesí
    buf = [[(0, 0, 0, 0)] * 208 for _ in range(208)]
    cx, cy, R = 104, 104, 28
    for y in range(-50, 51):
        for x in range(-50, 51):
            d = math.hypot(x, y)
            if d <= R:
                buf[cy + y][cx + x] = (40, 20, 30, 255)
            elif d < 44 and dith(cx + x, cy + y, ((44 - d) / 16.0) ** 2.0 * 0.5):
                buf[cy + y][cx + x] = (160, 30, 30, 180)
    return buf

def main():
    target_dirs = [
        sys.argv[1] if len(sys.argv) > 1 else '/tmp/test_mordor_layers',
    ]
    for out in target_dirs:
        os.makedirs(out, exist_ok=True)
        print(f"Generando capas en {out}...")
        for fase in ('noche', 'dorado', 'dia'):
            png_rgb(os.path.join(out, f'cielo-{fase}.png'), genera_cielo(fase), W, H)
            png_rgba(os.path.join(out, f'escena-{fase}.png'), genera_escena(fase), W, H)
        png_rgba(os.path.join(out, 'sol.png'), genera_sol(), 208, 208)
        png_rgba(os.path.join(out, 'luna.png'), genera_luna(), 208, 208)

        # Generar datos.json con las coordenadas del Ojo y las ascuas
        import random
        random.seed(42)
        ascuas = [[random.randint(20, 620), random.randint(10, 260), random.choice(['#ff5500', '#ff9900', '#ff2200']), 0] for _ in range(120)]
        datos = {
            "W": 640, "H": 400,
            "estrellas": ascuas,
            "ventanas": [],
            "faroles": [[195, 74, 18]], # El Ojo de Sauron como foco de luz viva
            "destellos": [[395, 152], [390, 160], [400, 160], [392, 175], [405, 180]], # destellos de magma
            "nubes": [[65, 62, 190, 6, 0], [305, 100, 150, 6, 6], [-15, 170, 210, 6, 12]],
            "nubes_w": 210,
            "barca": [0, 0],
            "luna": [100, 60, 22]
        }
        json.dump(datos, open(os.path.join(out, 'datos.json'), 'w'))
        print("Capas de Mordor completadas.")

if __name__ == '__main__':
    main()
