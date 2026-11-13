// PixelZen para GNOME - Panel de datos (HUD) temático Mordor (El Señor de los Anillos).
// - Interactividad total con clics y efectos sonoros de la Tierra Media:
//   * Clic en Reloj/Fecha: Abre Calendario de GNOME.
//   * Clic en Forjas: Abre Terminal con htop.
//   * Clic en Huestes: Abre Configuración de Red.
//   * Clic en Armería: Abre Explorador de Archivos en $HOME.
//   * Clic en Citas: Cicla entre las citas de Sauron, el Anillo y el Rey Brujo con sonido de campana de oro.
// - Efecto de resplandor ígneo al pasar el ratón (hover) sobre cada tarjeta.
// - Barra de Corrupción y Poder de Sauron calculada con la carga total del sistema.
// - Inscripción del Anillo Único en dos líneas con brillo de oro ardiente continuo.

import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import St from 'gi://St';
import Pango from 'gi://Pango';
import PangoCairo from 'gi://PangoCairo';

const ANCHO = 336, ALTO = 890, ALTO_COLAPSADO = 126;

const PAL = {
    bg: '#0c0507', bg2: '#160a0e', track: '#260f14', line: '#4a191d',
    border: '#782622', border_gold: '#b45309',
    text: '#e6dedc', dim: '#b39d98', faint: '#6e5653',
    red: '#ff3700', hot: '#ff1100', lava: '#ff5500',
    amber: '#f59e0b', gold: '#fbbf24', gold_light: '#fef08a',
    cyan: '#ff7733', blue: '#991b1b'
};
const MONO = 'Departure Mono';

const DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

const CITAS_MORDOR = [
    {tit: 'EL ANILLO ÚNICO', es: 'Ash nazg durbatulûk, ash nazg gimbatul, ash nazg thrakatulûk agh burzum-ishi krimpatul.', au: 'Sauron'},
    {tit: 'EL OJO DE SAURON', es: 'No hay vida en el vacío... solo muerte. No puedes esconderte. ¡Te veo!', au: 'El Gran Ojo'},
    {tit: 'ORODRUIN', es: 'Forjado en las profundidades ardientes del Monte del Destino.', au: 'El Señor Oscuro'},
    {tit: 'EL REY BRUJO', es: '¿Conoces el miedo? Se congelará tu carne y tu corazón morirá ante mi presencia.', au: 'Rey Brujo de Angmar'},
    {tit: 'BARAD-DÛR', es: 'La sombra se extiende sobre todo el mundo. La era del Hombre ha terminado.', au: 'Boca de Sauron'},
    {tit: 'GORGOROTH', es: 'Ni una brizna de hierba crece en la tierra marchita donde se alzan las sombras.', au: 'Tierra de las Sombras'}
];

const p2 = n => (n < 10 ? '0' : '') + n;
const tasa = b => b >= 1048576 ? (b / 1048576).toFixed(1) + 'M' : b >= 1024 ? Math.round(b / 1024) + 'K' : b + 'B';
const horas = m => m > 0 ? Math.floor(m / 60) + 'h' + p2(m % 60) : '--';
function durac(s) {
    const dd = Math.floor(s / 86400), hh = Math.floor(s % 86400 / 3600), mm = Math.floor(s % 3600 / 60);
    return dd > 0 ? dd + 'd ' + hh + 'h' : hh + 'h ' + p2(mm) + 'm';
}
function luna() {
    const syn = 29.530588853, ref = Date.UTC(2000, 0, 6, 18, 14) / 86400000;
    const age = (((Date.now() / 86400000 - ref) % syn) + syn) % syn;
    return {age, p: age / syn};
}
function rgb(hex) {
    const h = hex.replace('#', '');
    return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255];
}

export class Hud {
    constructor(dir) {
        this._dir = dir;
        this._script = `${dir}/code/datos.py`;
        this.d = {cpu: 0, ram: {pct: 0, usado: 0, total: 0}, temp: 0, bat: null, net: {vpn: {}}, load: [0, 0, 0], up: 0, disco: 0, libre: 0, top: [], nuc: 0};
        this.s = {puertos: [], repos: [], tc: {}, tools: {}, fallos: 0, errores: 0, est: 0, vecinos: 0};
        this.cpuH = [];
        this.ramH = [];
        this.rxH = [];
        this.citaIdx = Math.floor(Date.now() / 25000) % CITAS_MORDOR.length;
        this._ocupado = {};
        this._timers = [];
        this._cancel = new Gio.Cancellable();
        this._fuentes = new Map();
        this.k = 1.0;

        // Estados interactivos
        this.colapsado = false;
        this.cardDestacada = -1;
        this.hoverCard = -1;
        this.areaTrabajo = null;

        // Actor interactivo (reactivo a clics y eventos de ratón)
        this.actor = new St.DrawingArea({reactive: true, can_focus: true, track_hover: true});
        this.actor.connect('repaint', a => this._pinta(a));
        this.actor.connect('button-press-event', (actor, event) => this._onButtonPress(event));
        this.actor.connect('motion-event', (actor, event) => {
            const [, , y] = event.get_coords();
            const ly = (y - this.actor.y) / this.k;
            let h = -1;
            if (this.colapsado) {
                h = 0;
            } else {
                if (ly < 130) h = 0;
                else if (ly < 342) h = 1;
                else if (ly < 546) h = 2;
                else if (ly < 685) h = 3;
                else h = 4;
            }
            if (this.hoverCard !== h) {
                this.hoverCard = h;
                this.actor.queue_repaint();
            }
            return false;
        });
        this.actor.connect('leave-event', () => {
            if (this.hoverCard !== -1) {
                this.hoverCard = -1;
                this.actor.queue_repaint();
            }
            return false;
        });

        this._lanza('rapido');
        this._lanza('lento');
        this._cada(2000, () => this._lanza('rapido'));
        this._cada(20000, () => this._lanza('lento'));
        this._cada(1000, () => this.actor.queue_repaint());
        this._cada(25000, () => {
            this.citaIdx = (this.citaIdx + 1) % CITAS_MORDOR.length;
            this.actor.queue_repaint();
        });
    }

    _suena(nombre) {
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

    cambiaCita() {
        this.citaIdx = (this.citaIdx + 1) % CITAS_MORDOR.length;
        this.cardDestacada = 4;
        this._suena('anillo');
        this._cadaUnaVez(250, () => { this.cardDestacada = -1; this.actor.queue_repaint(); });
        this.actor.queue_repaint();
    }

    _ejecuta(cmd) {
        try {
            Gio.Subprocess.new(cmd, Gio.SubprocessFlags.NONE);
        } catch (e) {
            logError(e, 'PixelZen Mordor HUD exec');
        }
    }

    _onButtonPress(event) {
        const [, , y] = event.get_coords();
        const localY = (y - this.actor.y) / this.k;

        // Botón superior derecho de colapso en Card 0
        if (localY <= 38) {
            this.colapsado = !this.colapsado;
            this._suena('anillo');
            if (this.areaTrabajo) this.coloca(this.areaTrabajo);
            return true;
        }

        // Si está colapsado, clic en cualquier parte lo expande
        if (this.colapsado) {
            this.colapsado = false;
            this._suena('anillo');
            if (this.areaTrabajo) this.coloca(this.areaTrabajo);
            return true;
        }

        // Card 0: 38..130 (Reloj y Calendario -> abre Calendario de GNOME)
        if (localY > 38 && localY < 130) {
            this.cardDestacada = 0;
            this._suena('anillo');
            this._ejecuta(['gnome-calendar']);
            this._cadaUnaVez(250, () => { this.cardDestacada = -1; this.actor.queue_repaint(); });
            this.actor.queue_repaint();
            return true;
        }

        // Card 1: 130..342 (Forjas - CPU / RAM / Temp -> abre htop en terminal)
        if (localY >= 130 && localY < 342) {
            this.cardDestacada = 1;
            this._suena('anillo');
            this._ejecuta(['gnome-terminal', '--', 'htop']);
            this._cadaUnaVez(250, () => { this.cardDestacada = -1; this.actor.queue_repaint(); });
            this.actor.queue_repaint();
            return true;
        }

        // Card 2: 342..546 (Huestes / Red -> abre configuración de Red)
        if (localY >= 342 && localY < 546) {
            this.cardDestacada = 2;
            this._suena('anillo');
            this._ejecuta(['gnome-control-center', 'network']);
            this._cadaUnaVez(250, () => { this.cardDestacada = -1; this.actor.queue_repaint(); });
            this.actor.queue_repaint();
            return true;
        }

        // Card 3: 546..685 (Armería e Inventario -> abre Archivos en $HOME)
        if (localY >= 546 && localY < 685) {
            this.cardDestacada = 3;
            this._suena('anillo');
            this._ejecuta(['nautilus', GLib.get_home_dir()]);
            this._cadaUnaVez(250, () => { this.cardDestacada = -1; this.actor.queue_repaint(); });
            this.actor.queue_repaint();
            return true;
        }

        // Card 4: >= 685 (Citas del Anillo Único -> cambia de cita)
        if (localY >= 685) {
            this.cambiaCita();
            return true;
        }

        return false;
    }

    _cadaUnaVez(ms, fn) {
        GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => {
            fn();
            return GLib.SOURCE_REMOVE;
        });
    }

    coloca(area) {
        this.areaTrabajo = area;
        const margen = 24;
        const altoRef = this.colapsado ? ALTO_COLAPSADO : ALTO;
        this.k = Math.max(0.65, Math.min(1.4, (area.height - 2 * margen) / ALTO));
        const w = Math.round(ANCHO * this.k);
        const h = Math.round(altoRef * this.k);
        this.actor.set_size(w, h);
        this.actor.set_position(area.x + area.width - w - margen, area.y + margen);
        this.actor.queue_repaint();
    }

    _cada(ms, fn) {
        this._timers.push(GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => {
            fn();
            return GLib.SOURCE_CONTINUE;
        }));
    }

    _push(a, v, n) {
        const b = a.slice();
        b.push(v);
        if (b.length > n) b.shift();
        return b;
    }

    _lanza(modo) {
        if (this._ocupado[modo]) return;
        this._ocupado[modo] = true;
        let proc;
        try {
            proc = Gio.Subprocess.new(['python3', '-I', this._script, modo, 'gnome'],
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE);
        } catch (e) {
            this._ocupado[modo] = false;
            return;
        }
        proc.communicate_utf8_async(null, this._cancel, (p, res) => {
            try {
                const [, out] = p.communicate_utf8_finish(res);
                if (out) {
                    const r = JSON.parse(out);
                    if (modo === 'rapido') {
                        this.d = r;
                        this.cpuH = this._push(this.cpuH, r.cpu ?? 0, 56);
                        this.ramH = this._push(this.ramH, r.ram?.pct ?? 0, 56);
                        this.rxH = this._push(this.rxH, r.net?.rx ?? 0, 40);
                    } else {
                        this.s = r;
                    }
                    this.actor.queue_repaint();
                }
            } catch (e) {}
            finally { this._ocupado[modo] = false; }
        });
    }

    _fuente(fam, px) {
        const k = fam + px;
        if (!this._fuentes.has(k)) {
            const f = Pango.FontDescription.from_string(fam);
            f.set_absolute_size(px * Pango.SCALE);
            this._fuentes.set(k, f);
        }
        return this._fuentes.get(k);
    }

    _col(hex, a = 1) { const [r, g, b] = rgb(hex); this.cr.setSourceRGBA(r, g, b, a); }
    _rect(x, y, w, h, hex, a = 1) {
        this._col(hex, a);
        this.cr.rectangle(x, y, w, h);
        this.cr.fill();
    }

    _t(x, y, txt, {fam = MONO, px = 12, col = PAL.text, w = 0, align = 'left', wrap = false} = {}) {
        const lay = PangoCairo.create_layout(this.cr);
        lay.set_font_description(this._fuente(fam, px));
        lay.set_text(String(txt ?? ''), -1);
        if (wrap && w > 0) {
            lay.set_width(w * Pango.SCALE);
            lay.set_wrap(Pango.WrapMode.WORD);
        }
        const [tw] = lay.get_pixel_size();
        let ax = x;
        if (align === 'right' && w > 0) ax = x + w - tw;
        else if (align === 'center' && w > 0) ax = x + (w - tw) / 2;
        this.cr.moveTo(ax, y);
        this._col(col);
        PangoCairo.show_layout(this.cr, lay);
        return tw;
    }

    _etq(x, y, s) { return this._t(x, y, String(s ?? ''), {fam: MONO, px: 11, col: PAL.dim}); }
    _val(x, y, s, opt = {}) { return this._t(x, y, String(s ?? ''), {fam: MONO, px: 11, col: PAL.text, ...opt}); }

    _pares(x, y, lista, pad = 12) {
        let px_c = x;
        for (const [e, v, col = PAL.text] of lista) {
            px_c += this._etq(px_c, y, e) + 6;
            px_c += this._val(px_c, y, v, {col}) + pad;
        }
    }

    _cardMordor(y, h, icono, title, meta, cardIdx = -1) {
        const pad = 12, w = ANCHO;
        const destacada = (this.cardDestacada === cardIdx && cardIdx >= 0);
        const hovered = (this.hoverCard === cardIdx && cardIdx >= 0);
        const colBorde = destacada ? PAL.gold_light : (hovered ? PAL.amber : PAL.border);
        const colFondo = destacada ? '#1f0d14' : (hovered ? '#14070a' : PAL.bg);

        this._rect(0, y, w, h, colFondo, 0.90);
        this._col(colBorde);
        this.cr.setLineWidth(1);
        this.cr.rectangle(0.5, y + 0.5, w - 1, h - 1);
        this.cr.stroke();

        // Esquinas reforzadas de hierro de Barad-dûr
        const cCorn = destacada ? PAL.gold_light : (hovered ? PAL.gold : PAL.red);
        this._rect(0, y, 7, 2, cCorn); this._rect(0, y, 2, 7, cCorn);
        this._rect(w - 7, y, 7, 2, cCorn); this._rect(w - 2, y, 2, 7, cCorn);
        this._rect(0, y + h - 2, 7, 2, cCorn); this._rect(0, y + h - 7, 2, 7, cCorn);
        this._rect(w - 7, y + h - 2, 7, 2, cCorn); this._rect(w - 2, y + h - 7, 2, 7, cCorn);

        const kw = this._t(pad, y + 7, icono, {px: 13, col: hovered ? PAL.gold_light : PAL.gold});
        this._t(pad + kw + 7, y + 9, title.split('').join(' '), {px: 11, col: hovered ? PAL.gold_light : PAL.gold});
        if (meta) {
            const wMeta = (cardIdx === 0) ? (w - 2 * pad - 42) : (w - 2 * pad);
            this._t(pad, y + 8, meta, {px: 11, col: PAL.dim, w: wMeta, align: 'right'});
        }
        for (let x = pad; x < w - pad - 2; x += 4) this._rect(x, y + 27, 2, 1, PAL.line);
        return {x: pad, y: y + 34, w: w - 2 * pad};
    }

    _barraLava(x, y, w, pct) {
        this._rect(x, y, w, 10, '#260a0f');
        this._col(PAL.border);
        this.cr.setLineWidth(1);
        this.cr.rectangle(x + 0.5, y + 0.5, w - 1, 9);
        this.cr.stroke();
        const fillW = Math.max(0, Math.min(w - 4, Math.round((w - 4) * (pct / 100))));
        this._rect(x + 2, y + 2, fillW, 6, PAL.red);
        this._rect(x + 2, y + 2, fillW, 2, PAL.lava);
    }

    _spark(x, y, w, h, serie, cols, maxv, col) {
        const bw = Math.floor((w - cols) / cols);
        const maxVal = Math.max(1, maxv);
        for (let i = 0; i < cols; i++) {
            const j = serie.length - cols + i;
            const v = j >= 0 && j < serie.length ? serie[j] : 0;
            const bx = x + i * (bw + 1);
            this._rect(bx, y + h - 1, bw, 1, PAL.line);
            const bh = Math.max(2, Math.round(Math.min(1, v / maxVal) * h));
            const prog = bh / h;
            const cBar = prog > 0.70 ? PAL.gold_light : (prog > 0.35 ? PAL.lava : col);
            this._rect(bx, y + h - bh, bw, bh, cBar, 0.40 + 0.60 * (i / cols));
            if (prog > 0.75) {
                this._rect(bx, y + h - bh, bw, 1, '#ffffff', 0.85);
            }
        }
    }

    _faseSolar(now) {
        const h = now.getHours() + now.getMinutes() / 60;
        if (h >= 8.5 && h < 17.5) {
            return 'CENIZA DIURNA';
        } else if ((h >= 7.0 && h < 8.5) || (h >= 17.5 && h < 19.0)) {
            return 'HORA DE SANGRE';
        } else {
            return 'NOCHE OSCURA';
        }
    }

    _pinta(area) {
        const cr = area.get_context();
        this.cr = cr;
        try {
            const [sw] = area.get_surface_size();
            const k = sw / ANCHO;
            cr.scale(k, k);
            const now = new Date(), d = this.d, s = this.s, net = d.net ?? {vpn: {}};
            let y = 0;

            // ===== 1. TIEMPO EN MORDOR (CABECERA) - Clic abre Calendario
            let b = this._cardMordor(y, 126, '👁', 'TIEMPO · ' + this._faseSolar(now), 'TERCERA EDAD', 0);
            this._t(b.x - 2, b.y - 2, p2(now.getHours()) + ':' + p2(now.getMinutes()), {px: 44, col: PAL.gold});
            this._t(b.x + 144, b.y + 16, p2(now.getSeconds()), {px: 18, col: PAL.red});
            this._t(b.x, b.y + 44, `${DIAS[now.getDay()]} ${now.getDate()} ${MESES[now.getMonth()]} ${now.getFullYear()}`, {px: 12, col: PAL.text});

            // Inscripción del Anillo Único pulsante en lengua negra
            const ringGlow = 0.70 + 0.30 * Math.sin(Date.now() / 600);
            const colRing = ringGlow > 0.88 ? PAL.gold_light : PAL.gold;
            this._t(b.x, b.y + 64, 'ASH NAZG DURBATULÛK', {fam: MONO, px: 11, col: colRing});

            // Botón de control: Colapso
            const colIcon = this.colapsado ? '▼' : '▲';
            this._t(b.x + b.w - 24, y + 8, `[${colIcon}]`, {fam: MONO, px: 11, col: PAL.gold});

            // Fase lunar
            const L = luna(), q = Math.cos(2 * Math.PI * L.p);
            const lx = b.x + b.w - 44, ly = b.y + 2;
            for (let j = 0; j < 9; j++) {
                for (let i = 0; i < 9; i++) {
                    const nx = (i - 4) / 4.5, ny = (j - 4) / 4.5;
                    if (nx * nx + ny * ny > 1.02) continue;
                    const ill = Math.sqrt(Math.max(0, 1 - ny * ny));
                    const lit = L.p < 0.5 ? nx >= q * ill : nx <= -Math.cos(2 * Math.PI * (1 - L.p)) * ill;
                    this._rect(lx + i * 4, ly + j * 4, 4, 4, lit ? '#ef4444' : '#16080e');
                }
            }
            this._t(b.x + b.w - 52, b.y + 40, 'LUNA ' + Math.round(L.age) + 'D', {fam: MONO, px: 10, col: PAL.dim, w: 52, align: 'center'});
            y += 130;

            if (this.colapsado) return;

            // ===== 2. FORJAS DE BARAD-DÛR (CPU, RAM, TEMPERATURA Y PODER OSCURO) - Clic abre htop
            b = this._cardMordor(y, 206, '🔥', 'FORJAS [MONITOR HTOP]', d.up ? 'UP ' + durac(d.up) : '', 1);
            let fy = b.y;

            // CPU - Núcleos incandescentes
            this._etq(b.x, fy, 'CPU');
            this._barraLava(b.x + 34, fy + 2, 160, d.cpu);
            this._val(b.x + 200, fy - 1, Math.round(d.cpu) + '% ' + (d.nuc ?? '') + 'c', {col: PAL.gold, w: 100, align: 'right'});
            fy += 22;

            // RAM - Magma acumulado
            this._etq(b.x, fy, 'RAM');
            this._barraLava(b.x + 34, fy + 2, 160, d.ram?.pct ?? 0);
            this._val(b.x + 200, fy - 1, (d.ram?.usado ?? 0) + '/' + Math.round(d.ram?.total ?? 0) + 'G', {col: PAL.red, w: 100, align: 'right'});
            fy += 22;

            // Medidor del Poder de Sauron (Corrupción del Anillo)
            const poderSauron = Math.min(100, Math.max(12, Math.round(d.cpu * 0.45 + (d.ram?.pct ?? 0) * 0.35 + ((d.temp ?? 40) - 35) * 0.6)));
            this._etq(b.x, fy, 'PODER');
            this._barraLava(b.x + 46, fy + 2, 148, poderSauron);
            this._val(b.x + 200, fy - 1, poderSauron + '% FORJA', {col: poderSauron > 65 ? PAL.red : PAL.gold, w: 100, align: 'right'});
            fy += 22;

            // Sensores térmicos
            let rx = b.x;
            rx += this._etq(rx, fy + 2, 'TMP') + 4;
            rx += this._val(rx, fy + 2, (d.temp ? d.temp.toFixed(0) : '--') + '°C', {col: PAL.lava}) + 14;
            rx += this._etq(rx, fy + 2, 'DISCO') + 4;
            rx += this._val(rx, fy + 2, Math.round(d.disco ?? 0) + '%', {col: PAL.gold}) + 14;
            this._pares(rx, fy + 2, [['CARGA', (d.load?.[0] ?? 0).toFixed(2), PAL.text]], 6);
            fy += 26;

            // Historial de actividad de las forjas
            this._spark(b.x, fy, b.w, 24, this.cpuH, 56, Math.max(12, ...this.cpuH, 0), PAL.red);
            fy += 30;

            const topProc = d.top?.length ? d.top[0][0].substring(0, 10) : '--';
            const isHigh = (d.cpu > 55);
            this._pares(b.x, fy, [
                ['PROCESO', topProc, isHigh ? PAL.hot : PAL.gold],
                ['ORDEN', isHigh ? '¡AMENAZA!' : 'SAURON', isHigh ? PAL.red : PAL.lava]
            ], 16);
            y += 214;

            // ===== 3. HUESTES & RED DE MORDOR - Clic abre Configuración Red
            b = this._cardMordor(y, 194, '⚔', 'HUESTES · RED', net.iface ?? 'sin enlace', 2);
            fy = b.y;
            for (let i = 0; i < 4; i++) {
                const on = net.senal !== null && net.senal !== undefined && net.senal >= (i + 1) * 25 - 10;
                const bh = 3 + i * 3;
                this._rect(b.x + i * 4, fy + 14 - bh, 3, bh, on ? PAL.red : PAL.track);
            }
            this._t(b.x + 24, fy, net.ssid ?? (net.iface ? 'cableado' : '--'), {px: 13, col: PAL.text});
            fy += 19;
            this._pares(b.x, fy, [['IP', net.ip ?? '--', PAL.lava], ['GW', net.gw ?? '--']]);
            fy += 19;
            const vpn = net.vpn ?? {};
            this._rect(b.x, fy + 3, 9, 9, vpn.on ? PAL.red : PAL.faint);
            this._etq(b.x + 17, fy + 2, 'SOMBRA');
            this._val(b.x + 72, fy, vpn.on ? `${vpn.iface} ACTIVA` : 'sin velo', {col: vpn.on ? PAL.red : PAL.dim});
            fy += 19;
            this._val(b.x, fy, '↓ ' + tasa(net.rx ?? 0), {col: PAL.lava});
            this._val(b.x, fy + 15, '↑ ' + tasa(net.tx ?? 0), {col: PAL.gold});
            this._spark(b.x + 102, fy, 200, 28, this.rxH, 40, Math.max(20000, ...this.rxH, 0), PAL.red);
            fy += 36;
            this._pares(b.x, y + 194 - 11 - 16, [['ENLACES', String(s.est ?? 0)], ['HUESTES', (s.vecinos ?? 0) + ' orcos'], ['DNS', s.dns ?? '--']]);
            y += 204;

            // ===== 4. ARMERÍA & REPOSITORIOS - Clic abre Archivos en $HOME
            const repos = s.repos ?? [];
            const hDev = 110 + Math.max(0, repos.length - 1) * 17;
            b = this._cardMordor(y, hDev, '💍', 'ARMERÍA [ARCHIVOS]', s.kernel ? 'KERNEL ' + s.kernel : '', 3);
            fy = b.y;

            this._val(b.x, fy + 2, 'El Anillo Único · Grond · Maza de Sauron', {col: PAL.gold});
            fy += 24;

            for (const r of repos) {
                this._rect(b.x, fy + 5, 8, 8, r.sucio > 0 ? PAL.red : PAL.gold);
                let x_r = b.x + 16;
                x_r += this._val(x_r, fy, r.n.substring(0, 14)) + 8;
                x_r += this._val(x_r, fy, r.b, {col: PAL.lava}) + 8;
                this._val(x_r, fy, (r.sucio ? '~' + r.sucio : '') + (r.adelante ? ' ↑' + r.adelante : ''), {col: PAL.gold});
                fy += 17;
            }
            const tc = s.tc ?? {};
            this._pares(b.x, fy, [['PY', tc.py ?? '—'], ['NODE', tc.node ?? '—'], ['RUST', tc.rust ?? '—']], 12);
            fy += 17;
            this._pares(b.x, fy, [['DEFENSA', s.fallos > 0 ? `${s.fallos} ALERTA` : 'GUARDIA DE MORGUL', s.fallos > 0 ? PAL.red : PAL.lava]], 10);
            y += hDev + 10;

            // ===== 5. CITAS DEL ANILLO Y SAURON - Clic cicla citas
            const cita = CITAS_MORDOR[this.citaIdx];
            b = this._cardMordor(y, 96, '★', `${cita.tit} [CAMBIAR]`, cita.au, 4);
            this._t(b.x, b.y + 4, cita.es, {px: 12, col: PAL.gold, w: b.w, wrap: true});
        } catch (e) {
            logError(e, 'PixelZen Mordor HUD');
        } finally {
            cr.$dispose();
            this.cr = null;
        }
    }

    destroy() {
        this._cancel.cancel();
        for (const t of this._timers) GLib.source_remove(t);
        this._timers = [];
        this.actor.destroy();
    }
}
