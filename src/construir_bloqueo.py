#!/usr/bin/env python3
"""construir_bloqueo.py - Generador del fondo de pantalla de bloqueo de Mordor (El Morannon y el Gran Ojo).
Genera arte pixelado nativo 640x400 escalado x3 (1920x1200) de la Puerta Negra de Mordor
con las Torres de los Dientes (Carchost y Narchost), el Ojo de Sauron llameante en alta fidelidad
y la inscripción de fuego optimizada para la pantalla de bloqueo de GNOME."""

import math, os, random, struct, sys, zlib
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = '/home/2asird/Descargas/mordor'
FONDOS_DIR = os.path.join(BASE_DIR, 'fondos')
CAPTURAS_DIR = os.path.join(BASE_DIR, 'capturas')
os.makedirs(FONDOS_DIR, exist_ok=True)
os.makedirs(CAPTURAS_DIR, exist_ok=True)

W, H = 640, 400

# Paleta atmosférica
PAL = {
    'sky': [(4, 2, 8), (8, 3, 14), (16, 6, 24), (26, 8, 34), (40, 10, 44), (60, 14, 50), (84, 18, 48), (114, 26, 42)],
    'montana_lejana': (18, 7, 18),
    'montana_media': (11, 4, 12),
    'torre_hierro': (14, 7, 12),
    'torre_sombra': (6, 2, 6),
    'torre_brillo': (28, 14, 22),
    'torre_filo': (46, 20, 34),
    'puerta_hierro': (16, 8, 14),
    'puerta_lineas': (7, 3, 6),
    'puerta_remache': (220, 38, 38),
    'suelo_ceniza': (18, 9, 14),
    'suelo_foso': (8, 3, 7),
    'fuego_ojo_ext': (220, 38, 38),
    'fuego_ojo_mid': (249, 115, 22),
    'fuego_ojo_int': (254, 240, 138),
    'oro_runas': (251, 191, 36),
    'sangre': (185, 28, 28)
}

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dith(x, y, t):
    return (BAYER[y % 4][x % 4] + 0.5) / 16.0 < t

def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] * (1.0 - t) + c2[i] * t) for i in range(3))

def main():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    pix = img.load()

    # 1. Cielo crepuscular con gradiente suave y nubes de tormenta
    sky_colors = PAL['sky']
    n_sky = len(sky_colors)
    for y in range(H):
        t_global = y / 285.0
        if t_global < 1.0:
            idx = t_global * (n_sky - 1)
            i0 = int(idx)
            i1 = min(n_sky - 1, i0 + 1)
            frac = idx - i0
            for x in range(W):
                nube = math.sin(x * 0.02 + y * 0.015) * 0.09 + math.cos(x * 0.05 - y * 0.02) * 0.06
                val = frac + nube
                c = mix(sky_colors[i0], sky_colors[i1], val)
                if dith(x, y, val % 1.0):
                    c = sky_colors[min(n_sky - 1, i1)]
                pix[x, y] = c
        else:
            for x in range(W):
                pix[x, y] = sky_colors[-1]

    # 2. Relámpagos carmesíes laterales (sin cruzar el centro donde va el reloj / Ojo)
    random.seed(88)
    for rx_start in [85, 140, 495, 565]:
        ry_start = random.randint(15, 45)
        cur_x = rx_start
        for ry in range(ry_start, ry_start + 75, 2):
            for dx in range(-1, 2):
                if 0 <= cur_x + dx < W:
                    pix[cur_x + dx, ry] = (255, 230, 240) if dx == 0 else (225, 29, 72)
            cur_x += random.choice([-2, -1, 0, 1, 2])
            # Ramificación
            if ry == ry_start + 35:
                bx = cur_x
                for by in range(ry, ry + 25, 2):
                    bx += 2 if rx_start > 320 else -2
                    if 0 <= bx < W:
                        pix[bx, by] = (244, 63, 94)

    # 3. Montañas de Cirith Gorgor (Ephel Dúath y Ered Lithui)
    # Cordillera lejana
    for x in range(W):
        dist_c = abs(x - (W // 2))
        h_mont = 195 - int((dist_c / 320.0) * 115 + math.sin(x * 0.035) * 16 + math.cos(x * 0.08) * 8)
        for y in range(max(0, h_mont), H):
            if pix[x, y][0] < 35:
                pix[x, y] = PAL['montana_lejana']

    # Cordillera media escarpada con riscos
    for x in range(W):
        dist_c = abs(x - (W // 2))
        h_mont2 = 225 - int((dist_c / 320.0) * 95 + math.cos(x * 0.045) * 12 + math.sin(x * 0.1) * 6)
        for y in range(max(0, h_mont2), H):
            pix[x, y] = PAL['montana_media']

    # 4. LA PUERTA NEGRA (EL MORANNON)
    gate_left = 165
    gate_right = 475
    gate_top = 230
    gate_bottom = 352
    gate_cx = (gate_left + gate_right) // 2

    # Torres de los Dientes (Carchost y Narchost)
    def dibuja_diente(tx, dir_luz=1):
        w_base = 56
        w_top = 34
        h_torre = 185
        ty_base = gate_bottom
        ty_top = ty_base - h_torre

        # Cuerpo tronco-piramidal de la torre
        for y in range(ty_top, ty_base):
            prog = (y - ty_top) / float(h_torre)
            w_cur = int(w_top + (w_base - w_top) * prog)
            x_min = tx - w_cur // 2
            x_max = tx + w_cur // 2
            for x in range(x_min, x_max + 1):
                if 0 <= x < W:
                    prog_x = (x - x_min) / float(max(1, w_cur))
                    if prog_x < 0.22:
                        pix[x, y] = PAL['torre_filo'] if dir_luz > 0 else PAL['torre_sombra']
                    elif prog_x < 0.45:
                        pix[x, y] = PAL['torre_brillo']
                    elif prog_x < 0.78:
                        pix[x, y] = PAL['torre_hierro']
                    else:
                        pix[x, y] = PAL['torre_sombra']

            # Contrafuertes y molduras horizontales
            if (y - ty_top) in [45, 95, 140]:
                for x in range(x_min - 2, x_max + 3):
                    if 0 <= x < W:
                        pix[x, y] = PAL['torre_filo']

        # Almenas góticas superiores con espinas de hierro
        for p in range(-w_top // 2, w_top // 2 + 1, 5):
            px_p = tx + p
            for py in range(ty_top - 16, ty_top):
                if 0 <= px_p < W:
                    pix[px_p, py] = PAL['torre_brillo']
                    if 0 <= px_p + 1 < W:
                        pix[px_p + 1, py] = PAL['torre_hierro']
            # Punta de lanza
            if 0 <= px_p < W:
                pix[px_p, ty_top - 18] = (254, 240, 138)

        # Fuego / antorcha incandescente en la almena
        for dy in range(-14, -8):
            for dx in range(-3, 4):
                if 0 <= tx + dx < W:
                    pix[tx + dx, ty_top + dy] = PAL['fuego_ojo_mid']
        for dy in range(-12, -9):
            pix[tx, ty_top + dy] = PAL['fuego_ojo_int']

        # Troneras defensivas con fuego interior
        for ty_win in [ty_top + 55, ty_top + 105]:
            for dy in range(6):
                for dx in range(-1, 2):
                    if 0 <= tx + dx < W:
                        pix[tx + dx, ty_win + dy] = (255, 69, 0)
                pix[tx, ty_win + dy] = (254, 240, 138)

    dibuja_diente(gate_left - 12, dir_luz=1)
    dibuja_diente(gate_right + 12, dir_luz=-1)

    # El Murallón del Morannon
    for y in range(gate_top, gate_bottom):
        for x in range(gate_left, gate_right + 1):
            fila = (y - gate_top) // 16
            col = (x - gate_left) // 22
            borde = (y - gate_top) % 16 == 0 or (x - gate_left) % 22 == 0
            if borde:
                pix[x, y] = PAL['puerta_lineas']
            else:
                grad = 1.0 - 0.22 * abs(x - gate_cx) / float(gate_right - gate_left)
                pix[x, y] = mix(PAL['puerta_hierro'], PAL['torre_sombra'], 1.0 - grad)

    # Almenas de hierro sobre la muralla
    for x in range(gate_left, gate_right + 1, 7):
        for y in range(gate_top - 12, gate_top):
            if 0 <= x < W:
                pix[x, y] = PAL['torre_brillo']
                if 0 <= x + 1 < W:
                    pix[x + 1, y] = PAL['torre_hierro']
        if 0 <= x < W:
            pix[x, gate_top - 14] = (220, 38, 38)

    # Las dos grandes hojas batientes de hierro (costura central)
    for y in range(gate_top + 16, gate_bottom):
        for dx in range(-2, 3):
            pix[gate_cx + dx, y] = (4, 1, 4)
        # Remaches de acero ensangrentado en las puertas
        if (y - gate_top) % 10 == 0:
            pix[gate_cx - 8, y] = (220, 38, 38)
            pix[gate_cx + 8, y] = (220, 38, 38)
            pix[gate_cx - 24, y] = (185, 28, 28)
            pix[gate_cx + 24, y] = (185, 28, 28)

    # Arcos reforzados con púas en las puertas
    for x in range(gate_left + 15, gate_right - 15):
        dx_c = abs(x - gate_cx)
        y_arco = gate_top + int(dx_c * 0.16)
        for y in range(y_arco - 3, y_arco + 1):
            pix[x, y] = PAL['torre_filo']

    # 5. EL GRAN OJO DE SAURON (FLOTANDO EN LLAMAS VIVAS EN EL CIELO)
    eye_x = gate_cx
    eye_y = 126
    eye_rx = 54
    eye_ry = 32

    # Llamas exteriores hiperrealistas en pixel art con ruido angular
    for dy in range(-eye_ry - 26, eye_ry + 27):
        for dx in range(-eye_rx - 32, eye_rx + 33):
            angle = math.atan2(dy, dx)
            dist_norm = math.sqrt((dx / float(eye_rx))**2 + (dy / float(eye_ry))**2)
            # Modulación de llamas en espiral
            flame_noise = math.sin(angle * 14.0 + dist_norm * 4.0) * 0.22 + math.cos(angle * 7.0 - dist_norm * 2.0) * 0.14
            effective_dist = dist_norm - flame_noise

            if effective_dist < 1.7:
                cur_x = eye_x + dx
                cur_y = eye_y + dy
                if 0 <= cur_x < W and 0 <= cur_y < H:
                    t_flame = max(0.0, min(1.0, (1.7 - effective_dist) / 0.7))
                    c_flame = mix(PAL['fuego_ojo_ext'], PAL['fuego_ojo_mid'], t_flame)
                    c_prev = pix[cur_x, cur_y]
                    pix[cur_x, cur_y] = mix(c_prev, c_flame, min(0.92, t_flame * 1.4))

    # Cuerpo del Ojo (Almendra de magma ardiente)
    for dy in range(-eye_ry, eye_ry + 1):
        for dx in range(-eye_rx, eye_rx + 1):
            dist_sq = (dx / float(eye_rx))**2 + (dy / float(eye_ry))**2
            if dist_sq <= 1.0:
                cur_x = eye_x + dx
                cur_y = eye_y + dy
                if 0 <= cur_x < W and 0 <= cur_y < H:
                    r_norm = math.sqrt(dist_sq)
                    if r_norm < 0.35:
                        c_ojo = PAL['fuego_ojo_int']
                    elif r_norm < 0.72:
                        c_ojo = PAL['fuego_ojo_mid']
                    else:
                        c_ojo = PAL['fuego_ojo_ext']
                    pix[cur_x, cur_y] = c_ojo

    # Pupila de gato vertical (Hendidura en negro absoluto)
    for dy in range(-eye_ry + 3, eye_ry - 2):
        w_pupila = int(4.0 * math.cos((dy / float(eye_ry)) * (math.pi / 2))) + 1
        for dx in range(-w_pupila, w_pupila + 1):
            pix[eye_x + dx, eye_y + dy] = (0, 0, 0)
    # Brillo carmesí en el interior de la pupila
    for dy in range(-eye_ry // 2, eye_ry // 2):
        pix[eye_x, eye_y + dy] = (185, 28, 28)
    pix[eye_x, eye_y] = (254, 240, 138)

    # Haz de búsqueda proyectándose sobre el Morannon
    for y in range(eye_y + eye_ry + 1, gate_top + 45):
        prog = (y - (eye_y + eye_ry)) / float(gate_top + 45 - (eye_y + eye_ry))
        w_beam = int(22 + prog * 120)
        for x in range(eye_x - w_beam // 2, eye_x + w_beam // 2):
            if 0 <= x < W:
                edge = 1.0 - abs(x - eye_x) / float(w_beam // 2)
                alpha = edge * (1.0 - prog * 0.65) * 0.32
                pix[x, y] = mix(pix[x, y], (249, 115, 22), alpha)

    # 6. Suelo de Gorgoroth frente a la Puerta Negra
    for y in range(gate_bottom, H):
        prog_suelo = (y - gate_bottom) / float(H - gate_bottom)
        for x in range(W):
            c_base = mix(PAL['suelo_foso'], PAL['suelo_ceniza'], prog_suelo)
            # Grietas ardientes
            if (x * 7 + y * 13) % 43 < 2 and y > gate_bottom + 12:
                pix[x, y] = (255, 69, 0)
            elif (x * 5 - y * 11) % 59 < 2 and y > gate_bottom + 22:
                pix[x, y] = (254, 240, 138)
            else:
                pix[x, y] = c_base

    # Picas con estandartes orcos en el desfiladero
    for px_pica in [130, 205, 435, 510]:
        for py_pica in range(gate_bottom + 5, gate_bottom + 36):
            if 0 <= px_pica < W:
                pix[px_pica, py_pica] = (24, 12, 18)
        # Estandarte negro rasgado con Ojo Rojo
        for dy in range(10):
            for dx in range(1, 12 - (dy // 2)):
                if 0 <= px_pica + dx < W:
                    pix[px_pica + dx, gate_bottom + 6 + dy] = (8, 3, 7)
        pix[px_pica + 4, gate_bottom + 10] = (220, 38, 38)
        pix[px_pica + 5, gate_bottom + 10] = (254, 240, 138)

    # Ascuas volcánicas flotantes
    random.seed(999)
    for _ in range(110):
        ax = random.randint(0, W - 1)
        ay = random.randint(gate_top - 30, H - 1)
        pix[ax, ay] = random.choice([PAL['fuego_ojo_int'], PAL['fuego_ojo_mid'], PAL['fuego_ojo_ext']])

    # 7. ROTULACIÓN Y LEMAS ÉPICOS INTEGRADOS
    draw = ImageDraw.Draw(img)

    font_path = '/home/2asird/.local/share/fonts/pixelzen/DepartureMono-Regular.otf'
    if not os.path.isfile(font_path):
        font_path = '/home/2asird/Descargas/mordor/fuentes/DepartureMono-Regular.otf'

    try:
        font_title = ImageFont.truetype(font_path, 17)
        font_sub = ImageFont.truetype(font_path, 11)
        font_runas = ImageFont.truetype(font_path, 9)
    except Exception:
        font_title = font_sub = font_runas = ImageFont.load_default()

    def dibuja_texto_brillo(txt, fnt, y_pos, col_frente, col_borde):
        bbox = draw.textbbox((0, 0), txt, font=fnt)
        w_txt = bbox[2] - bbox[0]
        x_txt = (W - w_txt) // 2
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)]:
            draw.text((x_txt + dx, y_pos + dy), txt, font=fnt, fill=col_borde)
        draw.text((x_txt, y_pos), txt, font=fnt, fill=col_frente)

    # Lemas en el firmamento superior y sobre la Puerta Negra:
    # Arriba del todo: runas del Anillo
    dibuja_texto_brillo("ASH NAZG DURBATULÛK · ASH NAZG GIMBATUL", font_runas, 18, (251, 191, 36), (153, 27, 27))
    # Sobre el Ojo:
    dibuja_texto_brillo("NO PUEDES ESCONDERTE. ¡TE VEO!", font_title, 34, (254, 240, 138), (185, 28, 28))
    # Lintel de la Puerta Negra:
    dibuja_texto_brillo("— CIRITH GORGOR · MORANNON · BARAD-DÛR —", font_sub, 214, (248, 113, 113), (12, 4, 8))

    # Guardar nativo 640x400
    img.save('/tmp/mordor_bloqueo_nativo.png')

    # Escalado HD x3 con NEAREST para máxima nitidez pixel art (1920x1200)
    hd_img = img.resize((W * 3, H * 3), Image.NEAREST)

    dest_fondo = os.path.join(FONDOS_DIR, 'mordor-bloqueo.png')
    dest_captura = os.path.join(CAPTURAS_DIR, 'mordor-bloqueo.png')
    hd_img.save(dest_fondo)
    hd_img.save(dest_captura)
    print(f"Fondo de pantalla de bloqueo generado exitosamente:\n  {dest_fondo}\n  {dest_captura}")

if __name__ == '__main__':
    main()
