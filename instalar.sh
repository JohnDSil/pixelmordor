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

# 3. Instalar herramienta de línea de comandos 'mordor'
echo "==> 3/5 Instalando comando 'mordor' en ~/.local/bin..."
mkdir -p "$HOME/.local/bin"
cp "$AQUI/mordor" "$HOME/.local/bin/mordor"
chmod +x "$HOME/.local/bin/mordor"

if [ -f "$HOME/.bashrc" ] && ! grep -q "complete -W .*mordor" "$HOME/.bashrc"; then
    echo 'complete -W "auto dia noche sangre ocaso demo erupcion colera nazgul hobbits ambiente cita estado banner cursor hud info" mordor' >> "$HOME/.bashrc"
fi

# 4. Desplegar extensión para GNOME Shell
echo "==> 4/5 Desplegando extensión interactiva de GNOME Shell..."
EXT_DIR="$HOME/.local/share/gnome-shell/extensions/$UUID"
mkdir -p "$EXT_DIR"
cp -r "$AQUI/gnome/$UUID/"* "$EXT_DIR/"

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
