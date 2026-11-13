#!/usr/bin/env bash
# PixelMordor - Desinstalador oficial y restauración limpia
set -euo pipefail

UUID="pixelzen@mosqui1988.github.io"
EXT_DIR="$HOME/.local/share/gnome-shell/extensions/$UUID"

echo "==> Desinstalando PixelMordor y restaurando ajustes originales..."

if command -v gnome-extensions >/dev/null 2>&1; then
    gnome-extensions disable "$UUID" 2>/dev/null || true
fi

# Eliminar extensión y datos locales
rm -rf "$EXT_DIR" 2>/dev/null || true
rm -rf "$HOME/.local/share/pixelzen" 2>/dev/null || true
rm -rf "$HOME/.local/share/icons/MordorCursor" 2>/dev/null || true
rm -rf "$HOME/.local/share/icons/Mordor" 2>/dev/null || true
rm -rf "$HOME/.local/share/sounds/mordor" 2>/dev/null || true
rm -f "$HOME/.config/pixelzen/campana_activa" 2>/dev/null || true
rm -f "$HOME/.config/nvim/colors/mordor.vim" "$HOME/.vim/colors/mordor.vim" 2>/dev/null || true
rm -rf "$HOME/.config/nvim/lua/mordor" 2>/dev/null || true

# Restaurar estilos GTK
rm -f "$HOME/.config/gtk-4.0/gtk.css" "$HOME/.config/gtk-3.0/gtk.css" 2>/dev/null || true

# Limpiar entradas en .bashrc
if [ -f "$HOME/.bashrc" ]; then
    sed -i '/mordor_motd\.sh/d' "$HOME/.bashrc"
    sed -i '/mordor_prompt\.sh/d' "$HOME/.bashrc"
fi

# Eliminar atajos de teclado globales GNOME
if command -v python3 >/dev/null 2>&1; then
    python3 -c "
try:
    from gi.repository import Gio
    s = Gio.Settings(schema='org.gnome.settings-daemon.plugins.media-keys')
    cur = list(s.get_strv('custom-keybindings'))
    clean = [p for p in cur if '/mordor-' not in p]
    s.set_strv('custom-keybindings', clean)
except Exception:
    pass
" 2>/dev/null || true
fi

# Restaurar configuraciones GNOME por defecto
if command -v gsettings >/dev/null 2>&1; then
    gsettings reset org.gnome.desktop.interface cursor-theme 2>/dev/null || true
    gsettings reset org.gnome.desktop.interface accent-color 2>/dev/null || true
    gsettings reset org.gnome.desktop.interface icon-theme 2>/dev/null || true
    gsettings reset org.gnome.desktop.sound theme-name 2>/dev/null || true
fi

rm -f "$HOME/.local/bin/mordor" 2>/dev/null || true

echo "PixelMordor ha sido desinstalado. Tus ajustes originales han sido restaurados."
