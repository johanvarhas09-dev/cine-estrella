"""
Punto de Venta Visual de Boletería — CINE ESTRELLA.
Incluye visualización de cartelera, mapa interactivo de asientos,
validación de RUT Módulo 11, control de edad y carrito de compra atómico.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from ui.estilos import COLORS, FONTS, TYPE_COLORS, CLASIF_LABELS, CLASIF_COLORS, estilizar_entry
from dao.funcion_dao import FuncionDAO
from dao.producto_dao import ProductoDAO
from dao.venta_dao import VentaDAO
from dao.trabajador_dao import TrabajadorDAO
from model.boletero import Boletero
from model.encargado_dulceria import EncargadoDulceria
from model.venta import Venta
from model.detalle_venta import DetalleVenta
from model.cliente import Cliente
from model.excepciones import SinAsientosException, RestriccionEdadException, ReglaNegocioException
from service.venta_service import VentaService
from ui.ventana_cuadratura import VentanaCuadratura


class VentanaBoleteria(tk.Toplevel):
    W, H = 1260, 750

    def __init__(self, parent, boletero: Boletero):
        super().__init__(parent)
        self.parent = parent
        self.boletero = boletero

        self.title("CINE ESTRELLA — Punto de Venta Boletería")
        self.geometry(f"{self.W}x{self.H}")
        self.minsize(1100, 700)
        self.configure(bg=COLORS['bg_main'])

        # Estado del punto de venta
        self.funcion_activa = None
        self.venta_actual = Venta(id_venta=None)

        # Variables reactivas
        self.var_rut = tk.StringVar()
        self.var_edad = tk.StringVar(value="18")
        self.var_nombre = tk.StringVar()
        self.var_cantidad = tk.IntVar(value=1)

        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._build_ui()

    def _build_ui(self):
        # 1. Cabecera Corporativa
        hdr = tk.Frame(self, bg=COLORS['header_bg'], height=65, highlightbackground=COLORS['border'], highlightthickness=1)
        hdr.pack(fill='x')

        tk.Label(hdr, text="🎟️ CINE ESTRELLA", font=FONTS['title'], bg=COLORS['header_bg'], fg=COLORS['accent_gold']).pack(side='left', padx=20, pady=10)
        tk.Label(hdr, text="Punto de Venta de Boletos", font=FONTS['subtitle'], bg=COLORS['header_bg'], fg=COLORS['text_light']).pack(side='left', padx=6)

        # Barra derecha
        r_bar = tk.Frame(hdr, bg=COLORS['header_bg'])
        r_bar.pack(side='right', padx=20)
        tk.Label(r_bar, text=f"Boletero: {self.boletero.nombre}", font=FONTS['small_b'], bg=COLORS['header_bg'], fg=COLORS['accent_gold']).pack(side='left', padx=8)

        tk.Button(
            r_bar, text="📊 Mi Cuadratura", font=FONTS['small_b'], bg='#1c2b3a', fg='#9bbcf0',
            relief='flat', padx=10, pady=4, cursor='hand2', command=self._abrir_cuadratura
        ).pack(side='left', padx=4)

        tk.Button(
            r_bar, text="Cerrar Turno ◀", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white',
            relief='flat', padx=10, pady=4, cursor='hand2', command=self._cerrar
        ).pack(side='left', padx=4)

        # 2. Contenedor Principal (3 Columnas)
        body = tk.Frame(self, bg=COLORS['bg_main'])
        body.pack(fill='both', expand=True, padx=12, pady=10)

        # COLUMNA 1: Cartelera de Funciones
        self.col_cartelera = tk.Frame(body, bg=COLORS['bg_main'], width=380)
        self.col_cartelera.pack(side='left', fill='both', expand=True, padx=(0, 6))
        self._build_col_cartelera()

        # COLUMNA 2: Detalle de Función y Matriz de Butacas
        self.col_detalle = tk.Frame(body, bg=COLORS['bg_panel'], width=480, highlightbackground=COLORS['border'], highlightthickness=1)
        self.col_detalle.pack(side='left', fill='both', expand=True, padx=6)
        self._build_col_detalle_placeholder()

        # COLUMNA 3: Resumen de Compra / Carrito Unificado
        self.col_carrito = tk.Frame(body, bg=COLORS['bg_card'], width=340, highlightbackground=COLORS['border'], highlightthickness=1)
        self.col_carrito.pack(side='right', fill='y', padx=(6, 0))
        self.col_carrito.pack_propagate(False)
        self._build_col_carrito()

    def _cerrar(self):
        if self.venta_actual.detalles:
            if not messagebox.askyesno("Venta en Curso", "Tiene ítems en el carrito. ¿Desea cancelar y salir?\nLos asientos reservados serán devueltos a la sala.", parent=self):
                return
            self._devolver_asientos_carrito()
        self.destroy()
        self.parent.deiconify()

    def _abrir_cuadratura(self):
        VentanaCuadratura(self, self.boletero)

    # =========================================================================
    # COLUMNA 1: CARTELERA DE FUNCIONES
    # =========================================================================
    def _build_col_cartelera(self):
        hdr = tk.Frame(self.col_cartelera, bg=COLORS['bg_main'])
        hdr.pack(fill='x', pady=(0, 6))
        tk.Label(hdr, text="Cartelera de Funciones", font=FONTS['subtitle'], bg=COLORS['bg_main'], fg=COLORS['accent_gold']).pack(side='left')

        # Contenedor con scroll para tarjetas
        canvas_f = tk.Frame(self.col_cartelera, bg=COLORS['bg_main'])
        canvas_f.pack(fill='both', expand=True)

        canvas = tk.Canvas(canvas_f, bg=COLORS['bg_main'], highlightthickness=0)
        sb = ttk.Scrollbar(canvas_f, orient='vertical', command=canvas.yview)
        self.frame_cards = tk.Frame(canvas, bg=COLORS['bg_main'])

        self.frame_cards.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.frame_cards, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        self._render_cartelera()

    def _render_cartelera(self):
        for w in self.frame_cards.winfo_children():
            w.destroy()

        funciones = FuncionDAO.listar()
        if not funciones:
            tk.Label(self.frame_cards, text="No hay funciones programadas.", font=FONTS['body'], bg=COLORS['bg_main'], fg=COLORS['text_muted']).pack(pady=30)
            return

        for f in funciones:
            self._crear_tarjeta_funcion(f)

    def _crear_tarjeta_funcion(self, f):
        card = tk.Frame(
            self.frame_cards, bg=COLORS['bg_panel'], padx=12, pady=10,
            highlightbackground=COLORS['border'], highlightthickness=1, cursor='hand2'
        )
        card.pack(fill='x', pady=4)

        # Fila superior: Badges e importe
        top = tk.Frame(card, bg=COLORS['bg_panel'])
        top.pack(fill='x')

        tipo_bg = TYPE_COLORS.get(f.tipo, '#555555')
        tk.Label(top, text=f" {f.tipo} ", font=FONTS['tag'], bg=tipo_bg, fg='white').pack(side='left')

        clasif_bg = CLASIF_COLORS.get(f.pelicula.clasificacion_edad, '#555555')
        clasif_txt = CLASIF_LABELS.get(f.pelicula.clasificacion_edad, f"+{f.pelicula.clasificacion_edad}")
        tk.Label(top, text=f" {clasif_txt} ", font=FONTS['tag'], bg=clasif_bg, fg='white').pack(side='left', padx=6)

        tk.Label(top, text=f"${f.calcular_precio():,.0f}", font=FONTS['price'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(side='right')

        # Título y Horario
        tk.Label(card, text=f.pelicula.titulo, font=FONTS['body_b'], bg=COLORS['bg_panel'], fg='white', anchor='w').pack(fill='x', pady=(4, 2))
        tk.Label(card, text=f"Horario: {f.fecha_hora}", font=FONTS['small'], bg=COLORS['bg_panel'], fg=COLORS['text_muted'], anchor='w').pack(fill='x')

        # Barra de Disponibilidad
        disp = f.asientos_disponibles
        total = f.capacidad
        vendidos = f.asientos_vendidos
        pct = (disp / total) if total > 0 else 0
        color_barra = COLORS['seat_avail'] if pct > 0.3 else (COLORS['accent_gold'] if pct > 0.1 else COLORS['seat_taken'])

        bar_f = tk.Frame(card, bg='#331118', height=6)
        bar_f.pack(fill='x', pady=(6, 4))
        bar_f.pack_propagate(False)

        fill_f = tk.Frame(bar_f, bg=color_barra, width=int(320 * pct), height=6)
        fill_f.place(x=0, y=0, relwidth=pct, height=6)

        info_asientos = tk.Frame(card, bg=COLORS['bg_panel'])
        info_asientos.pack(fill='x', pady=(2, 4))
        tk.Label(info_asientos, text=f"Vendidos: {vendidos}", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg='#ff8888').pack(side='left')
        tk.Label(info_asientos, text=f"Disponibles: {disp} / {total}", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=color_barra).pack(side='right')

        # Botón explícito para seleccionar y vender boletos de esta función
        if disp <= 0:
            btn_vender = tk.Button(
                card, text="⛔ SALA COMPLETA (AGOTADA)",
                font=FONTS['btn'], bg=COLORS['btn_gray'], fg='#aaaaaa',
                relief='flat', pady=6, state='disabled'
            )
        else:
            btn_vender = tk.Button(
                card, text="🎟️ VENDER ENTRADAS / SELECCIONAR ▶",
                font=FONTS['btn'], bg=COLORS['accent_red'], fg='white',
                activebackground='#ff2222', activeforeground='white',
                relief='flat', pady=6, cursor='hand2',
                command=lambda func=f: self._seleccionar_funcion(func)
            )
        btn_vender.pack(fill='x', pady=(4, 2))

        # Evento clic para seleccionar en la tarjeta
        for widget in (card, top, info_asientos):
            widget.bind("<Button-1>", lambda e, func=f: self._seleccionar_funcion(func))

    def _seleccionar_funcion(self, f):
        # Obtener el registro más reciente desde la base de datos
        f_db = FuncionDAO.obtener_por_id(f.id_funcion) or f
        self.funcion_activa = f_db
        self.var_rut.set("")
        self.var_edad.set("18")
        self.var_nombre.set("")
        self.var_cantidad.set(1 if f_db.asientos_disponibles > 0 else 0)
        self._render_col_detalle()

    # =========================================================================
    # COLUMNA 2: DETALLE Y MATRIZ DE BUTACAS
    # =========================================================================
    def _build_col_detalle_placeholder(self):
        for w in self.col_detalle.winfo_children():
            w.destroy()
        tk.Label(
            self.col_detalle, text="◀ Seleccione una función en cartelera\npara ver butacas y emitir boletos",
            font=FONTS['subtitle'], bg=COLORS['bg_panel'], fg=COLORS['text_muted'], justify='center'
        ).place(relx=0.5, rely=0.5, anchor='center')

    def _render_col_detalle(self):
        for w in self.col_detalle.winfo_children():
            w.destroy()

        f = self.funcion_activa
        pane = self.col_detalle

        # Cabecera de la función seleccionada
        head = tk.Frame(pane, bg=COLORS['bg_panel'], padx=16, pady=12)
        head.pack(fill='x')

        tk.Label(head, text=f.pelicula.titulo, font=FONTS['title'], bg=COLORS['bg_panel'], fg='white', wraplength=420, justify='left').pack(anchor='w')
        tk.Label(head, text=f"Función [{f.tipo}] · {f.fecha_hora}", font=FONTS['body'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(anchor='w', pady=2)

        # Precio y Cupos
        p_row = tk.Frame(head, bg=COLORS['bg_panel'])
        p_row.pack(fill='x', pady=4)
        tk.Label(p_row, text=f"Precio por Entrada: ${f.calcular_precio():,.0f} CLP", font=FONTS['price'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(side='left')
        tk.Label(p_row, text=f"Vendidos: {f.asientos_vendidos}  |  Libres: {f.asientos_disponibles} de {f.capacidad}", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(side='right')

        tk.Frame(pane, bg=COLORS['border'], height=1).pack(fill='x', padx=16, pady=4)

        # MATRIZ VISUAL DE BUTACAS
        tk.Label(pane, text=f"💺 Mapa de Sala y Asientos (Vendidos: {f.asientos_vendidos} | Libres: {f.asientos_disponibles}):", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', padx=16, pady=(6, 2))

        grid_card = tk.Frame(pane, bg=COLORS['bg_card'], padx=12, pady=10, highlightbackground=COLORS['border'], highlightthickness=1)
        grid_card.pack(fill='x', padx=16, pady=4)

        # Pantalla visual
        tk.Label(grid_card, text="[ PANTALLA PROYECTOR ]", font=FONTS['tag'], bg='#331116', fg=COLORS['accent_gold'], pady=3).pack(fill='x', pady=(0, 8))

        seats_frame = tk.Frame(grid_card, bg=COLORS['bg_card'])
        seats_frame.pack()

        cap = f.capacidad
        vendidos = f.asientos_vendidos
        columnas = 10
        filas = (min(cap, 40) + columnas - 1) // columnas

        for i in range(min(cap, 40)):
            r_idx = i // columnas
            c_idx = i % columnas
            ocupado = i < vendidos

            if ocupado:
                color = COLORS['seat_taken']
            else:
                color = COLORS['seat_vip'] if f.tipo == "VIP" else COLORS['seat_avail']

            sq = tk.Frame(seats_frame, bg=color, width=22, height=16)
            sq.grid(row=r_idx, column=c_idx, padx=3, pady=3)

        # Leyenda de butacas
        leyenda = tk.Frame(grid_card, bg=COLORS['bg_card'], pady=6)
        leyenda.pack(fill='x')
        tk.Label(leyenda, text=f"■ Disponibles ({f.asientos_disponibles})", font=FONTS['tag'], bg=COLORS['bg_card'], fg=COLORS['seat_avail']).pack(side='left', padx=8)
        tk.Label(leyenda, text=f"■ Vendidos ({f.asientos_vendidos})", font=FONTS['tag'], bg=COLORS['bg_card'], fg=COLORS['seat_taken']).pack(side='left', padx=8)
        if f.tipo == "VIP":
            tk.Label(leyenda, text="■ Asiento VIP", font=FONTS['tag'], bg=COLORS['bg_card'], fg=COLORS['seat_vip']).pack(side='left', padx=8)

        tk.Frame(pane, bg=COLORS['border'], height=1).pack(fill='x', padx=16, pady=6)

        # CONTROL DE ACCESO Y EDAD (Casos P07, P08, P15)
        form_f = tk.Frame(pane, bg=COLORS['bg_panel'], padx=16)
        form_f.pack(fill='x')

        if f.pelicula.clasificacion_edad > 0:
            tk.Label(
                form_f, text=f"⚠ Película Clasificada (+{f.pelicula.clasificacion_edad}): Se requiere RUT y edad",
                font=FONTS['small_b'], bg=COLORS['bg_panel'], fg='#ffaa00'
            ).pack(anchor='w', pady=(0, 4))

            r_f = tk.Frame(form_f, bg=COLORS['bg_panel'])
            r_f.pack(fill='x', pady=2)
            tk.Label(r_f, text="RUT Comprador:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light'], width=15, anchor='w').pack(side='left')
            e_rut = tk.Entry(r_f, textvariable=self.var_rut, font=FONTS['body'], bg=COLORS['bg_input'], fg='white', relief='flat')
            estilizar_entry(e_rut)
            e_rut.pack(side='left', fill='x', expand=True, ipady=3)

            ed_f = tk.Frame(form_f, bg=COLORS['bg_panel'])
            ed_f.pack(fill='x', pady=2)
            tk.Label(ed_f, text="Edad (Años):", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light'], width=15, anchor='w').pack(side='left')
            e_edad = tk.Entry(ed_f, textvariable=self.var_edad, font=FONTS['body'], bg=COLORS['bg_input'], fg='white', relief='flat')
            estilizar_entry(e_edad)
            e_edad.pack(side='left', fill='x', expand=True, ipady=3)

        # Cantidad de entradas
        qty_f = tk.Frame(form_f, bg=COLORS['bg_panel'], pady=6)
        qty_f.pack(fill='x')

        tk.Label(qty_f, text="Cantidad de Entradas:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light'], width=18, anchor='w').pack(side='left')

        btn_menos = tk.Button(
            qty_f, text=" − ", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white', relief='flat',
            command=lambda: self.var_cantidad.set(max(1 if f.asientos_disponibles > 0 else 0, self.var_cantidad.get() - 1))
        )
        btn_menos.pack(side='left')

        tk.Label(qty_f, textvariable=self.var_cantidad, font=FONTS['price'], bg=COLORS['bg_panel'], fg='white', width=4).pack(side='left')

        btn_mas = tk.Button(
            qty_f, text=" + ", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white', relief='flat',
            command=lambda: self.var_cantidad.set(min(f.asientos_disponibles, self.var_cantidad.get() + 1) if f.asientos_disponibles > 0 else 0)
        )
        btn_mas.pack(side='left')

        if f.asientos_disponibles <= 0:
            btn_menos.configure(state='disabled')
            btn_mas.configure(state='disabled')
            tk.Label(qty_f, text="⛔ AGOTADA", font=FONTS['tag'], bg='#331118', fg='#ff6666').pack(side='left', padx=8)

        # Botón Agregar al Carrito
        if f.asientos_disponibles <= 0:
            tk.Button(
                form_f, text="⛔ SALA COMPLETA — SIN ASIENTOS DISPONIBLES", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='#999999',
                relief='flat', pady=10, state='disabled'
            ).pack(fill='x', pady=(10, 8))
        else:
            tk.Button(
                form_f, text="🎟️ AGREGAR ENTRADAS AL RESUMEN", font=FONTS['btn'], bg='#0055b3', fg='white',
                relief='flat', pady=10, cursor='hand2', activebackground='#0066d6', command=self._agregar_al_carrito
            ).pack(fill='x', pady=(10, 8))

    def _agregar_al_carrito(self):
        f = self.funcion_activa
        if not f:
            return

        cant = self.var_cantidad.get()
        if cant <= 0:
            messagebox.showwarning("Cantidad Inválida", "Seleccione al menos una entrada para agregar.", parent=self)
            return

        # Consultar disponibilidad en tiempo real en la base de datos
        f_db = FuncionDAO.obtener_por_id(f.id_funcion)
        if not f_db:
            messagebox.showerror("Error", "La función seleccionada ya no existe.", parent=self)
            return

        # REQUISITO 4: Control estricto de cupos para evitar sobrepasar disponibilidad
        if cant > f_db.asientos_disponibles:
            messagebox.showerror(
                "Capacidad Excedida",
                f"No es posible agregar {cant} entrada(s).\n"
                f"Solo quedan {f_db.asientos_disponibles} asiento(s) disponible(s) en la sala (Capacidad: {f_db.capacidad}).",
                parent=self
            )
            self.funcion_activa = f_db
            self.var_cantidad.set(max(0, f_db.asientos_disponibles))
            self._render_cartelera()
            self._render_col_detalle()
            return

        # Validación de comprador en película clasificada (P07, P08, P15)
        cliente = None
        # [FUNCIONALIDAD: RESTRICCIÓN ETARIA Y VALIDACIÓN DE RUT EN LA INTERFAZ - Casos P07, P08 y P15]
        # Si la película tiene clasificación (+14, +18), es obligatorio ingresar el RUT del comprador.
        # Se ejecuta la validación del algoritmo Módulo 11 y la verificación de edad mínima sin congelar la ventana.
        if f.pelicula.clasificacion_edad > 0:
            rut = self.var_rut.get().strip()
            edad_str = self.var_edad.get().strip()

            if not rut:
                messagebox.showerror("RUT Obligatorio", "Debe ingresar el RUT del comprador.", parent=self)
                return

            try:
                edad = int(edad_str)
            except ValueError:
                messagebox.showerror("Edad Inválida", "La edad debe ser un número entero.", parent=self)
                return

            try:
                cliente = VentaService.validar_cliente_para_funcion(f.id_funcion, rut, "Comprador", edad)
            except RestriccionEdadException as e:
                # Caso P15: Alerta modal sin cerrar el programa si el comprador no cumple la edad
                messagebox.showerror("Acceso Denegado (Edad)", str(e), parent=self)
                return
            except ReglaNegocioException as e:
                # Caso P08: Alerta modal sin cerrar el programa si el dígito verificador es erróneo
                messagebox.showerror("RUT Inválido", str(e), parent=self)
                return

        # REQUISITO 3: Descontar los asientos inmediatamente en la BD al agregar entradas
        nuevos_disponibles = f_db.asientos_disponibles - cant
        FuncionDAO.actualizar_asientos(f.id_funcion, nuevos_disponibles)

        # Actualizar objeto en memoria
        f_db.asientos_disponibles = nuevos_disponibles
        self.funcion_activa = f_db

        precio_unitario = f_db.calcular_precio()
        descripcion = f"Entrada [{f_db.tipo}] {f_db.pelicula.titulo} ({f_db.fecha_hora})"
        detalle = DetalleVenta(
            id_detalle=None,
            id_venta=None,
            tipo_item="entrada",
            id_item=f_db.id_funcion,
            descripcion=descripcion,
            cantidad=cant,
            precio_unitario=precio_unitario,
            id_trabajador=self.boletero.id_trabajador
        )

        if cliente:
            self.venta_actual.cliente = cliente
        self.venta_actual.agregar_detalle(detalle)

        # Reajustar valor reactivo de cantidad
        self.var_cantidad.set(1 if nuevos_disponibles > 0 else 0)

        # Actualizar componentes visuales de la interfaz
        self._render_col_carrito()
        self._render_cartelera()
        self._render_col_detalle()

    # =========================================================================
    # COLUMNA 3: RESUMEN DE COMPRA / CARRITO UNIFICADO
    # =========================================================================
    def _build_col_carrito(self):
        pane = self.col_carrito

        tk.Label(pane, text="🛒 Resumen de Compra", font=FONTS['subtitle'], bg=COLORS['bg_card'], fg=COLORS['accent_gold']).pack(anchor='w', padx=14, pady=(12, 6))
        tk.Frame(pane, bg=COLORS['border'], height=1).pack(fill='x', padx=14)

        # Contenedor de líneas de detalle
        self.cart_items_frame = tk.Frame(pane, bg=COLORS['bg_card'])
        self.cart_items_frame.pack(fill='both', expand=True, padx=10, pady=8)

        # Pie del carrito con totales
        foot = tk.Frame(pane, bg=COLORS['bg_card'], padx=14, pady=10)
        foot.pack(fill='x', side='bottom')

        self.lbl_total = tk.Label(foot, text="TOTAL: $0 CLP", font=FONTS['amount'], bg=COLORS['bg_card'], fg=COLORS['accent_gold'])
        self.lbl_total.pack(pady=4)

        tk.Button(
            foot, text="✅ CONFIRMAR VENTA", font=FONTS['btn'], bg=COLORS['btn_green'], fg='white',
            activebackground=COLORS['btn_green_hover'], relief='flat', pady=10, cursor='hand2', command=self._confirmar_venta
        ).pack(fill='x', pady=3)

        tk.Button(
            foot, text="🍿 Anexar Confitería (Venta Compartida)", font=FONTS['small_b'], bg='#332200', fg=COLORS['accent_gold'],
            relief='flat', pady=6, cursor='hand2', command=self._modal_venta_compartida
        ).pack(fill='x', pady=3)

        tk.Button(
            foot, text="🗑️ Vaciar Carrito Completo", font=FONTS['small'], bg=COLORS['btn_gray'], fg='white',
            relief='flat', pady=4, cursor='hand2', command=self._vaciar_carrito
        ).pack(fill='x', pady=3)

        self._render_col_carrito()

    def _render_col_carrito(self):
        for w in self.cart_items_frame.winfo_children():
            w.destroy()

        detalles = self.venta_actual.detalles
        if not detalles:
            tk.Label(self.cart_items_frame, text="El carrito está vacío.\nSeleccione entradas para agregar.", font=FONTS['small'], bg=COLORS['bg_card'], fg=COLORS['text_muted'], justify='center').pack(pady=40)
            self.lbl_total.configure(text="TOTAL: $0 CLP")
            return

        for idx, d in enumerate(detalles):
            row = tk.Frame(self.cart_items_frame, bg=COLORS['bg_panel'], padx=8, pady=6, highlightbackground=COLORS['border'], highlightthickness=1)
            row.pack(fill='x', pady=3)

            top = tk.Frame(row, bg=COLORS['bg_panel'])
            top.pack(fill='x')
            tk.Label(top, text=f"x{d.cantidad}", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(side='left')
            tk.Label(top, text=f"${d.subtotal:,.0f}", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg='white').pack(side='right')

            # Botón individual para quitar solo esta línea (Req 10)
            tk.Button(
                top, text="✕ Quitar", font=FONTS['tag'], bg='#4a111a', fg='#ff8888',
                activebackground=COLORS['accent_red'], activeforeground='white',
                relief='flat', padx=6, pady=1, cursor='hand2',
                command=lambda i=idx: self._quitar_item_carrito(i)
            ).pack(side='right', padx=(0, 8))

            tk.Label(row, text=d.descripcion[:36], font=FONTS['small'], bg=COLORS['bg_panel'], fg=COLORS['text_light'], anchor='w').pack(fill='x')

        self.lbl_total.configure(text=f"TOTAL: ${self.venta_actual.total:,.0f} CLP")

    def _devolver_asientos_carrito(self):
        """Restaura en la base de datos los asientos de entradas que estaban reservados en el carrito."""
        for d in self.venta_actual.detalles:
            if d.tipo_item == "entrada" and d.id_item:
                f_db = FuncionDAO.obtener_por_id(d.id_item)
                if f_db:
                    nuevos = min(f_db.capacidad, f_db.asientos_disponibles + d.cantidad)
                    FuncionDAO.actualizar_asientos(d.id_item, nuevos)
                    if self.funcion_activa and self.funcion_activa.id_funcion == d.id_item:
                        self.funcion_activa.asientos_disponibles = nuevos

    def _quitar_item_carrito(self, idx: int):
        removido = self.venta_actual.quitar_detalle(idx)
        if removido and removido.tipo_item == "entrada" and removido.id_item:
            f_db = FuncionDAO.obtener_por_id(removido.id_item)
            if f_db:
                nuevos = min(f_db.capacidad, f_db.asientos_disponibles + removido.cantidad)
                FuncionDAO.actualizar_asientos(removido.id_item, nuevos)
                if self.funcion_activa and self.funcion_activa.id_funcion == removido.id_item:
                    self.funcion_activa.asientos_disponibles = nuevos
        self._render_col_carrito()
        self._render_cartelera()
        if self.funcion_activa:
            self._render_col_detalle()

    def _vaciar_carrito(self):
        if not self.venta_actual.detalles:
            return
        if messagebox.askyesno("Vaciar Carrito", "¿Desea eliminar todas las entradas y productos del carrito actual?\nLos asientos reservados serán devueltos a la sala.", parent=self):
            self._devolver_asientos_carrito()
            self.venta_actual.limpiar_detalles()
            self._render_col_carrito()
            self._render_cartelera()
            if self.funcion_activa:
                f_db = FuncionDAO.obtener_por_id(self.funcion_activa.id_funcion)
                if f_db:
                    self.funcion_activa = f_db
                self._render_col_detalle()

    def _nueva_venta(self):
        self._devolver_asientos_carrito()
        self.venta_actual = Venta(id_venta=None)
        self.var_rut.set("")
        self.var_edad.set("18")
        self.var_nombre.set("")
        self.var_cantidad.set(1)
        self._render_col_carrito()
        self._render_cartelera()
        if self.funcion_activa:
            f_db = FuncionDAO.obtener_por_id(self.funcion_activa.id_funcion)
            if f_db:
                self.funcion_activa = f_db
            self._render_col_detalle()

    def _limpiar_estado_tras_venta(self):
        self.venta_actual = Venta(id_venta=None)
        self.var_rut.set("")
        self.var_edad.set("18")
        self.var_nombre.set("")
        self.var_cantidad.set(1)
        self.funcion_activa = None
        self._build_col_detalle_placeholder()
        self._render_col_carrito()
        self._render_cartelera()

    def _confirmar_venta(self):
        if not self.venta_actual.detalles:
            messagebox.showwarning("Carrito Vacío", "Agregue entradas o productos antes de confirmar.", parent=self)
            return

        try:
            # Los asientos ya fueron descontados en tiempo real al agregarse al carrito
            venta_guardada = VentaService.concretar_venta(self.venta_actual, descontar_asientos=False)
            messagebox.showinfo(
                "¡Venta Exitosa!",
                f"✔ Venta registrada exitosamente bajo Folio #{venta_guardada.id_venta}.\n"
                f"Total Pagado: ${venta_guardada.total:,.0f} CLP\n"
                f"Líneas Emitidas: {len(venta_guardada.detalles)}",
                parent=self
            )
            # Limpiar estado completamente (Req 8 y Req 9)
            self._limpiar_estado_tras_venta()
        except Exception as e:
            messagebox.showerror("Error al Registrar Venta", str(e), parent=self)

    def _modal_venta_compartida(self):
        """Permite anexar productos de dulcería a la misma compra (Caso P12)."""
        dlg = tk.Toplevel(self)
        dlg.title("Anexar Confitería a la Compra")
        dlg.geometry("420x360")
        dlg.configure(bg=COLORS['bg_main'])
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="Seleccione Producto de Confitería:", font=FONTS['subtitle'], bg=COLORS['bg_main'], fg=COLORS['accent_gold']).pack(pady=12)

        prods = ProductoDAO.listar()
        nombres = [f"{p.nombre} ({p.tipo}) - ${p.precio_base:,.0f}" for p in prods]
        var_p = tk.StringVar(value=nombres[0] if nombres else "")
        cb = ttk.Combobox(dlg, textvariable=var_p, values=nombres, state='readonly', width=35)
        cb.pack(pady=8)

        tk.Label(dlg, text="Cantidad:", font=FONTS['small_b'], bg=COLORS['bg_main'], fg=COLORS['text_light']).pack()
        var_q = tk.IntVar(value=1)
        eq = tk.Entry(dlg, textvariable=var_q, font=FONTS['body'], width=8, justify='center')
        estilizar_entry(eq)
        eq.pack(pady=6)

        def agregar():
            idx = cb.current()
            if idx >= 0:
                prod = prods[idx]
                cant = var_q.get()
                # Delegar en cajero de dulcería
                dulceros = [t for t in TrabajadorDAO.listar() if t.rol == "dulceria"]
                id_dulcero = dulceros[0].id_trabajador if dulceros else 1
                proxy_dulcero = EncargadoDulceria(id_trabajador=id_dulcero, nombre="Dulcería", username="dulc", password_hash="")
                det = VentaService.crear_detalle_producto(prod.id_producto, cant, proxy_dulcero)
                self.venta_actual.agregar_detalle(det)
                self._render_col_carrito()
                dlg.destroy()

        tk.Button(dlg, text="Agregar al Carrito", font=FONTS['btn'], bg=COLORS['accent_red'], fg='white', relief='flat', pady=8, padx=20, command=agregar).pack(pady=16)

