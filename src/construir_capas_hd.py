#!/usr/bin/env python3
"""PixelMordor HD - Generador de capas de arte pixelado para Mordor (El Señor de los Anillos).
Construye:
- Fondos de pantalla (1920x1200) para Noche, Día y Dorado
- Capas para GNOME Shell PixelZen: cielo-*.png, escena-*.png (RGBA con transparencia), sol.png, luna.png
- datos.json con coordenadas exactas del Ojo de Sauron, ascuas ardientes y ríos de magma.
"""

import json, math, os, random, struct, sys, zlib
from PIL import Image, ImageDraw

BASE_DIR = '/home/2asird/Descargas/mordor'
FONDOS_DIR = os.path.join(BASE_DIR, 'fondos')
CAPTURAS_DIR = os.path.join(BASE_DIR, 'capturas')
GNOME_DIR = os.path.join(BASE_DIR, 'gnome', 'pixelzen@mosqui1988.github.io')
GNOME_IMG = os.path.join(GNOME_DIR, 'images')

W, H = 640, 400
HORIZONTE = 275

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dith(x, y, t):
    return (BAYER[y % 4][x % 4] + 0.5) / 16.0 < t

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
        'sky': ['#160c1c', '#241228', '#381634', '#521c36', '#722432', '#8f2c2c', '#b03c24', '#ce5620'],
        'nubes_humo': ((44, 26, 36), (31, 19, 26), (68, 34, 43)),
        'montana_fondo': ((38, 20, 28), (24, 12, 18)),
        'orodruin': ((43, 24, 32), (28, 16, 22), (18, 10, 14)),
        'baraddur': ((30, 20, 29), (19, 12, 18), (42, 27, 40)),
        'baraddur_filo': '#66334d',
        'gorgoroth': ((34, 22, 27), (22, 13, 17), (47, 30, 36)),
        'lava': ((255, 55, 0), (255, 123, 0), (255, 204, 0)),
        'ojo': ((255, 34, 0), (255, 136, 0), (255, 238, 85)),
        'sol_sangre': '#d6301a',
        'oro_runas': '#f59e0b',
        'borde_box': '#782622'
    },
    'dorado': {
        'sky': ['#180820', '#2c0e2c', '#4a1236', '#701636', '#9c202e', '#c43422', '#de581c', '#ec9024'],
        'nubes_humo': ((54, 20, 38), (37, 12, 27), (87, 28, 43)),
        'montana_fondo': ((42, 16, 26), (28, 10, 18)),
        'orodruin': ((45, 18, 28), (30, 10, 19), (20, 6, 12)),
        'baraddur': ((26, 12, 22), (15, 6, 13), (40, 19, 34)),
        'baraddur_filo': '#7a284c',
        'gorgoroth': ((36, 14, 23), (24, 8, 15), (51, 19, 32)),
        'lava': ((255, 42, 0), (255, 106, 0), (255, 196, 0)),
        'ojo': ((255, 26, 0), (255, 119, 0), (255, 230, 64)),
        'sol_sangre': '#e63312',
        'oro_runas': '#fbbf24',
        'borde_box': '#854d0e'
    },
    'noche': {
        'sky': ['#050208', '#0a040e', '#120718', '#1b0922', '#240c2c', '#300f36', '#3e123d', '#4d1440'],
        'nubes_humo': ((24, 8, 26), (15, 4, 16), (37, 11, 40)),
        'montana_fondo': ((20, 8, 16), (12, 4, 10)),
        'orodruin': ((28, 10, 20), (16, 5, 12), (10, 3, 7)),
        'baraddur': ((14, 7, 16), (6, 2, 7), (22, 10, 24)),
        'baraddur_filo': '#451e4a',
        'gorgoroth': ((18, 6, 11), (10, 3, 6), (26, 8, 16)),
        'lava': ((255, 34, 0), (255, 102, 0), (255, 204, 0)),
        'ojo': ((255, 21, 0), (255, 119, 0), (255, 255, 255)),
        'sol_sangre': '#8a180c',
        'oro_runas': '#f59e0b',
        'borde_box': '#782622'
    }
}

def crear_cielo(fase):
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    SKY = PALETAS[fase]['sky']
    for y in range(H):
        y_ref = min(y, HORIZONTE)
        t = (y_ref / float(HORIZONTE)) ** 1.35 * (len(SKY) - 1)
        i = int(t); f = t - i
        c1 = hx(SKY[min(i, len(SKY) - 1)])
        c2 = hx(SKY[min(i + 1, len(SKY) - 1)])
        for x in range(W):
            col = c2 if dith(x, y, f) else c1
            img.putpixel((x, y), col)
    return img

def componer_escena_mordor(fase, fondo_completo=False):
    """
    Si fondo_completo=True, pinta el cielo opaco de fondo (para fondos de pantalla 1920x1200).
    Si fondo_completo=False, deja el cielo transparente (para escena-*.png de GNOME Shell).
    """
    if fondo_completo:
        img = crear_cielo(fase).convert('RGBA')
    else:
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))

    draw = ImageDraw.Draw(img)
    pal = PALETAS[fase]

    # 1. CORDILLERA LEJANA DE CENIZA (EPHEL DÚATH Y ERED LITHUI)
    c_m1, c_m2 = pal['montana_fondo']
    for x in range(W):
        # Perfil montañoso escarpado
        alt = int(220 - 45 * math.sin(x * 0.012) - 25 * math.cos(x * 0.035 + 1.2) - 12 * math.sin(x * 0.08))
        draw.line([(x, alt), (x, HORIZONTE)], fill=c_m1 + (255,))
        draw.line([(x, alt + 14), (x, HORIZONTE)], fill=c_m2 + (255,))

    # 2. MONTE DEL DESTINO (ORODRUIN / MOUNT DOOM)
    # Cono volcánico a la derecha (centro X=395, cráter en Y=146)
    OX, OY = 395, 146
    c_oro1, c_oro2, c_oro3 = pal['orodruin']
    for y in range(OY, HORIZONTE + 10):
        dy = y - OY
        w_volc = int(14 + dy * 0.95 + 6 * math.sin(dy * 0.12) + 3 * math.cos(dy * 0.06))
        for dx in range(-w_volc, w_volc + 1):
            x = OX + dx
            if 0 <= x < W:
                t_prof = abs(dx) / float(w_volc + 1)
                # Sombreado rocoso de crestas
                c_v = c_oro1 if t_prof < 0.4 else (c_oro2 if t_prof < 0.75 else c_oro3)
                if (dx + dy) % 7 == 0:
                    c_v = c_oro3 # sombras en grietas
                draw.point((x, y), fill=c_v + (255,))

    # Cráter del volcán con magma hirviendo
    c_l1, c_l2, c_l3 = pal['lava']
    for dx in range(-16, 17):
        draw.point((OX + dx, OY), fill=c_l2 + (255,))
        draw.point((OX + dx, OY + 1), fill=c_l1 + (255,))
        if abs(dx) <= 8:
            draw.point((OX + dx, OY - 1), fill=c_l3 + (255,))

    # Ríos de lava descendiendo por las laderas de Orodruin
    random.seed(42)
    for rama in range(3):
        lx, ly = float(OX + (rama - 1) * 8), float(OY + 2)
        for paso in range(68):
            ly += 1.8
            lx += math.sin(paso * 0.25 + rama * 2) * 2.2 + (rama - 1) * 0.85
            ix, iy = int(lx), int(ly)
            if 0 <= ix < W and 0 <= iy < H:
                c_ri = c_l3 if paso % 3 == 0 else c_l2
                draw.point((ix, iy), fill=c_ri + (255,))
                draw.point((ix + 1, iy), fill=c_l1 + (255,))
                draw.point((ix - 1, iy), fill=(180, 20, 0, 255))

    # 3. BARAD-DÛR - LA TORRE OSCURA (THE DARK TOWER)
    # Fortaleza de hierro negro y adamantio a la izquierda (centro X=195)
    BX = 195
    c_bd1, c_bd2, c_bd3 = pal['baraddur']
    c_filo = hx(pal['baraddur_filo'])

    TIERS_BD = [
        (56, 240, 275),  # Gran Bastión Base
        (46, 210, 241),  # Segundo Nivel
        (36, 180, 211),  # Tercer Nivel
        (26, 150, 181),  # Cuarto Nivel
        (20, 120, 151),  # Quinto Nivel
        (15, 96,  121),  # Aguja Superior
    ]

    for w_b, y0, y1 in TIERS_BD:
        # Cuerpo del nivel
        for y in range(y0, y1 + 1):
            for x in range(BX - w_b, BX + w_b + 1):
                dx = x - BX
                c_b = c_bd1 if abs(dx) < w_b - 4 else c_bd2
                # Ranuras y sillería de obsidiana
                if (x + y) % 6 == 0:
                    c_b = c_bd3
                if y == y0 and abs(dx) % 5 == 0:
                    c_b = c_filo
                draw.point((x, y), fill=c_b + (255,))

        # Contrafuertes y púas exteriores
        for dy in range(y0, y1 + 1):
            draw.point((BX - w_b - 1, dy), fill=c_filo + (255,))
            draw.point((BX + w_b + 1, dy), fill=c_bd2 + (255,))

        # Almenas puntiagudas en el remate de cada nivel
        for px_b in range(BX - w_b, BX + w_b + 1, 4):
            draw.line([(px_b, y0 - 3), (px_b, y0)], fill=c_filo + (255,))

    # Los Dos Grandes Cuernos de Hierro de Barad-dûr
    for cy in range(50, 96):
        prog_c = (96 - cy) / 46.0
        w_c = max(1, int(3 - prog_c * 2))
        # Cuerno izquierdo
        c_izq = BX - int(15 + prog_c * 11)
        for dx in range(-w_c, w_c + 1):
            draw.point((c_izq + dx, cy), fill=c_bd1 + (255,))
        draw.point((c_izq - w_c, cy), fill=c_filo + (255,))

        # Cuerno derecho
        c_der = BX + int(15 + prog_c * 11)
        for dx in range(-w_c, w_c + 1):
            draw.point((c_der + dx, cy), fill=c_filo + (255,))
        draw.point((c_der + w_c, cy), fill=c_bd2 + (255,))

    # Puentes de hierro suspendidos y agujas secundarias
    draw.line([(BX - 38, 160), (BX - 14, 175)], fill=c_filo + (255,), width=2)
    draw.line([(BX + 38, 160), (BX + 14, 175)], fill=c_filo + (255,), width=2)

    # 4. EL OJO DE SAURON (THE EYE OF SAURON)
    # Asentado en la cima entre los dos cuernos (X=195, Y=74)
    EYE_X, EYE_Y = BX, 74
    c_oj1, c_oj2, c_oj3 = pal['ojo']

    # Resplandor de fuego en capas concéntricas
    for r, col, a_val in [(28, c_oj1, 60), (18, c_oj2, 110), (10, c_oj3, 170)]:
        overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        odraw.ellipse([(EYE_X - r, EYE_Y - r), (EYE_X + r, EYE_Y + r)], fill=col + (a_val,))
        img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Forma de almendra del ojo llameante
    for dy in range(-12, 13):
        w_eye = int(18 * math.cos(dy * math.pi / 26.0))
        for dx in range(-w_eye, w_eye + 1):
            d_norm = math.hypot(dx / 1.5, dy)
            if d_norm <= 7.5:
                c_e = c_oj3 if d_norm < 3.2 else c_oj2
                draw.point((EYE_X + dx, EYE_Y + dy), fill=c_e + (255,))
            elif d_norm <= 11:
                if (dx + dy) % 2 == 0:
                    draw.point((EYE_X + dx, EYE_Y + dy), fill=c_oj1 + (240,))

    # Pupila rasgada vertical felina de oscuridad abisal
    for py in range(-8, 9):
        w_pup = 1 if abs(py) > 4 else 2
        for pw in range(-w_pup, w_pup + 1):
            draw.point((EYE_X + pw, EYE_Y + py), fill=(4, 1, 3, 255))

    # Lenguas de fuego que brotan de la corona del Ojo
    random.seed(17)
    for fl in range(24):
        ang = fl / 24.0 * 2 * math.pi
        dist = 11 + random.randint(2, 6)
        fx = int(EYE_X + math.cos(ang) * dist * 1.3)
        fy = int(EYE_Y + math.sin(ang) * dist)
        draw.point((fx, fy), fill=(c_oj2 if fl % 2 else c_oj1) + (255,))

    # 5. LLANURA DE GORGOROTH (Y=275..400)
    c_g1, c_g2, c_g3 = pal['gorgoroth']
    for y in range(HORIZONTE, H):
        for x in range(W):
            c_g = c_g1 if (x + y) % 3 == 0 else (c_g2 if (x + y) % 5 == 0 else c_g3)
            draw.point((x, y), fill=c_g + (255,))

    # Gran red de fisuras de lava y grietas terrestres
    for grieta in range(7):
        gx = 30 + grieta * 88
        gy = HORIZONTE + 6 + (grieta % 3) * 10
        for paso in range(48):
            gy += 1
            gx += ((paso * 7 + grieta * 3) % 5) - 2
            if 0 <= gx < W and 0 <= gy < H:
                draw.point((gx, gy), fill=c_l2 + (255,))
                draw.point((gx + 1, gy), fill=c_l1 + (255,))
                if paso % 4 == 0:
                    draw.point((gx, gy - 1), fill=c_l3 + (255,))

    return img

def genera_sol():
    # 208x208 con sol de sangre en (104, 104)
    img = Image.new('RGBA', (208, 208), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy, R = 104, 104, 24
    # Corona y halo
    draw.ellipse([(cx - 48, cy - 48), (cx + 48, cy + 48)], fill=(180, 40, 15, 60))
    draw.ellipse([(cx - 36, cy - 36), (cx + 36, cy + 36)], fill=(220, 60, 20, 120))
    draw.ellipse([(cx - R, cy - R), (cx + R, cy + R)], fill=(239, 68, 68, 255))
    draw.ellipse([(cx - R + 4, cy - R + 4), (cx + R - 4, cy + R - 4)], fill=(249, 115, 22, 255))
    return img

def genera_luna():
    # 208x208 con luna de ceniza eclipsada con halo carmesí
    img = Image.new('RGBA', (208, 208), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy, R = 104, 104, 28
    draw.ellipse([(cx - 44, cy - 44), (cx + 44, cy + 44)], fill=(120, 20, 30, 80))
    draw.ellipse([(cx - 34, cy - 34), (cx + 34, cy + 34)], fill=(180, 30, 40, 150))
    draw.ellipse([(cx - R, cy - R), (cx + R, cy + R)], fill=(30, 15, 22, 255))
    # Borde de fuego en eclipse
    draw.arc([(cx - R, cy - R), (cx + R, cy + R)], start=40, end=280, fill=(245, 158, 11, 255), width=2)
    return img

def main():
    print("==> Generando capas artísticas de Mordor en 100% 2D Pixel Art...")
    os.makedirs(FONDOS_DIR, exist_ok=True)
    os.makedirs(CAPTURAS_DIR, exist_ok=True)
    os.makedirs(GNOME_IMG, exist_ok=True)

    for fase in ['dia', 'dorado', 'noche']:
        # 1. Capas para GNOME Shell PixelZen (640x400)
        cielo = crear_cielo(fase)
        cielo_path = os.path.join(GNOME_IMG, f'cielo-{fase}.png')
        cielo.save(cielo_path, 'PNG')
        print(f"  [GNOME] Cielo: {cielo_path}")

        escena = componer_escena_mordor(fase, fondo_completo=False)
        escena_path = os.path.join(GNOME_IMG, f'escena-{fase}.png')
        escena.save(escena_path, 'PNG')
        print(f"  [GNOME] Escena: {escena_path}")

        # 2. Fondos de pantalla de alta resolución (1920x1200, escalado x3 Nearest Neighbor)
        wall_640 = componer_escena_mordor(fase, fondo_completo=True)
        wall_1920 = wall_640.resize((1920, 1200), Image.Resampling.NEAREST)
        fondo_path = os.path.join(FONDOS_DIR, f'mordor-{fase}.png')
        wall_1920.save(fondo_path, 'PNG')
        captura_path = os.path.join(CAPTURAS_DIR, f'mordor-{fase}.png')
        wall_1920.save(captura_path, 'PNG')
        print(f"  [Wallpaper] Guardado: {fondo_path}")

    # Sol y Luna
    sol = genera_sol()
    sol.save(os.path.join(GNOME_IMG, 'sol.png'), 'PNG')
    luna = genera_luna()
    luna.save(os.path.join(GNOME_IMG, 'luna.png'), 'PNG')
    print("  [GNOME] Sol y Luna creados.")

    # Copias de vista previa
    import shutil
    shutil.copy2(os.path.join(FONDOS_DIR, 'mordor-noche.png'), os.path.join(FONDOS_DIR, 'mordor-preview.png'))
    shutil.copy2(os.path.join(FONDOS_DIR, 'mordor-noche.png'), os.path.join(CAPTURAS_DIR, 'mordor-preview.png'))

    # Fondo activo de escritorio
    dest_bg = os.path.expanduser('~/.local/share/backgrounds/mordor.png')
    os.makedirs(os.path.dirname(dest_bg), exist_ok=True)
    shutil.copy2(os.path.join(FONDOS_DIR, 'mordor-noche.png'), dest_bg)
    print(f"  Fondo activo actualizado en {dest_bg}")

    # Generar datos.json limpios sin nubes rotas
    random.seed(88)
    ascuas = [[random.randint(10, 630), random.randint(10, 260), random.choice(['#ff3700', '#ff8800', '#ffaa00', '#e11d48']), 0] for _ in range(96)]
    datos = {
        "W": 640, "H": 400,
        "estrellas": ascuas,
        "ventanas": [],
        "faroles": [[195, 74, 18]], # El Ojo de Sauron
        "destellos": [[395, 146], [390, 155], [402, 158], [394, 172], [408, 178], [390, 192]], # Magma Orodruin
        "nubes": [], # Limpio para evitar errores de hoja de sprites
        "nubes_w": 210,
        "barca": [0, 0],
        "luna": [100, 60, 22]
    }
    with open(os.path.join(GNOME_DIR, 'datos.json'), 'w') as f:
        json.dump(datos, f, indent=2)
    print("  datos.json generado con éxito.")

if __name__ == '__main__':
    main()
