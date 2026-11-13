#!/usr/bin/env python3
"""PixelMordor - Tema de cursores pixel art de Mordor (El Señor de los Anillos).
Formato Xcursor estándar para X11 y Wayland, sin dependencias externas.
- Flecha: Daga forjada en Barad-dûr con punta de magma y filo de acero oscuro.
- Puntero (Mano): Guantelete de hierro de Sauron con el Anillo Único grabado en oro.
- Espera (Girando): El Anillo Único girando con runas ardientes.
- Prohibido: El Ojo de Sauron tachado.
- Texto: Aguja de obsidiana.
"""
import math, os, shutil, struct

OUT = os.path.expanduser('~/.local/share/icons/MordorCursor')
COL = {
    'X': (8, 3, 6),        # Obsidiana de Barad-dûr
    'o': (168, 155, 158),   # Acero forjado
    'r': (239, 68, 68),     # Fuego carmesí
    'y': (254, 240, 138),   # Núcleo ardiente
    'a': (245, 158, 11),    # Oro del Anillo Único
    'g': (234, 88, 12),     # Magma naranja
    'v': (88, 28, 48),      # Sombra púrpura
    'c': (249, 115, 22),    # Lava ardiente
    'p': (251, 191, 36)     # Oro brillante
}

def vacio(): return [['.'] * 16 for _ in range(16)]

def linea(g, x0, y0, x1, y1, c='o'):
    n = max(abs(x1 - x0), abs(y1 - y0)) or 1
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n)
        y = round(y0 + (y1 - y0) * i / n)
        if 0 <= x < 16 and 0 <= y < 16: g[y][x] = c

def contorno(g):
    r = [fila[:] for fila in g]
    for y in range(16):
        for x in range(16):
            if g[y][x] != '.' and g[y][x] != 'X':
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        xx, yy = x + dx, y + dy
                        if 0 <= xx < 16 and 0 <= yy < 16 and r[yy][xx] == '.': r[yy][xx] = 'X'
    return r

def desde(filas, ox=0, oy=0, g=None):
    g = g or vacio()
    for y, f in enumerate(filas):
        for x, ch in enumerate(f):
            if ch != '.' and 0 <= x + ox < 16 and 0 <= y + oy < 16: g[y + oy][x + ox] = ch
    return g

FLECHA = [
    'X', 'XX', 'XrX', 'XrrX', 'XryrX', 'XroorX', 'XrooorX', 'XroooorX',
    'XrooooorX', 'XrooooorXX', 'XroXoorX', 'XrXXoorX', 'XX..XoorX',
    'X...XoorX', '.....XoorX', '.....XXXX'
]

def flecha(extra=None):
    g = desde(FLECHA)
    for x, y in ((0, 0), (0, 1), (1, 1)): g[y][x] = 'y' # Punta ardiente de magma
    if extra: extra(g)
    return g, (0, 0)

def manita():
    # Guantelete de hierro negro de Sauron con el Anillo Único en oro
    f = [
        '....XX..........', '...XoX..........', '...XoX..........', '...XoX..........',
        '...XoXXX........', '...XoXoXXX......', '.XXXoXoXoXX.....', 'XooXooooooooX...',
        'XoooooooooooX...', '.XooooooooooX...', '..XoooooooooX...', '..XoooooooooX...',
        '...XooooooooX...', '...XooooooooX...', '....XoooooooX...', '....XXXXXXXXX...'
    ]
    g = desde(f)
    # Punta en hierro afilado
    for x, y in ((4, 0), (5, 0), (4, 1)): g[y][x] = 'r'
    # El Anillo Único en el dedo (X=7, Y=7)
    for x, y in ((6, 8), (7, 8), (8, 8)): g[y][x] = 'a'
    g[8][7] = 'y' # Reflejo de oro vivo
    return g, (4, 0)

def ibeam(rot=False):
    g = vacio()
    for x in range(5, 10): g[0][x] = 'X'; g[15][x] = 'X'
    for x in (6, 7, 8): g[1][x] = 'r'; g[14][x] = 'r'
    for x in (5, 9): g[1][x] = 'X'; g[14][x] = 'X'
    for y in range(2, 14):
        g[y][6] = 'X'; g[y][7] = 'y'; g[y][8] = 'X'
    g[2][5] = 'X'; g[2][9] = 'X'; g[13][5] = 'X'; g[13][9] = 'X'
    if rot: g = [[g[x][y] for x in range(16)] for y in range(16)]
    return g, (7, 8)

def cruz():
    g = vacio()
    for a, b in (((7, 1), (7, 5)), ((7, 9), (7, 13)), ((1, 7), (5, 7)), ((9, 7), (13, 7))): linea(g, *a, *b, 'r')
    g[7][7] = 'y'
    return contorno(g), (7, 7)

def flechas(dirs, diag=None):
    g = vacio()
    if diag == 'nwse':
        linea(g, 3, 3, 12, 12, 'r')
        for a, b in (((3, 3), (7, 3)), ((3, 3), (3, 7)), ((12, 12), (8, 12)), ((12, 12), (12, 8))): linea(g, *a, *b, 'g')
    elif diag == 'nesw':
        linea(g, 12, 3, 3, 12, 'r')
        for a, b in (((12, 3), (8, 3)), ((12, 3), (12, 7)), ((3, 12), (7, 12)), ((3, 12), (3, 8))): linea(g, *a, *b, 'g')
    else:
        h = 2 if len(dirs) > 1 else 3
        if 'h' in dirs:
            linea(g, 2, 7, 13, 7, 'r')
            for a, b in (((2, 7), (2 + h, 7 - h)), ((2, 7), (2 + h, 7 + h)), ((13, 7), (13 - h, 7 - h)), ((13, 7), (13 - h, 7 + h))): linea(g, *a, *b, 'g')
        if 'v' in dirs:
            linea(g, 7, 2, 7, 13, 'r')
            for a, b in (((7, 2), (7 - h, 2 + h)), ((7, 2), (7 + h, 2 + h)), ((7, 13), (7 - h, 13 - h)), ((7, 13), (7 + h, 13 - h))): linea(g, *a, *b, 'g')
    return contorno(g), (7, 7)

def prohibido():
    g = vacio()
    for i in range(64):
        a = i / 64 * 2 * math.pi
        x, y = round(7.5 + 6 * math.cos(a)), round(7.5 + 6 * math.sin(a))
        if 0 <= x < 16 and 0 <= y < 16: g[y][x] = 'r'
    linea(g, 3, 12, 12, 3, 'X')
    g[7][7] = 'y' # El Ojo de Sauron en el centro
    return contorno(g), (7, 7)

def girando(frame, con_flecha=False):
    # El Anillo Único girando con runas ardientes
    g = vacio()
    for i in range(12):
        a = i / 12 * 2 * math.pi - math.pi / 2
        x, y = round(7.5 + 5.2 * math.cos(a)), round(7.5 + 5.2 * math.sin(a))
        d = (i - frame) % 12
        c = 'y' if d == 0 else ('a' if d in (1, 2) else ('r' if d in (3, 4) else 'X'))
        if 0 <= x < 16 and 0 <= y < 16: g[y][x] = c
    return contorno(g), (7, 7)

def ayuda():
    def extra(g):
        for x, y in ((9, 8), (10, 8), (11, 9), (11, 10), (10, 11), (10, 12), (10, 14)): g[y][x] = 'a'
    g, h = flecha(extra)
    return g, h

def con_signo(simbolo):
    g, h = flecha()
    pts = {'+': [(11, 9), (11, 10), (11, 11), (11, 12), (11, 13), (9, 11), (10, 11), (12, 11), (13, 11)],
           'l': [(9, 10), (10, 10), (11, 10), (12, 10), (12, 11), (12, 12), (12, 13), (11, 12), (10, 13)],
           'm': [(9, 10), (10, 10), (11, 10), (12, 10), (9, 12), (10, 12), (11, 12), (12, 12), (9, 14), (10, 14), (11, 14), (12, 14)]}[simbolo]
    for x, y in pts:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < 16 and 0 <= y + dy < 16 and g[y + dy][x + dx] == '.': g[y + dy][x + dx] = 'X'
    for x, y in pts: g[y][x] = 'a' if simbolo == '+' else 'r'
    return g, h

def mano_abierta():
    f = [
        '....X.X.X.......', '...XoXoXoX......', '...XoXoXoXX.....', '..XXoooooooX....',
        '.XooXooooooX....', '.XoooooooooX....', '..XooooooooX....', '..XooooooooX....',
        '...XoooooooX....', '...XoooooooX....', '....XXXXXXXX....'
    ]
    g = desde(f, 1, 2)
    g[6][7] = 'a'; g[7][7] = 'y' # Anillo Único
    return g, (7, 7)

def puno():
    f = [
        '...XXXXXXXX.....', '..XoXoXoXoXX....', '..XooooooooX....', '..XooooooooX....',
        '..XoooooooooX...', '...XooooooooX...', '...XoooooooX....', '....XXXXXXXX....'
    ]
    g = desde(f, 1, 4)
    g[7][6] = 'a'; g[7][7] = 'y'
    return g, (7, 8)

def lupa(mas):
    g = vacio()
    for i in range(48):
        a = i / 48 * 2 * math.pi
        x, y = round(6.5 + 4.5 * math.cos(a)), round(6.5 + 4.5 * math.sin(a))
        g[y][x] = 'a'
    linea(g, 10, 10, 14, 14, 'o'); linea(g, 11, 10, 14, 13, 'X')
    linea(g, 4, 6, 8, 6, 'r')
    if mas: linea(g, 6, 4, 6, 8, 'r')
    return contorno(g), (6, 6)

BASE = {
    'default': lambda: flecha(), 'pointer': manita, 'text': lambda: ibeam(), 'vertical-text': lambda: ibeam(True), 'crosshair': cruz,
    'move': lambda: flechas('hv'), 'ew-resize': lambda: flechas('h'), 'ns-resize': lambda: flechas('v'),
    'nwse-resize': lambda: flechas('', 'nwse'), 'nesw-resize': lambda: flechas('', 'nesw'), 'not-allowed': prohibido,
    'help': ayuda, 'copy': lambda: con_signo('+'), 'alias': lambda: con_signo('l'), 'context-menu': lambda: con_signo('m'),
    'grab': mano_abierta, 'grabbing': puno, 'zoom-in': lambda: lupa(True), 'zoom-out': lambda: lupa(False)
}

ANIM = {'wait': lambda fr: girando(fr), 'progress': lambda fr: girando(fr, True)}

ALIAS = {
    'default': 'arrow top_left_arrow left_ptr 00000400000200040008000408080408',
    'pointer': 'hand hand1 hand2 pointing_hand e29285e634086352946a0e7090d702f0 9d800488f4286424687e40e608816663',
    'text': 'xterm ibeam', 'crosshair': 'cross cross_reverse tcross',
    'move': 'fleur 4498f0e0c1937ffe01e2183675003b10 size_all',
    'ew-resize': 'h_double_arrow size_hor col-resize e-resize w-resize 028006030e0e7ebffc7f7070c0600140',
    'ns-resize': 'b_v_double_arrow size_ver v_double_arrow n-resize s-resize split_v top_side bottom_side 2870a09082c103050810ffdffffe0204',
    'nwse-resize': 'size_fdiag nw-resize se-resize top_left_corner bottom_right_corner c7088f0f3e6c8088236ef8e1e3e70000 bd_double_arrow',
    'nesw-resize': 'size_bdiag ne-resize sw-resize top_right_corner bottom_left_corner fcf1c3c7cd4491d801f1e1c78f100000 fd_double_arrow',
    'not-allowed': 'crossed_circle no-drop forbidden circle dnd-no-drop 03b6e0fcb3499374a867c041f52298f0',
    'help': 'question_arrow whats_this left_ptr_help d9ce0ab605698f320427677b458ad60b',
    'grabbing': 'closedhand dnd-grabbing fcf21c00b30f7e3f83fe0dfd12e71cff', 'grab': 'dnd_grab openhand',
    'zoom-in': 'zoom_in', 'zoom-out': 'zoom_out',
    'wait': 'watch', 'progress': 'left_ptr_watch half-busy 08e8e1c95fe2fc01f976f1e063a24ccd_',
}

def render(g, k, hot):
    n = 16 * k
    px = []
    for y in range(n):
        for x in range(n):
            ch = g[y // k][x // k]
            if ch == '.': px.append(0)
            else:
                r, gg, b = COL[ch]
                px.append((255 << 24) | (r << 16) | (gg << 8) | b)
    return n, n, hot[0] * k + (k // 2 if k > 1 else 0), hot[1] * k + (k // 2 if k > 1 else 0), px

def escribe_xcursor(ruta, cuadros):
    n = len(cuadros); ptr = 16 + 12 * n; toc = b''; cuerpo = b''
    for (sz, w, h, xh, yh, delay, px) in cuadros:
        toc += struct.pack('<III', 0xfffd0002, sz, ptr + len(cuerpo))
        cuerpo += struct.pack('<IIIIIIIII', 36, 0xfffd0002, sz, 1, w, h, xh, yh, delay) + struct.pack('<%dI' % len(px), *px)
    open(ruta, 'wb').write(b'Xcur' + struct.pack('<III', 16, 0x10000, n) + toc + cuerpo)

def construir():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT + '/cursors', exist_ok=True)
    for nombre, f in BASE.items():
        g, hot = f()
        cuadros = []
        for k in (1, 2, 3, 4):
            w, h, xh, yh, px = render(g, k, hot)
            cuadros.append((16 * k, w, h, xh, yh, 0, px))
        escribe_xcursor(f'{OUT}/cursors/{nombre}', cuadros)
    for nombre, f in ANIM.items():
        cuadros = []
        for k in (2, 3, 4):
            for fr in range(12):
                g, hot = f(fr)
                w, h, xh, yh, px = render(g, k, hot)
                cuadros.append((16 * k, w, h, xh, yh, 80, px))
        escribe_xcursor(f'{OUT}/cursors/{nombre}', cuadros)
    for base, nombres in ALIAS.items():
        for a in nombres.split():
            a = a.rstrip('_')
            if a != base and not os.path.exists(f'{OUT}/cursors/{a}'):
                try: os.symlink(base, f'{OUT}/cursors/{a}')
                except Exception: pass
    open(f'{OUT}/index.theme', 'w').write('[Icon Theme]\nName=MordorCursor\nComment=Cursor Pixel Art de Mordor (El Señor de los Anillos)\nInherits=breeze_cursors\n')
    return len(os.listdir(OUT + '/cursors'))

if __name__ == '__main__':
    print('==> Generando cursores temáticos de Mordor...')
    n = construir()
    print(f'==> {n} cursores generados con éxito en {OUT}')
