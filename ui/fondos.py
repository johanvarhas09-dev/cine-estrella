"""
Fondos de pantalla dinámicos para CINE ESTRELLA.

- Lee la imagen desde ./fondos/ (por ejemplo fondo_principal.jpg).
- Si reemplazas el archivo, la ventana lo detecta sola y cambia con transición.
- Si falta la imagen, genera un fondo cinematográfico en memoria (nunca falla).
- Este módulo NO usa tkinter: solo Pillow y pathlib.
"""
import random
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageChops
    HAY_PIL = True
except ImportError:          # el sistema sigue funcionando sin imagen de fondo
    HAY_PIL = False

EXTENSIONES = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')

# nombre de archivo -> (color base, color de luz)
TONOS = {
    'fondo_principal':  ((74, 8, 26),  (255, 196, 80)),
    'fondo_boleteria':  ((58, 6, 20),  (255, 96, 96)),
    'fondo_confiteria': ((70, 30, 6),  (255, 170, 40)),
    'fondo_admin':      ((14, 22, 48), (110, 160, 255)),
}


def buscar_fondo(carpeta: Path, nombre: str):
    """Busca <nombre>.<ext>; si no existe, usa el genérico fondo.<ext>."""
    for base in (nombre, 'fondo'):
        for ext in EXTENSIONES:
            ruta = Path(carpeta) / (base + ext)
            if ruta.is_file():
                return ruta
    return None


def _cubrir(img, w, h):
    """Escala y recorta la imagen para llenar w x h sin deformarla."""
    esc = max(w / img.width, h / img.height)
    nueva = img.resize((max(w, round(img.width * esc)), max(h, round(img.height * esc))),
                       Image.LANCZOS)
    x, y = (nueva.width - w) // 2, (nueva.height - h) // 2
    return nueva.crop((x, y, x + w, y + h))


def generar_fondo(w, h, color, luz, semilla=7):
    """Fondo cinematográfico: degradado vino, haces de luz, bokeh, viñeta y grano."""
    rnd = random.Random(semilla)
    base = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(base)
    for y in range(h):
        k = max(0.0, 1 - abs(y / (h - 1) - 0.36) / 0.64) ** 1.1
        d.line([(0, y), (w, y)], fill=tuple(min(255, int(6 + (c * 1.45 - 6) * k)) for c in color))

    mw, mh = w // 2, h // 2                       # capa de luz a media resolución
    capa = Image.new('RGB', (mw, mh), (0, 0, 0))
    dl = ImageDraw.Draw(capa)
    for dx, ancho, fuerza in ((-0.34, 0.09, 0.42), (0.0, 0.12, 0.52), (0.34, 0.09, 0.42)):
        cx = mw / 2 + dx * mw * 0.35
        pts = [(cx - 6, -10), (cx + 6, -10),
               (mw / 2 + dx * mw * 1.6 + ancho * mw, mh), (mw / 2 + dx * mw * 1.6 - ancho * mw, mh)]
        dl.polygon(pts, fill=tuple(int(c * fuerza) for c in luz))
    for _ in range(46):                           # bokeh
        r = rnd.randint(5, 30)
        x, y = rnd.randint(0, mw), int(rnd.random() ** 1.7 * mh)
        f = rnd.uniform(0.14, 0.42)
        dl.ellipse((x - r, y - r, x + r, y + r), fill=tuple(int(c * f) for c in luz))
    capa = capa.filter(ImageFilter.GaussianBlur(11)).resize((w, h), Image.BICUBIC)
    caida = ImageChops.invert(Image.linear_gradient('L')).resize((w, h)).point(lambda v: int(v ** 1.0 * 0.95)).convert('RGB')
    capa = ImageChops.multiply(capa, caida)                  # los haces se desvanecen hacia abajo
    base = ImageChops.add(base, capa)

    borde = Image.radial_gradient('L').resize((w, h)).point(lambda v: int(max(0, v - 120) * 1.1))
    base = Image.composite(Image.new('RGB', (w, h), (0, 0, 0)), base, borde)   # viñeta

    ruido = Image.effect_noise((w, h), 16).point(lambda v: 128 + int((v - 128) * 0.3)).convert('RGB')
    return ImageChops.add(base, ruido, 1.0, -128)                              # grano de película


def cargar_fondo(carpeta, nombre, w, h, oscurecer=0.22):
    """Devuelve un fondo RGB de w x h (archivo del disco o, si falla, uno generado)."""
    ruta = buscar_fondo(carpeta, nombre)
    img = None
    if ruta:
        try:
            img = Image.open(ruta)
            img.load()
            img = _cubrir(img.convert('RGB'), w, h)
        except Exception:                         # archivo a medio copiar o dañado
            img = None
    if img is None:
        img = generar_fondo(w, h, *TONOS.get(nombre, TONOS['fondo_principal']))
    if oscurecer:
        img = Image.blend(img, Image.new('RGB', img.size, (0, 0, 0)), oscurecer)
    return img


def asegurar_fondos(carpeta):
    """Si ./fondos/ no tiene imágenes, crea los 4 fondos por defecto."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    if not HAY_PIL or any(p.suffix.lower() in EXTENSIONES for p in carpeta.iterdir()):
        return
    for i, (nombre, (color, luz)) in enumerate(TONOS.items()):
        generar_fondo(1920, 1080, color, luz, semilla=7 + i).save(
            carpeta / f'{nombre}.jpg', quality=88)


def _mascara_redonda(w, h, radio, inset=0):
    """Máscara con bordes redondeados suavizados (supersampling x3)."""
    k = 3
    m = Image.new('L', (w * k, h * k), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        (inset * k, inset * k, w * k - 1 - inset * k, h * k - 1 - inset * k),
        radius=max(1, (radio - inset) * k), fill=255)
    return m.resize((w, h), Image.LANCZOS)


def panel_vidrio(base, caja, radio=24, tinte=(26, 5, 14), opacidad=0.58,
                 desenfoque=16, borde=(255, 215, 0), borde_alpha=70):
    """Panel de 'vidrio esmerilado' sobre la imagen: sombra + desenfoque + tinte + borde."""
    x0, y0, x1, y1 = caja
    w, h = x1 - x0, y1 - y0
    sombra = Image.new('L', base.size, 0)
    sombra.paste(_mascara_redonda(w, h, radio), (x0, y0 + 10))
    sombra = sombra.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.55))
    base.paste(Image.new('RGB', base.size, (0, 0, 0)), (0, 0), sombra)

    vidrio = base.crop(caja).filter(ImageFilter.GaussianBlur(desenfoque))
    vidrio = Image.blend(vidrio, Image.new('RGB', (w, h), tinte), opacidad)
    base.paste(vidrio, (x0, y0), _mascara_redonda(w, h, radio))

    anillo = ImageChops.subtract(_mascara_redonda(w, h, radio), _mascara_redonda(w, h, radio, 2))
    base.paste(Image.new('RGB', (w, h), borde), (x0, y0), anillo.point(lambda v: v * borde_alpha // 255))
    return base


class FondoDinamico:
    """Vigila el archivo de fondo y avisa (al_cambiar) cuando lo reemplazas."""

    def __init__(self, widget, carpeta, nombre, al_cambiar, intervalo_ms=1500):
        self.widget, self.carpeta, self.nombre = widget, Path(carpeta), nombre
        self.al_cambiar, self.intervalo = al_cambiar, intervalo_ms
        self._job = None
        self._sig = self._visto = self._firma()

    def _firma(self):
        ruta = buscar_fondo(self.carpeta, self.nombre)
        if not ruta:
            return None
        st = ruta.stat()
        return (str(ruta), st.st_mtime_ns, st.st_size)

    def iniciar(self):
        self._job = self.widget.after(self.intervalo, self._tick)

    def detener(self):
        if self._job:
            self.widget.after_cancel(self._job)
            self._job = None

    def _tick(self):
        try:
            f = self._firma()
        except OSError:
            f = self._sig
        if f != self._sig:
            if f == self._visto:       # estable durante 2 revisiones: ya terminó de copiarse
                self._sig = f
                try:
                    self.al_cambiar()
                except Exception as e:
                    print(f'[fondo] No se pudo actualizar el fondo: {e}')
            else:
                self._visto = f
        self._job = self.widget.after(self.intervalo, self._tick)
