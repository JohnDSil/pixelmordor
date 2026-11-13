// PixelZen para GNOME - Capas y Escena Dinámica de Mordor (El Señor de los Anillos).
// Lienzo pixel art nativo de 640x400 con escala NEAREST en Clutter / Cairo.
// Sincronización astronómica precisa en tiempo real (NOAA Solar Algorithm):
// - Transición automática según la hora solar real (Amanecer, Cénit Diurno, Crepúsculo de Sangre y Noche Profunda).
// - Sincronización automática del fondo de pantalla estático (mordor.png) con la fase horaria actual.
// - Adaptación ambiental de los elementos vivos (Ojo de Sauron, antorchas de orcos, erupción y luna).
// - Clics interactivos en el escritorio (Monte del Destino, Barad-dûr y fisuras de magma en Gorgoroth).

import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import GdkPixbuf from 'gi://GdkPixbuf';
import Clutter from 'gi://Clutter';
import Cogl from 'gi://Cogl';
import St from 'gi://St';
import Cairo from 'cairo';

const W = 640, H = 400;

// Utilidades de color y actores
const cacheColor = new Map();
function hexA(hex) {
    const h = hex.replace('#', '');
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}
export function color(hex, alpha = 255) {
    const k = hex + alpha;
    if (cacheColor.has(k)) return cacheColor.get(k);
    const [red, green, blue] = hexA(hex);
    const C = Clutter.Color ?? Cogl.Color;
    const c = new C({red, green, blue, alpha});
    cacheColor.set(k, c);
    return c;
}

const clamp01 = v => v < 0 ? 0 : v > 1 ? 1 : v;
const op255 = v => Math.round(clamp01(v) * 255);

// Píxel de arte pintado con Cairo en coordenadas de 640x400
const cacheRgb = new Map();
function px(cr, hex, op, ax, ay, aw = 1, ah = 1) {
    if (op <= 0.004) return;
    let c = cacheRgb.get(hex);
    if (!c) { c = hexA(hex).map(v => v / 255); cacheRgb.set(hex, c); }
    cr.setSourceRGBA(c[0], c[1], c[2], op > 1 ? 1 : op);
    cr.rectangle(Math.round(ax), Math.round(ay), aw, ah);
    cr.fill();
}

function fija(a, op) {
    const o = op255(op);
    const v = o > 1;
    if (a.visible !== v) a.visible = v;
    if (v && a.opacity !== o) a.opacity = o;
    return v;
}

function contenido(pixbuf) {
    const c = St.ImageContent.new_with_preferred_size(pixbuf.width, pixbuf.height);
    const fmt = pixbuf.has_alpha ? Cogl.PixelFormat.RGBA_8888 : Cogl.PixelFormat.RGB_888;
    const bytes = pixbuf.read_pixel_bytes();
    try {
        c.set_bytes(bytes, fmt, pixbuf.width, pixbuf.height, pixbuf.rowstride);
    } catch (e) {
        const ctx = global.stage.context.get_backend().get_cogl_context();
        c.set_bytes(ctx, bytes, fmt, pixbuf.width, pixbuf.height, pixbuf.rowstride);
    }
    return c;
}

function imagen(padre, cont, w, h) {
    const a = new Clutter.Actor({width: w, height: h});
    a.set_content(cont);
    a.set_content_scaling_filters(Clutter.ScalingFilter.NEAREST, Clutter.ScalingFilter.NEAREST);
    padre.add_child(a);
    return a;
}

export class Escena {
    constructor(dir, contenedor, settings) {
        this._dir = dir;
        this._cont = contenedor;
        this._settings = settings;
        this._monitores = [];
        this._timer = 0;
        this._pausa = false;
        this.tick = 0;

        this.lat = 40.4; this.lon = -3.7;
        this.faseNombre = 'dia';
        this._ultimaFaseFondo = null;

        // Estado interactivo del Ojo de Sauron
        this.eyeCurX = 195;
        this.eyeCurY = 74;
        this.eyeTargetX = 195;
        this.eyeTargetY = 74;
        this.lastPointer = [0, 0];
        this.pointerStillTicks = 0;
        this.proximityAlert = 0.0;
        this._monPrincipal = null;

        // Ondas de choque, fisuras interactivas y relámpago manual
        this.shockwaves = [];
        this.grietasTemporales = [];
        this.relampagoManual = 0;
        this.sonidoActivo = true;
        this.lluviaCeniza = true;
        this.ambienteActivo = false;
        this.ambienteTimer = 0;
        this.nazCurX = 140;
        this.nazCurY = 108;
        this.nazgulDive = 0;

        // Easter Egg: Frodo y Sam infiltrándose en Gorgoroth (Y=304)
        this.hobbits = { x: 252, y: 304, state: 'hidden', glint: 0 };

        // Lluvia de ceniza volcánica (32 copos de ceniza en suspensión)
        this.ashFlakes = [];
        for (let i = 0; i < 32; i++) {
            this.ashFlakes.push({
                x: Math.random() * W,
                y: Math.random() * H,
                vy: 0.35 + Math.random() * 0.45,
                sway: Math.random() * Math.PI * 2,
                size: Math.random() > 0.7 ? 2 : 1
            });
        }

        // Sistemas de partículas volcánicas y física
        this.smokeParticles = [];
        this.lavaBombs = [];
        this.volcanicEmbers = [];

        // Conectar interacción de clics en el fondo del escritorio
        this._cont.connect('button-press-event', (actor, event) => this._onDesktopClick(event));

        try {
            this.D = JSON.parse(new TextDecoder().decode(
                GLib.file_get_contents(`${dir}/datos.json`)[1]));
        } catch (e) {
            this.D = { W: 640, H: 400, estrellas: [], faroles: [[195, 74, 18]], destellos: [], nubes: [] };
        }

        this._cargaTexturas();
        this._leeAjustes();
        this.recalcula();
    }

    _suena(nombre) {
        if (!this.sonidoActivo) return;
        const ruta = `${this._dir}/sounds/${nombre}.wav`;
        try {
            Gio.Subprocess.new(['canberra-gtk-play', '-f', ruta], Gio.SubprocessFlags.NONE);
        } catch (e) {
            try {
                Gio.Subprocess.new(['pw-play', ruta], Gio.SubprocessFlags.NONE);
            } catch (err) {
                try {
                    Gio.Subprocess.new(['aplay', '-q', ruta], Gio.SubprocessFlags.NONE);
                } catch (err2) {}
            }
        }
    }

    _onDesktopClick(event) {
        if (!this._monPrincipal) return false;
        const [, gx, gy] = event.get_coords();
        const mon = this._monPrincipal;
        const u = Math.max(mon.width / W, mon.height / H);
        const ox = (mon.width - W * u) / 2;
        const oy = (mon.height - H * u) / 2;
        const cx = (gx - mon.x - ox) / u;
        const cy = (gy - mon.y - oy) / u;

        // 1. Clic en Monte del Destino (X ~ 395, Y ~ 146)
        if (Math.abs(cx - 395) < 55 && Math.abs(cy - 146) < 45) {
            this.desataErupcion();
            return true;
        }

        // 2. Clic en Barad-dûr / El Gran Ojo (X ~ 195, Y ~ 74)
        if (Math.abs(cx - 195) < 50 && Math.abs(cy - 74) < 50) {
            this.desataColera();
            return true;
        }

        // 3. Clic en la Bestia Alada Nazgûl
        if (Math.abs(cx - this.nazCurX) < 28 && Math.abs(cy - this.nazCurY) < 22) {
            this.desataNazgul();
            return true;
        }

        // 4. Clic en Frodo y Sam
        if (Math.abs(cx - this.hobbits.x) < 20 && Math.abs(cy - this.hobbits.y) < 16) {
            this.desataHobbits();
            return true;
        }

        // 5. Clic en las llanuras de Gorgoroth (Y > 260)
        if (cy >= 260 && cy <= 390 && cx >= 20 && cx <= 620) {
            this.grietasTemporales.push({x: Math.round(cx), y: Math.round(cy), life: 75, maxLife: 75});
            for (let k = 0; k < 6; k++) {
                this.volcanicEmbers.push({
                    x: cx, y: cy,
                    vx: (Math.random() - 0.5) * 2.0,
                    vy: -1.0 - Math.random() * 1.5,
                    age: 0, maxAge: 20
                });
            }
            this._suena('anillo');
            this.pinta();
            return true;
        }

        return false;
    }

    desataErupcion() {
        const ox = 395, oy = 146;
        for (let i = 0; i < 14; i++) {
            this.lavaBombs.push({
                x: ox + (Math.random() - 0.5) * 8,
                y: oy - 3,
                vx: (Math.random() - 0.5) * 3.2 - 0.3,
                vy: -3.8 - Math.random() * 2.2,
                age: 0
            });
        }
        for (let s = 0; s < 12; s++) {
            this.smokeParticles.push({
                x: ox + (Math.random() - 0.5) * 12,
                y: oy - 2,
                vx: -0.5 - Math.random() * 0.6,
                vy: -1.0 - Math.random() * 0.8,
                age: 0,
                maxAge: 55 + Math.floor(Math.random() * 30)
            });
        }
        this._suena('erupcion');
        this.pinta();
    }

    desataColera() {
        this.proximityAlert = 1.0;
        this.shockwaves.push({x: 195, y: 74, r: 8, maxR: 260, life: 32, maxLife: 32});
        this._suena('sauron');
        this.pinta();
    }

    desataNazgul() {
        this.nazgulDive = 32;
        this._suena('nazgul');
        this.pinta();
    }

    desataHobbits() {
        this.hobbits.glint = 16;
        this._suena('anillo');
        this.pinta();
    }

    setAmbiente(activo) {
        this.ambienteActivo = activo;
        if (this.ambienteTimer) { GLib.source_remove(this.ambienteTimer); this.ambienteTimer = 0; }
        if (activo) {
            this._suena('ambiente');
            this.ambienteTimer = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 6, () => {
                if (this.ambienteActivo && !this._pausa) this._suena('ambiente');
                return GLib.SOURCE_CONTINUE;
            });
        }
    }

    fuerzaRelampago() {
        this.relampagoManual = 4;
        this._suena('erupcion');
        this.pinta();
    }

    _cargaTexturas() {
        const img = f => GdkPixbuf.Pixbuf.new_from_file(`${this._dir}/images/${f}.png`);
        this.tex = {};
        for (const f of ['cielo-noche', 'cielo-dorado', 'cielo-dia', 'escena-noche', 'escena-dorado', 'escena-dia', 'sol', 'luna'])
            this.tex[f] = contenido(img(f));

        this.texNubes = { noche: [], dorado: [], dia: [] };
        if (this.D.nubes && this.D.nubes.length > 0) {
            for (const fase of ['noche', 'dorado', 'dia']) {
                try {
                    const hoja = img(`nubes-${fase}`);
                    this.texNubes[fase] = this.D.nubes.map(nb => contenido(hoja.new_subpixbuf(0, nb[4], nb[2], nb[3]).copy()));
                } catch (e) {
                    this.texNubes[fase] = [];
                }
            }
        }
    }

    _leeAjustes() {
        const s = this._settings;
        this.animar = s.get_boolean('animar');
        this.fps = Math.max(2, Math.min(24, s.get_int('fps')));
        this.horaSim = s.get_double('hora-simulada');
        this.demo = s.get_boolean('ciclo-rapido');
    }

    ajustesCambiados() {
        this._leeAjustes();
        this.recalcula();
        this.pinta();
        this._programa();
    }

    static suave(t) { t = clamp01(t); return t * t * (3 - 2 * t); }

    // Algoritmo solar astronómico NOAA de alta precisión
    sol(fecha) {
        const startOfYear = new Date(Date.UTC(fecha.getUTCFullYear(), 0, 1));
        const dayOfYear = Math.floor((fecha - startOfYear) / 86400000) + 1;
        const gamma = (2 * Math.PI / 365) * (dayOfYear - 1 + (fecha.getUTCHours() - 12) / 24);

        // Ecuación del tiempo en minutos
        const eqtime = 229.18 * (0.000075 + 0.001868 * Math.cos(gamma) - 0.032077 * Math.sin(gamma)
                       - 0.014615 * Math.cos(2 * gamma) - 0.040849 * Math.sin(2 * gamma));

        // Declinación solar
        const decl = (0.006918 - 0.399912 * Math.cos(gamma) + 0.070257 * Math.sin(gamma)
                    - 0.006758 * Math.cos(2 * gamma) + 0.000907 * Math.sin(2 * gamma)
                    - 0.002697 * Math.cos(3 * gamma) + 0.00148 * Math.sin(3 * gamma));

        const timeOffset = eqtime + 4 * this.lon;
        const tst = fecha.getUTCHours() * 60 + fecha.getUTCMinutes() + fecha.getUTCSeconds() / 60 + timeOffset;
        let ha = (tst / 4) - 180;
        if (ha < -180) ha += 360;
        if (ha > 180) ha -= 360;

        const rad = Math.PI / 180;
        const haRad = ha * rad;
        const latRad = this.lat * rad;

        const cosZenith = Math.sin(latRad) * Math.sin(decl) + Math.cos(latRad) * Math.cos(decl) * Math.cos(haRad);
        const zenith = Math.acos(Math.max(-1, Math.min(1, cosZenith))) / rad;
        const alt = 90 - zenith;

        // Azimut
        const sinAz = -Math.sin(haRad) * Math.cos(decl) / Math.sin(zenith * rad);
        const cosAz = (Math.sin(decl) - Math.sin(latRad) * Math.cos(zenith * rad)) / (Math.cos(latRad) * Math.sin(zenith * rad));
        let az = Math.atan2(sinAz, cosAz) / rad;
        if (az < 0) az += 360;

        return {alt, az};
    }

    ponUbicacion(lat, lon) {
        this.lat = lat; this.lon = lon;
        this.recalcula();
        this.pinta();
    }

    _actualizaFondoEstatico(fase) {
        try {
            const home = GLib.get_home_dir();
            const src = `${home}/Descargas/mordor/fondos/mordor-${fase}.png`;
            const dst = `${home}/.local/share/backgrounds/mordor.png`;
            const fileSrc = Gio.File.new_for_path(src);
            const fileDst = Gio.File.new_for_path(dst);
            if (fileSrc.query_exists(null)) {
                fileSrc.copy_async(fileDst, Gio.FileCopyFlags.OVERWRITE, GLib.PRIORITY_DEFAULT, null, null, null);
            }
        } catch (e) {}
    }

    recalcula() {
        let f = new Date();
        if (this.demo) {
            const msDia = 90000;
            const tDia = (Date.now() % msDia) / msDia;
            const horasSim = tDia * 24;
            f.setHours(Math.floor(horasSim), Math.floor((horasSim % 1) * 60), Math.floor(((horasSim * 60) % 1) * 60));
        } else if (this.horaSim >= 0) {
            f.setHours(Math.floor(this.horaSim), Math.floor((this.horaSim % 1) * 60), 0);
        }

        const s = this.sol(f);
        this.elev = s.alt;
        this.elevNorm = clamp01((s.alt + 6) / 12);

        const rad = Math.PI / 180;
        // Posición del sol a lo largo de la bóveda celeste
        const azNorm = (s.az - 70) / 220; // arco este-sur-oeste
        this.solX = 60 + azNorm * 520;
        this.solY = 275 - Math.sin(Math.max(0, s.alt) * rad) * 230;

        // La luna se posiciona en el cuadrante nocturno opuesto
        const moonAzNorm = ((s.az + 180) % 360 - 70) / 220;
        this.lunaX = 60 + moonAzNorm * 520;
        this.lunaY = 275 - Math.sin(Math.max(0, -s.alt) * rad) * 230;

        const e = this.elev;
        // Transición suave entre las 3 fases celestes de Mordor:
        // e < -6° -> 100% Noche (sombras absolutas)
        // -6° <= e <= +6° -> 100% Dorado (Crepúsculo / Hora de Sangre)
        // e > +6° -> 100% Día (Ceniza diurna / Cénit)
        const wNoche = Escena.suave(clamp01((-e) / 6));
        const wDia = Escena.suave(clamp01((e - 3) / 6));
        const wDor = Escena.suave(clamp01(1 - Math.abs(e) / 6));
        const sum = (wNoche + wDor + wDia) || 1;
        this.wA = wDor / sum;
        this.wB = wDia / sum;

        this.solOp = Escena.suave(clamp01((e + 2) / 6));
        this.lunaOp = Escena.suave(clamp01((-e - 2) / 6));
        this.nocheF = clamp01((-e) / 6);

        // Determinación de la fase actual y sincronización del fondo estático
        let faseAct = 'dia';
        if (this.wB > 0.55) faseAct = 'dia';
        else if (this.wA > 0.35) faseAct = 'dorado';
        else faseAct = 'noche';

        this.faseNombre = faseAct;
        if (this._ultimaFaseFondo !== faseAct) {
            this._ultimaFaseFondo = faseAct;
            this._actualizaFondoEstatico(faseAct);
        }
    }

    construye(monitores) {
        this.destruyeMonitores();
        this._lienzo = this._creaLienzo();
        monitores.forEach((mon, i) => this._monitores.push(this._creaMonitor(mon, i === 0)));
        this.pinta();
        this._programa();
    }

    _creaLienzo() {
        const T = this.tex;
        const l = {};
        const raiz = new Clutter.Actor({width: W, height: H});
        l.raiz = raiz;

        const area = fn => {
            const a = new St.DrawingArea({width: W, height: H});
            a.set_content_scaling_filters(Clutter.ScalingFilter.NEAREST, Clutter.ScalingFilter.NEAREST);
            a.connect('repaint', ar => {
                const cr = ar.get_context();
                try {
                    const [sw] = ar.get_surface_size();
                    cr.scale(sw / W, sw / W);
                    cr.setAntialias(Cairo.Antialias.NONE);
                    fn(cr);
                } catch (e) {
                    logError(e, 'PixelZen Mordor escena');
                } finally {
                    cr.$dispose();
                }
            });
            raiz.add_child(a);
            return a;
        };

        l.cielo = ['noche', 'dorado', 'dia'].map(f => imagen(raiz, T[`cielo-${f}`], W, H));
        l.atras = area(cr => this._pintaAtras(cr)); // cenizas, relámpagos e iluminación ambiental
        l.sol = imagen(raiz, T.sol, 208, 208);
        l.luna = imagen(raiz, T.luna, 208, 208);
        l.escena = ['noche', 'dorado', 'dia'].map(f => imagen(raiz, T[`escena-${f}`], W, H));
        l.delante = area(cr => this._pintaDelante(cr)); // El Ojo, erupción, ondas de choque, orcos y Fell Beast
        return l;
    }

    _creaMonitor(mon, principal) {
        if (principal) this._monPrincipal = mon;
        const raiz = new Clutter.Actor({x: mon.x, y: mon.y, width: mon.width, height: mon.height, clip_to_allocation: true, reactive: true});
        raiz.set_background_color(color('#0a040e'));
        this._cont.add_child(raiz);

        const u = Math.max(mon.width / W, mon.height / H);
        const arte = new Clutter.Actor({width: W, height: H, reactive: true});
        arte.set_scale(u, u);
        arte.set_position(Math.round((mon.width - W * u) / 2), Math.round((mon.height - H * u) / 2));
        raiz.add_child(arte);
        arte.add_child(principal ? this._lienzo.raiz : new Clutter.Clone({source: this._lienzo.raiz, width: W, height: H}));
        return {raiz};
    }

    destruyeMonitores() {
        for (const m of this._monitores.slice().reverse()) m.raiz.destroy();
        this._monitores = [];
        this._lienzo = null;
        this._monPrincipal = null;
    }

    _programa() {
        if (this._timer) { GLib.source_remove(this._timer); this._timer = 0; }
        if (this._pausa || !this._lienzo) return;
        const ms = this.animar ? Math.round(1000 / this.fps) : 60000;
        this._timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => {
            if (this.animar) {
                this.tick++;
                if (this.demo || this.tick % this.fps === 0) this.recalcula();
            } else {
                this.recalcula();
            }
            this.pinta();
            return GLib.SOURCE_CONTINUE;
        });
    }

    pausa(p) {
        if (p === this._pausa) return;
        this._pausa = p;
        if (!p) { this.recalcula(); this.pinta(); }
        this._programa();
    }

    pinta() {
        const l = this._lienzo;
        if (!l) return;
        fija(l.cielo[1], this.wA); fija(l.cielo[2], this.wB);
        fija(l.escena[1], this.wA); fija(l.escena[2], this.wB);

        l.sol.set_position(Math.round(this.solX - 104), Math.round(this.solY - 104));
        fija(l.sol, this.solOp);
        l.luna.set_position(Math.round(this.lunaX - 104), Math.round(this.lunaY - 104));
        fija(l.luna, this.lunaOp);

        l.atras.queue_repaint();
        l.delante.queue_repaint();
    }

    _pintaAtras(cr) {
        const t = this.tick, D = this.D;
        cr.setOperator(Cairo.Operator.CLEAR); cr.paint(); cr.setOperator(Cairo.Operator.OVER);

        // Relámpago carmesí
        const relampagoFase = (this.relampagoManual > 0) ? (4 - this.relampagoManual) : (t % 170);
        if (this.relampagoManual > 0) this.relampagoManual--;

        if (relampagoFase < 4) {
            const opFlash = (relampagoFase === 0 || relampagoFase === 2) ? 0.22 : 0.10;
            cr.setSourceRGBA(0.35, 0.05, 0.18, opFlash);
            cr.rectangle(0, 0, W, H);
            cr.fill();

            const rx_base = 370 + (t % 60);
            let rx = rx_base;
            const opRel = relampagoFase % 2 === 0 ? 0.95 : 0.65;
            for (let ry = 28; ry < 132; ry += 3) {
                px(cr, '#fff1f2', opRel, rx, ry, 2, 3);
                px(cr, '#e11d48', opRel * 0.75, rx - 1, ry, 4, 3);
                rx += (Math.sin(ry * 0.45) > 0) ? 2 : -1;
                if (ry === 64) {
                    let bx = rx, by = ry;
                    for (let s = 0; s < 7; s++) {
                        bx += 3; by += 2;
                        px(cr, '#fda4af', opRel * 0.7, bx, by, 1, 2);
                    }
                }
                // Rama secundaria hacia Barad-dûr
                if (ry === 48) {
                    let sx = rx, sy = ry;
                    for (let b = 0; b < 9; b++) {
                        sx -= 4; sy += 2;
                        px(cr, '#fda4af', opRel * 0.65, sx, sy, 1, 2);
                    }
                }
            }
        }

        // Runas del Anillo Único en Tengwar resplandeciendo en el firmamento volcánico
        if (this.nocheF > 0.12 || this.wB > 0.15) {
            const runeOp = (0.22 + 0.16 * Math.sin(t * 0.05)) * Math.max(this.nocheF, this.wB);
            const runes = [
                [[1,0],[2,0],[0,1],[2,1],[0,2],[1,2],[2,2],[2,3],[1,4],[2,5]], // Ash
                [[0,0],[1,0],[2,0],[2,1],[1,2],[0,3],[0,4],[1,4],[2,4]],       // Nazg
                [[0,0],[0,1],[1,1],[2,2],[2,3],[1,4],[0,4],[0,5]],             // Dur
                [[1,0],[2,0],[0,1],[1,2],[2,2],[2,3],[2,4],[1,5]],             // Ba
                [[0,0],[2,0],[1,1],[1,2],[1,3],[2,4],[1,5]],                   // Tu
                [[0,0],[0,1],[1,1],[2,0],[2,2],[1,3],[2,4],[0,5]],             // Lûk
                [[1,0],[0,1],[2,1],[0,2],[1,3],[2,3],[2,4],[1,5]],             // Gimb
                [[0,0],[1,0],[2,1],[1,2],[0,3],[1,4],[2,4],[2,5]]              // Atul
            ];
            const runeBaseX = Math.round(((t * 0.10) % 320) + 20);
            for (let rIdx = 0; rIdx < runes.length; rIdx++) {
                const rx = ((runeBaseX + rIdx * 20) % 360) + 25;
                const ry = Math.round(34 + Math.sin(t * 0.04 + rIdx * 0.7) * 4);
                for (const [dx, dy] of runes[rIdx]) {
                    px(cr, '#fbbf24', runeOp, rx + dx, ry + dy, 1, 1);
                    if (runeOp > 0.25) {
                        px(cr, '#ef4444', runeOp * 0.45, rx + dx - 1, ry + dy, 2, 1);
                    }
                }
            }
        }

        // Ascuas y cenizas en suspensión (brillan con mayor intensidad en noche y crepúsculo)
        const brilloParticulas = 0.35 + 0.50 * this.nocheF;
        if (D.estrellas) {
            D.estrellas.forEach((e, i) => {
                const dx = Math.sin(t * 0.04 + i) * 3;
                const dy = ((e[1] - t * 0.35 + i * 2) % 250);
                const py = dy < 0 ? dy + 250 : dy;
                const px_pos = (e[0] + dx) % W;
                const o = brilloParticulas * (0.4 + 0.6 * Math.sin(t * 0.12 + i * 1.5));
                px(cr, e[2], o, px_pos, py, 1, 1);
            });
        }
    }

    _pintaDelante(cr) {
        const t = this.tick;
        cr.setOperator(Cairo.Operator.CLEAR); cr.paint(); cr.setOperator(Cairo.Operator.OVER);

        // Posición del ratón para tracking dinámico
        let mouseX = null, mouseY = null;
        if (this._monPrincipal && typeof global !== 'undefined' && global.get_pointer) {
            try {
                const [gx, gy] = global.get_pointer();
                const mon = this._monPrincipal;
                const u = Math.max(mon.width / W, mon.height / H);
                const ox = (mon.width - W * u) / 2;
                const oy = (mon.height - H * u) / 2;
                mouseX = (gx - mon.x - ox) / u;
                mouseY = (gy - mon.y - oy) / u;
            } catch (e) {}
        }

        if (mouseX !== null) {
            const dmx = mouseX - (this.lastPointer[0] ?? 0);
            const dmy = mouseY - (this.lastPointer[1] ?? 0);
            if (dmx * dmx + dmy * dmy > 4) {
                this.lastPointer = [mouseX, mouseY];
                this.pointerStillTicks = 0;
            } else {
                this.pointerStillTicks++;
            }
        }

        // 1. EL OJO DE SAURON (X=195, Y=74)
        const eyeBaseX = 195, eyeBaseY = 74;
        let targetX = eyeBaseX, targetY = eyeBaseY;
        let inProximity = 0;

        if (mouseX !== null && this.pointerStillTicks < 75) {
            const dx = mouseX - eyeBaseX, dy = mouseY - eyeBaseY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const ang = Math.atan2(dy, dx);
            const factor = Math.min(1.0, dist / 90.0);
            targetX = eyeBaseX + Math.cos(ang) * (4.5 * factor);
            targetY = eyeBaseY + Math.sin(ang) * (2.8 * factor);
            if (dist < 130) inProximity = Math.max(0, 1.0 - dist / 130);
        } else {
            targetX = eyeBaseX + Math.sin(t * 0.05) * 3.5;
            targetY = eyeBaseY + Math.sin(t * 0.025) * 1.5;
        }

        this.eyeCurX += (targetX - this.eyeCurX) * 0.22;
        this.eyeCurY += (targetY - this.eyeCurY) * 0.22;
        this.proximityAlert += (inProximity - this.proximityAlert) * 0.15;

        // El fuego del Ojo es más contrastado y brillante en la noche y crepúsculo
        const factorNoche = 0.85 + 0.35 * this.nocheF;
        const pOjo = (0.80 + 0.20 * Math.sin(t * 0.15) + this.proximityAlert * 0.45) * factorNoche;

        px(cr, '#ef4444', 0.18 * pOjo, eyeBaseX - 24, eyeBaseY - 24, 48, 48);
        px(cr, '#f97316', 0.32 * pOjo, eyeBaseX - 16, eyeBaseY - 16, 32, 32);
        px(cr, '#fef08a', 0.55 * pOjo, eyeBaseX - 7, eyeBaseY - 7, 14, 14);

        // Haz de búsqueda
        const gazeDx = this.eyeCurX - eyeBaseX, gazeDy = this.eyeCurY - eyeBaseY;
        const gazeDist = Math.sqrt(gazeDx * gazeDx + gazeDy * gazeDy);
        if (gazeDist > 0.5) {
            const gAngle = Math.atan2(gazeDy, gazeDx);
            for (let distBeam = 10; distBeam <= 45; distBeam += 5) {
                const spread = distBeam * 0.35;
                const bx = eyeBaseX + Math.cos(gAngle) * distBeam;
                const by = eyeBaseY + Math.sin(gAngle) * distBeam;
                const bAlpha = (1.0 - distBeam / 50.0) * (0.04 + this.proximityAlert * 0.06 + this.nocheF * 0.04);
                px(cr, '#ff5500', bAlpha, bx - spread / 2, by - spread / 2, spread, spread);
            }
        }

        // Llamaradas radiales
        const flareBoost = Math.round(this.proximityAlert * 6 + this.nocheF * 2);
        for (let fl = 0; fl < 16; fl++) {
            const ang = (fl / 16.0) * 2 * Math.PI + Math.sin(t * 0.08) * 0.12;
            const flare_h = 10 + flareBoost + Math.round(Math.sin(t * 0.3 + fl * 1.8) * 4);
            const fx = eyeBaseX + Math.cos(ang) * (flare_h + 3);
            const fy = eyeBaseY + Math.sin(ang) * (flare_h * 0.7 + 3);
            px(cr, (fl % 2 === 0) ? '#ff5500' : '#fef08a', 0.85, fx, fy, 2, 2);
        }

        if (this.proximityAlert > 0.18) {
            for (let arc = -12; arc <= 12; arc += 4) {
                if (Math.sin(t * 0.5 + arc) > 0.2) {
                    px(cr, '#fef08a', 0.75, eyeBaseX + arc, eyeBaseY - 14, 2, 1);
                    px(cr, '#ef4444', 0.80, eyeBaseX + arc, eyeBaseY - 13, 2, 1);
                }
            }
        }

        // Arcos de plasma y energía entre las agujas de hierro de Barad-dûr
        if ((t % 28 < 7) || this.proximityAlert > 0.15) {
            const arcOp = (this.proximityAlert > 0.15) ? 0.95 : 0.65;
            for (let step = 0; step < 6; step++) {
                const k1 = step / 6.0;
                const j1 = (Math.sin(t * 0.7 + step) > 0) ? 1 : -1;
                const j2 = (Math.cos(t * 0.7 + step) > 0) ? 1 : -1;
                px(cr, '#f43f5e', arcOp, Math.round(190 + k1 * 5 + j1), Math.round(66 + k1 * 7), 1, 1);
                px(cr, '#fef08a', arcOp * 0.9, Math.round(200 - k1 * 5 + j2), Math.round(66 + k1 * 7), 1, 1);
            }
        }

        // Pupila rasgada
        const scanX = Math.round(this.eyeCurX);
        const scanY = Math.round(this.eyeCurY);
        for (let py = -7; py <= 7; py++) {
            const pw = (Math.abs(py) > 4) ? 1 : (this.proximityAlert > 0.3 ? 3 : 2);
            px(cr, '#050102', 1.0, scanX - pw / 2, scanY + py, pw, 1);
        }
        px(cr, '#ffffff', 0.95 * pOjo, scanX, scanY - 1, 1, 1);

        // Ondas de choque
        this.shockwaves = this.shockwaves.filter(sw => {
            sw.life--;
            const progress = 1.0 - sw.life / sw.maxLife;
            const curR = sw.r + progress * (sw.maxR - sw.r);
            const opSw = (1.0 - progress) * 0.55;
            for (let deg = 0; deg < 36; deg++) {
                const rad = (deg / 36.0) * 2 * Math.PI;
                const wx = sw.x + Math.cos(rad) * curR;
                const wy = sw.y + Math.sin(rad) * (curR * 0.65);
                if (wx >= 0 && wx < W && wy >= 0 && wy < H) {
                    px(cr, (deg % 2 === 0) ? '#ff5500' : '#fef08a', opSw, wx, wy, 2, 2);
                }
            }
            return sw.life > 0;
        });

        // 2. MONTE DEL DESTINO (ORODRUIN: X=395, Y=146)
        const ox = 395, oy = 146;
        const pMagma = 0.5 + 0.5 * Math.sin(t * 0.22);
        px(cr, '#fef08a', 0.95 * pMagma, ox - 7, oy - 1, 14, 2);
        px(cr, '#ff5500', 0.85, ox - 14, oy, 28, 2);

        // Humo volcánico (en día es más grisáceo y denso; en crepúsculo rojizo; en noche carbón oscuro)
        if (t % 3 === 0 && this.smokeParticles.length < 40) {
            this.smokeParticles.push({
                x: ox + (Math.sin(t * 0.4) * 6),
                y: oy - 2,
                vx: -0.38 - Math.random() * 0.35,
                vy: -0.65 - Math.random() * 0.40,
                age: 0,
                maxAge: 42 + Math.floor(Math.random() * 25)
            });
        }
        this.smokeParticles = this.smokeParticles.filter(p => {
            p.age++;
            p.x += p.vx;
            p.y += p.vy;
            const progress = p.age / p.maxAge;
            const rad = Math.min(9, 2 + Math.floor(progress * 7));
            const opSmoke = (1.0 - progress) * (0.35 + 0.15 * (1 - this.nocheF));
            let colSmoke = '#1c0d18';
            if (this.wA > 0.4) colSmoke = (progress < 0.3) ? '#c2410c' : '#331220';
            else if (this.wB > 0.5) colSmoke = (progress < 0.2) ? '#78350f' : '#291823';
            else colSmoke = (progress < 0.25) ? '#ff5500' : '#140810';
            px(cr, colSmoke, opSmoke, p.x - rad / 2, p.y - rad / 2, rad, rad);
            return p.age < p.maxAge;
        });

        // Bombas de lava
        if (t % 45 === 0 && this.lavaBombs.length < 3) {
            this.lavaBombs.push({
                x: ox + (Math.random() - 0.5) * 6,
                y: oy - 2,
                vx: (Math.random() - 0.5) * 1.6 - 0.2,
                vy: -2.8 - Math.random() * 1.0,
                age: 0
            });
        }
        this.lavaBombs = this.lavaBombs.filter(b => {
            b.age++;
            b.vy += 0.12;
            b.x += b.vx;
            b.y += b.vy;
            px(cr, '#ff3700', 0.85, b.x - b.vx * 0.7, b.y - b.vy * 0.7, 1, 1);
            px(cr, '#fef08a', 0.95, b.x, b.y, 2, 2);
            if (b.y >= 152 && b.vy > 0) {
                for (let k = 0; k < 3; k++) {
                    this.volcanicEmbers.push({
                        x: b.x, y: b.y,
                        vx: (Math.random() - 0.5) * 1.2,
                        vy: -0.6 - Math.random() * 0.8,
                        age: 0, maxAge: 15
                    });
                }
                return false;
            }
            return b.age < 60;
        });

        this.volcanicEmbers = this.volcanicEmbers.filter(e => {
            e.age++;
            e.x += e.vx; e.y += e.vy; e.vy += 0.08;
            px(cr, '#fbbf24', 1.0 - e.age / e.maxAge, e.x, e.y, 1, 1);
            return e.age < e.maxAge;
        });

        // Ríos de lava
        for (const [lx, ly] of [[395, 155], [402, 168], [394, 185], [408, 198]]) {
            const pLava = Math.pow(Math.max(0, Math.sin(t * 0.18 + lx * 0.05)), 2);
            if (pLava > 0.05) px(cr, '#fef08a', 0.85 * pLava, lx - 1, ly - 1, 3, 2);
        }

        // Cascada continua de lava ardiente por las laderas del Orodruin
        const lavaVeins = [
            [[395,148],[394,154],[392,162],[389,172],[385,184],[381,198],[377,214]],
            [[396,148],[399,156],[403,166],[408,178],[414,192],[421,208],[428,226]],
            [[395,149],[396,158],[395,170],[393,184],[390,200],[388,218],[386,236]]
        ];
        for (let v = 0; v < lavaVeins.length; v++) {
            const vein = lavaVeins[v];
            for (let seg = 0; seg < vein.length - 1; seg++) {
                const pt = vein[seg];
                const lavaFlow = Math.sin(t * 0.25 - seg * 0.8 + v * 1.5);
                if (lavaFlow > -0.2) {
                    const colVein = (lavaFlow > 0.5) ? '#fef08a' : (lavaFlow > 0.1 ? '#fb923c' : '#dc2626');
                    px(cr, colVein, 0.75 + 0.25 * lavaFlow, pt[0], pt[1], (seg < 3 ? 1 : 2), 2);
                }
            }
        }

        // Grietas permanentes
        const pFisura = 0.6 + 0.4 * Math.sin(t * 0.14);
        for (const [gx, gy] of [[118, 288], [206, 298], [382, 312], [470, 324], [558, 305]]) {
            px(cr, '#ff6600', 0.35 * pFisura, gx - 4, gy - 1, 9, 3);
            px(cr, '#fef08a', 0.70 * pFisura, gx - 1, gy, 3, 1);
        }

        // Grietas temporales
        this.grietasTemporales = this.grietasTemporales.filter(g => {
            g.life--;
            const opG = g.life / g.maxLife;
            const flicker = Math.sin(t * 0.5 + g.x);
            px(cr, '#ff5500', opG * 0.65, g.x - 8, g.y - 1, 16, 3);
            px(cr, '#fef08a', opG * (0.8 + 0.2 * flicker), g.x - 4, g.y, 8, 1);
            return g.life > 0;
        });

        // 3. LEGIÓN DE ORCOS CON PICAS Y ANTORCHAS
        const baseX = Math.round(((W + 180) - ((t * 0.38) % (W + 260))) - 80);

        // Estandarte del Gran Ojo Rojo liderando la hueste
        const bannerX = baseX - 10;
        if (bannerX >= -12 && bannerX <= W + 12) {
            px(cr, '#1c1917', 1.0, bannerX, 354, 1, 15);
            const ondula = (t % 6 < 3) ? 0 : 1;
            px(cr, '#09090b', 0.95, bannerX + 1, 354, 7 - ondula, 6);
            px(cr, '#ef4444', 1.0, bannerX + 3, 356, 3, 2);
            px(cr, '#fef08a', 0.95, bannerX + 4, 357, 1, 1);
        }
        for (let i = 0; i < 14; i++) {
            const orcX = baseX + i * 12;
            if (orcX >= -12 && orcX <= W + 12) {
                const marchStep = ((t + i * 2) % 4) < 2;
                px(cr, '#080309', 1.0, orcX, 365, 2, 2);
                px(cr, '#080309', 1.0, orcX - 1, 367, 3, 3);
                if (marchStep) {
                    px(cr, '#080309', 1.0, orcX - 1, 370, 1, 2);
                    px(cr, '#080309', 1.0, orcX + 1, 369, 1, 2);
                } else {
                    px(cr, '#080309', 1.0, orcX - 1, 369, 1, 2);
                    px(cr, '#080309', 1.0, orcX + 1, 370, 1, 2);
                }
                px(cr, '#17060f', 1.0, orcX + 1, 364, 1, 2);
                px(cr, '#2d1422', 1.0, orcX - 1, 361, 1, 3);
                px(cr, '#5a2233', 1.0, orcX - 2, 360, 1, 1);

                if (i % 4 === 0) {
                    const flick = Math.sin(t * 0.4 + i);
                    const tx = orcX - 3, ty = 359 + (flick > 0 ? 0 : 1);
                    px(cr, '#ff5500', 0.95, tx, ty, 2, 2);
                    px(cr, '#fef08a', 0.85, tx + 1, ty, 1, 1);
                    // Las antorchas resaltan mucho más en la oscuridad de la noche
                    const glowOp = 0.20 + 0.25 * this.nocheF;
                    px(cr, '#eab308', glowOp, orcX - 5, 371, 6, 1);
                }
            }
        }

        // 4. BESTIA ALADA NAZGÛL
        const nazAngle = t * 0.016;
        const nazX = Math.round(140 + Math.cos(nazAngle) * 92);
        const alturaBase = 108 - Math.round(this.wB * 14);
        let nazY = Math.round(alturaBase + Math.sin(nazAngle * 2) * 16);

        if (this.nazgulDive > 0) {
            this.nazgulDive--;
            nazY += Math.round(Math.sin((32 - this.nazgulDive) * 0.20) * 22);
        }

        this.nazCurX = nazX;
        this.nazCurY = nazY;

        const facingRight = (-Math.sin(nazAngle) > 0);
        const climbing = Math.cos(nazAngle * 2) < 0 || this.nazgulDive > 0;
        const aleteo = (this.nazgulDive > 0) ? Math.sin(t * 0.8) : (climbing ? Math.sin(t * 0.40) : Math.sin(t * 0.15) * 0.5);
        const wingOffset = Math.round(aleteo * 5);

        px(cr, '#060208', 1.0, nazX - 5, nazY, 11, 2);
        px(cr, '#000000', 1.0, nazX, nazY - 2, 2, 2);

        if (facingRight) {
            px(cr, '#060208', 1.0, nazX + 6, nazY - 3, 5, 2);
            px(cr, '#060208', 1.0, nazX + 11, nazY - 4, 3, 2);
            px(cr, '#060208', 1.0, nazX - 10, nazY + 2, 6, 1);
        } else {
            px(cr, '#060208', 1.0, nazX - 10, nazY - 3, 5, 2);
            px(cr, '#060208', 1.0, nazX - 13, nazY - 4, 3, 2);
            px(cr, '#060208', 1.0, nazX + 5, nazY + 2, 6, 1);
        }

        if (wingOffset >= 0) {
            px(cr, '#060208', 1.0, nazX - 13, nazY - 8 - wingOffset, 10, 8);
            px(cr, '#060208', 1.0, nazX + 4, nazY - 7 - wingOffset, 10, 8);
        } else {
            px(cr, '#060208', 1.0, nazX - 13, nazY - 2 - wingOffset, 10, 6);
            px(cr, '#060208', 1.0, nazX + 4, nazY - 2 - wingOffset, 10, 6);
        }

        // 5. EASTER EGG: FRODO Y SAM INFILTRÁNDOSE EN GORGOROTH (Y=304)
        const sauronMirando = (this.eyeCurX > 196 && this.eyeCurY > 74);
        const ratonCerca = (mouseX !== null && Math.hypot(mouseX - this.hobbits.x, mouseY - this.hobbits.y) < 70);

        if (sauronMirando || ratonCerca) {
            this.hobbits.state = 'crouched';
        } else {
            this.hobbits.state = 'sneaking';
            this.hobbits.x += 0.22;
            if (this.hobbits.x > 330) this.hobbits.x = 248;
        }

        const hx = Math.round(this.hobbits.x);
        const hy = this.hobbits.y;

        if (this.hobbits.state === 'crouched') {
            px(cr, '#3f3f46', 0.95, hx - 2, hy, 4, 3);
            px(cr, '#52525b', 0.85, hx - 1, hy - 1, 3, 2);
            px(cr, '#27272a', 1.0, hx - 3, hy + 2, 6, 1);
            if (this.nocheF > 0.6 && (t % 80 === 0)) {
                px(cr, '#e0f2fe', 0.95, hx, hy - 1, 1, 1);
            }
        } else {
            const paso = (Math.floor(t * 0.3) % 2) === 0;
            px(cr, '#475569', 1.0, hx + 3, hy - 1, 2, 3);
            px(cr, '#94a3b8', 1.0, hx + 4, hy - 2, 1, 1);
            px(cr, '#1e293b', 1.0, hx + 3, hy + 2, paso ? 2 : 1, 1);
            px(cr, '#334155', 1.0, hx - 2, hy, 3, 3);
            px(cr, '#71717a', 1.0, hx - 1, hy - 1, 2, 1);
            px(cr, '#1e293b', 1.0, hx - 2, hy + 2, paso ? 1 : 2, 1);
        }

        // 6. LLUVIA DE CENIZA VOLCÁNICA EN SUSPENSIÓN (ATMÓSFERA DE MORDOR)
        if (this.lluviaCeniza) {
            for (let i = 0; i < this.ashFlakes.length; i++) {
                const f = this.ashFlakes[i];
                f.y = (f.y + f.vy) % H;
                f.x = (f.x - 0.20 + Math.sin(t * 0.05 + f.sway) * 0.35 + W) % W;
                const op = 0.25 + 0.15 * Math.sin(t * 0.1 + i);
                const colAsh = (this.wA > 0.4) ? '#451a28' : '#1e0c18';
                px(cr, colAsh, op, f.x, f.y, f.size, f.size);
            }
        }
    }

    destroy() {
        if (this._timer) GLib.source_remove(this._timer);
        this._timer = 0;
        if (this.ambienteTimer) {
            GLib.source_remove(this.ambienteTimer);
            this.ambienteTimer = 0;
        }
        this.destruyeMonitores();
    }

    destruye() {
        this.destroy();
    }
}
