import time
import tkinter as tk

from ui.estilos import COLORS, FONTS, RUTA_FONDOS
from ui.componentes import BotonCanvas, rect_redondeado
from ui import fondos

if fondos.HAY_PIL:
    from PIL import Image, ImageTk


class VentanaPrincipal(tk.Tk):
    """Ventana principal: pantalla fija (sin scroll) para elegir el módulo del sistema.

    Fondo: ./fondos/fondo_principal.jpg  (si lo reemplazas, cambia solo, sin reiniciar).
    Atajos de teclado: 1 = Administración, 2 = Boletería, 3 = Confitería.
    """

    W, H = 1100, 680
    NOMBRE_FONDO = 'fondo_principal'

    def __init__(self):
        super().__init__()
        self.title('CINE ESTRELLA – Sistema de Venta')
        x, y = (self.winfo_screenwidth() - self.W) // 2, (self.winfo_screenheight() - self.H) // 3
        self.geometry(f'{self.W}x{self.H}+{max(0, x)}+{max(0, y)}')
        self.resizable(False, False)
        self.configure(bg=COLORS['bg_main'])

        self._escena = None          # imagen PIL actual (fondo + paneles de vidrio)
        self._foto = None            # referencia para que Tk no la borre
        self._hover = -1
        self._focos = []
        self._encendido = True

        self.canvas = tk.Canvas(self, width=self.W, height=self.H, bg=COLORS['bg_main'],
                                highlightthickness=0, bd=0)
        self.canvas.pack()
        self._build()

        fondos.asegurar_fondos(RUTA_FONDOS)
        self._refrescar_fondo()
        self.vigia = fondos.FondoDinamico(self, RUTA_FONDOS, self.NOMBRE_FONDO,
                                          self._refrescar_fondo)
        self.vigia.iniciar()

        self.canvas.bind('<Motion>', self._mover)
        self.canvas.bind('<Leave>', lambda e: self._resaltar(-1))
        for tecla, accion in (('1', self._open_admin), ('2', self._open_boleteria),
                              ('3', self._open_dulceria)):
            self.bind(tecla, lambda e, a=accion: a())
        self._reloj()
        self._parpadeo()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        W, H = self.W, self.H
        self._img_id = self.canvas.create_image(0, 0, anchor='nw')
        self._marquesina()
        self._tarjetas()
        self.canvas.create_text(W // 2, H - 26, fill=COLORS['text_muted'], font=FONTS['small'],
                                text='INACAP  ·  Programación Orientada a Objetos Segura  ·  2026')

    def _marquesina(self):
        c, W = self.canvas, self.W
        for x in range(30, W - 10, 34):                       # foquitos de marquesina
            self._focos.append(c.create_oval(x - 5, 18, x + 5, 28, fill='#ffd700', outline=''))
        c.create_text(W // 2 + 2, 74, text='★  CINE ESTRELLA  ★', fill='#000000',
                      font=FONTS['hero'])                      # sombra del título
        c.create_text(W // 2, 72, text='★  CINE ESTRELLA  ★', fill=COLORS['accent_gold'],
                      font=FONTS['hero'])
        c.create_text(W // 2, 118, text='Sistema Integrado de Venta de Entradas y Confitería',
                      fill=COLORS['text_light'], font=FONTS['subtitle'])
        self._lbl_reloj = c.create_text(W - 34, 72, anchor='e', text='',
                                        fill=COLORS['gold_soft'], font=FONTS['clock'])

    def _tarjetas(self):
        c = self.canvas
        margen, sep, y0, alto = 48, 28, 168, 400
        ancho = (self.W - 2 * margen - 2 * sep) // 3
        defs = [
            ('⚙️', 'ADMINISTRACIÓN', 'Películas · Funciones · Productos\nTrabajadores · Reportes\nTipo de cambio USD',
             self._open_admin, 'dorado', '1'),
            ('🎟️', 'BOLETERÍA', 'Venta de entradas\nMapa de asientos\nControl de edad y cupos',
             self._open_boleteria, 'primario', '2'),
            ('🍿', 'CONFITERÍA', 'Venta de snacks y bebidas\nCombos y productos importados\nPrecios en CLP automáticos',
             self._open_dulceria, 'primario', '3'),
        ]
        self._cajas, self._bordes = [], []
        for i, (icono, titulo, desc, cmd, estilo, atajo) in enumerate(defs):
            x0 = margen + i * (ancho + sep)
            caja = (x0, y0, x0 + ancho, y0 + alto)
            self._cajas.append(caja)
            cx = x0 + ancho // 2
            if not fondos.HAY_PIL:                             # sin Pillow: tarjeta sólida
                rect_redondeado(c, *caja, 24, fill=COLORS['bg_card'], outline='')
            self._bordes.append(rect_redondeado(c, *caja, 24, fill='', outline=COLORS['border'],
                                                width=1))
            c.create_text(cx, y0 + 74, text=icono, font=FONTS['emoji'])
            c.create_text(cx, y0 + 152, text=titulo, font=FONTS['card_title'],
                          fill=COLORS['accent_gold'])
            c.create_line(cx - 30, y0 + 180, cx + 30, y0 + 180, fill=COLORS['accent_gold_dark'],
                          width=2)
            c.create_text(cx, y0 + 202, text=desc, font=FONTS['card_desc'], justify='center',
                          fill=COLORS['text_light'], anchor='n', width=ancho - 40)
            BotonCanvas(c, x0 + 28, y0 + alto - 92, ancho - 56, 52, 'INGRESAR  ▶', cmd, estilo)
            c.create_text(cx, y0 + alto - 24, text=f'Atajo: tecla {atajo}',
                          font=FONTS['small'], fill=COLORS['text_muted'])

    # ── Fondo dinámico ───────────────────────────────────────────────────────

    def _componer(self):
        base = fondos.cargar_fondo(RUTA_FONDOS, self.NOMBRE_FONDO, self.W, self.H, oscurecer=0.15)
        for caja in self._cajas:
            fondos.panel_vidrio(base, caja, tinte=(26, 5, 14), opacidad=0.58)
        return base

    def _mostrar(self, img):
        self._foto = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self._img_id, image=self._foto)

    def _refrescar_fondo(self):
        """Lee el archivo de ./fondos y lo muestra (con transición si ya había uno)."""
        if not fondos.HAY_PIL:
            return
        nueva = self._componer()
        if self._escena is None:
            self._escena = nueva
            self._mostrar(nueva)
        else:
            vieja, self._escena = self._escena, nueva
            self._fundir(vieja, nueva, 1)

    def _fundir(self, vieja, nueva, paso, pasos=10):
        self._mostrar(Image.blend(vieja, nueva, paso / pasos))
        if paso < pasos:
            self.after(30, self._fundir, vieja, nueva, paso + 1)

    # ── Detalles animados ────────────────────────────────────────────────────

    def _mover(self, ev):
        self._resaltar(next((i for i, (a, b, c2, d) in enumerate(self._cajas)
                             if a <= ev.x <= c2 and b <= ev.y <= d), -1))

    def _resaltar(self, idx):
        if idx == self._hover:
            return
        self._hover = idx
        for i, b in enumerate(self._bordes):
            self.canvas.itemconfig(b, outline=COLORS['accent_gold'] if i == idx else COLORS['border'],
                                   width=2 if i == idx else 1)

    def _reloj(self):
        self.canvas.itemconfig(self._lbl_reloj, text=time.strftime('%H:%M'))
        self.after(10000, self._reloj)

    def _parpadeo(self):
        self._encendido = not self._encendido
        for i, f in enumerate(self._focos):
            self.canvas.itemconfig(f, fill='#ffd700' if (i % 2 == 0) == self._encendido else '#7a5a00')
        self.after(700, self._parpadeo)

    # ── Navigation ────────────────────────────────────────────────────────────

    def _open_admin(self):
        from ui.ventana_admin import VentanaAdmin
        self.withdraw()
        win = VentanaAdmin(self)
        win.protocol('WM_DELETE_WINDOW', lambda: self._return(win))

    def _open_boleteria(self):
        from ui.ventana_boleteria import VentanaBoleteria
        self.withdraw()
        win = VentanaBoleteria(self)
        win.protocol('WM_DELETE_WINDOW', lambda: self._return(win))

    def _open_dulceria(self):
        from ui.ventana_dulceria import VentanaDulceria
        self.withdraw()
        win = VentanaDulceria(self)
        win.protocol('WM_DELETE_WINDOW', lambda: self._return(win))

    def _return(self, win):
        win.destroy()
        self.deiconify()
