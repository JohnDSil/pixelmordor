#!/usr/bin/env bash
# PixelMordor - Instalador oficial
# Tema completo de escritorio en pixel art: La Tierra de Mordor (El Señor de los Anillos)
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UUID="pixelzen@mosqui1988.github.io"
DEST="$HOME/.local/share/pixelzen"

echo -e "\033[1;31m"
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║        PIXELMORDOR · EL SEÑOR DE LOS ANILLOS         ║"
echo "  ║     Tema de escritorio animado en Pixel Art (LOTR)   ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo -e "\033[0m"

# 1. Instalar fuentes tipográficas
echo "==> 1/5 Instalando fuentes tipográficas en ~/.local/share/fonts/pixelzen..."
mkdir -p "$HOME/.local/share/fonts/pixelzen"
cp -n "$AQUI"/fuentes/*.{otf,ttf} "$HOME/.local/share/fonts/pixelzen/" 2>/dev/null || true
fc-cache -f "$HOME/.local/share/fonts/pixelzen" >/dev/null 2>&1 || true

# 2. Generar e instalar cursor temático MordorCursor
echo "==> 2/5 Compilando e instalando cursor temático 'MordorCursor' y paletas..."
if [ -f "$AQUI/src/cursor.py" ]; then
    python3 "$AQUI/src/cursor.py" >/dev/null 2>&1 || true
fi

# Instalar paleta oficial para Ptyxis Terminal
if [ -f "$AQUI/Mordor.palette" ]; then
    mkdir -p "$HOME/.local/share/org.gnome.Ptyxis/palettes"
    cp "$AQUI/Mordor.palette" "$HOME/.local/share/org.gnome.Ptyxis/palettes/"
fi

# Instalar tema para VS Code si está instalado
if [ -d "$AQUI/vscode" ]; then
    mkdir -p "$HOME/.vscode/extensions/mordor-theme-1.0.0"
    cp -r "$AQUI/vscode/"* "$HOME/.vscode/extensions/mordor-theme-1.0.0/" 2>/dev/null || true
fi

# Instalar tema oficial de sonido XDG Mordor
if [ -d "$AQUI/gnome/sound-theme/mordor" ]; then
    mkdir -p "$HOME/.local/share/sounds/mordor"
    cp -r "$AQUI/gnome/sound-theme/mordor/"* "$HOME/.local/share/sounds/mordor/"
    gsettings set org.gnome.desktop.sound theme-name 'mordor' 2>/dev/null || true
    gsettings set org.gnome.desktop.sound event-sounds true 2>/dev/null || true
fi

# Instalar prompt temático para Bash
mkdir -p "$HOME/.config/pixelzen"
[ -f "$AQUI/src/mordor_prompt.sh" ] && cp "$AQUI/src/mordor_prompt.sh" "$HOME/.config/pixelzen/"

# Generar fondo de pantalla de bloqueo si no existe
if [ ! -f "$AQUI/fondos/mordor-bloqueo.png" ] && [ -f "$AQUI/src/construir_bloqueo.py" ]; then
    python3 "$AQUI/src/construir_bloqueo.py" >/dev/null 2>&1 || true
fi

# 3. Instalar herramienta de línea de comandos 'mordor'
echo "==> 3/5 Instalando comando 'mordor' en ~/.local/bin..."
mkdir -p "$HOME/.local/bin"
cp "$AQUI/mordor" "$HOME/.local/bin/mordor"
chmod +x "$HOME/.local/bin/mordor"

if [ -f "$HOME/.bashrc" ] && ! grep -q "complete -W .*mordor" "$HOME/.bashrc"; then
    echo 'complete -W "auto dia noche sangre ocaso demo erupcion colera nazgul hobbits ambiente cita estado banner cursor hud clima terminal notif bloqueo prompt sonido forjar gtk atajos info" mordor' >> "$HOME/.bashrc"
fi

# 4. Desplegar extensión para GNOME Shell y temas GTK
echo "==> 4/5 Desplegando extensión interactiva de GNOME Shell y tema GTK..."
EXT_DIR="$HOME/.local/share/gnome-shell/extensions/$UUID"
mkdir -p "$EXT_DIR"
cp -r "$AQUI/gnome/$UUID/"* "$EXT_DIR/"

# Desplegar tema GTK4 / Libadwaita
if [ -f "$AQUI/gnome/gtk/mordor-gtk.css" ]; then
    mkdir -p "$EXT_DIR/gtk" "$HOME/.local/share/pixelzen/gtk"
    cp "$AQUI/gnome/gtk/mordor-gtk.css" "$EXT_DIR/gtk/"
    cp "$AQUI/gnome/gtk/mordor-gtk.css" "$HOME/.local/share/pixelzen/gtk/"
    "$HOME/.local/bin/mordor" gtk on >/dev/null 2>&1 || true
fi

# Configurar atajos de teclado globales GNOME
"$HOME/.local/bin/mordor" atajos on >/dev/null 2>&1 || true

# Compilar esquemas GSettings
if command -v glib-compile-schemas >/dev/null 2>&1 && [ -d "$EXT_DIR/schemas" ]; then
    glib-compile-schemas "$EXT_DIR/schemas" 2>/dev/null || true
fi

# 5. Aplicar fondos y configurar escritorio
echo "==> 5/5 Aplicando fondo de pantalla, cursor y paleta..."
"$AQUI/aplicar.sh" auto

echo -e "\033[1;32m"
echo "¡Instalación de PixelMordor completada con éxito!"
echo -e "\033[0m"
echo "Para interactuar con Mordor:"
echo "  • Haz clic en el fondo (Monte del Destino, Ojo de Sauron, Nazgûl, Hobbits)"
echo "  • Usa el menú superior '👁 Mordor' en tu barra de tareas"
echo "  • Escribe 'mordor estado' en tu terminal para ver el reporte astronómico"
