#!/usr/bin/env bash
# PixelMordor - Mensaje del Día (MOTD) / Citas de El Señor de los Anillos
# Se ejecuta en < 1ms al abrir una nueva terminal Bash

CITAS_MORDOR=(
    "« Ash nazg durbatulûk, ash nazg gimbatul,\n    ash nazg thrakatulûk agh burzum-ishi krimpatul »\n   — Inscripción de Fuego en el Anillo Único"
    "« No puedes esconderte. ¡Te veo!\n    No hay vida en el vacío... solo muerte. »\n   — El Gran Ojo de Barad-dûr"
    "« ¿Conoces el miedo? Se congelará tu carne y tu corazón morirá ante mi presencia. »\n   — Rey Brujo de Angmar"
    "« Un Anillo para gobernarlos a todos, un Anillo para encontrarlos,\n    un Anillo para atraerlos a todos y atarlos en las tinieblas. »\n   — Versos del Anillo"
    "« La era del Hombre ha terminado. El tiempo del Gran Ojo ha llegado. »\n   — Gothmog, Señor de Morgul"
    "« Las raíces del Orodruin tiemblan. La Sombra ha regresado para reclamar la Tierra Media. »\n   — Crónicas de Mordor"
    "« No todos los que vagan están perdidos;\n    las raíces profundas no son alcanzadas por la escarcha. »\n   — Poema de Aragorn"
    "« Mi Tessssoro... El Gran Ojo lo busca sin descanso, lo llama desde las grietas ardientes. »\n   — Gollum / Sméagol"
    "« Sauron no comparte el poder. Su mirada traspasa la nube, la sombra, la tierra y la carne. »\n   — Saruman de Isengard"
    "« Que la estrella de Eärendil te guíe en los lugares oscuros,\n    cuando todas las demás luces se hayan apagado. »\n   — Frasco de Galadriel"
    "« ¡No puedes pasar! Soy un siervo del Fuego Secreto, administrador de la llama de Anor. »\n   — Gandalf en el Abismo"
    "« La sombra de la Torre Oscura se extiende hacia el Oeste. La pupila roja nunca duerme. »\n   — Centinelas del Morannon"
    "« ¡Por todo lo que más queréis en esta tierra, os digo: resistid, Hombres del Oeste! »\n   — Aragorn en la Puerta Negra"
    "« Las fauces de Gorgoroth se abren para devorar a los que osen pisar sus cenizas. »\n   — Boca de Sauron"
    "« En la tierra de Mordor, donde se extienden las sombras. »\n   — J.R.R. Tolkien"
)

# Seleccionar cita aleatoria
TOTAL=${#CITAS_MORDOR[@]}
INDICE=$(( RANDOM % TOTAL ))
CITA="${CITAS_MORDOR[$INDICE]}"

echo -e "\033[1;31m  ╔═════════════════════════════════════════════════════════════════════════╗\033[0m"
echo -e "\033[1;33m   👁  PALABRAS DE MORDOR · EL SEÑOR DE LOS ANILLOS\033[0m"
echo -e "\033[0;37m   $CITA\033[0m"
echo -e "\033[1;31m  ╚═════════════════════════════════════════════════════════════════════════╝\033[0m"
