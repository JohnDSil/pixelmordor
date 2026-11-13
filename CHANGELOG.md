# Registro de Cambios (Changelog) - PixelMordor

Todos los cambios notables en este proyecto están documentados en este archivo.
El formato sigue las convenciones de [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y cumple con [Semantic Versioning](https://semver.org/lang/es/).

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
