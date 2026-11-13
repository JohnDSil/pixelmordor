#!/usr/bin/env python3
"""PixelMordor - mordor fetch
Presentador de telemetría y especificaciones del sistema con arte ASCII de Barad-dûr y el Ojo de Sauron.
Funciona de forma autónoma con colores ANSI puros (sin dependencias externas).
"""

import math, os, platform, re, shutil, sys, time

# Códigos de color ANSI
R = "\033[1;31m"      # Rojo intenso
DR = "\033[0;31m"     # Rojo oscuro
O = "\033[1;33m"      # Oro / Amarillo ardiente
OR = "\033[38;5;208m" # Naranja lava
W = "\033[1;37m"      # Blanco brillante
G = "\033[0;90m"      # Gris ceniza
RESET = "\033[0m"     # Reset

def strip_ansi(text):
    return re.sub(r'\033\[[0-9;]*m', '', text)

def get_os_info():
    distro = "Linux"
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    distro = line.split("=")[1].strip().strip('"')
                    break
    return distro

def get_uptime():
    try:
        with open("/proc/uptime") as f:
            total_sec = float(f.readline().split()[0])
            days = int(total_sec // 86400)
            hours = int((total_sec % 86400) // 3600)
            mins = int((total_sec % 3600) // 60)
            if days > 0:
                return f"{days}d {hours}h {mins}m"
            elif hours > 0:
                return f"{hours}h {mins}m"
            else:
                return f"{mins} mins"
    except Exception:
        return "Desconocido"

def get_cpu_info():
    model = "Desconocida"
    cores = os.cpu_count() or 1
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    model = line.split(":")[1].strip()
                    # Abreviar nombres largos de Intel/AMD
                    model = model.replace("(R)", "").replace("(TM)", "").replace("CPU", "").strip()
                    break
    except Exception:
        pass
    return f"{model} ({cores} núcleos)"

def get_mem_info():
    total_kb = 0
    avail_kb = 0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if "MemTotal:" in line:
                    total_kb = int(line.split()[1])
                elif "MemAvailable:" in line:
                    avail_kb = int(line.split()[1])
        used_gb = (total_kb - avail_kb) / 1024 / 1024
        total_gb = total_kb / 1024 / 1024
        pct = int(((total_kb - avail_kb) / total_kb) * 100) if total_kb > 0 else 0
        return f"{used_gb:.1f} GiB / {total_gb:.1f} GiB ({pct}%)"
    except Exception:
        return "Desconocida"

def get_disk_info():
    try:
        total, used, free = shutil.disk_usage("/")
        used_gb = used / (1024**3)
        total_gb = total / (1024**3)
        pct = int((used / total) * 100)
        return f"{used_gb:.1f} GiB / {total_gb:.1f} GiB ({pct}%)"
    except Exception:
        return "Desconocido"

def print_fetch():
    user = os.getenv("USER", "senor")
    host = platform.node()
    distro = get_os_info()
    kernel = platform.release()
    uptime = get_uptime()
    cpu = get_cpu_info()
    mem = get_mem_info()
    disk = get_disk_info()
    shell = os.path.basename(os.getenv("SHELL", "bash"))
    term = os.getenv("TERM_PROGRAM", os.getenv("TERM", "ptyxis"))

    ascii_art = [
        f"{R}          /\\          /\\{RESET}",
        f"{R}         /  \\        /  \\{RESET}",
        f"{R}        / /\\ \\      / /\\ \\{RESET}",
        f"{R}       / /  \\ \\    / /  \\ \\{RESET}",
        f"{R}      /_/    \\_\\  /_/    \\_\\{RESET}",
        f"{R}           \\   ||   /{RESET}",
        f"{R}            \\  ||  /{RESET}",
        f"{OR}         .---.-||-.---.{RESET}",
        f"{OR}        /   (  {O}👁{OR}  )   \\{RESET}",
        f"{R}       |   .-------.   |{RESET}",
        f"{R}       |  /  {W}SAURON{R} \\  |{RESET}",
        f"{R}       | | {O}TIERRA DE{R} | |{RESET}",
        f"{R}       |  \\  {W}MORDOR{R} /  |{RESET}",
        f"{R}        \\  '-------'  /{RESET}",
        f"{R}         '---.---.---'{RESET}",
        f"{DR}             | | |{RESET}",
        f"{DR}            /  |  \\{RESET}",
        f"{DR}           /___|___\\{RESET}",
    ]

    info_lines = [
        f"{O}👑 Señor de la Torre:{RESET}  {W}{user}@{host}{RESET}",
        f"{G}─────────────────────────────────────────────────{RESET}",
        f"{R}🏰 Reino Terrenal:{RESET}     {W}{distro}{RESET}",
        f"{R}🛡️  Núcleo de Poder:{RESET}   {W}Linux {kernel}{RESET}",
        f"{OR}⏳ Tiempo de Guardia:{RESET}  {W}{uptime}{RESET}",
        f"{O}🌋 Forjas Orodruin:{RESET}    {W}{cpu}{RESET}",
        f"{O}🏛️  Bóvedas Barad-dûr:{RESET} {W}{mem}{RESET}",
        f"{R}⚔️  Armería de Mordor:{RESET}  {W}{disk}{RESET}",
        f"{OR}🐚 Concha de Mando:{RESET}    {W}{shell} ({term}){RESET}",
        f"{O}💍 Inscripción Arcana:{RESET}  {O}Ash nazg durbatulûk, ash nazg gimbatul{RESET}",
        f"{G}─────────────────────────────────────────────────{RESET}",
        f"  {R}●{RESET} {OR}●{RESET} {O}●{RESET} {DR}●{RESET} {W}●{RESET} {G}●{RESET} {R}●{RESET} {OR}●{RESET} {O}●{RESET}"
    ]

    max_rows = max(len(ascii_art), len(info_lines))
    print()
    for i in range(max_rows):
        left = ascii_art[i] if i < len(ascii_art) else ""
        vis_len = len(strip_ansi(left))
        pad = " " * max(0, 36 - vis_len)
        right = info_lines[i] if i < len(info_lines) else ""
        print(f"  {left}{pad}  {right}")
    print()

if __name__ == "__main__":
    print_fetch()
