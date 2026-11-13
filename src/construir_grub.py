#!/usr/bin/env python3
"""PixelMordor - Generador de Tema de Arranque GRUB 2.
Construye el tema completo en grub/mordor:
- background.png (1920x1080)
- Fuentes .pf2 (mordor_16.pf2, mordor_title_24.pf2)
- Pixmaps de selección (select_*.png) con efecto lava y marco obsidiana
- Barra de progreso (__timeout__) con resaltado de magma
- Iconos de sistema operativo (ubuntu, linux, windows)
- theme.txt oficial de GRUB 2
"""

import os, subprocess
from PIL import Image, ImageDraw

REPO_DIR = '/home/2asird/Descargas/pixelmordor'
GRUB_THEME_DIR = os.path.join(REPO_DIR, 'grub', 'mordor')
ICONS_DIR = os.path.join(GRUB_THEME_DIR, 'icons')
os.makedirs(ICONS_DIR, exist_ok=True)

# 1. Background image (1920x1080) a partir de mordor-bloqueo.png
src_bg = os.path.join(REPO_DIR, 'fondos', 'mordor-bloqueo.png')
if not os.path.exists(src_bg):
    src_bg = os.path.join(REPO_DIR, 'fondos', 'mordor-noche.png')

im = Image.open(src_bg)
# Center crop de 1920x1200 a 1920x1080
if im.size != (1920, 1080):
    w, h = im.size
    top = (h - 1080) // 2
    im_cropped = im.crop((0, max(0, top), min(1920, w), max(0, top) + 1080))
    if im_cropped.size != (1920, 1080):
        im_cropped = im_cropped.resize((1920, 1080), Image.Resampling.LANCZOS)
    im = im_cropped

bg_out = os.path.join(GRUB_THEME_DIR, 'background.png')
im.save(bg_out, 'PNG')
print(f"  [GRUB] Fondo generado: {bg_out} ({im.size})")

# 2. Fuentes PF2
font_otf = os.path.join(REPO_DIR, 'fuentes', 'DepartureMono-Regular.otf')
if os.path.exists(font_otf):
    p1 = os.path.join(GRUB_THEME_DIR, 'mordor_16.pf2')
    p2 = os.path.join(GRUB_THEME_DIR, 'mordor_title_24.pf2')
    subprocess.run(['grub-mkfont', '-s', '16', '-o', p1, font_otf], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['grub-mkfont', '-s', '24', '-o', p2, font_otf], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("  [GRUB] Fuentes mordor_16.pf2 y mordor_title_24.pf2 compiladas con éxito.")

# 3. Pixmaps de selección (Caja de 9 slices)
# Borde rojo/oro con fondo obsidiana
slices = {
    'c': (32, 32, '#1f0714'),
    'w': (6, 32, '#dc2626'),
    'e': (6, 32, '#dc2626'),
    'n': (32, 6, '#f59e0b'),
    's': (32, 6, '#dc2626'),
    'nw': (6, 6, '#f59e0b'),
    'ne': (6, 6, '#f59e0b'),
    'sw': (6, 6, '#dc2626'),
    'se': (6, 6, '#dc2626')
}

for name, (sw, sh, col) in slices.items():
    s_img = Image.new('RGBA', (sw, sh), col)
    s_img.save(os.path.join(GRUB_THEME_DIR, f'select_{name}.png'), 'PNG')

# 4. Progress bar slices
for name in ['c', 'w', 'e', 'n', 's', 'nw', 'ne', 'sw', 'se']:
    pb = Image.new('RGBA', (8, 8), '#0d0308')
    pb.save(os.path.join(GRUB_THEME_DIR, f'progress_bar_{name}.png'), 'PNG')
    ph = Image.new('RGBA', (8, 8), '#dc2626' if name in ('c', 'n', 's') else '#f59e0b')
    ph.save(os.path.join(GRUB_THEME_DIR, f'progress_hl_{name}.png'), 'PNG')

# 5. Iconos de sistemas operativos
def crea_icono(color, nombre):
    ico = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(ico)
    # Círculo / emblema de fuego
    d.ellipse((2, 2, 29, 29), outline='#dc2626', width=2, fill='#17070f')
    d.ellipse((8, 8, 23, 23), fill=color)
    d.rectangle((14, 4, 17, 27), fill='#f59e0b')
    ico.save(os.path.join(ICONS_DIR, f'{nombre}.png'), 'PNG')

crea_icono('#ef4444', 'ubuntu')
crea_icono('#f97316', 'linux')
crea_icono('#dc2626', 'gnu-linux')
crea_icono('#38bdf8', 'windows')
crea_icono('#f59e0b', 'recovery')
print("  [GRUB] Iconos de SO creados en icons/.")

# 6. theme.txt
theme_txt = """# ====================================================================
# GRUB 2 Theme: PixelMordor
# El Señor de los Anillos: La Tierra Oscura
# ====================================================================

title-text: "TIERRA DE MORDOR  ·  EL SEÑOR DE LOS ANILLOS"
title-font: "mordor_title_24"
title-color: "#f59e0b"

message-font: "mordor_16"
message-color: "#ef4444"
message-bg-color: "#0d0308"

desktop-image: "background.png"
desktop-color: "#070205"

terminal-box: "select_*.png"
terminal-font: "mordor_16"

+ boot_menu {
    left = 22%
    top = 32%
    width = 56%
    height = 50%
    item_font = "mordor_16"
    item_color = "#e6dedc"
    selected_item_color = "#fef08a"
    selected_item_pixmap_style = "select_*.png"
    icon_height = 32
    icon_width = 32
    item_height = 42
    item_padding = 10
    item_spacing = 12
}

+ progress_bar {
    id = "__timeout__"
    left = 25%
    top = 86%
    width = 50%
    height = 16
    show_text = true
    font = "mordor_16"
    text_color = "#f59e0b"
    align = "center"
    bar_style = "progress_bar_*.png"
    highlight_style = "progress_hl_*.png"
}

+ label {
    top = 92%
    left = 25%
    width = 50%
    align = "center"
    font = "mordor_16"
    text = "« Ash nazg durbatulûk, ash nazg gimbatul »"
    color = "#b91c1c"
}
"""

with open(os.path.join(GRUB_THEME_DIR, 'theme.txt'), 'w', encoding='utf-8') as f:
    f.write(theme_txt)

print(f"  [GRUB] Archivo theme.txt guardado en {GRUB_THEME_DIR}/theme.txt")
