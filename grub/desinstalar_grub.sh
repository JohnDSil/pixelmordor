#!/usr/bin/env bash
# PixelMordor - Desinstalador del tema GRUB 2
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo -e "\033[1;31mError:\033[0m Este script debe ejecutarse con privilegios de superusuario (sudo)."
    exit 1
fi

TEMA_DIR="/boot/grub/themes/mordor"
rm -rf "$TEMA_DIR"

if [ -f /etc/default/grub.mordor.bak ]; then
    cp /etc/default/grub.mordor.bak /etc/default/grub
else
    sed -i '/^GRUB_THEME=/d' /etc/default/grub
fi

update-grub
echo -e "\033[1;32mTema GRUB de Mordor desinstalado y restaurado a la configuración previa.\033[0m"
