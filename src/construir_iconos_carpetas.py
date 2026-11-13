#!/usr/bin/env python3
"""PixelMordor - Generador del tema de iconos para carpetas de GNOME (Nautilus).
Construye el tema de iconos en icons/Mordor:
- index.theme con herencia a Adwaita / Yaru / hicolor
- Carpetas en obsidian volcánico (#17070f) con filo carmesí (#dc2626) y emblemas en pixel art
- user-home, folder-download, folder-documents, folder-music, folder-videos, folder-pictures, user-trash
"""

import os
from PIL import Image, ImageDraw

REPO_DIR = '/home/2asird/Descargas/pixelmordor'
ICONS_BASE = os.path.join(REPO_DIR, 'icons', 'Mordor')
DIR_48 = os.path.join(ICONS_BASE, 'places', '48')
DIR_128 = os.path.join(ICONS_BASE, 'places', '128')
os.makedirs(DIR_48, exist_ok=True)
os.makedirs(DIR_128, exist_ok=True)

# index.theme
index_theme = """[Icon Theme]
Name=Mordor
Comment=Tema de iconos temáticos de Mordor (El Señor de los Anillos)
Inherits=Adwaita,Yaru,breeze,hicolor
Directories=places/48,places/128

[places/48]
Size=48
Type=Fixed
Context=Places

[places/128]
Size=128
Type=Fixed
Context=Places
"""

with open(os.path.join(ICONS_BASE, 'index.theme'), 'w', encoding='utf-8') as f:
    f.write(index_theme)

def dibuja_base_carpeta(draw, w, h):
    # Pestaña trasera
    tab_w = int(w * 0.42)
    tab_h = int(h * 0.22)
    draw.rounded_rectangle([int(w * 0.1), int(h * 0.15), int(w * 0.1) + tab_w, int(h * 0.15) + tab_h], radius=int(w*0.04), fill='#450a0a', outline='#782622')
    # Cuerpo principal de la carpeta
    box_t = int(h * 0.26)
    box_b = int(h * 0.88)
    box_l = int(w * 0.08)
    box_r = int(w * 0.92)
    # Fondo obsidiana
    draw.rounded_rectangle([box_l, box_t, box_r, box_b], radius=int(w * 0.08), fill='#17070f', outline='#dc2626', width=max(1, int(w*0.02)))
    # Filo decorativo de lava
    draw.line([(box_l + int(w*0.05), box_t + int(h*0.04)), (box_r - int(w*0.05), box_t + int(h*0.04))], fill='#f59e0b', width=max(1, int(w*0.015)))

def genera_icono(tipo, size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = h = size

    if tipo == 'user-trash':
        # Cráter de Orodruin vacío
        d.polygon([(int(w*0.15), int(h*0.85)), (int(w*0.35), int(h*0.35)), (int(w*0.65), int(h*0.35)), (int(w*0.85), int(h*0.85))], fill='#17070f', outline='#782622')
        # Caldera
        d.ellipse([int(w*0.32), int(h*0.30), int(w*0.68), int(h*0.42)], fill='#0d0208', outline='#dc2626')
        return img
    elif tipo == 'user-trash-full':
        # Cráter lleno de lava hirviendo
        d.polygon([(int(w*0.15), int(h*0.85)), (int(w*0.35), int(h*0.35)), (int(w*0.65), int(h*0.35)), (int(w*0.85), int(h*0.85))], fill='#17070f', outline='#ef4444')
        d.ellipse([int(w*0.32), int(h*0.30), int(w*0.68), int(h*0.42)], fill='#f59e0b', outline='#ef4444')
        d.ellipse([int(w*0.42), int(h*0.33), int(w*0.58), int(h*0.39)], fill='#fef08a')
        return img

    dibuja_base_carpeta(d, w, h)
    cx, cy = w // 2, int(h * 0.58)

    if tipo == 'folder-home':
        # Silueta de Barad-dûr
        sw = int(w * 0.12)
        sh = int(h * 0.24)
        d.rectangle([cx - sw, cy - sh, cx + sw, cy + sh], fill='#2a0815', outline='#dc2626')
        # Cuernos
        d.line([(cx - sw, cy - sh), (cx - sw - int(w*0.04), cy - sh - int(h*0.08))], fill='#ef4444', width=max(1, int(w*0.02)))
        d.line([(cx + sw, cy - sh), (cx + sw + int(w*0.04), cy - sh - int(h*0.08))], fill='#ef4444', width=max(1, int(w*0.02)))
        # Pupila central
        d.ellipse([cx - int(w*0.03), cy - sh - int(h*0.02), cx + int(w*0.03), cy - sh + int(h*0.04)], fill='#f59e0b')

    elif tipo == 'folder-download':
        # Puertas Negras con flecha de descarga ardiente
        d.rectangle([cx - int(w*0.16), cy - int(h*0.12), cx + int(w*0.16), cy + int(h*0.14)], outline='#782622', fill='#0d0208')
        # Flecha dorada hacia abajo
        d.line([(cx, cy - int(h*0.14)), (cx, cy + int(h*0.08))], fill='#f59e0b', width=max(2, int(w*0.03)))
        d.polygon([(cx - int(w*0.08), cy + int(h*0.06)), (cx + int(w*0.08), cy + int(h*0.06)), (cx, cy + int(h*0.16))], fill='#f59e0b')

    elif tipo == 'folder-documents':
        # Pergamino con versos Tengwar
        pw, ph = int(w * 0.14), int(h * 0.18)
        d.rectangle([cx - pw, cy - ph, cx + pw, cy + ph], fill='#fef08a', outline='#f59e0b')
        # Líneas de escritura
        for line_y in range(cy - ph + int(h*0.04), cy + ph - int(h*0.02), int(h*0.04)):
            d.line([(cx - pw + int(w*0.03), line_y), (cx + pw - int(w*0.03), line_y)], fill='#991b1b', width=max(1, int(w*0.01)))

    elif tipo == 'folder-music':
        # El Anillo Único de oro
        r = int(w * 0.13)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline='#f59e0b', width=max(2, int(w*0.04)), fill='#260a12')
        d.ellipse([cx - r + int(w*0.04), cy - r + int(w*0.04), cx + r - int(w*0.04), cy + r - int(w*0.04)], fill='#17070f')

    elif tipo == 'folder-videos':
        # El Palantír (Orbe con llama interior)
        r = int(w * 0.14)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill='#0d0208', outline='#dc2626', width=max(1, int(w*0.02)))
        d.ellipse([cx - int(r*0.6), cy - int(r*0.6), cx + int(r*0.6), cy + int(r*0.6)], fill='#ef4444')
        d.ellipse([cx - int(r*0.25), cy - int(r*0.25), cx + int(r*0.25), cy + int(r*0.25)], fill='#fef08a')

    elif tipo == 'folder-pictures':
        # El Gran Ojo de Sauron
        rx, ry = int(w * 0.16), int(h * 0.10)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill='#ef4444', outline='#f59e0b')
        d.ellipse([cx - int(rx*0.5), cy - int(ry*0.7), cx + int(rx*0.5), cy + int(ry*0.7)], fill='#fef08a')
        d.ellipse([cx - int(w*0.02), cy - int(ry*0.7), cx + int(w*0.02), cy + int(ry*0.7)], fill='#0d0208')

    return img

ICONOS = [
    'folder',
    'folder-home',
    'folder-download',
    'folder-documents',
    'folder-music',
    'folder-videos',
    'folder-pictures',
    'user-trash',
    'user-trash-full',
]

# Aliases estándar de FreeDesktop
ALIASES = {
    'folder-home': ['user-home', 'user-bookmarks'],
    'folder-download': ['folder-downloads'],
    'folder-pictures': ['folder-photos', 'folder-images'],
}

def construir_iconos():
    print("==> Generando tema de iconos Mordor para GNOME Files...")
    for size, target_dir in [(48, DIR_48), (128, DIR_128)]:
        for ico_name in ICONOS:
            im = genera_icono(ico_name, size)
            f_path = os.path.join(target_dir, f"{ico_name}.png")
            im.save(f_path, 'PNG')
            # Crear enlaces o copias para aliases
            if ico_name in ALIASES:
                for alias in ALIASES[ico_name]:
                    im.save(os.path.join(target_dir, f"{alias}.png"), 'PNG')
        print(f"  Iconos {size}x{size} guardados en {target_dir}")

if __name__ == '__main__':
    construir_iconos()
