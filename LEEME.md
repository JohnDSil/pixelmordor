# PixelMordor

> Tema completo de escritorio en pixel art inspirado en **El Señor de los Anillos: Mordor**: paisaje volcánico animado que sigue la trayectoria solar real de tu ciudad (algoritmo NOAA), panel de datos interactivo (HUD), síntesis de audio sin dependencias, cursores temáticos y soporte para GNOME Shell y Linux.

![PixelMordor Vista Previa](capturas/preview_mordor_definitivo.png)

## Instalación Rápida

Ejecuta el instalador en tu terminal:

```bash
./instalar.sh
```

El instalador:
1. Instala las fuentes tipográficas pixel art (`Departure Mono`, `Pixelify Sans`, etc.).
2. Compila e instala el tema de cursor `MordorCursor` (Daga de Morgul y Guantelete con el Anillo).
3. Instala el comando CLI `mordor` en `~/.local/bin/mordor` y configura el autocompletado en Bash.
4. Despliega la extensión animada interactiva para GNOME Shell.
5. Sincroniza el fondo con la elevación solar exacta de tu ubicación.

## Características Principales

- **Fondo Solar Animado:**
  - El sol y la atmósfera se adaptan a la hora astronómica real calculada mediante las ecuaciones solares oficiales de la NOAA.
  - Tres fases visuales dinámicas: *Ceniza Diurna* (mediodía), *Hora de Sangre* (crepúsculo carmesí) y *Noche de Sombras*.
- **Interactividad en el Escritorio:**
  - El Ojo de Sauron sigue los movimientos del cursor con inercia, proyector de búsqueda y modo cólera.
  - Clic en el Monte del Destino: Provoca una super-erupción con bombas de lava y estruendo.
  - Clic en Barad-dûr: Desata la onda expansiva del Ojo.
  - Clic en la Bestia Alada Nazgûl: Picado aéreo con chillido desgarrador.
  - Clic en Frodo y Sam: Destello del Frasco de Galadriel en la cresta de Gorgoroth.
  - Clic en las llanuras: Abre fisuras de magma incandescentes.
- **Paisaje Sonoro Propio:**
  - Síntesis de audio pura en Python (PCM 16-bit 44.1 kHz, sin librerías externas ni descargas):
    - `anillo.wav`: Campanada mística armónica.
    - `erupcion.wav`: Retumbar sísmico y explosión volcánica.
    - `sauron.wav`: Resonancia sobrenatural del Gran Ojo.
    - `nazgul.wav`: Chillido penetrante de la Bestia Alada.
    - `ambiente.wav`: Bucle continuo de eco subterráneo y viento ardiente.
- **Panel HUD de Métricas:**
  - Visualización en tiempo real de CPU, RAM, temperatura, disco y red.
  - Tarjetas interactivas con sonido al hacer clic (abre Calendario, htop, Nautilus o Ajustes de Red).
  - Indicador del "Poder de Sauron" según la carga de procesamiento del sistema.
- **Control Total desde la Terminal:**
  - Comando `mordor` para alternar fases, probar demostraciones aceleradas, desatar erupciones o consultar el estado astronómico.

## Licencia

Distribuido bajo licencia **GPL-3.0**. Las fuentes y glifos mantienen sus licencias originales en el directorio `licencias/`.
