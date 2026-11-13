#!/usr/bin/env bash
# PixelMordor - Desinstalador
set -euo pipefail

UUID="pixelzen@mosqui1988.github.io"
EXT_DIR="$HOME/.local/share/gnome-shell/extensions/$UUID"

echo "==> Desinstalando PixelMordor..."

if command -v gnome-extensions >/dev/null 2>&1; then
    gnome-extensions disable "$UUID" 2>/dev/null || true
fi

rm -rf "$EXT_DIR" 2>/dev/null || true
rm -rf "$HOME/.local/share/icons/MordorCursor" 2>/dev/null || true
rm -f "$HOME/.local/bin/mordor" 2>/dev/null || true

# Restaurar cursor por defecto
if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.interface cursor-theme 'Adwaita' 2>/dev/null || true
    gsettings set org.gnome.desktop.interface accent-color 'blue' 2>/dev/null || true
fi

echo "PixelMordor ha sido desinstalado. Tus ajustes originales han sido restaurados."
