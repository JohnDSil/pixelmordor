#!/usr/bin/env bash
# Tema Mordor - La Tierra Oscura (El Señor de los Anillos)
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FASE="${1:-noche}"
FONDO="$AQUI/fondos/mordor-${FASE}.png"
[ -f "$FONDO" ] || FONDO="$AQUI/fondos/mordor-noche.png"
[ -f "$FONDO" ] || FONDO="$AQUI/capturas/mordor-preview.png"

echo "==> Aplicando tema de Mordor (${FASE})..."

# 1. Instalar fuentes si no están
mkdir -p "$HOME/.local/share/fonts/pixelzen"
cp -n "$AQUI"/fuentes/*.{otf,ttf} "$HOME/.local/share/fonts/pixelzen/" 2>/dev/null || true
fc-cache -f "$HOME/.local/share/fonts/pixelzen" >/dev/null 2>&1 || true

# 2. Configurar fondo estático en GNOME
mkdir -p "$HOME/.local/share/backgrounds"
cp "$FONDO" "$HOME/.local/share/backgrounds/mordor.png"
URI="file://$HOME/.local/share/backgrounds/mordor.png"

# Fondo de pantalla de bloqueo dedicado (El Morannon y el Gran Ojo)
FONDO_BLOQUEO="$AQUI/fondos/mordor-bloqueo.png"
if [ -f "$FONDO_BLOQUEO" ]; then
    cp "$FONDO_BLOQUEO" "$HOME/.local/share/backgrounds/mordor-bloqueo.png"
    URI_BLOQUEO="file://$HOME/.local/share/backgrounds/mordor-bloqueo.png"
else
    URI_BLOQUEO="$URI"
fi

if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.background picture-uri "$URI" || true
    gsettings set org.gnome.desktop.background picture-uri-dark "$URI" || true
    gsettings set org.gnome.desktop.background picture-options zoom || true
    gsettings set org.gnome.desktop.screensaver picture-uri "$URI_BLOQUEO" || true
    gsettings set org.gnome.desktop.screensaver picture-options zoom || true
    gsettings set org.gnome.desktop.screensaver primary-color '#050208' || true
    gsettings set org.gnome.desktop.screensaver secondary-color '#050208' || true
    gsettings set org.gnome.desktop.interface cursor-theme 'MordorCursor' || true
    gsettings set org.gnome.desktop.interface accent-color 'red' || true
fi

# 2b. Configurar paleta de terminal Ptyxis
if [ -f "$AQUI/Mordor.palette" ]; then
    mkdir -p "$HOME/.local/share/org.gnome.Ptyxis/palettes"
    cp "$AQUI/Mordor.palette" "$HOME/.local/share/org.gnome.Ptyxis/palettes/"
    prof_uuid=$(gsettings get org.gnome.Ptyxis default-profile-uuid 2>/dev/null | tr -d "'" || true)
    if [ -n "$prof_uuid" ]; then
        gsettings set "org.gnome.Ptyxis.Profile:$prof_uuid" palette 'Mordor' 2>/dev/null || true
    fi
fi

# 3. Actualizar la extensión de GNOME con las capas animadas y el HUD
UUID="pixelzen@mosqui1988.github.io"
EXT_DIR="$HOME/.local/share/gnome-shell/extensions/$UUID"
if [ -d "$EXT_DIR" ]; then
    echo "==> Desplegando capas animadas y HUD de Mordor en GNOME Shell..."
    cp "$AQUI/gnome/$UUID/hud.js" "$EXT_DIR/hud.js"
    cp "$AQUI/gnome/$UUID/escena.js" "$EXT_DIR/escena.js"
    cp "$AQUI/gnome/$UUID/extension.js" "$EXT_DIR/extension.js"
    [ -f "$AQUI/gnome/$UUID/stylesheet.css" ] && cp "$AQUI/gnome/$UUID/stylesheet.css" "$EXT_DIR/stylesheet.css"
    cp "$HOME/.local/share/backgrounds/mordor.png" "$EXT_DIR/fondo.png"
    
    # Capas dinámicas (cielo, escena con transparencias, sol y luna)
    if [ -d "$AQUI/gnome/$UUID/images" ]; then
        cp -r "$AQUI/gnome/$UUID/images/"* "$EXT_DIR/images/"
    fi
    if [ -f "$AQUI/gnome/$UUID/datos.json" ]; then
        cp "$AQUI/gnome/$UUID/datos.json" "$EXT_DIR/datos.json"
    fi
    if [ -d "$AQUI/gnome/$UUID/code" ]; then
        mkdir -p "$EXT_DIR/code"
        cp -r "$AQUI/gnome/$UUID/code/"* "$EXT_DIR/code/"
    fi
    if [ -d "$AQUI/gnome/$UUID/sounds" ]; then
        mkdir -p "$EXT_DIR/sounds"
        cp -r "$AQUI/gnome/$UUID/sounds/"* "$EXT_DIR/sounds/"
    fi

    if command -v gnome-extensions >/dev/null 2>&1; then
        gnome-extensions disable "$UUID" 2>/dev/null || true
        sleep 0.5
        gnome-extensions enable "$UUID" 2>/dev/null || true
    fi
fi

# 4. Si se ejecuta en KDE Plasma
if command -v plasma-apply-wallpaperimage >/dev/null 2>&1; then
    plasma-apply-wallpaperimage "$HOME/.local/share/backgrounds/mordor.png" || true
fi

echo "¡Tema de Mordor aplicado y sincronizado con el sol real!"
