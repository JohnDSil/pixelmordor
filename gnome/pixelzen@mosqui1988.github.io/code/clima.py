#!/usr/bin/env python3
"""clima.py - Consulta meteorológica local y ligera con Open-Meteo para el tema de Mordor.
Sin claves API y con timeout de seguridad de 3.5 segundos. Salida: JSON por stdout."""
import json, urllib.request, os

lat, lon = 40.4168, -3.7038
ubi_path = os.path.expanduser('~/.config/pixelzen/ubicacion.json')
if os.path.isfile(ubi_path):
    try:
        with open(ubi_path) as f:
            cfg = json.load(f)
            lat = cfg.get('casa', {}).get('lat', lat)
            lon = cfg.get('casa', {}).get('lon', lon)
    except Exception:
        pass

url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=weather_code,temperature_2m,wind_speed_10m"
req = urllib.request.Request(url, headers={'User-Agent': 'PixelMordor/1.0'})

try:
    with urllib.request.urlopen(req, timeout=3.5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        cur = data.get('current', {})
        code = cur.get('weather_code', 0)
        temp = cur.get('temperature_2m', 15.0)
        wind = cur.get('wind_speed_10m', 10.0)

        # Mapeo WMO:
        tormenta = code in [95, 96, 99]
        lluvia = code in [51, 53, 55, 61, 63, 65, 80, 81, 82] or tormenta
        niebla = code in [45, 48, 3]
        despejado = code in [0, 1]

        if tormenta:
            desc = "Tormenta carmesí de relámpagos"
        elif lluvia:
            desc = "Lluvia de ceniza densa"
        elif niebla:
            desc = "Bruma volcánica opaca"
        else:
            desc = "Atmósfera despejada sobre Barad-dûr"

        print(json.dumps({
            "ok": True,
            "code": code,
            "temp": round(temp),
            "wind": round(wind),
            "tormenta": tormenta,
            "lluvia": lluvia,
            "niebla": niebla,
            "despejado": despejado,
            "desc": desc
        }, ensure_ascii=False))
except Exception as e:
    print(json.dumps({
        "ok": False,
        "code": 0,
        "temp": 16,
        "wind": 12,
        "tormenta": False,
        "lluvia": False,
        "niebla": False,
        "despejado": True,
        "desc": "Ceniza volcánica estándar"
    }))
