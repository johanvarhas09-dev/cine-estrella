"""
Componentes visuales reutilizables de CINE ESTRELLA (solo apariencia).

- rect_redondeado : rectángulo con esquinas redondeadas en un Canvas.
- BotonCanvas     : botón moderno dibujado dentro de un Canvas existente (sobre fondos con imagen).
- BotonModerno    : el mismo botón como widget independiente, para usar en cualquier Frame.

Estilos de botón: 'primario' (rojo), 'dorado', 'exito' (verde), 'fantasma', 'peligro'.
"""
import tkinter as tk
from ui.estilos import COLORS, FONTS


def _rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mezclar(c1, c2, t):
    """Color intermedio entre c1 y c2 (t de 0 a 1), en formato #rrggbb."""
    a, b = _rgb(c1), _rgb(c2)
    return '#%02x%02x%02x' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rect_redondeado(canvas, x0, y0, x1, y1, r, **kw):
    r = min(r, (x1 - x0) // 2, (y1 - y0) // 2)
    pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1,
           x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return canvas.create_polygon(pts, smooth=True, **kw)


ESTILOS_BOTON = {
    'primario': dict(base='#b30000', hover='#e10613', texto='#ffffff', borde='#ff6b6b'),
    'dorado':   dict(base='#c8a200', hover='#ffd700', texto='#1a0a00', borde='#fff0a0'),
    'exito':    dict(base='#00802b', hover='#00a337', texto='#ffffff', borde='#5df08e'),
    'fantasma': dict(base='#2a0d14', hover='#471822', texto='#f0e6e6', borde='#7a2a3a'),
    'peligro':  dict(base='#5a0a0a', hover='#a31212', texto='#ffffff', borde='#ff6b6b'),
}


class BotonCanvas:
    """Botón redondeado con efecto hover suave y de pulsación, dentro de un Canvas."""

    def __init__(self, canvas, x, y, w, h, texto, comando, estilo='primario',
                 fuente=None, radio=14, grupo=None):
        self.c, self.comando, self.est = canvas, comando, ESTILOS_BOTON[estilo]
        self.habilitado, self._t, self._meta, self._job = True, 0.0, 0.0, None
        tag = f'btn{id(self)}'
        tags = (tag, grupo) if grupo else (tag,)
        self.cuerpo = rect_redondeado(canvas, x, y, x + w, y + h, radio,
                                      fill=self.est['base'], outline=self.est['borde'],
                                      width=1, tags=tags)
        self.brillo = canvas.create_line(x + radio, y + 2, x + w - radio, y + 2,
                                         fill=mezclar(self.est['base'], '#ffffff', 0.35),
                                         tags=tags)
        self.texto = canvas.create_text(x + w / 2, y + h / 2, text=texto, tags=tags,
                                        fill=self.est['texto'], font=fuente or FONTS['btn_big'])
        canvas.tag_bind(tag, '<Enter>', lambda e: self._ir(1.0, 'hand2'))
        canvas.tag_bind(tag, '<Leave>', lambda e: self._ir(0.0, ''))
        canvas.tag_bind(tag, '<ButtonPress-1>', lambda e: self._pulsar(True))
        canvas.tag_bind(tag, '<ButtonRelease-1>', self._soltar)

    def _ir(self, meta, cursor):
        if not self.habilitado:
            return
        self.c.configure(cursor=cursor)
        self._meta = meta
        if self._job is None:
            self._paso()

    def _paso(self):
        self._t += 0.34 if self._meta > self._t else -0.34
        self._t = min(1.0, max(0.0, self._t))
        self.c.itemconfig(self.cuerpo, fill=mezclar(self.est['base'], self.est['hover'], self._t))
        self._job = self.c.after(16, self._paso) if abs(self._t - self._meta) > 0.01 else None

    def _pulsar(self, abajo):
        if self.habilitado:
            self.c.itemconfig(self.cuerpo,
                              fill=mezclar(self.est['base'], '#000000', 0.25) if abajo
                              else mezclar(self.est['base'], self.est['hover'], self._t))

    def _soltar(self, ev):
        self._pulsar(False)
        x0, y0, x1, y1 = self.c.bbox(self.cuerpo)
        if self.habilitado and x0 <= self.c.canvasx(ev.x) <= x1 and y0 <= self.c.canvasy(ev.y) <= y1:
            self.comando()

    def configurar(self, texto=None, habilitado=None):
        if texto is not None:
            self.c.itemconfig(self.texto, text=texto)
        if habilitado is not None:
            self.habilitado = habilitado
            self.c.itemconfig(self.cuerpo, fill=self.est['base'] if habilitado else '#3a2a2d')
            self.c.itemconfig(self.texto, fill=self.est['texto'] if habilitado else '#8a7a7d')


class BotonModerno(tk.Canvas):
    """Botón moderno como widget independiente: BotonModerno(frame, 'GUARDAR', cmd, 'exito')."""

    def __init__(self, master, texto, comando, estilo='primario', ancho=180, alto=46,
                 fondo=None, fuente=None, **kw):
        try:
            fondo = fondo or master.cget('bg')
        except tk.TclError:
            fondo = COLORS['bg_main']
        super().__init__(master, width=ancho, height=alto, bg=fondo,
                         highlightthickness=0, bd=0, **kw)
        self.boton = BotonCanvas(self, 1, 1, ancho - 3, alto - 3, texto, comando, estilo, fuente)

    def configurar(self, **kw):
        self.boton.configurar(**kw)
