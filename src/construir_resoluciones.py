#!/usr/bin/env python3
"""PixelMordor - Generador de Fondos Multi-Resolución (1080p, 2K, 4K, Ultrawide 21:9).
Genera fondos adaptados al aspect ratio y resolución sin deformaciones:
- 1080p: 1920x1080 (16:9)
- 2K QHD: 2560x1440 (16:9)
- 4K UHD: 3840x2160 (16:9)
- Ultrawide: 3440x1440 (21:9) y 2560x1080 (21:9)
"""

import math, os, random, sys
from PIL import Image, ImageDraw

REPO_DIR = '/home/2asird/Descargas/pixelmordor'
FONDOS_DIR = os.path.join(REPO_DIR, 'fondos')
os.makedirs(FONDOS_DIR, exist_ok=True)

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dith(x, y, t):
    return (BAYER[y % 4][x % 4] + 0.5) / 16.0 < t

def hx(c):
    if isinstance(c, tuple): return c
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

PALETAS = {
    'dia': {
        'sky': ['#160c1c', '#241228', '#381634', '#521c36', '#722432', '#8f2c2c', '#b03c24', '#ce5620'],
        'montana_fondo': ((38, 20, 28), (24, 12, 18)),
        'orodruin': ((43, 24, 32), (28, 16, 22), (18, 10, 14)),
        'baraddur': ((30, 20, 29), (19, 12, 18), (42, 27, 40)),
        'baraddur_filo': '#66334d',
        'gorgoroth': ((34, 22, 27), (22, 13, 17), (47, 30, 36)),
        'lava': ((255, 55, 0), (255, 123, 0), (255, 204, 0)),
        'ojo': ((255, 34, 0), (255, 136, 0), (255, 238, 85)),
    },
    'dorado': {
        'sky': ['#140718', '#220822', '#3b0a2a', '#5c0f2a', '#841924', '#a8241b', '#c43a14', '#e05810'],
        'montana_fondo': ((42, 18, 26), (28, 10, 17)),
        'orodruin': ((46, 20, 28), (30, 14, 19), (20, 8, 12)),
        'baraddur': ((34, 18, 26), (22, 10, 16), (46, 24, 35)),
        'baraddur_filo': '#782622',
        'gorgoroth': ((38, 19, 25), (25, 11, 15), (50, 25, 30)),
        'lava': ((255, 60, 0), (255, 140, 0), (255, 215, 0)),
        'ojo': ((255, 40, 0), (255, 150, 0), (255, 245, 100)),
    },
    'noche': {
        'sky': ['#06010a', '#0b0212', '#14031c', '#1f0426', '#2d062e', '#3d082f', '#4f0c2a', '#611022'],
        'montana_fondo': ((24, 8, 18), (14, 4, 10)),
        'orodruin': ((30, 10, 22), (18, 6, 12), (10, 3, 7)),
        'baraddur': ((22, 8, 18), (12, 4, 10), (32, 12, 26)),
        'baraddur_filo': '#4d142e',
        'gorgoroth': ((26, 9, 18), (15, 5, 10), (36, 12, 24)),
        'lava': ((255, 45, 0), (255, 110, 0), (255, 195, 0)),
        'ojo': ((255, 20, 0), (255, 120, 0), (255, 230, 60)),
    }
}

def render_scene(fase, w_px, h_px):
    img = Image.new('RGB', (w_px, h_px), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    pal = PALETAS[fase]
    SKY = pal['sky']
    HORIZONTE = int(h_px * 0.68)

    # 1. Cielo con degradado Dithered Bayer 4x4
    for y in range(h_px):
        t = (y / float(h_px)) * (len(SKY) - 1)
        i = int(t); f = t - i
        c1 = hx(SKY[min(i, len(SKY) - 1)])
        c2 = hx(SKY[min(i + 1, len(SKY) - 1)])
        for x in range(w_px):
            col = c2 if dith(x, y, f) else c1
            img.putpixel((x, y), col)

    # 2. Cordillera lejana
    c_m1, c_m2 = pal['montana_fondo']
    for x in range(w_px):
        alt = int(HORIZONTE * 0.80 - (h_px * 0.11) * math.sin(x * 0.012) - (h_px * 0.06) * math.cos(x * 0.035 + 1.2))
        draw.line([(x, alt), (x, HORIZONTE)], fill=c_m1)
        draw.line([(x, alt + 14), (x, HORIZONTE)], fill=c_m2)

    # 3. Monte del Destino (Orodruin)
    OX = int(w_px * 0.62)
    OY = int(h_px * 0.36)
    c_oro1, c_oro2, c_oro3 = pal['orodruin']
    for y in range(OY, HORIZONTE + 10):
        dy = y - OY
        w_volc = int(14 + dy * 0.95 + 6 * math.sin(dy * 0.12) + 3 * math.cos(dy * 0.06))
        for dx in range(-w_volc, w_volc + 1):
            x = OX + dx
            if 0 <= x < w_px:
                t_prof = abs(dx) / float(w_volc + 1)
                c_v = c_oro1 if t_prof < 0.4 else (c_oro2 if t_prof < 0.75 else c_oro3)
                if (dx + dy) % 7 == 0: c_v = c_oro3
                draw.point((x, y), fill=c_v)

    # Cráter del volcán
    c_l1, c_l2, c_l3 = pal['lava']
    for dx in range(-16, 17):
        draw.point((OX + dx, OY), fill=c_l2)
        draw.point((OX + dx, OY + 1), fill=c_l1)
        if abs(dx) <= 8: draw.point((OX + dx, OY - 1), fill=c_l3)

    # Ríos de lava
    random.seed(42)
    for rama in range(3):
        lx, ly = float(OX + (rama - 1) * 8), float(OY + 2)
        for paso in range(68):
            ly += 1.8
            lx += math.sin(paso * 0.25 + rama * 2) * 2.2 + (rama - 1) * 0.85
            ix, iy = int(lx), int(ly)
            if 0 <= ix < w_px and 0 <= iy < h_px:
                c_ri = c_l3 if paso % 3 == 0 else c_l2
                draw.point((ix, iy), fill=c_ri)
                draw.point((ix + 1, iy), fill=c_l1)

    # 4. Barad-dûr
    BX = int(w_px * 0.30)
    c_bd1, c_bd2, c_bd3 = pal['baraddur']
    c_filo = hx(pal['baraddur_filo'])
    scale_y = h_px / 400.0

    TIERS_BD = [
        (int(56 * (h_px / 400)), int(240 * scale_y), int(275 * scale_y)),
        (int(46 * (h_px / 400)), int(210 * scale_y), int(241 * scale_y)),
        (int(36 * (h_px / 400)), int(180 * scale_y), int(211 * scale_y)),
        (int(26 * (h_px / 400)), int(150 * scale_y), int(181 * scale_y)),
        (int(20 * (h_px / 400)), int(120 * scale_y), int(151 * scale_y)),
        (int(15 * (h_px / 400)), int(96  * scale_y), int(121 * scale_y)),
    ]

    for w_b, y0, y1 in TIERS_BD:
        for y in range(y0, y1 + 1):
            for x in range(BX - w_b, BX + w_b + 1):
                dx = x - BX
                c_b = c_bd1 if abs(dx) < w_b - 4 else c_bd2
                if (x + y) % 6 == 0: c_b = c_bd3
                if y == y0 and abs(dx) % 5 == 0: c_b = c_filo
                draw.point((x, y), fill=c_b)

    # Cuernos superiores de Barad-dûr
    y_apex = int(96 * scale_y)
    for dy in range(int(62 * scale_y)):
        y = y_apex - dy
        w_fork = int(14 + dy * 0.38)
        # Cuerno izquierdo
        draw.line([(BX - w_fork - 2, y), (BX - w_fork + 2, y)], fill=c_bd1)
        # Cuerno derecho
        draw.line([(BX + w_fork - 2, y), (BX + w_fork + 2, y)], fill=c_bd1)

    # 5. El Gran Ojo de Sauron
    eye_x = BX
    eye_y = int(58 * scale_y)
    r_aura = int(22 * scale_y)
    for dy in range(-r_aura, r_aura + 1):
        for dx in range(-r_aura * 2, r_aura * 2 + 1):
            d_norm = math.hypot(dx / 1.8, dy) / float(r_aura)
            if d_norm <= 1.0:
                c_eye = pal['ojo'][0] if d_norm > 0.6 else (pal['ojo'][1] if d_norm > 0.3 else pal['ojo'][2])
                draw.point((eye_x + dx, eye_y + dy), fill=c_eye)

    # Pupila vertical de fuego
    pupil_h = int(10 * scale_y)
    for dy in range(-pupil_h, pupil_h + 1):
        w_pup = 1 if abs(dy) > pupil_h * 0.7 else 2
        for dx in range(-w_pup, w_pup + 1):
            draw.point((eye_x + dx, eye_y + dy), fill=(10, 2, 4))

    # 6. Llanuras de Gorgoroth (Suelo inferior)
    c_g1, c_g2, c_g3 = pal['gorgoroth']
    for y in range(HORIZONTE, h_px):
        dy = y - HORIZONTE
        for x in range(w_px):
            c_g = c_g1 if dy < 25 else (c_g2 if dy < 75 else c_g3)
            if (x * 3 + y * 7) % 19 == 0:
                c_g = (c_l1[0] // 2, c_l1[1] // 2, c_l1[2] // 2) # grieta tenue
            draw.point((x, y), fill=c_g)

    return img

RESOLUCIONES = {
    '1080p': (1920, 1080, 640, 360),
    '2k': (2560, 1440, 640, 360),
    '4k': (3840, 2160, 640, 360),
    'ultrawide': (3440, 1440, 860, 360),
    'ultrawide-1080': (2560, 1080, 854, 360)
}

def construir_todo():
    print("==> Generando fondos multi-resolución de PixelMordor...")
    for res_name, (out_w, out_h, base_w, base_h) in RESOLUCIONES.items():
        print(f"--- Resolucion {res_name}: {out_w}x{out_h} (Pixel Base: {base_w}x{base_h}) ---")
        for fase in ['noche', 'dorado', 'dia']:
            base_img = render_scene(fase, base_w, base_h)
            final_img = base_img.resize((out_w, out_h), Image.Resampling.NEAREST)
            out_file = os.path.join(FONDOS_DIR, f"mordor-{fase}-{res_name}.png")
            final_img.save(out_file, 'PNG')
            print(f"  Guardado: {out_file}")

if __name__ == '__main__':
    construir_todo()
