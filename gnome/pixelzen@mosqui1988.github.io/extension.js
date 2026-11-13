// PixelZen para GNOME Shell: fondo pixel art animado de Mordor + panel de datos interactivo.
// Tema The Lord of the Rings: Mordor.

import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import Clutter from 'gi://Clutter';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

import {Escena} from './escena.js';
import {Hud} from './hud.js';

export default class PixelZenExtension extends Extension {
    async enable() {
        this._settings = this.getSettings();
        this._ids = [];
        this._grupo = Main.layoutManager._backgroundGroup;

        // Contenedor interactivo para capturar clics en el HUD y en la escena
        this._raiz = new Clutter.Actor({reactive: true});
        this._grupo.add_child(this._raiz);

        try {
            const [escenaMod, hudMod] = await Promise.all([
                import(`file://${this.path}/escena.js?v=${Date.now()}`),
                import(`file://${this.path}/hud.js?v=${Date.now()}`)
            ]);
            this._EscenaClass = escenaMod.Escena;
            this._HudClass = hudMod.Hud;
            this._escena = new this._EscenaClass(this.path, this._raiz, this._settings);
        } catch (e) {
            try {
                this._escena = new Escena(this.path, this._raiz, this._settings);
            } catch (err) {
                logError(err, 'PixelZen Mordor: error al cargar escena');
                this._escena = null;
            }
        }
        this._hud = null;
        this._btnPanel = null;

        // Menú temático en la barra superior
        this._creaBotonPanel();

        this._construye();
        this._ubicacion();
        this._timerUbi = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 1800, () => {
            this._ubicacion();
            return GLib.SOURCE_CONTINUE;
        });

        const con = (obj, sig, fn) => this._ids.push([obj, obj.connect(sig, fn)]);
        con(Main.layoutManager, 'monitors-changed', () => this._construye());
        con(global.display, 'workareas-changed', () => this._colocaHud());
        con(this._grupo, 'child-added', (_g, hijo) => {
            if (hijo !== this._raiz) this._grupo.set_child_above_sibling(this._raiz, null);
        });
        con(global.display, 'in-fullscreen-changed', () => this._actualizaPausa());
        con(Main.sessionMode, 'updated', () => this._actualizaPausa());
        con(this._settings, 'changed', (_s, clave) => {
            if (clave === 'hud' || clave === 'hud-monitor' || clave === 'todos-monitores') this._construye();
            else this._escena?.ajustesCambiados();
        });
        this._actualizaPausa();
    }

    _creaBotonPanel() {
        try {
            this._btnPanel = new PanelMenu.Button(0.0, 'PixelZenMordorHUD', false);
            const box = new St.BoxLayout({style_class: 'panel-status-indicators-box'});
            const lbl = new St.Label({
                text: '👁 Mordor',
                y_align: Clutter.ActorAlign.CENTER,
                style: 'font-weight: bold; color: #ef4444;'
            });
            box.add_child(lbl);
            this._btnPanel.add_child(box);

            // Menú desplegable interactivo de Mordor
            const menu = this._btnPanel.menu;

            // Encabezado
            const headerItem = new PopupMenu.PopupMenuItem('🌋 Tierra de Mordor · LOTR', {reactive: false});
            menu.addMenuItem(headerItem);

            menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

            // Alternar HUD
            const itemHud = new PopupMenu.PopupSwitchMenuItem('Panel HUD (Sistema)', this._settings.get_boolean('hud'));
            itemHud.connect('toggled', (item, state) => {
                this._settings.set_boolean('hud', state);
            });
            menu.addMenuItem(itemHud);

            // Alternar Efectos de Sonido
            const itemSonido = new PopupMenu.PopupSwitchMenuItem('🔊 Efectos de Sonido', true);
            itemSonido.connect('toggled', (item, state) => {
                if (this._escena) this._escena.sonidoActivo = state;
                if (this._hud) this._hud.sonidoActivo = state;
            });
            menu.addMenuItem(itemSonido);

            // Alternar Lluvia de Ceniza Volcánica
            const itemCeniza = new PopupMenu.PopupSwitchMenuItem('🌫️ Lluvia de Ceniza', true);
            itemCeniza.connect('toggled', (item, state) => {
                if (this._escena) {
                    this._escena.lluviaCeniza = state;
                    this._escena.pinta();
                }
            });
            menu.addMenuItem(itemCeniza);

            // Alternar Eco Sísmico Continuo (Ambiente)
            const itemAmbiente = new PopupMenu.PopupSwitchMenuItem('🌋 Eco Sísmico Continuo', false);
            itemAmbiente.connect('toggled', (item, state) => {
                this._escena?.setAmbiente(state);
            });
            menu.addMenuItem(itemAmbiente);

            // Alternar Runas del Anillo sobre Barad-dûr
            const itemRunas = new PopupMenu.PopupSwitchMenuItem('📜 Runas sobre Barad-dûr', true);
            itemRunas.connect('toggled', (item, state) => {
                if (this._escena) {
                    this._escena.runasTorre = state;
                    this._escena.pinta();
                }
            });
            menu.addMenuItem(itemRunas);

            menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

            // Acciones cinematográficas manuales
            const itemErupcion = new PopupMenu.PopupMenuItem('🔥 Desatar Erupción de Orodruin');
            itemErupcion.connect('activate', () => {
                this._escena?.desataErupcion();
            });
            menu.addMenuItem(itemErupcion);

            const itemColera = new PopupMenu.PopupMenuItem('👁 Cólera del Gran Ojo (Onda Ígnea)');
            itemColera.connect('activate', () => {
                this._escena?.desataColera();
            });
            menu.addMenuItem(itemColera);

            const itemRelampago = new PopupMenu.PopupMenuItem('⚡ Tormenta y Relámpago Carmesí');
            itemRelampago.connect('activate', () => {
                this._escena?.fuerzaRelampago();
            });
            menu.addMenuItem(itemRelampago);

            const itemNazgul = new PopupMenu.PopupMenuItem('🦅 Chillido y Picado del Nazgûl');
            itemNazgul.connect('activate', () => {
                this._escena?.desataNazgul();
            });
            menu.addMenuItem(itemNazgul);

            const itemHobbits = new PopupMenu.PopupMenuItem('💍 Resplandor de Galadriel (Frodo & Sam)');
            itemHobbits.connect('activate', () => {
                this._escena?.desataHobbits();
            });
            menu.addMenuItem(itemHobbits);

            const itemCita = new PopupMenu.PopupMenuItem('📜 Cambiar Cita del Anillo');
            itemCita.connect('activate', () => {
                this._hud?.cambiaCita();
            });
            menu.addMenuItem(itemCita);

            menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

            // Selector del ciclo solar de Mordor
            const timeHeader = new PopupMenu.PopupMenuItem('⏰ Control del Ciclo Solar', {reactive: false});
            menu.addMenuItem(timeHeader);

            const itemHoraReal = new PopupMenu.PopupMenuItem('⏱️ Hora Real Automática (Reloj)');
            itemHoraReal.connect('activate', () => {
                this._settings.set_double('hora-simulada', -1.0);
                this._settings.set_boolean('ciclo-rapido', false);
            });
            menu.addMenuItem(itemHoraReal);

            const itemDia = new PopupMenu.PopupMenuItem('☀️ Probar Modo Día (Cénit de Ceniza)');
            itemDia.connect('activate', () => {
                this._settings.set_boolean('ciclo-rapido', false);
                this._settings.set_double('hora-simulada', 13.5);
            });
            menu.addMenuItem(itemDia);

            const itemDorado = new PopupMenu.PopupMenuItem('🌅 Probar Hora de Sangre (Atardecer)');
            itemDorado.connect('activate', () => {
                this._settings.set_boolean('ciclo-rapido', false);
                this._settings.set_double('hora-simulada', 18.0);
            });
            menu.addMenuItem(itemDorado);

            const itemNoche = new PopupMenu.PopupMenuItem('🌑 Probar Modo Noche (Sombras)');
            itemNoche.connect('activate', () => {
                this._settings.set_boolean('ciclo-rapido', false);
                this._settings.set_double('hora-simulada', 23.0);
            });
            menu.addMenuItem(itemNoche);

            const itemDemo = new PopupMenu.PopupMenuItem('⚡ Demostración Rápida (24h en 90s)');
            itemDemo.connect('activate', () => {
                this._settings.set_double('hora-simulada', -1.0);
                this._settings.set_boolean('ciclo-rapido', true);
            });
            menu.addMenuItem(itemDemo);

            Main.panel.addToStatusArea('pixelzen-hud-toggle', this._btnPanel, 1, 'right');
        } catch (e) {
            logError(e, 'PixelZen Mordor: error al crear boton en panel');
        }
    }

    _monitores() {
        const lm = Main.layoutManager;
        return this._settings.get_boolean('todos-monitores') ? lm.monitors : [lm.primaryMonitor];
    }

    _construye() {
        this._escena?.construye(this._monitores().filter(Boolean));
        this._grupo.set_child_above_sibling(this._raiz, null);

        const quiereHud = this._settings.get_boolean('hud');
        if (quiereHud && !this._hud) {
            const HClass = this._HudClass || Hud;
            this._hud = new HClass(this.path);
            this._raiz.add_child(this._hud.actor);
        } else if (!quiereHud && this._hud) {
            this._hud.destroy();
            this._hud = null;
        }
        if (this._hud) {
            this._raiz.set_child_above_sibling(this._hud.actor, null);
            this._colocaHud();
        }
    }

    _colocaHud() {
        if (!this._hud) return;
        const lm = Main.layoutManager;
        let i = this._settings.get_int('hud-monitor');
        if (i < 0 || i >= lm.monitors.length) i = lm.primaryIndex;
        this._hud.coloca(lm.getWorkAreaForMonitor(i));
    }

    _actualizaPausa() {
        const bloqueada = Main.sessionMode.isLocked || Main.sessionMode.isGreeter;
        const lm = Main.layoutManager;
        const completa = lm.primaryIndex >= 0 && global.display.get_monitor_in_fullscreen(lm.primaryIndex);
        this._escena?.pausa(bloqueada || completa);
    }

    _ubicacion() {
        if (!this._escena) return;
        try {
            const p = Gio.Subprocess.new(['python3', '-I', `${this.path}/code/ubicacion.py`],
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE);
            p.communicate_utf8_async(null, null, (proc, res) => {
                try {
                    const [, out] = proc.communicate_utf8_finish(res);
                    const r = JSON.parse(out);
                    this._escena?.ponUbicacion(r.lat, r.lon);
                } catch (e) {}
            });
        } catch (e) {}
    }

    disable() {
        for (const [obj, id] of this._ids) obj.disconnect(id);
        this._ids = [];
        if (this._timerUbi) GLib.source_remove(this._timerUbi);
        this._timerUbi = 0;
        this._btnPanel?.destroy();
        this._hud?.destroy();
        this._escena?.destroy();
        this._raiz?.destroy();
        this._grupo = null;
    }
}
