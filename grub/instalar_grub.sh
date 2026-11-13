#!/usr/bin/env bash
# PixelMordor - Instalador del tema de arranque GRUB 2
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo -e "\033[1;31mError:\033[0m Este script debe ejecutarse con privilegios de superusuario (sudo)."
    exit 1
fi

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMA_DIR="/boot/grub/themes/mordor"

echo -e "\033[1;33m==> 1/3 Instalando tema GRUB PixelMordor en $TEMA_DIR...\033[0m"
mkdir -p "$TEMA_DIR"
cp -r "$AQUI/mordor/"* "$TEMA_DIR/"

echo -e "\033[1;33m==> 2/3 Configurando /etc/default/grub...\033[0m"
if [ ! -f /etc/default/grub.mordor.bak ]; then
    cp /etc/default/grub /etc/default/grub.mordor.bak
fi

# Configurar GRUB_THEME y GRUB_GFXMODE
sed -i '/^GRUB_THEME=/d' /etc/default/grub
echo 'GRUB_THEME="/boot/grub/themes/mordor/theme.txt"' >> /etc/default/grub
sed -i '/^GRUB_GFXMODE=/d' /etc/default/grub
echo 'GRUB_GFXMODE="1920x1080,auto"' >> /etc/default/grub

# Asegurar que el menú sea visible durante 5 segundos
sed -i 's/^GRUB_TIMEOUT_STYLE=hidden/GRUB_TIMEOUT_STYLE=menu/' /etc/default/grub 2>/dev/null || true
sed -i 's/^GRUB_TIMEOUT=0/GRUB_TIMEOUT=5/' /etc/default/grub 2>/dev/null || true

echo -e "\033[1;33m==> 3/3 Actualizando la configuración de GRUB (update-grub)...\033[0m"
update-grub

echo -e "\033[1;32m"
echo "╔═════════════════════════════════════════════════════════════════╗"
echo "║  ¡Tema de arranque GRUB 2 de Mordor instalado con éxito!       ║"
echo "║  Al reiniciar verás a El Morannon y el Ojo de Sauron en 1080p.  ║"
echo "╚═════════════════════════════════════════════════════════════════╝"
echo -e "\033[0m"
