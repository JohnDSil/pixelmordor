# Registro de Cambios (Changelog) - PixelMordor

Todos los cambios notables en este proyecto están documentados en este archivo.
El formato sigue las convenciones de [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y cumple con [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.7.1] - 2026-11-17

### Corregido
- **🔔 Campana de Terminal Desacoplada (`mordor_prompt.sh`):**
  - Subproceso de reproducción de audio desacoplado mediante técnica de doble *fork* (`( ( ... ) & )`), eliminando completamente las notificaciones de tareas de fondo de Bash (`[1] <PID>` y `[1]+ Hecho`).
- **🐚 Detección Robusta de Ramas Git:**
  - Uso de `git branch --show-current` con fallback a `git rev-parse --short HEAD` para dar soporte a repositorios en estado de HEAD desacoplado sin producir errores de consola.
- **📜 Protección de Salida MOTD:**
  - Envoltura estricta para terminales interactivas (`-t 1`), evitando interferencias en conexiones no interactivas, túneles SSH y tuberías.
  - Corrección de la integración de citas en `~/.bashrc` desde el CLI `mordor motd on`.

---

## [1.7.0] - 2026-11-13

### Añadido
- **👁️ Fastfetch / Neofetch Nativo de Mordor (`mordor fetch`):**
  - Arte ASCII a todo color de la Torre Oscura de Barad-dûr y el Gran Ojo en `src/mordor_fetch.py`.
  - Telemetría en terminología de la Tierra Media (Señor de la Torre, Reino Terrenal, Núcleo de Poder, Forjas de Orodruin, Bóvedas de Barad-dûr, Armería).
  - Configuración y plantilla para Fastfetch en `fastfetch/mordor.jsonc`.
- **🗂️ Tema de Iconos de Carpetas para GNOME Files / Nautilus (`mordor iconos [on|off]`):**
  - Tema oficial en `icons/Mordor/` con herencia a Adwaita y Yaru.
  - Emblemas forjados en pixel art: Carpeta personal (Barad-dûr), Descargas (Minas Morgul), Documentos (Pergamino Tengwar), Música (Anillo Único), Vídeos (Palantír) y Papelera (Cráter de Orodruin).
- **⌨️ Tema de Colores para Neovim / Vim (`mordor nvim on`):**
  - Implementaciones en Vimscript (`nvim/colors/mordor.vim`) y Lua (`nvim/lua/mordor/init.lua`).
  - Paleta con fondo obsidiana (`#0d0308`), palabras clave en rojo magma (`#ef4444`) y cadenas en oro élfico (`#f59e0b`).
- **🔔 Campana Reactiva de Terminal (`mordor campana [on|off]`):**
  - Retroalimentación auditiva al ejecutar comandos en Bash.
  - Alerta sónica automática con el eco subterráneo de Sauron ante cualquier error (`exit != 0`).

---

## [1.6.0] - 2026-11-13

### Añadido
- **🚀 Tema de Arranque GRUB 2 (`mordor grub [on|off]`):**
  - Pantalla de inicio de sistema en `grub/mordor/` con arte Full HD (1920x1080) de El Morannon y Barad-dûr.
  - Fuentes rúnicas `mordor_16.pf2` y `mordor_title_24.pf2`, marco selector en obsidiana y lava, barra de cuenta regresiva e iconos de sistemas operativos.
  - Scripts dedicados `grub/instalar_grub.sh` y `grub/desinstalar_grub.sh`.
- **🖼️ Fondos Multi-Resolución 2K, 4K y Ultrawide 21:9 (`mordor fondo`):**
  - Generador paramétrico en `src/construir_resoluciones.py` con aspect ratio adaptativo.
  - Generación nativa para 1080p (1920x1080), 2K QHD (2560x1440), 4K UHD (3840x2160) y Ultrawide 21:9 (3440x1440 y 2560x1080) en las tres fases solares.
- **📜 Citas de Tolkien al Abrir Terminal MOTD (`mordor motd [on|off]`):**
  - Módulo ultraligero (< 1ms) en `src/mordor_motd.sh` con 15 citas de El Señor de los Anillos en castellano y Lengua Negra de Mordor.
  - Interruptor directo para integrar o desintegrar de `~/.bashrc`.
- **🎨 Tema GTK4 / Libadwaita y GTK3 (`mordor gtk [on|off]`):**
  - Estilos volcánicos en `gnome/gtk/mordor-gtk.css` integrados con `~/.config/gtk-4.0/gtk.css` y `~/.config/gtk-3.0/gtk.css`.
  - Ventanas obsidiana (`#0d0308`), acentos carmesí de Libadwaita (`#ef4444`, `#dc2626`), barras de scroll con brillo de lava y botones sugeridos en gradiente ígneo.
  - Subcomando CLI: `mordor gtk [on|off|estado]`.
- **⌨️ Atajos de Teclado Globales GNOME (`mordor atajos [on|off]`):**
  - Mapeo nativo de 5 atajos globales en GNOME Settings Daemon:
    - `Super + Alt + E`: Super-erupción en el Orodruin (`mordor erupcion`).
    - `Super + Alt + S`: Cólera del Gran Ojo de Sauron (`mordor colera`).
    - `Super + Alt + N`: Chillido y ataque en picado del Nazgûl (`mordor nazgul`).
    - `Super + Alt + B`: Bloquear pantalla en El Morannon (`mordor bloqueo lock`).
    - `Super + Alt + F`: Forja interactiva 3D del Anillo Único en Ptyxis (`ptyxis -- mordor forjar`).
  - Subcomando CLI: `mordor atajos [on|off|estado]`.
- **🌐 Sitio Web Interactivo en GitHub Pages (`docs/index.html`):**
  - Landing page con HTML5 Canvas en tiempo real a 60 FPS con Orodruin en erupción, Ojo de Sauron cuya pupila sigue suavemente el cursor del ratón, y vuelo del Nazgûl.
  - Sintetizador de audio puro en Web Audio API (cero dependencias externas o MP3s) para erupciones volcánicas, drone de Sauron, campanadas armónicas del Anillo y chillido del Nazgûl.
  - Simulador interactivo de la terminal Ptyxis con paleta oficial de Mordor y ejecución de comandos en vivo.
  - Galería de capturas en alta fidelidad y botón de instalación rápida en 1 clic.
  - Desplegable de inmediato en GitHub Pages (`https://johndsil.github.io/pixelmordor/`).

---

## [1.4.0] - 2026-11-13

### Añadido
- **🔊 Tema Oficial de Sonidos XDG (FreeDesktop / GNOME):**
  - Mapeo completo en `gnome/sound-theme/mordor/` con `index.theme` y perfil estéreo.
  - Asignación de sonidos para conexión de dispositivos (USB/cargador con tintineo del Anillo), papelera (Orodruin), alertas y errores del sistema (Barad-dûr).
  - Nuevo subcomando CLI: `mordor sonido [on|off]`.
- **🐚 Prompt Temático de Terminal para Bash (`mordor prompt`):**
  - Prompt ligero en `src/mordor_prompt.sh` con el Ojo de Sauron `👁`, estado de Git interactivo (`💍` limpio, `🌋` con cambios) y flecha reactiva en color oro o rojo sangre.
  - Configurable con `mordor prompt on` y `mordor prompt off`.
- **💍 Animación Terminal: La Forja del Anillo Único (`mordor forjar`):**
  - Secuencia de arte ASCII 3D y colorimetría ANSI de la forja del Anillo Único en las llamas del Monte del Destino, con ascuas y versos en lengua negra.
- **📈 Mini-gráficos Sparkline de Historial en el HUD:**
  - Telemetría en tiempo real de CPU y memoria RAM con barras incandescentes que alertan de picos de carga.
- **📦 Paquete Oficial EGO para extensions.gnome.org:**
  - Compilación y empaquetado del archivo `gnome/pixelzen@mosqui1988.github.io.shell-extension.zip` mediante `gnome-extensions pack`.

---

## [1.3.0] - 2026-11-13

### Añadido
- **🔒 Pantalla de Bloqueo Personalizada de Mordor (El Morannon):**
  - Fondo de pantalla exclusivo para la pantalla de bloqueo y screensaver (`fondos/mordor-bloqueo.png`, 1920x1200) representando la imponente **Puerta Negra de Mordor (*El Morannon*)**, las torres gemelas de los Dientes de Mordor (*Carchost y Narchost*) con antorchas encendidas, el Gran Ojo de Sauron proyectando su haz y el lema: *"NO PUEDES ESCONDERTE. ¡TE VEO!"*.
  - Generador automatizado de arte en píxeles: `src/construir_bloqueo.py`.
  - Estilizado de la pantalla de bloqueo de GNOME Shell en `stylesheet.css` (reloj gigante en oro élfico `#fbbf24`, fecha en carmesí `#ef4444` y caja de contraseña en obsidiana con borde de lava).
  - Nuevo subcomando CLI: `mordor bloqueo` (y `mordor bloqueo lock` para bloquear al instante).
  - Entrada añadida al menú superior de GNOME: `🔒 Bloquear Pantalla (El Morannon)`.

---

## [1.2.0] - 2026-11-13

### Añadido
- **🔋 Modo Eficiencia Energética / Batería Inteligente:**
  - Lector directo de estado y capacidad de batería en `/sys/class/power_supply/BAT*`.
  - Escala automáticamente el framerate de 24 FPS a 12 FPS y reduce las partículas de ceniza a 8 cuando el equipo está en batería (`Discharging`) y con carga inferior al 25%.
  - Nuevo interruptor en el menú del panel superior de GNOME: `🔋 Ahorro Inteligente de Batería`.
- **🌩️ Clima Real Sincronizado (Open-Meteo):**
  - Módulo autónomo en Python `gnome/pixelzen@mosqui1988.github.io/code/clima.py` que consulta la API pública de Open-Meteo sin necesidad de claves API y con tiempo de espera seguro (3.5 s).
  - Efectos visuales reactivos: los relámpagos carmesíes sobre Barad-dûr cuadruplican su frecuencia (cada 45 ticks en lugar de 170) durante tormentas reales; la lluvia o niebla densifica la bruma volcánica.
  - Nuevo subcomando CLI: `mordor clima`.
  - Interruptor en el menú de GNOME: `🌩️ Clima Real Sincronizado`.
- **🔔 Alertas y Notificaciones Temáticas de Sauron:**
  - Sistema de avisos nativos en el escritorio mediante `notify-send` y `Main.notify`.
  - Alerta de batería crítica (< 15%) y aviso de saturación de disco raíz (> 90%), ambos con estética de Mordor y sonidos temáticos.
  - Nuevo subcomando CLI: `mordor notif`.
  - Interruptor en el panel de GNOME: `🔔 Alertas Temáticas de Mordor`.
- **🎨 Paleta Oficial para Terminal Ptyxis:**
  - Archivo de esquema `Mordor.palette` con tonos obsidiana (`#0d0208`), rojo lava (`#ef4444`, `#dc2626`) y fuego (`#f59e0b`).
  - Comando `mordor terminal` para aplicarlo automáticamente al perfil activo de Ptyxis.
  - Entrada en el menú de GNOME: `🎨 Activar Paleta Mordor en Terminal`.
- **💻 Extensión Oficial de Tema para Visual Studio Code:**
  - Extensión completa empaquetada en `vscode/` con `package.json` y `themes/mordor-color-theme.json`.
  - Tema `Mordor Dark (LOTR)` listo para activarse en VS Code.

---

## [1.1.0] - 2026-11-13

### Corregido
- **📜 Fijación de Runas Tengwar:** Las runas del Anillo Único se fijaron de forma estática y centrada sobre la cúspide de Barad-dûr `(X=195, Y=34)`, eliminando el desplazamiento horizontal no deseado por la pantalla y manteniendo un sutil pulso ígneo.
- **🦅 Patrulla de Nazgûl:** Se eliminó el dibujo estático que aparecía congelado en las capas rasterizadas y se implementó un segundo Nazgûl animado en trayectoria opuesta sobre el Monte del Destino, ambos reactivos a clics con su chillido y picado rasante.

### Añadido
- Interruptor `📜 Runas sobre Barad-dûr` en el menú del panel superior de GNOME.
- Corrección de conectividad de red y resolución DNS para GitHub en `/etc/hosts`.

---

## [1.0.0] - 2026-11-13

### Añadido
- Estructura y arquitectura completa basada en el estándar de [pixelzen](https://github.com/mosqui1988/pixelzen).
- Fondos de pantalla en alta resolución para Ceniza Diurna (`mordor-dia.png`), Hora de Sangre (`mordor-dorado.png`) y Noche de Sombras (`mordor-noche.png`).
- Motor Cairo/Clutter con cálculo solar astronómico NOAA sin conexión a internet.
- Seguimiento visual del ratón por la pupila del Ojo de Sauron con haz de búsqueda.
- Sistema de partículas volcánicas: humo, bombas balísticas de magma, fisuras en Gorgoroth y cascadas de lava continuas en el Orodruin.
- Animación de la hueste orca marchando con estandarte del Gran Ojo y antorchas.
- Easter egg interactivo de Frodo y Sam infiltrándose en Mordor con el Frasco de Galadriel.
- Panel HUD lateral interactivo con métricas del sistema (CPU, RAM, red, disco, reloj lunar y versos del Anillo).
- Cinco efectos de sonido PCM sintetizados digitalmente en Python puro (`anillo.wav`, `erupcion.wav`, `sauron.wav`, `nazgul.wav`, `ambiente.wav`).
- Cursor temático `MordorCursor` (Daga de Morgul, Guantelete de Sauron y Anillo rotatorio en 12 frames).
- Herramienta CLI de gestión `mordor` con autocompletado en Bash.
- Scripts automatizados de despliegue `instalar.sh`, `desinstalar.sh` y `aplicar.sh`.
