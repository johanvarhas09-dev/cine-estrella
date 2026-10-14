"""
Base común de las ventanas de trabajo (Boletería, Confitería, ...).

Una pantalla fija (sin scroll): un Canvas con el fondo de ./fondos, paneles de
vidrio y el contenido dibujado encima. El fondo se actualiza solo si cambias el archivo.

Cada ventana define: W, H, NOMBRE_FONDO y PANELES (cajas de vidrio), y al terminar de
dibujar llama a self.iniciar_fondo().
"""
import tkinter as tk

from ui import fondos
from ui.componentes import BotonCanvas, rect_redondeado
from ui.estilos import COLORS, FONTS, FUENTE, RUTA_FONDOS

if fondos.HAY_PIL:
    from PIL import Image, ImageTk

EMOJI = 'Segoe UI Emoji'


class VentanaBase(tk.Toplevel):
    W, H = 1240, 700
    NOMBRE_FONDO = 'fondo_principal'
    PANELES = []                      # [(x0, y0, x1, y1), ...]

    def __init__(self, parent, titulo):
        super().__init__(parent)
        self.parent = parent
        self.title(titulo)
        x = max(0, (self.winfo_screenwidth() - self.W) // 2)
        y = max(0, (self.winfo_screenheight() - self.H) // 3)
        self.geometry(f'{self.W}x{self.H}+{x}+{y}')
        self.resizable(False, False)
        self.configure(bg=COLORS['bg_main'])
        self.canvas = tk.Canvas(self, width=self.W, height=self.H, bg=COLORS['bg_main'],
                                highlightthickness=0, bd=0)
        self.canvas.pack()
        self._img_id = self.canvas.create_image(0, 0, anchor='nw')
        self._escena = self._foto = self.vigia = None
        self.bind('<Destroy>', self._al_destruir)

    # ── Ayudas de dibujo ─────────────────────────────────────────────────────

    def texto(self, x, y, txt, fuente='body', color=None, anchor='w', **kw):
        f = FONTS[fuente] if isinstance(fuente, str) else fuente
        return self.canvas.create_text(x, y, text=txt, font=f, anchor=anchor,
                                       fill=color or COLORS['text_white'], **kw)

    def boton(self, x, y, w, h, texto, cmd, estilo='primario', fuente=None, grupo=None, radio=12):
        return BotonCanvas(self.canvas, x, y, w, h, texto, cmd, estilo, fuente, radio, grupo)

    def tarjeta(self, x0, y0, x1, y1, radio=14, fill=None, grupo=None):
        return rect_redondeado(self.canvas, x0, y0, x1, y1, radio, fill=fill or COLORS['bg_card'],
                               outline=COLORS['border'], width=1, tags=(grupo,) if grupo else ())

    # ── Fondo dinámico ───────────────────────────────────────────────────────

    def iniciar_fondo(self):
        """Llamar al terminar de dibujar el contenido."""
        fondos.asegurar_fondos(RUTA_FONDOS)
        if not fondos.HAY_PIL:                       # sin Pillow: paneles sólidos
            for caja in self.PANELES:
                r = rect_redondeado(self.canvas, *caja, 20, fill=COLORS['bg_panel'], outline=COLORS['border'])
                self.canvas.tag_lower(r)
        self._refrescar_fondo()
        self.vigia = fondos.FondoDinamico(self, RUTA_FONDOS, self.NOMBRE_FONDO, self._refrescar_fondo)
        self.vigia.iniciar()

    def _al_destruir(self, ev):
        if ev.widget is self and self.vigia:
            self.vigia.detener()
            self.vigia = None

    def _componer(self):
        base = fondos.cargar_fondo(RUTA_FONDOS, self.NOMBRE_FONDO, self.W, self.H, oscurecer=0.15)
        for x0, y0, x1, y1 in self.PANELES:
            fondos.panel_vidrio(base, (x0, y0, x1, y1), radio=min(22, (y1 - y0) // 2),
                                tinte=(26, 5, 14), opacidad=0.62)
        return base

    def _mostrar(self, img):
        self._foto = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self._img_id, image=self._foto)

    def _refrescar_fondo(self):
        if not fondos.HAY_PIL:
            return
        nueva = self._componer()
        vieja, self._escena = self._escena, nueva
        if vieja is None:
            self._mostrar(nueva)
        else:
            self._fundir(vieja, nueva, 1)

    def _fundir(self, vieja, nueva, paso, pasos=10):
        if self.vigia is None:                       # la ventana se cerró durante la transición
            return
        self._mostrar(Image.blend(vieja, nueva, paso / pasos))
        if paso < pasos:
            self.after(30, self._fundir, vieja, nueva, paso + 1)
