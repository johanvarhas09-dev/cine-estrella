"""
Punto de Venta Visual de Confitería — CINE ESTRELLA.
Catálogo en tarjetas (paginado, sin scroll) con conversión automática de dólares a
pesos chilenos en tiempo real y carrito de compras atómico.

Fondo: ./fondos/fondo_confiteria.jpg (si lo reemplazas, cambia solo, sin reiniciar).
"""
import math
from tkinter import messagebox

from ui.base import VentanaBase, EMOJI
from ui.componentes import rect_redondeado
from ui.estilos import COLORS, FONTS
from dao.producto_dao import ProductoDAO
from dao.venta_dao import VentaDAO
from model.encargado_dulceria import EncargadoDulceria
from model.producto_importado import ProductoImportado
from model.venta import Venta
from service.tipo_cambio_service import TipoCambioService
from service.venta_service import VentaService
from ui.ventana_cuadratura import VentanaCuadratura

POR_PAGINA = 6        # productos por página (3 columnas x 2 filas)
LINEAS_CARRITO = 5    # líneas visibles del carrito por página


class VentanaDulceria(VentanaBase):
    W, H = 1240, 700
    NOMBRE_FONDO = 'fondo_confiteria'
    PANELES = [(20, 16, 1220, 86),      # cabecera
               (20, 96, 1220, 134),     # cotización del dólar
               (20, 146, 840, 680),     # catálogo
               (860, 146, 1220, 680)]   # carrito

    def __init__(self, parent, dulcero: EncargadoDulceria):
        super().__init__(parent, "CINE ESTRELLA — Punto de Venta Confitería")
        self.dulcero = dulcero

        self._tasa_dolar = None
        self._cargar_dolar()

        self.venta_actual = Venta(id_venta=None)
        self._productos, self._filtro = [], 'todos'
        self._pag, self._pag_cart = 0, 0
        self._qty, self._qty_ids = {}, {}

        self._build_ui()
        self.iniciar_fondo()

    def _cargar_dolar(self):
        """
        [FUNCIONALIDAD: CARGA DINÁMICA DE DÓLAR EN TIEMPO REAL - Casos P16 y P17]
        Consulta la cotización oficial del dólar observado al iniciar la pantalla de dulcería.
        Si la API responde con éxito, actualiza la tasa y los precios de productos importados.
        Si no hay internet (Caso P17), activa modo offline con tasa referencial sin interrumpir
        las ventas ni congelar la pantalla.
        """
        try:
            tc = TipoCambioService.obtener_dolar_dia()
            self._tasa_dolar = tc.valor
            self._dolar_info = f"${tc.valor:,.2f} CLP ({tc.fuente})"
        except Exception:
            self._tasa_dolar = 950.0
            self._dolar_info = "$950.00 CLP (Modo Offline)"

    # ── Estructura fija ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Cabecera
        self.texto(40, 41, "🍿 CINE ESTRELLA", 'card_title', COLORS['accent_gold'])
        self.texto(40, 65, "Punto de Venta de Confitería y Snacks", 'small', COLORS['text_light'])
        self.texto(860, 51, f"Atiende: {self.dulcero.nombre}", 'small_b', COLORS['accent_gold'], 'e')
        self.boton(884, 30, 150, 38, "📊 Mi Cuadratura", self._abrir_cuadratura, 'dorado', FONTS['small_b'])
        self.boton(1048, 30, 156, 38, "Cerrar Turno ◀", self._cerrar, 'fantasma', FONTS['small_b'])

        # Cotización
        self.texto(40, 115, f"💵 Dólar oficial en vivo: {self._dolar_info} — los precios de los "
                            f"artículos importados se calculan en tiempo real.",
                   'body_b', COLORS['accent_gold'])

        # Títulos de columnas
        self.texto(40, 177, "Catálogo de Confitería", 'subtitle', COLORS['accent_gold'])
        self.texto(880, 177, "🛒 Carrito de Confitería", 'subtitle', COLORS['accent_gold'])
        self.canvas.create_line(880, 198, 1200, 198, fill=COLORS['border'])

        # Pie del carrito (fijo)
        self._lbl_total = self.texto(1040, 548, "TOTAL: $0 CLP", 'amount', COLORS['accent_gold'], 'center')
        self.boton(880, 572, 320, 48, "✅ CONFIRMAR VENTA", self._confirmar_venta, 'exito')
        self.boton(880, 628, 320, 36, "🗑️ Vaciar Carrito", self._vaciar_carrito, 'fantasma', FONTS['small_b'])

        self._render_catalogo()
        self._render_col_carrito()

    def _cerrar(self):
        if self.venta_actual.detalles:
            if not messagebox.askyesno("Venta en Curso", "Tiene productos en el carrito. ¿Desea cancelar y salir?", parent=self):
                return
        self.destroy()
        self.parent.deiconify()

    def _abrir_cuadratura(self):
        VentanaCuadratura(self, self.dulcero)

    # =========================================================================
    # CATÁLOGO DE PRODUCTOS
    # =========================================================================
    def _render_catalogo(self):
        """Lee los productos de la base de datos y dibuja la página actual."""
        self._productos = ProductoDAO.listar()
        self._dibujar_catalogo()

    def _set_filtro(self, clave):
        self._filtro, self._pag = clave, 0
        self._dibujar_catalogo()

    def _ir_pagina(self, delta):
        self._pag += delta
        self._dibujar_catalogo()

    def _dibujar_catalogo(self):
        c = self.canvas
        c.delete('cat')
        self._qty_ids = {}

        # Filtros
        for i, (clave, txt) in enumerate((('todos', 'Todos'), ('nacional', 'Nacionales'),
                                          ('importado', 'Importados'))):
            self.boton(492 + i * 112, 162, 104, 30, txt, lambda k=clave: self._set_filtro(k),
                       'dorado' if self._filtro == clave else 'fantasma', FONTS['small_b'],
                       grupo='cat', radio=10)

        lista = self._productos
        if self._filtro == 'importado':
            lista = [p for p in lista if isinstance(p, ProductoImportado)]
        elif self._filtro == 'nacional':
            lista = [p for p in lista if not isinstance(p, ProductoImportado)]

        if not lista:
            self.texto(430, 400, "No hay productos disponibles.", 'body', COLORS['text_muted'],
                       'center', tags='cat')
            return

        paginas = max(1, math.ceil(len(lista) / POR_PAGINA))
        self._pag = max(0, min(self._pag, paginas - 1))
        visibles = lista[self._pag * POR_PAGINA:(self._pag + 1) * POR_PAGINA]

        for k, prod in enumerate(visibles):
            fila, col = divmod(k, 3)
            self._tarjeta_producto(prod, 40 + col * 268, 204 + fila * 212)

        if paginas > 1:
            self.boton(330, 632, 44, 30, "◀", lambda: self._ir_pagina(-1), 'fantasma',
                       FONTS['small_b'], grupo='cat', radio=10)
            self.texto(430, 647, f"Página {self._pag + 1} / {paginas}", 'small_b',
                       COLORS['text_light'], 'center', tags='cat')
            self.boton(486, 632, 44, 30, "▶", lambda: self._ir_pagina(1), 'fantasma',
                       FONTS['small_b'], grupo='cat', radio=10)

    def _tarjeta_producto(self, prod, x, y, w=244, h=196):
        c, tasa = self.canvas, self._tasa_dolar or 950.0
        importado = isinstance(prod, ProductoImportado)
        rect_redondeado(c, x, y, x + w, y + h, 16, fill=COLORS['bg_card'],
                        outline=COLORS['border'], width=1, tags='cat')

        nombre = prod.nombre.lower()
        icono = "🍿" if "popcorn" in nombre else (
            "🥤" if "bebida" in nombre or "agua" in nombre else (
                "🌭" if "dog" in nombre else "🍫"))
        c.create_text(x + 16, y + 12, text=icono, font=(EMOJI, 30), anchor='nw', tags='cat')

        bx = x + w - 14 - 92
        rect_redondeado(c, bx, y + 16, bx + 92, y + 36, 8,
                        fill='#b8860b' if importado else '#236b23', outline='', tags='cat')
        c.create_text(bx + 46, y + 26, text="IMPORTADO" if importado else "NACIONAL",
                      font=FONTS['tag'], fill='white', tags='cat')

        titulo = prod.nombre if len(prod.nombre) <= 56 else prod.nombre[:55] + '…'
        c.create_text(x + 16, y + 62, text=titulo, font=FONTS['body_b'], fill='white',
                      anchor='nw', width=w - 32, tags='cat')

        if importado:
            precio_clp = prod.calcular_precio(tasa)
            c.create_text(x + w - 16, y + 120, text=f"USD ${prod.precio_usd:.2f}", font=FONTS['small'],
                          fill=COLORS['text_muted'], anchor='e', tags='cat')
        else:
            precio_clp = prod.calcular_precio()
        c.create_text(x + 16, y + 120, text=f"${precio_clp:,.0f} CLP", font=FONTS['price'],
                      fill=COLORS['accent_gold'], anchor='w', tags='cat')

        # Controles: [−] cantidad [+]   [Agregar ▶]
        yb, pid = y + h - 48, prod.id_producto
        self.boton(x + 14, yb, 34, 34, "−", lambda p=pid: self._cambiar_qty(p, -1), 'fantasma',
                   FONTS['btn_big'], grupo='cat', radio=10)
        self._qty_ids[pid] = c.create_text(x + 64, yb + 17, text=str(self._qty.get(pid, 1)),
                                           font=FONTS['price'], fill='white', tags='cat')
        self.boton(x + 80, yb, 34, 34, "+", lambda p=pid: self._cambiar_qty(p, 1), 'fantasma',
                   FONTS['btn_big'], grupo='cat', radio=10)
        self.boton(x + 124, yb, 106, 34, "Agregar ▶",
                   lambda p=prod: self._agregar_al_carrito(p, self._qty.get(p.id_producto, 1)),
                   'primario', FONTS['small_b'], grupo='cat', radio=10)

    def _cambiar_qty(self, pid, delta):
        self._qty[pid] = max(1, min(99, self._qty.get(pid, 1) + delta))
        if pid in self._qty_ids:
            self.canvas.itemconfig(self._qty_ids[pid], text=str(self._qty[pid]))

    # =========================================================================
    # CARRITO DE DULCERÍA
    # =========================================================================
    def _ir_pagina_carrito(self, delta):
        self._pag_cart += delta
        self._render_col_carrito()

    def _render_col_carrito(self):
        c = self.canvas
        c.delete('cart')
        detalles = self.venta_actual.detalles
        if not detalles:
            self.texto(1040, 340, "Carrito vacío.\nSeleccione productos para agregar.", 'small',
                       COLORS['text_muted'], 'center', justify='center', tags='cart')
            c.itemconfig(self._lbl_total, text="TOTAL: $0 CLP")
            return

        paginas = max(1, math.ceil(len(detalles) / LINEAS_CARRITO))
        self._pag_cart = max(0, min(self._pag_cart, paginas - 1))
        ini = self._pag_cart * LINEAS_CARRITO

        for i, d in enumerate(detalles[ini:ini + LINEAS_CARRITO]):
            idx, y = ini + i, 208 + i * 58
            rect_redondeado(c, 880, y, 1200, y + 52, 12, fill=COLORS['bg_panel'],
                            outline=COLORS['border'], width=1, tags='cart')
            c.create_text(894, y + 16, text=f"x{d.cantidad}", font=FONTS['small_b'],
                          fill=COLORS['accent_gold'], anchor='w', tags='cart')
            c.create_text(1150, y + 16, text=f"${d.subtotal:,.0f}", font=FONTS['small_b'],
                          fill='white', anchor='e', tags='cart')
            c.create_text(894, y + 37, text=d.descripcion[:34], font=FONTS['small'],
                          fill=COLORS['text_light'], anchor='w', tags='cart')
            # Quitar solo esta línea (Req 10)
            self.boton(1158, y + 10, 34, 32, "✕", lambda j=idx: self._quitar_item(j), 'peligro',
                       FONTS['small_b'], grupo='cart', radio=9)

        if paginas > 1:
            self.boton(930, 500, 44, 26, "◀", lambda: self._ir_pagina_carrito(-1), 'fantasma',
                       FONTS['small_b'], grupo='cart', radio=9)
            self.texto(1040, 513, f"{self._pag_cart + 1} / {paginas}", 'small_b',
                       COLORS['text_light'], 'center', tags='cart')
            self.boton(1106, 500, 44, 26, "▶", lambda: self._ir_pagina_carrito(1), 'fantasma',
                       FONTS['small_b'], grupo='cart', radio=9)

        c.itemconfig(self._lbl_total, text=f"TOTAL: ${self.venta_actual.total:,.0f} CLP")

    def _agregar_al_carrito(self, prod, cantidad, qty_var=None):
        if cantidad <= 0:
            return
        try:
            det = VentaService.crear_detalle_producto(prod.id_producto, cantidad, self.dulcero)
        except Exception as e:
            messagebox.showerror("No se pudo agregar", str(e), parent=self)
            return
        self.venta_actual.agregar_detalle(det)
        if qty_var:
            qty_var.set(1)
        self._qty[prod.id_producto] = 1          # unidades vuelven a 1 tras agregar (Req 13)
        if prod.id_producto in self._qty_ids:
            self.canvas.itemconfig(self._qty_ids[prod.id_producto], text="1")
        self._pag_cart = max(0, math.ceil(len(self.venta_actual.detalles) / LINEAS_CARRITO) - 1)
        self._render_col_carrito()

    def _quitar_item(self, idx: int):
        if 0 <= idx < len(self.venta_actual.detalles):
            self.venta_actual.detalles.pop(idx)
            self._render_col_carrito()

    def _vaciar_carrito(self):
        if not self.venta_actual.detalles:
            return
        if messagebox.askyesno("Vaciar Carrito", "¿Desea eliminar todos los productos del carrito actual?", parent=self):
            self._nueva_venta()

    def _nueva_venta(self):
        self.venta_actual = Venta(id_venta=None)
        self._qty, self._pag_cart = {}, 0
        self._render_catalogo()  # Re-inicializar catálogo y unidades (Req 13)
        self._render_col_carrito()

    def _confirmar_venta(self):
        if not self.venta_actual.detalles:
            messagebox.showwarning("Carrito Vacío", "Agregue productos antes de cobrar.", parent=self)
            return

        try:
            v_guardada = VentaService.concretar_venta(self.venta_actual)
            messagebox.showinfo(
                "¡Venta Exitosa!",
                f"✔ Venta de confitería registrada exitosamente.\n"
                f"Folio Fiscal: #{v_guardada.id_venta}\n"
                f"Total Cobrado: ${v_guardada.total:,.0f} CLP",
                parent=self
            )
            self._nueva_venta()
        except Exception as e:
            messagebox.showerror("Error al Registrar Venta", str(e), parent=self)
