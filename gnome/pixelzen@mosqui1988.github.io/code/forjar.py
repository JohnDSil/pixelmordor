#!/usr/bin/env python3
"""forjar.py - Animación interactiva en terminal de la Forja del Anillo Único en Orodruin.
Arte ASCII 3D animado en 256 colores ANSI con fuego, ascuas y versos en Tengwar."""

import math, os, subprocess, sys, time

# Sonidos
SOUNDS_DIR = os.path.expanduser('~/.local/share/gnome-shell/extensions/pixelzen@mosqui1988.github.io/sounds')
def suena(nombre):
    s = os.path.join(SOUNDS_DIR, f"{nombre}.wav")
    if os.path.isfile(s):
        try:
            subprocess.Popen(['canberra-gtk-play', '-f', s], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            try:
                subprocess.Popen(['pw-play', s], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

# Versos de fuego
VERSOS = [
    "Ash nazg durbatulûk,",
    "ash nazg gimbatul,",
    "ash nazg thrakatulûk",
    "agh burzum-ishi krimpatul."
]

TRADUCCION = [
    "Un Anillo para gobernarlos a todos,",
    "un Anillo para encontrarlos,",
    "un Anillo para atraerlos a todos",
    "y atarlos en las tinieblas."
]

def render_ring(angle_y, tick):
    # Proyección 3D de un toroide (Anillo)
    w, h = 60, 22
    buf = [[' ' for _ in range(w)] for _ in range(h)]
    zbuf = [[-1000.0 for _ in range(w)] for _ in range(h)]
    cbuf = [['' for _ in range(w)] for _ in range(h)]

    R1 = 1.2 # Radio del tubo
    R2 = 3.6 # Radio mayor del anillo

    cos_b, sin_b = math.cos(angle_y), math.sin(angle_y)
    cos_a, sin_a = math.cos(0.42), math.sin(0.42) # Inclinación fija

    # Muestreo angular
    for theta_i in range(0, 628, 12):
        theta = theta_i / 100.0
        cos_t, sin_t = math.cos(theta), math.sin(theta)

        for phi_i in range(0, 628, 16):
            phi = phi_i / 100.0
            cos_p, sin_p = math.cos(phi), math.sin(phi)

            # Coordenadas del toroide
            circ_x = R2 + R1 * cos_t
            circ_y = R1 * sin_t

            # Rotación Y y X
            x = circ_x * cos_b + circ_y * sin_a * sin_b
            y = circ_y * cos_a
            z = -circ_x * sin_b + circ_y * sin_a * cos_b + 8.0

            ooz = 1.0 / z
            xp = int(w / 2 + 19.0 * ooz * x * 2.1)
            yp = int(h / 2 + 19.0 * ooz * y)

            # Iluminación
            L = cos_p * cos_t * sin_b - cos_a * cos_t * sin_b - sin_a * sin_t + cos_b * (cos_a * sin_t - sin_a * cos_t * sin_p)
            if 0 <= xp < w and 0 <= yp < h:
                if ooz > zbuf[yp][xp]:
                    zbuf[yp][xp] = ooz
                    luminance = max(0.0, min(1.0, (L + 1.4) / 2.8))
                    chars = ".,-~:;=!*#$@"
                    ch_idx = int(luminance * (len(chars) - 1))
                    buf[yp][xp] = chars[ch_idx]
                    # Paleta dorada ardiente
                    if luminance > 0.75:
                        cbuf[yp][xp] = "\033[1;37m" # Blanco brillante
                    elif luminance > 0.50:
                        cbuf[yp][xp] = "\033[1;33m" # Oro vivo
                    elif luminance > 0.25:
                        cbuf[yp][xp] = "\033[38;5;208m" # Naranja lava
                    else:
                        cbuf[yp][xp] = "\033[1;31m" # Rojo oscuro

    # Dibujar ascuas flotantes
    import random
    random.seed(tick // 2)
    for _ in range(14):
        ex = random.randint(2, w - 3)
        ey = random.randint(1, h - 2)
        if buf[ey][ex] == ' ':
            buf[ey][ex] = random.choice(['·', '*', '°'])
            cbuf[ey][ex] = random.choice(["\033[1;31m", "\033[1;33m", "\033[38;5;208m"])

    # Convertir a líneas coloreadas
    lines = []
    for y_idx in range(h):
        line_str = ""
        last_c = ""
        for x_idx in range(w):
            c = cbuf[y_idx][x_idx]
            if c != last_c:
                line_str += c
                last_c = c
            line_str += buf[y_idx][x_idx]
        lines.append(line_str + "\033[0m")
    return lines

def main():
    # Ocultar cursor de terminal
    sys.stdout.write("\033[?25l\033[2J")
    sys.stdout.flush()

    suena('erupcion')
    time.sleep(0.4)
    suena('anillo')

    total_frames = 110
    start_time = time.time()

    try:
        for f in range(total_frames):
            angle = (f / 35.0) * math.pi
            ring_lines = render_ring(angle, f)

            # Imprimir encabezado y anillo
            output = "\033[H"
            output += "\033[1;31m╔════════════════════════════════════════════════════════════╗\033[0m\n"
            output += "\033[1;33m║          LA FORJA DEL ANILLO ÚNICO · ORODRUIN              ║\033[0m\n"
            output += "\033[1;31m╚════════════════════════════════════════════════════════════╝\033[0m\n"

            for rl in ring_lines:
                output += "  " + rl + "\n"

            # Versos que van apareciendo según avanza la forja
            output += "\033[1;31m──────────────────────────────────────────────────────────────\033[0m\n"
            prog = f / float(total_frames)
            num_versos = min(4, int(prog * 5))

            for v_idx in range(4):
                if v_idx < num_versos:
                    output += f"  \033[1;33m🔥 {VERSOS[v_idx]:<30} \033[0;37m{TRADUCCION[v_idx]}\033[0m\n"
                else:
                    output += "  \033[1;30m· · ·\033[0m\n"

            output += "\033[1;31m──────────────────────────────────────────────────────────────\033[0m\n"
            output += "  \033[1;30m[Pulsa Ctrl+C para salir de la forja]\033[0m\n"

            sys.stdout.write(output)
            sys.stdout.flush()

            # Sonido de resonancia a mitad de la forja
            if f == 55:
                suena('sauron')

            time.sleep(0.045)

        suena('anillo')
        time.sleep(0.5)

    except (KeyboardInterrupt, BrokenPipeError):
        pass
    finally:
        try:
            # Restaurar cursor
            sys.stdout.write("\033[?25h\n\033[1;32m¡El Anillo Único ha sido forjado en las llamas del Destino!\033[0m\n\n")
            sys.stdout.flush()
        except Exception:
            pass

if __name__ == '__main__':
    main()
