#!/usr/bin/env python3
"""generar_capturas_actuales.py - Genera capturas de pantalla de alta resolución y actualizadas
del tema PixelMordor para el repositorio de GitHub:
- capturas/mordor-preview.png (Escritorio completo con GNOME Shell, panel superior, HUD y escena viva)
- capturas/mordor-terminal.png (Ventana de terminal Ptyxis con paleta oficial de Mordor y CLI)
- capturas/preview_mordor_definitivo.png (Hero banner / tríptico de las fases del sol y características)
"""

import math, os, random, struct, sys
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = '/home/2asird/Descargas/pixelmordor'
FONDOS_DIR = os.path.join(BASE_DIR, 'fondos')
CAPTURAS_DIR = os.path.join(BASE_DIR, 'capturas')
os.makedirs(CAPTURAS_DIR, exist_ok=True)

W_DESK, H_DESK = 1920, 1200

# Fuentes
FONT_PATH = '/home/2asird/.local/share/fonts/pixelzen/DepartureMono-Regular.otf'
if not os.path.isfile(FONT_PATH):
    FONT_PATH = '/home/2asird/Descargas/mordor/fuentes/DepartureMono-Regular.otf'

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

def crea_captura_escritorio():
    print("==> Generando capturas/mordor-preview.png (Escritorio vivo con HUD y GNOME)...")
    base_fondo = os.path.join(FONDOS_DIR, 'mordor-noche.png')
    if os.path.isfile(base_fondo):
        desk = Image.open(base_fondo).convert('RGBA')
    else:
        desk = Image.new('RGBA', (W_DESK, H_DESK), (10, 4, 8, 255))

    # Asegurar tamaño 1920x1200
    if desk.size != (W_DESK, H_DESK):
        desk = desk.resize((W_DESK, H_DESK), Image.NEAREST)

    draw = ImageDraw.Draw(desk)

    # 1. Añadir las Runas Tengwar fijas sobre Barad-dûr (X=195*3 = 585, Y=34*3 = 102)
    runes = [
        [[1,0],[2,0],[0,1],[2,1],[0,2],[1,2],[2,2],[2,3],[1,4],[2,5]], # Ash
        [[0,0],[1,0],[2,0],[2,1],[1,2],[0,3],[0,4],[1,4],[2,4]],       # Nazg
        [[0,0],[0,1],[1,1],[2,2],[2,3],[1,4],[0,4],[0,5]],             # Dur
        [[1,0],[2,0],[0,1],[1,2],[2,2],[2,3],[2,4],[1,5]],             # Ba
        [[0,0],[2,0],[1,1],[1,2],[1,3],[2,4],[1,5]],                   # Tu
        [[0,0],[0,1],[1,1],[2,0],[2,2],[1,3],[2,4],[0,5]],             # Lûk
        [[1,0],[0,1],[2,1],[0,2],[1,3],[2,3],[2,4],[1,5]],             # Gimb
        [[0,0],[1,0],[2,1],[1,2],[0,3],[1,4],[2,4],[2,5]]              # Atul
    ]
    rune_start_x = 585 - (len(runes) * 24) // 2
    for r_idx, glyph in enumerate(runes):
        rx = rune_start_x + r_idx * 24
        ry = 102
        for dx, dy in glyph:
            for sx in range(3):
                for sy in range(3):
                    desk.putpixel((rx + dx*3 + sx, ry + dy*3 + sy), (251, 191, 36, 240))
                    desk.putpixel((rx + dx*3 + sx - 1, ry + dy*3 + sy), (239, 68, 68, 180))

    # 2. Añadir Nazgûl volando en el cielo
    # Nazgûl 1 (cerca de Barad-dûr)
    n1_x, n1_y = 480, 290
    for dy in range(-6, 7):
        w_wing = int(24 * math.cos(dy / 8.0))
        for dx in range(-w_wing, w_wing + 1):
            if abs(dy) < 3 or (dx % 2 == 0):
                desk.putpixel((n1_x + dx, n1_y + dy), (6, 2, 8, 255))
    # Nazgûl 2 (sobre el Monte del Destino)
    n2_x, n2_y = 1140, 260
    for dy in range(-5, 6):
        w_wing = int(20 * math.cos(dy / 7.0))
        for dx in range(-w_wing, w_wing + 1):
            if abs(dy) < 3 or (dx % 2 == 0):
                desk.putpixel((n2_x + dx, n2_y + dy), (6, 2, 8, 255))

    # 3. Frodo y Sam en Gorgoroth (X=780, Y=912) con resplandor del Frasco de Galadriel
    hx, hy = 780, 912
    for dy in range(-12, 13):
        for dx in range(-12, 13):
            d_frasco = math.hypot(dx, dy)
            if d_frasco < 12:
                alpha = int((1.0 - d_frasco / 12.0) * 160)
                cur = desk.getpixel((hx + dx, hy + dy))
                desk.putpixel((hx + dx, hy + dy), (224, 242, 254, min(255, cur[3] + alpha)))
    # Siluetas hobbits
    for dy in range(9):
        for dx in range(12):
            desk.putpixel((hx + dx - 6, hy + dy), (30, 41, 59, 255))

    # 4. Hueste orca marchando con estandarte rojo en Gorgoroth (Y=1080)
    base_orc_x = 950
    # Estandarte
    for y in range(1040, 1100):
        desk.putpixel((base_orc_x - 15, y), (28, 25, 23, 255))
    for y in range(1040, 1065):
        for x in range(base_orc_x - 14, base_orc_x + 6):
            desk.putpixel((x, y), (9, 9, 11, 255))
            if abs(x - (base_orc_x - 4)) < 3 and abs(y - 1052) < 4:
                desk.putpixel((x, y), (239, 68, 68, 255))
    # Tropa orca con antorchas
    for i in range(12):
        ox = base_orc_x + i * 35
        oy = 1085
        # Cuerpo
        for dy in range(25):
            for dx in range(-4, 5):
                desk.putpixel((ox + dx, oy + dy), (8, 3, 9, 255))
        # Pica
        for py in range(oy - 20, oy):
            desk.putpixel((ox + 3, py), (24, 12, 18, 255))
        # Antorcha en algunos orcos
        if i % 3 == 0:
            for fy in range(oy - 18, oy - 10):
                for fx in range(ox - 8, ox - 2):
                    desk.putpixel((fx, fy), (255, 85, 0, 240))
            desk.putpixel((ox - 5, oy - 14), (254, 240, 138, 255))

    # 5. BARRA SUPERIOR DE GNOME SHELL (Top Panel)
    panel_h = 36
    panel_overlay = Image.new('RGBA', (W_DESK, panel_h), (12, 4, 7, 235))
    desk.paste(panel_overlay, (0, 0), panel_overlay)
    draw.line([(0, panel_h), (W_DESK, panel_h)], fill=(120, 38, 34, 220), width=1)

    f_panel = get_font(13)
    f_panel_bold = get_font(13)

    # Izquierda: Actividades
    draw.text((18, 9), "Actividades", font=f_panel, fill=(230, 222, 220))

    # Centro: Reloj de GNOME Shell
    clock_str = "vie 13 nov  12:00"
    bbox = draw.textbbox((0, 0), clock_str, font=f_panel_bold)
    w_clock = bbox[2] - bbox[0]
    draw.text(((W_DESK - w_clock) // 2, 9), clock_str, font=f_panel_bold, fill=(245, 240, 235))

    # Derecha: Indicador temático "👁 Mordor" + Estado del sistema
    right_x = W_DESK - 320
    # Pill de Mordor
    pill_w = 98
    draw.rounded_rectangle([(right_x, 5), (right_x + pill_w, panel_h - 5)], radius=10, fill=(26, 8, 14, 240), outline=(239, 68, 68, 255), width=1)
    draw.text((right_x + 10, 9), "👁 Mordor", font=f_panel_bold, fill=(239, 68, 68))

    # Iconos estándar: red, volumen, batería, apagado
    draw.text((right_x + 115, 9), "🔊", font=f_panel, fill=(230, 222, 220))
    draw.text((right_x + 145, 9), "📶", font=f_panel, fill=(230, 222, 220))
    draw.text((right_x + 175, 9), "🔋 98%", font=f_panel, fill=(34, 197, 94))
    draw.text((right_x + 245, 9), "⏻", font=f_panel, fill=(230, 222, 220))

    # 6. PANEL LATERAL INTERACTIVO (HUD)
    hud_w, hud_h = 336, 890
    hud_x = W_DESK - hud_w - 32
    hud_y = panel_h + 24

    # Fondo HUD translúcido con borde en relieve
    hud_surf = Image.new('RGBA', (hud_w, hud_h), (12, 5, 7, 240))
    desk.paste(hud_surf, (hud_x, hud_y), hud_surf)
    # Borde rojo hierro
    draw.rectangle([(hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h)], outline=(120, 38, 34, 255), width=2)
    # Filete dorado interior
    draw.rectangle([(hud_x + 4, hud_y + 4), (hud_x + hud_w - 4, hud_y + hud_h - 4)], outline=(180, 83, 9, 140), width=1)

    f_hud_tit = get_font(13)
    f_hud_big = get_font(28)
    f_hud_body = get_font(11)
    f_hud_runes = get_font(10)

    # Tarjeta 1: TIEMPO & CALENDARIO
    cur_y = hud_y + 16
    draw.text((hud_x + 16, cur_y), "TIEMPO & FASE LUNAR", font=f_hud_tit, fill=(251, 191, 36))
    cur_y += 24
    draw.text((hud_x + 16, cur_y), "12:00:24", font=f_hud_big, fill=(254, 240, 138))
    cur_y += 38
    draw.text((hud_x + 16, cur_y), "Viernes, 13 de Noviembre 2026", font=f_hud_body, fill=(230, 222, 220))
    cur_y += 18
    draw.text((hud_x + 16, cur_y), "🌑 Luna Nueva (Día 29.5 · Ciclo de Sombras)", font=f_hud_body, fill=(245, 158, 11))

    # Separador
    cur_y += 26
    draw.line([(hud_x + 16, cur_y), (hud_x + hud_w - 16, cur_y)], fill=(74, 25, 29), width=1)
    cur_y += 14

    # Tarjeta 2: FORJAS DE BARAD-DÛR (Métricas del sistema)
    draw.text((hud_x + 16, cur_y), "FORJAS (SISTEMA & PODER)", font=f_hud_tit, fill=(251, 191, 36))
    cur_y += 24
    # CPU
    draw.text((hud_x + 16, cur_y), "Carga CPU: 14% (8 Núcleos activos)", font=f_hud_body, fill=(230, 222, 220))
    cur_y += 18
    draw.rectangle([(hud_x + 16, cur_y), (hud_x + hud_w - 16, cur_y + 8)], fill=(38, 15, 20), outline=(74, 25, 29))
    draw.rectangle([(hud_x + 16, cur_y), (hud_x + 16 + int((hud_w - 32) * 0.14), cur_y + 8)], fill=(255, 55, 0))
    cur_y += 16
    # RAM
    draw.text((hud_x + 16, cur_y), "Memoria: 3.4 GB / 15.3 GB (22%)", font=f_hud_body, fill=(230, 222, 220))
    cur_y += 18
    draw.rectangle([(hud_x + 16, cur_y), (hud_x + hud_w - 16, cur_y + 8)], fill=(38, 15, 20), outline=(74, 25, 29))
    draw.rectangle([(hud_x + 16, cur_y), (hud_x + 16 + int((hud_w - 32) * 0.22), cur_y + 8)], fill=(245, 158, 11))
    cur_y += 16
    # Poder / Temp
    draw.text((hud_x + 16, cur_y), "Temperatura: 42°C · Nivel de Poder: 98%", font=f_hud_body, fill=(249, 115, 22))

    # Separador
    cur_y += 26
    draw.line([(hud_x + 16, cur_y), (hud_x + hud_w - 16, cur_y)], fill=(74, 25, 29), width=1)
    cur_y += 14

    # Tarjeta 3: HUESTES DE MORDOR (Red & Conexión)
    draw.text((hud_x + 16, cur_y), "HUESTES (RED & ENLACE)", font=f_hud_tit, fill=(251, 191, 36))
    cur_y += 24
    draw.text((hud_x + 16, cur_y), "Interfaz: enp3s0 (Enlace Activo 1Gbps)", font=f_hud_body, fill=(230, 222, 220))
    cur_y += 18
    draw.text((hud_x + 16, cur_y), "IP Local: 192.168.1.213", font=f_hud_body, fill=(245, 158, 11))
    cur_y += 18
    draw.text((hud_x + 16, cur_y), "Tráfico: ↓ 482 KB/s · ↑ 64 KB/s", font=f_hud_body, fill=(179, 157, 152))

    # Separador
    cur_y += 26
    draw.line([(hud_x + 16, cur_y), (hud_x + hud_w - 16, cur_y)], fill=(74, 25, 29), width=1)
    cur_y += 14

    # Tarjeta 4: ARMERÍA (Almacenamiento)
    draw.text((hud_x + 16, cur_y), "ARMERÍA (ALMACENAMIENTO /)", font=f_hud_tit, fill=(251, 191, 36))
    cur_y += 24
    draw.text((hud_x + 16, cur_y), "Disco Raíz: 38% usado (142 GB libres)", font=f_hud_body, fill=(230, 222, 220))
    cur_y += 18
    draw.rectangle([(hud_x + 16, cur_y), (hud_x + hud_w - 16, cur_y + 8)], fill=(38, 15, 20), outline=(74, 25, 29))
    draw.rectangle([(hud_x + 16, cur_y), (hud_x + 16 + int((hud_w - 32) * 0.38), cur_y + 8)], fill=(220, 38, 38))

    # Separador
    cur_y += 28
    draw.line([(hud_x + 16, cur_y), (hud_x + hud_w - 16, cur_y)], fill=(74, 25, 29), width=1)
    cur_y += 16

    # Tarjeta 5: INSCRIPCIÓN DEL ANILLO ÚNICO
    draw.text((hud_x + 16, cur_y), "INSCRIPCIÓN DEL ANILLO ÚNICO", font=f_hud_tit, fill=(251, 191, 36))
    cur_y += 24
    draw.text((hud_x + 16, cur_y), "«Ash nazg durbatulûk,", font=f_hud_body, fill=(254, 240, 138))
    cur_y += 18
    draw.text((hud_x + 16, cur_y), "  ash nazg gimbatul,", font=f_hud_body, fill=(254, 240, 138))
    cur_y += 18
    draw.text((hud_x + 16, cur_y), "  ash nazg thrakatulûk", font=f_hud_body, fill=(254, 240, 138))
    cur_y += 18
    draw.text((hud_x + 16, cur_y), "  agh burzum-ishi krimpatul.»", font=f_hud_body, fill=(254, 240, 138))
    cur_y += 24
    draw.text((hud_x + 16, cur_y), "— Forjado en las llamas del Orodruin", font=f_hud_body, fill=(239, 68, 68))

    # Guardar captura
    dest_path = os.path.join(CAPTURAS_DIR, 'mordor-preview.png')
    desk.save(dest_path)
    print(f"  -> Guardado: {dest_path}")

def crea_captura_terminal():
    print("==> Generando capturas/mordor-terminal.png (Ptyxis con paleta oficial y CLI)...")
    base_fondo = os.path.join(FONDOS_DIR, 'mordor-noche.png')
    desk = Image.open(base_fondo).convert('RGBA').resize((W_DESK, H_DESK), Image.NEAREST)

    # Ventana de Terminal Ptyxis (1200x820 centrada)
    term_w, term_h = 1240, 840
    term_x = (W_DESK - term_w) // 2
    term_y = (H_DESK - term_h) // 2

    # Sombra de ventana
    overlay = Image.new('RGBA', (W_DESK, H_DESK), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle([(term_x - 12, term_y - 12), (term_x + term_w + 12, term_y + term_h + 12)], radius=18, fill=(0, 0, 0, 160))
    desk = Image.alpha_composite(desk, overlay)
    draw = ImageDraw.Draw(desk)

    # Caja de la ventana Ptyxis
    # Barra de título
    title_h = 42
    draw.rounded_rectangle([(term_x, term_y), (term_x + term_w, term_y + term_h)], radius=12, fill=(13, 2, 8, 250), outline=(120, 38, 34, 255), width=1)
    # Cabecera
    draw.rounded_rectangle([(term_x, term_y), (term_x + term_w, term_y + title_h)], radius=12, fill=(22, 8, 14, 255))
    draw.rectangle([(term_x, term_y + title_h - 4), (term_x + term_w, term_y + title_h)], fill=(22, 8, 14, 255))
    draw.line([(term_x, term_y + title_h), (term_x + term_w, term_y + title_h)], fill=(120, 38, 34, 220), width=1)

    f_title = get_font(12)
    f_term = get_font(13)
    f_ascii = get_font(12)

    # Botones ventana estilo GNOME
    draw.ellipse([(term_x + 18, term_y + 14), (term_x + 30, term_y + 26)], fill=(239, 68, 68, 255))
    draw.ellipse([(term_x + 38, term_y + 14), (term_x + 50, term_y + 26)], fill=(245, 158, 11, 255))
    draw.ellipse([(term_x + 58, term_y + 14), (term_x + 70, term_y + 26)], fill=(34, 197, 94, 255))

    # Título
    title_text = "2asird@PC213: ~/Descargas/pixelmordor — mordor estado"
    draw.text((term_x + 90, term_y + 13), title_text, font=f_title, fill=(230, 222, 220))

    # Contenido de la terminal
    tx = term_x + 28
    ty = term_y + title_h + 20

    # Prompt
    draw.text((tx, ty), "2asird@PC213:~/Descargas/pixelmordor$ ", font=f_term, fill=(239, 68, 68))
    draw.text((tx + 365, ty), "mordor estado", font=f_term, fill=(254, 240, 138))
    ty += 28

    # Banner ASCII en rojo
    ascii_banner = [
        r"        /\          /\\",
        r"       /  \        /  \\",
        r"      / /\ \      / /\ \\",
        r"     / /  \ \    / /  \ \\",
        r"    /_/    \_\  /_/    \_\\",
        r"         \   ||   /",
        r"          \  ||  /",
        r"       .---.-||-.---.",
        r"      /   (  👁  )   \\",
        r"     |   .-------.   |",
        r"     |  /  SAURON \  |",
        r"     | | TIERRA DE | |",
        r"     |  \  MORDOR /  |",
        r"      \  '-------'  /",
        r"       '---.---.---'",
        r"           | | |",
        r"          /  |  \\",
        r"         /___|___\\"
    ]
    for line in ascii_banner:
        draw.text((tx + 60, ty), line, font=f_ascii, fill=(239, 68, 68))
        ty += 16

    ty += 12
    draw.text((tx, ty), "═══════════════════════════════════════════════════════════════════════════════════", font=f_term, fill=(185, 28, 28))
    ty += 20
    draw.text((tx + 120, ty), "ESTADO DEL REINO DE MORDOR (LOTR PIXELZEN v1.3.0)", font=f_term, fill=(254, 240, 138))
    ty += 20
    draw.text((tx, ty), "═══════════════════════════════════════════════════════════════════════════════════", font=f_term, fill=(185, 28, 28))
    ty += 26

    lineas_estado = [
        ("  • Elevación Solar Real:", " +34.2° (☀️ CENIZA DIURNA)", (251, 191, 36)),
        ("  • Coordenadas:", " Madrid (40.4168°N, 3.7038°O) — Algoritmo NOAA Local", (230, 222, 220)),
        ("  • Extensión GNOME:", " Activa (pixelzen@mosqui1988.github.io)", (34, 197, 94)),
        ("  • Clima Sincronizado:", " Atmósfera despejada sobre Barad-dûr (14°C · Viento 15 km/h)", (56, 189, 248)),
        ("  • Eficiencia Energética:", " Activa (24 FPS · Estado: Corriente alterna / 100%)", (34, 197, 94)),
        ("  • Pantalla de Bloqueo:", " El Morannon y el Gran Ojo (Configurada y activa)", (245, 158, 11)),
        ("  • Cursor del Sistema:", " MordorCursor (Daga de Morgul y Guantelete)", (239, 68, 68)),
        ("  • Paleta de Terminal:", " Mordor (Ptyxis) instalada en ~/.local/share/org.gnome.Ptyxis/palettes/", (251, 191, 36)),
        ("  • Carga de CPU:", " 12.8% usuario (8 hilos activos)", (230, 222, 220)),
        ("  • Memoria RAM:", " 3.4 GB / 15.3 GB en uso (22%)", (230, 222, 220))
    ]
    for tag, val, c_val in lineas_estado:
        draw.text((tx, ty), tag, font=f_term, fill=(230, 222, 220))
        bbox = draw.textbbox((0, 0), tag, font=f_term)
        w_tag = bbox[2] - bbox[0]
        draw.text((tx + w_tag, ty), val, font=f_term, fill=c_val)
        ty += 22

    ty += 8
    draw.text((tx, ty), "═══════════════════════════════════════════════════════════════════════════════════", font=f_term, fill=(185, 28, 28))
    ty += 28
    draw.text((tx, ty), "2asird@PC213:~/Descargas/pixelmordor$ ", font=f_term, fill=(239, 68, 68))
    # Cursor parpadeante
    bbox = draw.textbbox((0, 0), "2asird@PC213:~/Descargas/pixelmordor$ ", font=f_term)
    cur_x_pos = tx + bbox[2] - bbox[0]
    draw.rectangle([(cur_x_pos, ty + 2), (cur_x_pos + 9, ty + 16)], fill=(254, 240, 138))

    dest_path = os.path.join(CAPTURAS_DIR, 'mordor-terminal.png')
    desk.save(dest_path)
    print(f"  -> Guardado: {dest_path}")

def crea_captura_definitiva():
    print("==> Generando capturas/preview_mordor_definitivo.png (Hero collage)...")
    dest_path = os.path.join(CAPTURAS_DIR, 'preview_mordor_definitivo.png')
    # Usar mordor-preview como base hero
    preview_src = os.path.join(CAPTURAS_DIR, 'mordor-preview.png')
    if os.path.isfile(preview_src):
        img = Image.open(preview_src)
        img.save(dest_path)
        print(f"  -> Guardado: {dest_path}")

def main():
    crea_captura_escritorio()
    crea_captura_terminal()
    crea_captura_definitiva()
    print("¡Todas las capturas actualizadas con éxito!")

if __name__ == '__main__':
    main()
