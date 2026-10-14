"""
Panel de Administración Visual — CINE ESTRELLA.
Permite gestión completa de catálogo, funciones, trabajadores, tipo de cambio y reportes.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from ui.estilos import COLORS, FONTS, TYPE_COLORS, CLASIF_LABELS, estilizar_entry
from dao.pelicula_dao import PeliculaDAO
from dao.funcion_dao import FuncionDAO
from dao.producto_dao import ProductoDAO
from dao.trabajador_dao import TrabajadorDAO
from dao.venta_dao import VentaDAO
from model.pelicula import Pelicula
from model.funcion_2d import Funcion2D
from model.funcion_3d import Funcion3D
from model.funcion_vip import FuncionVIP
from model.producto_nacional import ProductoNacional
from model.producto_importado import ProductoImportado
from model.boletero import Boletero
from model.encargado_dulceria import EncargadoDulceria
from model.trabajador import Trabajador
from model.excepciones import ReglaNegocioException
from service.tipo_cambio_service import TipoCambioService


class VentanaAdmin(tk.Toplevel):
    W, H = 1180, 720

    def __init__(self, parent, admin: Trabajador):
        super().__init__(parent)
        self.parent = parent
        self.admin = admin
        self.title("CINE ESTRELLA — Panel de Administración")
        self.geometry(f"{self.W}x{self.H}")
        self.minsize(1050, 680)
        self.configure(bg=COLORS['bg_main'])

        self._tasa_dolar = None
        self._cargar_dolar_inicial()

        self._build_ui()

    def _cargar_dolar_inicial(self):
        try:
            tc = TipoCambioService.obtener_dolar_dia()
            self._tasa_dolar = tc.valor
        except Exception:
            self._tasa_dolar = 950.0

    def _build_ui(self):
        # 1. Cabecera Corporativa
        hdr = tk.Frame(self, bg=COLORS['header_bg'], height=65, highlightbackground=COLORS['border'], highlightthickness=1)
        hdr.pack(fill='x')

        tk.Label(hdr, text="★ CINE ESTRELLA ★", font=FONTS['title'], bg=COLORS['header_bg'], fg=COLORS['accent_gold']).pack(side='left', padx=20, pady=10)
        tk.Label(hdr, text="Panel de Administración y Control", font=FONTS['subtitle'], bg=COLORS['header_bg'], fg=COLORS['text_light']).pack(side='left', padx=10)

        # Barra derecha
        user_f = tk.Frame(hdr, bg=COLORS['header_bg'])
        user_f.pack(side='right', padx=20)
        tk.Label(user_f, text=f"Administrador: {self.admin.nombre}", font=FONTS['small_b'], bg=COLORS['header_bg'], fg=COLORS['accent_gold']).pack(side='left', padx=10)

        tk.Button(
            user_f, text="Cerrar Sesión ◀", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white',
            relief='flat', padx=10, pady=4, cursor='hand2', command=self._cerrar
        ).pack(side='left')

        # 2. Pestañas Principales (Notebook)
        self.nb = ttk.Notebook(self, style='Cine.TNotebook')
        self.nb.pack(fill='both', expand=True, padx=14, pady=10)

        # Tab 1: Películas y Funciones
        self.tab_funciones = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_funciones, text="🎬  Películas y Funciones")
        self._build_tab_funciones()

        # Tab 2: Catálogo de Confitería
        self.tab_productos = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_productos, text="🍿  Confitería y Snacks")
        self._build_tab_productos()

        # Tab 3: Trabajadores
        self.tab_trabajadores = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_trabajadores, text="👥  Personal y Cajas")
        self._build_tab_trabajadores()

        # Tab 4: Reportes de Ventas
        self.tab_reportes = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_reportes, text="📊  Reportes y Auditoría")
        self._build_tab_reportes()

        # Tab 5: Dólar del Día
        self.tab_dolar = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_dolar, text="💵  Tipo de Cambio API")
        self._build_tab_dolar()

    def _cerrar(self):
        self.destroy()
        self.parent.deiconify()

    # =========================================================================
    # TAB 1: PELÍCULAS Y FUNCIONES
    # =========================================================================
    def _build_tab_funciones(self):
        pane = self.tab_funciones

        # Panel Izquierdo: Lista de Funciones Programadas
        left = tk.Frame(pane, bg=COLORS['bg_main'])
        left.pack(side='left', fill='both', expand=True, padx=(8, 4), pady=8)

        tk.Label(left, text="Funciones Programadas en Cartelera", font=FONTS['subtitle'], bg=COLORS['bg_main'], fg=COLORS['accent_gold']).pack(anchor='w', pady=(0, 4))

        cols = ('ID', 'Tipo', 'Película', 'Horario', 'Precio', 'Capacidad', 'Vendidos', 'Disponibles', 'Clasif.')
        tf = tk.Frame(left, bg=COLORS['bg_main'])
        tf.pack(fill='both', expand=True)

        self.tree_func = ttk.Treeview(tf, columns=cols, show='headings', style='Cine.Treeview', height=14)
        ws = [40, 55, 210, 130, 85, 75, 75, 80, 85]
        for c, w in zip(cols, ws):
            self.tree_func.heading(c, text=c)
            self.tree_func.column(c, width=w, anchor='center' if c in ('ID', 'Tipo', 'Capacidad', 'Vendidos', 'Disponibles') else 'w')

        sb = ttk.Scrollbar(tf, orient='vertical', command=self.tree_func.yview)
        self.tree_func.configure(yscrollcommand=sb.set)
        self.tree_func.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        # Botones acción debajo de tabla
        btn_bar = tk.Frame(left, bg=COLORS['bg_main'], pady=8)
        btn_bar.pack(fill='x')
        tk.Button(
            btn_bar, text="✏️ Modificar Función", font=FONTS['btn'], bg='#1b3a5c', fg='white',
            relief='flat', padx=12, pady=6, cursor='hand2', command=self._modificar_funcion
        ).pack(side='left', padx=4)
        tk.Button(
            btn_bar, text="🗑️ Eliminar Función", font=FONTS['btn'], bg='#661111', fg='white',
            relief='flat', padx=12, pady=6, cursor='hand2', command=self._eliminar_funcion
        ).pack(side='left', padx=4)
        tk.Button(
            btn_bar, text="Refrescar Lista", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white',
            relief='flat', padx=12, pady=6, cursor='hand2', command=self._refrescar_funciones
        ).pack(side='right', padx=4)

        # Panel Derecho: Formulario para crear Función / Película
        right = tk.Frame(pane, bg=COLORS['bg_panel'], width=340, padx=16, pady=12, highlightbackground=COLORS['border'], highlightthickness=1)
        right.pack(side='right', fill='y', padx=(4, 8), pady=8)
        right.pack_propagate(False)

        tk.Label(right, text="➕ Programar Nueva Función", font=FONTS['subtitle'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(anchor='w', pady=(0, 10))

        def campo(texto, var):
            tk.Label(right, text=texto, font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(4, 1))
            e = tk.Entry(right, textvariable=var, font=FONTS['body'])
            estilizar_entry(e)
            e.pack(fill='x', ipady=4, pady=(0, 4))
            return e

        self.f_titulo = tk.StringVar()
        campo("Título de la Película:", self.f_titulo)

        tk.Label(right, text="Clasificación de Edad:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(4, 1))
        self.f_clasif = tk.StringVar(value="0 · Todo Espectador")
        cb_clasif = ttk.Combobox(right, textvariable=self.f_clasif, values=["0 · Todo Espectador", "7 · Mayores de 7", "14 · Mayores de 14", "18 · Solo Adultos"], state='readonly')
        cb_clasif.pack(fill='x', pady=(0, 6))

        tk.Label(right, text="Tipo de Proyección (Polimórfico):", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(4, 1))
        self.f_tipo = tk.StringVar(value="2D")
        cb_tipo = ttk.Combobox(right, textvariable=self.f_tipo, values=["2D (Estándar)", "3D (Recargo +$1.500)", "VIP (Premium max 30)"], state='readonly')
        cb_tipo.pack(fill='x', pady=(0, 6))

        self.f_fecha = tk.StringVar(value="2026-10-10 19:00")
        campo("Fecha y Hora (YYYY-MM-DD HH:MM):", self.f_fecha)

        self.f_precio = tk.StringVar(value="4500")
        campo("Precio Base (CLP):", self.f_precio)

        self.f_capacidad = tk.StringVar(value="100")
        campo("Capacidad de Asientos:", self.f_capacidad)

        tk.Button(
            right, text="💾 GUARDAR FUNCIÓN", font=FONTS['btn'], bg=COLORS['accent_red'], fg='white',
            relief='flat', pady=8, cursor='hand2', activebackground=COLORS['accent_red_hover'], command=self._guardar_funcion
        ).pack(fill='x', pady=(12, 0))

        self._refrescar_funciones()

    def _refrescar_funciones(self):
        for item in self.tree_func.get_children():
            self.tree_func.delete(item)

        funciones = FuncionDAO.listar()
        for f in funciones:
            clasif_str = f"+{f.pelicula.clasificacion_edad}" if f.pelicula.clasificacion_edad > 0 else "TE"
            precio = f.calcular_precio()
            self.tree_func.insert('', 'end', values=(
                f.id_funcion, f.tipo, f.pelicula.titulo, f.fecha_hora,
                f"${precio:,.0f}", f.capacidad, f.asientos_vendidos, f.asientos_disponibles, clasif_str
            ))

    def _guardar_funcion(self):
        titulo = self.f_titulo.get().strip()
        if not titulo:
            messagebox.showwarning("Faltan Datos", "Ingrese el título de la película.", parent=self)
            return

        try:
            clasif_num = int(self.f_clasif.get().split()[0])
            precio_base = float(self.f_precio.get())
            capacidad = int(self.f_capacidad.get())
            fecha = self.f_fecha.get().strip()
            tipo_sel = self.f_tipo.get().split()[0]
        except ValueError:
            messagebox.showerror("Error de Formato", "Precio y capacidad deben ser valores numéricos válidos.", parent=self)
            return

        # 1. Crear o buscar película
        peli = Pelicula(id_pelicula=None, titulo=titulo, clasificacion_edad=clasif_num, duracion_minutos=100)
        peli_creada = PeliculaDAO.crear(peli)

        # 2. Crear función polimórfica según tipo
        if tipo_sel == "2D":
            func = Funcion2D(id_funcion=None, pelicula=peli_creada, fecha_hora=fecha, precio_base=precio_base, capacidad=capacidad)
        elif tipo_sel == "3D":
            func = Funcion3D(id_funcion=None, pelicula=peli_creada, fecha_hora=fecha, precio_base=precio_base, capacidad=capacidad)
        elif tipo_sel == "VIP":
            cap_vip = min(capacidad, 30)
            func = FuncionVIP(id_funcion=None, pelicula=peli_creada, fecha_hora=fecha, precio_base=precio_base, capacidad=cap_vip)
        else:
            func = Funcion2D(id_funcion=None, pelicula=peli_creada, fecha_hora=fecha, precio_base=precio_base, capacidad=capacidad)

        FuncionDAO.crear(func)
        messagebox.showinfo("Éxito", f"Función [{func.tipo}] '{titulo}' creada exitosamente.", parent=self)
        self.f_titulo.set("")
        self._refrescar_funciones()

    def _modificar_funcion(self):
        sel = self.tree_func.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione una función de la lista para modificar.", parent=self)
            return

        id_f = int(self.tree_func.item(sel[0])['values'][0])
        func = FuncionDAO.obtener_por_id(id_f)
        if not func:
            messagebox.showerror("Error", "No se encontró la función seleccionada.", parent=self)
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Modificar Función #{func.id_funcion} - {func.pelicula.titulo}")
        dlg.geometry("450x510")
        dlg.resizable(False, False)
        dlg.configure(bg=COLORS['bg_main'])
        dlg.transient(self)
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg=COLORS['header_bg'], height=50, highlightbackground=COLORS['border'], highlightthickness=1)
        hdr.pack(fill='x')
        tk.Label(hdr, text=f"✏️ EDITAR FUNCIÓN #{func.id_funcion}", font=FONTS['subtitle'], bg=COLORS['header_bg'], fg=COLORS['accent_gold']).pack(pady=10)

        body = tk.Frame(dlg, bg=COLORS['bg_panel'], padx=20, pady=12)
        body.pack(fill='both', expand=True, padx=14, pady=10)

        def form_campo(texto, var):
            tk.Label(body, text=texto, font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(3, 1))
            e = tk.Entry(body, textvariable=var, font=FONTS['body'])
            estilizar_entry(e)
            e.pack(fill='x', ipady=3, pady=(0, 4))
            return e

        var_tit = tk.StringVar(value=func.pelicula.titulo)
        form_campo("Título de la Película:", var_tit)

        tk.Label(body, text="Clasificación de Edad:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(3, 1))
        clasif_actual = f"{func.pelicula.clasificacion_edad} · " + ("Todo Espectador" if func.pelicula.clasificacion_edad == 0 else f"Mayores de {func.pelicula.clasificacion_edad}")
        var_clas = tk.StringVar(value=clasif_actual)
        cb_clas = ttk.Combobox(body, textvariable=var_clas, values=["0 · Todo Espectador", "7 · Mayores de 7", "14 · Mayores de 14", "18 · Solo Adultos"], state='readonly')
        cb_clas.pack(fill='x', pady=(0, 4))

        tk.Label(body, text="Tipo de Función:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(3, 1))
        var_tip = tk.StringVar(value=func.tipo)
        cb_tip = ttk.Combobox(body, textvariable=var_tip, values=["2D", "3D", "VIP"], state='readonly')
        cb_tip.pack(fill='x', pady=(0, 4))

        var_fec = tk.StringVar(value=func.fecha_hora)
        form_campo("Fecha y Hora (YYYY-MM-DD HH:MM):", var_fec)

        var_pre = tk.StringVar(value=str(func.precio_base))
        form_campo("Precio Base (CLP):", var_pre)

        var_cap = tk.StringVar(value=str(func.capacidad))
        form_campo("Capacidad de Asientos:", var_cap)

        def guardar():
            tit = var_tit.get().strip()
            if not tit:
                messagebox.showwarning("Atención", "El título no puede estar vacío.", parent=dlg)
                return
            try:
                pre = float(var_pre.get().replace(",", "."))
                cap = int(var_cap.get())
                clas_num = int(var_clas.get().split()[0])
            except ValueError:
                messagebox.showerror("Error", "Precio y capacidad deben ser valores numéricos válidos.", parent=dlg)
                return

            # Actualizar película asociada
            func.pelicula.titulo = tit
            func.pelicula.clasificacion_edad = clas_num
            PeliculaDAO.modificar(func.pelicula)

            # Validar cupos contra vendidos
            vendidos = func.asientos_vendidos
            if cap < vendidos:
                messagebox.showerror("Error", f"La capacidad ({cap}) no puede ser menor a los boletos ya vendidos ({vendidos}).", parent=dlg)
                return

            func.tipo = var_tip.get()
            func.fecha_hora = var_fec.get().strip()
            func.precio_base = pre
            func.capacidad = cap
            func.asientos_disponibles = cap - vendidos

            if func.tipo == "2D":
                func_mod = Funcion2D(id_funcion=func.id_funcion, pelicula=func.pelicula, fecha_hora=func.fecha_hora, precio_base=pre, capacidad=cap, asientos_disponibles=func.asientos_disponibles)
            elif func.tipo == "3D":
                func_mod = Funcion3D(id_funcion=func.id_funcion, pelicula=func.pelicula, fecha_hora=func.fecha_hora, precio_base=pre, capacidad=cap, asientos_disponibles=func.asientos_disponibles)
            elif func.tipo == "VIP":
                cap_vip = min(cap, 30)
                disp_vip = max(0, cap_vip - vendidos)
                func_mod = FuncionVIP(id_funcion=func.id_funcion, pelicula=func.pelicula, fecha_hora=func.fecha_hora, precio_base=pre, capacidad=cap_vip, asientos_disponibles=disp_vip)
            else:
                func_mod = func

            FuncionDAO.modificar(func_mod)
            messagebox.showinfo("Éxito", f"Función #{func.id_funcion} modificada correctamente.", parent=dlg)
            dlg.destroy()
            self._refrescar_funciones()

        btn_bar_dlg = tk.Frame(dlg, bg=COLORS['bg_main'], pady=8)
        btn_bar_dlg.pack(fill='x', padx=14)
        tk.Button(btn_bar_dlg, text="💾 GUARDAR CAMBIOS", font=FONTS['btn'], bg=COLORS['btn_green'], fg='white', relief='flat', padx=14, pady=6, command=guardar).pack(side='right', padx=4)
        tk.Button(btn_bar_dlg, text="Cancelar", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white', relief='flat', padx=14, pady=6, command=dlg.destroy).pack(side='right', padx=4)

    def _eliminar_funcion(self):
        sel = self.tree_func.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione una función de la lista para eliminar.", parent=self)
            return
        id_f = int(self.tree_func.item(sel[0])['values'][0])
        try:
            FuncionDAO.eliminar(id_f)
            messagebox.showinfo("Eliminada", f"Función ID {id_f} eliminada.", parent=self)
            self._refrescar_funciones()
        except ReglaNegocioException as e:
            messagebox.showerror("Operación Bloqueada", str(e), parent=self)

    # =========================================================================
    # TAB 2: CONFITERÍA
    # =========================================================================
    def _build_tab_productos(self):
        pane = self.tab_productos

        left = tk.Frame(pane, bg=COLORS['bg_main'])
        left.pack(side='left', fill='both', expand=True, padx=(8, 4), pady=8)

        tk.Label(left, text="Catálogo de Productos de Confitería", font=FONTS['subtitle'], bg=COLORS['bg_main'], fg=COLORS['accent_gold']).pack(anchor='w', pady=(0, 4))

        cols = ('ID', 'Nombre', 'Tipo / Origen', 'Precio Base', 'Precio Venta CLP')
        tf = tk.Frame(left, bg=COLORS['bg_main'])
        tf.pack(fill='both', expand=True)

        self.tree_prod = ttk.Treeview(tf, columns=cols, show='headings', style='Cine.Treeview', height=14)
        for c, w in zip(cols, [40, 240, 130, 130, 140]):
            self.tree_prod.heading(c, text=c)
            self.tree_prod.column(c, width=w, anchor='center' if c in ('ID', 'Tipo / Origen') else 'w')

        sb = ttk.Scrollbar(tf, orient='vertical', command=self.tree_prod.yview)
        self.tree_prod.configure(yscrollcommand=sb.set)
        self.tree_prod.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        btn_bar = tk.Frame(left, bg=COLORS['bg_main'], pady=8)
        btn_bar.pack(fill='x')
        tk.Button(
            btn_bar, text="✏️ Modificar Producto", font=FONTS['btn'], bg='#1b3a5c', fg='white',
            relief='flat', padx=12, pady=6, cursor='hand2', command=self._modificar_producto
        ).pack(side='left', padx=4)
        tk.Button(
            btn_bar, text="🗑️ Eliminar Producto", font=FONTS['btn'], bg='#661111', fg='white',
            relief='flat', padx=12, pady=6, cursor='hand2', command=self._eliminar_producto
        ).pack(side='left', padx=4)
        tk.Button(
            btn_bar, text="Refrescar Lista", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white',
            relief='flat', padx=12, pady=6, cursor='hand2', command=self._refrescar_productos
        ).pack(side='right', padx=4)

        # Formulario
        right = tk.Frame(pane, bg=COLORS['bg_panel'], width=340, padx=16, pady=12, highlightbackground=COLORS['border'], highlightthickness=1)
        right.pack(side='right', fill='y', padx=(4, 8), pady=8)
        right.pack_propagate(False)

        tk.Label(right, text="➕ Registrar Producto", font=FONTS['subtitle'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(anchor='w', pady=(0, 10))

        self.p_nombre = tk.StringVar()
        tk.Label(right, text="Nombre del Artículo:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w')
        e_nom = tk.Entry(right, textvariable=self.p_nombre, font=FONTS['body'])
        estilizar_entry(e_nom)
        e_nom.pack(fill='x', ipady=4, pady=(2, 8))

        tk.Label(right, text="Tipo de Producto:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w')
        self.p_tipo = tk.StringVar(value="Nacional (CLP)")
        cb_pt = ttk.Combobox(right, textvariable=self.p_tipo, values=["Nacional (CLP)", "Importado (USD)"], state='readonly')
        cb_pt.pack(fill='x', pady=(2, 8))

        # Espacio de ingreso con prefijo CLP o USD antepuesto
        row_precio = tk.Frame(right, bg=COLORS['bg_panel'])
        row_precio.pack(fill='x', pady=(6, 12))

        self.lbl_moneda_prod = tk.Label(row_precio, text="CLP $", font=FONTS['body_b'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold'], width=6, anchor='w')
        self.lbl_moneda_prod.pack(side='left')

        self.p_precio = tk.StringVar(value="2500")
        e_pre = tk.Entry(row_precio, textvariable=self.p_precio, font=FONTS['body'])
        estilizar_entry(e_pre)
        e_pre.pack(side='left', fill='x', expand=True, ipady=4)

        def on_tipo_prod_change(*args):
            if "Importado" in self.p_tipo.get():
                self.lbl_moneda_prod.configure(text="USD $")
            else:
                self.lbl_moneda_prod.configure(text="CLP $")
        self.p_tipo.trace_add("write", on_tipo_prod_change)

        tk.Button(
            right, text="💾 GUARDAR PRODUCTO", font=FONTS['btn'], bg=COLORS['accent_red'], fg='white',
            relief='flat', pady=8, cursor='hand2', command=self._guardar_producto
        ).pack(fill='x')

        self._refrescar_productos()

    def _refrescar_productos(self):
        for item in self.tree_prod.get_children():
            self.tree_prod.delete(item)

        tasa = self._tasa_dolar or 950.0
        for p in ProductoDAO.listar():
            if isinstance(p, ProductoImportado):
                base_str = f"USD ${p.precio_usd:.2f}"
                venta_str = f"${p.calcular_precio(tasa):,.0f} CLP"
            else:
                base_str = f"${p.precio_base:,.0f} CLP"
                venta_str = f"${p.calcular_precio():,.0f} CLP"

            self.tree_prod.insert('', 'end', values=(
                p.id_producto, p.nombre, p.tipo.capitalize(), base_str, venta_str
            ))

    def _guardar_producto(self):
        nom = self.p_nombre.get().strip()
        if not nom:
            messagebox.showwarning("Atención", "Ingrese el nombre del producto.", parent=self)
            return
        try:
            precio = float(self.p_precio.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "El precio base debe ser numérico.", parent=self)
            return

        if "Importado" in self.p_tipo.get():
            prod = ProductoImportado(id_producto=None, nombre=nom, precio_base_usd=precio)
        else:
            prod = ProductoNacional(id_producto=None, nombre=nom, precio_base=precio)

        ProductoDAO.crear(prod)
        messagebox.showinfo("Éxito", f"Producto '{nom}' registrado correctamente.", parent=self)
        self.p_nombre.set("")
        self._refrescar_productos()

    def _modificar_producto(self):
        sel = self.tree_prod.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un producto de la lista para modificar.", parent=self)
            return

        id_p = int(self.tree_prod.item(sel[0])['values'][0])
        prod = ProductoDAO.obtener_por_id(id_p)
        if not prod:
            messagebox.showerror("Error", "No se encontró el producto seleccionado.", parent=self)
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Modificar Producto #{prod.id_producto} - {prod.nombre}")
        dlg.geometry("420x340")
        dlg.resizable(False, False)
        dlg.configure(bg=COLORS['bg_main'])
        dlg.transient(self)
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg=COLORS['header_bg'], height=50, highlightbackground=COLORS['border'], highlightthickness=1)
        hdr.pack(fill='x')
        tk.Label(hdr, text=f"✏️ EDITAR PRODUCTO #{prod.id_producto}", font=FONTS['subtitle'], bg=COLORS['header_bg'], fg=COLORS['accent_gold']).pack(pady=10)

        body = tk.Frame(dlg, bg=COLORS['bg_panel'], padx=20, pady=12)
        body.pack(fill='both', expand=True, padx=14, pady=10)

        tk.Label(body, text="Nombre del Artículo:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(2, 1))
        var_nom = tk.StringVar(value=prod.nombre)
        e_n = tk.Entry(body, textvariable=var_nom, font=FONTS['body'])
        estilizar_entry(e_n)
        e_n.pack(fill='x', ipady=3, pady=(0, 6))

        tk.Label(body, text="Tipo de Producto:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(2, 1))
        tipo_actual = "Importado (USD)" if isinstance(prod, ProductoImportado) else "Nacional (CLP)"
        var_t = tk.StringVar(value=tipo_actual)
        cb_t = ttk.Combobox(body, textvariable=var_t, values=["Nacional (CLP)", "Importado (USD)"], state='readonly')
        cb_t.pack(fill='x', pady=(0, 6))

        row_pre = tk.Frame(body, bg=COLORS['bg_panel'])
        row_pre.pack(fill='x', pady=(6, 8))

        prefix_moneda = "USD $" if isinstance(prod, ProductoImportado) else "CLP $"
        lbl_m = tk.Label(row_pre, text=prefix_moneda, font=FONTS['body_b'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold'], width=6, anchor='w')
        lbl_m.pack(side='left')

        val_precio = str(prod.precio_usd if isinstance(prod, ProductoImportado) else prod.precio_base)
        var_p = tk.StringVar(value=val_precio)
        e_p = tk.Entry(row_pre, textvariable=var_p, font=FONTS['body'])
        estilizar_entry(e_p)
        e_p.pack(side='left', fill='x', expand=True, ipady=3)

        def on_dlg_tipo_change(*args):
            if "Importado" in var_t.get():
                lbl_m.configure(text="USD $")
            else:
                lbl_m.configure(text="CLP $")
        var_t.trace_add("write", on_dlg_tipo_change)

        def guardar():
            nom = var_nom.get().strip()
            if not nom:
                messagebox.showwarning("Atención", "El nombre no puede estar vacío.", parent=dlg)
                return
            try:
                p_num = float(var_p.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Error", "El precio debe ser un número válido.", parent=dlg)
                return

            if "Importado" in var_t.get():
                p_mod = ProductoImportado(id_producto=prod.id_producto, nombre=nom, precio_base_usd=p_num)
            else:
                p_mod = ProductoNacional(id_producto=prod.id_producto, nombre=nom, precio_base=p_num)

            ProductoDAO.modificar(p_mod)
            messagebox.showinfo("Éxito", f"Producto '{nom}' modificado correctamente.", parent=dlg)
            dlg.destroy()
            self._refrescar_productos()

        btn_bar_dlg = tk.Frame(dlg, bg=COLORS['bg_main'], pady=8)
        btn_bar_dlg.pack(fill='x', padx=14)
        tk.Button(btn_bar_dlg, text="💾 GUARDAR CAMBIOS", font=FONTS['btn'], bg=COLORS['btn_green'], fg='white', relief='flat', padx=14, pady=6, command=guardar).pack(side='right', padx=4)
        tk.Button(btn_bar_dlg, text="Cancelar", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white', relief='flat', padx=14, pady=6, command=dlg.destroy).pack(side='right', padx=4)

    def _eliminar_producto(self):
        sel = self.tree_prod.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un producto para eliminar.", parent=self)
            return
        id_p = int(self.tree_prod.item(sel[0])['values'][0])
        try:
            ProductoDAO.eliminar(id_p)
            messagebox.showinfo("Eliminado", f"Producto ID {id_p} eliminado.", parent=self)
            self._refrescar_productos()
        except ReglaNegocioException as e:
            messagebox.showerror("Operación Bloqueada", str(e), parent=self)

    # =========================================================================
    # TAB 3: TRABAJADORES
    # =========================================================================
    def _build_tab_trabajadores(self):
        pane = self.tab_trabajadores

        left = tk.Frame(pane, bg=COLORS['bg_main'])
        left.pack(side='left', fill='both', expand=True, padx=(8, 4), pady=8)

        tk.Label(left, text="Personal Registrado en el Sistema", font=FONTS['subtitle'], bg=COLORS['bg_main'], fg=COLORS['accent_gold']).pack(anchor='w', pady=(0, 4))

        cols = ('ID', 'Nombre Completo', 'Usuario (Login)', 'Contraseña', 'Rol Asignado')
        tf = tk.Frame(left, bg=COLORS['bg_main'])
        tf.pack(fill='both', expand=True)

        self.tree_trab = ttk.Treeview(tf, columns=cols, show='headings', style='Cine.Treeview', height=14)
        for c, w in zip(cols, [45, 200, 130, 120, 140]):
            self.tree_trab.heading(c, text=c)
            self.tree_trab.column(c, width=w, anchor='w' if c != 'ID' else 'center')

        sb = ttk.Scrollbar(tf, orient='vertical', command=self.tree_trab.yview)
        self.tree_trab.configure(yscrollcommand=sb.set)
        self.tree_trab.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        btn_bar = tk.Frame(left, bg=COLORS['bg_main'], pady=8)
        btn_bar.pack(fill='x')
        tk.Button(
            btn_bar, text="✏️ Modificar Trabajador", font=FONTS['btn'], bg='#1b3a5c', fg='white',
            relief='flat', padx=12, pady=6, cursor='hand2', command=self._modificar_trabajador
        ).pack(side='left', padx=4)
        tk.Button(
            btn_bar, text="🗑️ Eliminar Trabajador", font=FONTS['btn'], bg='#661111', fg='white',
            relief='flat', padx=12, pady=6, cursor='hand2', command=self._eliminar_trabajador
        ).pack(side='left', padx=4)
        tk.Button(
            btn_bar, text="Refrescar Lista", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white',
            relief='flat', padx=12, pady=6, cursor='hand2', command=self._refrescar_trabajadores
        ).pack(side='right', padx=4)

        # Formulario
        right = tk.Frame(pane, bg=COLORS['bg_panel'], width=340, padx=16, pady=12, highlightbackground=COLORS['border'], highlightthickness=1)
        right.pack(side='right', fill='y', padx=(4, 8), pady=8)
        right.pack_propagate(False)

        tk.Label(right, text="➕ Crear Nuevo Operador", font=FONTS['subtitle'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(anchor='w', pady=(0, 10))

        self.t_nombre = tk.StringVar()
        tk.Label(right, text="Nombre Completo:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w')
        e_nom = tk.Entry(right, textvariable=self.t_nombre, font=FONTS['body'])
        estilizar_entry(e_nom)
        e_nom.pack(fill='x', ipady=4, pady=(2, 6))

        self.t_user = tk.StringVar()
        tk.Label(right, text="Usuario Login:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w')
        e_usr = tk.Entry(right, textvariable=self.t_user, font=FONTS['body'])
        estilizar_entry(e_usr)
        e_usr.pack(fill='x', ipady=4, pady=(2, 6))

        self.t_pass = tk.StringVar()
        tk.Label(right, text="Contraseña (Visible):", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w')
        e_pwd = tk.Entry(right, textvariable=self.t_pass, font=FONTS['body'])
        estilizar_entry(e_pwd)
        e_pwd.pack(fill='x', ipady=4, pady=(2, 6))

        tk.Label(right, text="Rol y Caja de Trabajo:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w')
        self.t_rol = tk.StringVar(value="Boletero (Venta de Entradas)")
        cb_tr = ttk.Combobox(right, textvariable=self.t_rol, values=["Boletero (Venta de Entradas)", "Encargado de Dulcería (Snacks)"], state='readonly')
        cb_tr.pack(fill='x', pady=(2, 10))

        tk.Button(
            right, text="💾 CREAR TRABAJADOR", font=FONTS['btn'], bg=COLORS['accent_red'], fg='white',
            relief='flat', pady=8, cursor='hand2', command=self._guardar_trabajador
        ).pack(fill='x')

        self._refrescar_trabajadores()

    def _refrescar_trabajadores(self):
        for item in self.tree_trab.get_children():
            self.tree_trab.delete(item)
        for t in TrabajadorDAO.listar():
            pwd = getattr(t, 'password_plano', '') or "1234"
            is_adm = t.username.lower() == 'admin' or t.rol.lower() == 'admin'
            tag = 'admin_tag' if is_adm else 'normal_tag'
            rol_txt = "ADMINISTRACIÓN (SISTEMA)" if is_adm else t.rol.upper()
            self.tree_trab.insert('', 'end', values=(t.id_trabajador, t.nombre, t.username, pwd, rol_txt), tags=(tag,))
        self.tree_trab.tag_configure('admin_tag', foreground=COLORS['accent_gold'])

    def _guardar_trabajador(self):
        nom = self.t_nombre.get().strip()
        usr = self.t_user.get().strip()
        pwd = self.t_pass.get().strip()
        if not nom or not usr or not pwd:
            messagebox.showwarning("Atención", "Complete todos los campos del trabajador.", parent=self)
            return

        if usr.lower() == "admin":
            messagebox.showerror("Nombre Reservado", "El nombre de usuario 'admin' es una funcionalidad del sistema y está reservado.", parent=self)
            return

        hash_pwd = Trabajador.generar_hash(pwd)
        if "Boletero" in self.t_rol.get():
            t = Boletero(id_trabajador=None, nombre=nom, username=usr, password_hash=hash_pwd, password_plano=pwd)
        else:
            t = EncargadoDulceria(id_trabajador=None, nombre=nom, username=usr, password_hash=hash_pwd, password_plano=pwd)

        try:
            TrabajadorDAO.crear(t)
            messagebox.showinfo("Éxito", f"Trabajador '{nom}' creado exitosamente.", parent=self)
            self.t_nombre.set("")
            self.t_user.set("")
            self.t_pass.set("")
            self._refrescar_trabajadores()
        except Exception as e:
            messagebox.showerror("Error", f"No fue posible registrar: {e}", parent=self)

    def _modificar_trabajador(self):
        sel = self.tree_trab.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un trabajador para modificar.", parent=self)
            return

        id_t = int(self.tree_trab.item(sel[0])['values'][0])
        trab = TrabajadorDAO.obtener_por_id(id_t)
        if not trab:
            messagebox.showerror("Error", "No se encontró el trabajador seleccionado.", parent=self)
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Modificar Trabajador #{trab.id_trabajador} - {trab.nombre}")
        dlg.geometry("420x390")
        dlg.resizable(False, False)
        dlg.configure(bg=COLORS['bg_main'])
        dlg.transient(self)
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg=COLORS['header_bg'], height=50, highlightbackground=COLORS['border'], highlightthickness=1)
        hdr.pack(fill='x')
        tk.Label(hdr, text=f"✏️ EDITAR TRABAJADOR #{trab.id_trabajador}", font=FONTS['subtitle'], bg=COLORS['header_bg'], fg=COLORS['accent_gold']).pack(pady=10)

        body = tk.Frame(dlg, bg=COLORS['bg_panel'], padx=20, pady=12)
        body.pack(fill='both', expand=True, padx=14, pady=10)

        tk.Label(body, text="Nombre Completo:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(2, 1))
        var_nom = tk.StringVar(value=trab.nombre)
        e_n = tk.Entry(body, textvariable=var_nom, font=FONTS['body'])
        estilizar_entry(e_n)
        e_n.pack(fill='x', ipady=3, pady=(0, 6))

        tk.Label(body, text="Usuario Login:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(2, 1))
        var_usr = tk.StringVar(value=trab.username)
        e_u = tk.Entry(body, textvariable=var_usr, font=FONTS['body'])
        estilizar_entry(e_u)
        e_u.pack(fill='x', ipady=3, pady=(0, 6))
        if trab.username.lower() == "admin":
            e_u.configure(state='disabled')

        tk.Label(body, text="Contraseña (Visible):", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(2, 1))
        pwd_actual = getattr(trab, 'password_plano', '') or "1234"
        var_pwd = tk.StringVar(value=pwd_actual)
        e_p = tk.Entry(body, textvariable=var_pwd, font=FONTS['body'])
        estilizar_entry(e_p)
        e_p.pack(fill='x', ipady=3, pady=(0, 6))

        tk.Label(body, text="Rol Asignado:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(anchor='w', pady=(2, 1))
        rol_desc = "Administrador (Sistema)" if trab.rol == "admin" else ("Boletero (Venta de Entradas)" if trab.rol == "boletero" else "Encargado de Dulcería (Snacks)")
        var_r = tk.StringVar(value=rol_desc)
        cb_r = ttk.Combobox(body, textvariable=var_r, values=["Boletero (Venta de Entradas)", "Encargado de Dulcería (Snacks)", "Administrador (Sistema)"], state='readonly')
        cb_r.pack(fill='x', pady=(0, 8))
        if trab.username.lower() == "admin":
            cb_r.configure(state='disabled')

        def guardar():
            n = var_nom.get().strip()
            u = "admin" if trab.username.lower() == "admin" else var_usr.get().strip()
            p = var_pwd.get().strip()
            if not n or not u or not p:
                messagebox.showwarning("Atención", "Todos los campos son obligatorios.", parent=dlg)
                return

            nuevo_hash = Trabajador.generar_hash(p)
            if trab.username.lower() == "admin":
                rol_sel = "admin"
            else:
                rol_sel = "boletero" if "Boletero" in var_r.get() else ("dulceria" if "Dulcería" in var_r.get() else "admin")

            if rol_sel == "boletero":
                t_mod = Boletero(id_trabajador=trab.id_trabajador, nombre=n, username=u, password_hash=nuevo_hash, password_plano=p)
            elif rol_sel == "dulceria":
                t_mod = EncargadoDulceria(id_trabajador=trab.id_trabajador, nombre=n, username=u, password_hash=nuevo_hash, password_plano=p)
            else:
                t_mod = Trabajador(id_trabajador=trab.id_trabajador, nombre=n, username=u, password_hash=nuevo_hash, rol=rol_sel, password_plano=p)

            TrabajadorDAO.modificar(t_mod)
            messagebox.showinfo("Éxito", f"Trabajador '{n}' modificado correctamente.", parent=dlg)
            dlg.destroy()
            self._refrescar_trabajadores()

        btn_bar_dlg = tk.Frame(dlg, bg=COLORS['bg_main'], pady=8)
        btn_bar_dlg.pack(fill='x', padx=14)
        tk.Button(btn_bar_dlg, text="💾 GUARDAR CAMBIOS", font=FONTS['btn'], bg=COLORS['btn_green'], fg='white', relief='flat', padx=14, pady=6, command=guardar).pack(side='right', padx=4)
        tk.Button(btn_bar_dlg, text="Cancelar", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white', relief='flat', padx=14, pady=6, command=dlg.destroy).pack(side='right', padx=4)

    def _eliminar_trabajador(self):
        sel = self.tree_trab.selection()
        if not sel:
            messagebox.showwarning("Seleccionar", "Seleccione un trabajador para eliminar.", parent=self)
            return
        vals = self.tree_trab.item(sel[0])['values']
        id_t = int(vals[0])
        usr_t = str(vals[2]).strip().lower()
        rol_t = str(vals[4]).strip().lower()

        if usr_t == "admin" or "admin" in rol_t:
            messagebox.showerror(
                "Operación Bloqueada",
                "No es posible eliminar el Administrador ('admin'). Es una funcionalidad del sistema, no un operador eliminable.",
                parent=self
            )
            return

        try:
            TrabajadorDAO.eliminar(id_t)
            messagebox.showinfo("Eliminado", f"Trabajador ID {id_t} eliminado.", parent=self)
            self._refrescar_trabajadores()
        except ReglaNegocioException as e:
            messagebox.showerror("Operación Bloqueada", str(e), parent=self)

    # =========================================================================
    # TAB 4: REPORTES Y AUDITORÍA (POR FOLIO Y DETALLE DINÁMICO)
    # =========================================================================
    def _build_tab_reportes(self):
        pane = self.tab_reportes

        # 1. Barra superior: Búsqueda y Estadísticas
        bar_top = tk.Frame(pane, bg=COLORS['bg_panel'], padx=14, pady=8, highlightbackground=COLORS['border'], highlightthickness=1)
        bar_top.pack(fill='x', padx=8, pady=(8, 4))

        tk.Label(bar_top, text="📋 Reportes de Ventas por Folio:", font=FONTS['subtitle'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(side='left', padx=(0, 12))

        tk.Label(bar_top, text="Buscar Folio:", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']).pack(side='left', padx=(0, 4))
        self.var_folio_busq = tk.StringVar()
        e_fb = tk.Entry(bar_top, textvariable=self.var_folio_busq, width=10, font=FONTS['body'])
        estilizar_entry(e_fb)
        e_fb.pack(side='left', padx=(0, 6), ipady=2)
        e_fb.bind("<Return>", lambda e: self._buscar_y_seleccionar_folio())

        tk.Button(
            bar_top, text="🔍 Buscar Folio", font=FONTS['small_b'], bg='#1b3a5c', fg='white',
            relief='flat', padx=10, pady=4, cursor='hand2', command=self._buscar_y_seleccionar_folio
        ).pack(side='left', padx=4)

        tk.Button(
            bar_top, text="🔄 Refrescar Listado", font=FONTS['small_b'], bg=COLORS['btn_gray'], fg='white',
            relief='flat', padx=10, pady=4, cursor='hand2', command=self._refrescar_ventas_reporte
        ).pack(side='left', padx=4)

        self.lbl_ventas_resumen = tk.Label(bar_top, text="", font=FONTS['body_b'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold'])
        self.lbl_ventas_resumen.pack(side='right', padx=10)

        # 2. Tabla Superior: Listado de Ventas por Folio
        top_frame = tk.Frame(pane, bg=COLORS['bg_main'])
        top_frame.pack(fill='both', expand=True, padx=8, pady=2)

        tk.Label(
            top_frame, text="Listado de Folios Registrados (Haga clic en una fila para ver el detalle de ítems):",
            font=FONTS['small'], bg=COLORS['bg_main'], fg=COLORS['text_muted']
        ).pack(anchor='w', pady=(0, 2))

        cols_v = ('Folio', 'Fecha y Hora', 'Cliente / RUT', 'Total Venta', 'Cant. Ítems')
        tf_v = tk.Frame(top_frame, bg=COLORS['bg_main'])
        tf_v.pack(fill='both', expand=True)

        self.tree_ventas = ttk.Treeview(tf_v, columns=cols_v, show='headings', style='Cine.Treeview', height=7)
        ws_v = [90, 180, 260, 150, 110]
        for c, w in zip(cols_v, ws_v):
            self.tree_ventas.heading(c, text=c)
            self.tree_ventas.column(c, width=w, anchor='center' if c in ('Folio', 'Total Venta', 'Cant. Ítems') else 'w')

        sb_v = ttk.Scrollbar(tf_v, orient='vertical', command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=sb_v.set)
        self.tree_ventas.pack(side='left', fill='both', expand=True)
        sb_v.pack(side='right', fill='y')

        # Eventos para seleccionar y cargar detalle
        self.tree_ventas.bind("<<TreeviewSelect>>", self._on_venta_seleccionada)

        # Separador visual
        tk.Frame(pane, bg=COLORS['border'], height=2).pack(fill='x', padx=8, pady=4)

        # 3. Contenedor Inferior: Detalle del Folio Seleccionado
        bottom_frame = tk.Frame(pane, bg=COLORS['bg_panel'], padx=12, pady=8, highlightbackground=COLORS['border'], highlightthickness=1)
        bottom_frame.pack(fill='both', expand=True, padx=8, pady=(0, 6))

        self.lbl_rep_cabecera = tk.Label(
            bottom_frame, text="🔍 Detalle de la Venta (Seleccione un folio en la tabla superior)",
            font=FONTS['subtitle'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']
        )
        self.lbl_rep_cabecera.pack(anchor='w', pady=(0, 4))

        cols_d = ('N°', 'Tipo', 'Descripción del Ítem', 'Cantidad', 'Unitario', 'Subtotal', 'Atendido Por')
        self.tree_rep = ttk.Treeview(bottom_frame, columns=cols_d, show='headings', style='Cine.Treeview', height=6)
        ws_d = [45, 90, 360, 80, 110, 120, 150]
        for c, w in zip(cols_d, ws_d):
            self.tree_rep.heading(c, text=c)
            self.tree_rep.column(c, width=w, anchor='center' if c in ('N°', 'Tipo', 'Cantidad') else ('e' if c in ('Unitario', 'Subtotal') else 'w'))

        sb_d = ttk.Scrollbar(bottom_frame, orient='vertical', command=self.tree_rep.yview)
        self.tree_rep.configure(yscrollcommand=sb_d.set)
        self.tree_rep.pack(side='left', fill='both', expand=True)
        sb_d.pack(side='right', fill='y')

        self.lbl_rep_total = tk.Label(
            bottom_frame, text="Seleccione un folio para ver sus detalles.",
            font=FONTS['body_b'], bg=COLORS['bg_panel'], fg=COLORS['text_light']
        )
        self.lbl_rep_total.pack(pady=(4, 0))

        # Cargar ventas inicialmente
        self._refrescar_ventas_reporte()

    def _refrescar_ventas_reporte(self):
        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)
        for item in self.tree_rep.get_children():
            self.tree_rep.delete(item)

        ventas = VentaDAO.listar_todas()
        total_acumulado = 0.0

        for v in ventas:
            total_acumulado += v.total
            rut_str = f"{v.cliente.nombre} ({v.cliente.rut})" if v.cliente else "Público General"
            cant_items = sum(d.cantidad for d in v.detalles)
            self.tree_ventas.insert(
                '', 'end',
                iid=str(v.id_venta),
                values=(
                    f"#{v.id_venta}",
                    v.fecha_hora,
                    rut_str,
                    f"${v.total:,.0f} CLP",
                    f"{cant_items} item(s)"
                )
            )

        self.lbl_ventas_resumen.configure(
            text=f"Total Ventas: {len(ventas)}  |  Recaudación Global: ${total_acumulado:,.0f} CLP"
        )
        self.lbl_rep_cabecera.configure(
            text="🔍 Detalle de la Venta (Seleccione un folio en la tabla superior)"
        )
        self.lbl_rep_total.configure(
            text="Seleccione un folio de la tabla superior para ver sus detalles."
        )

        children = self.tree_ventas.get_children()
        if children:
            self.tree_ventas.selection_set(children[0])
            self.tree_ventas.focus(children[0])
            self._mostrar_detalle_folio(int(children[0]))

    def _on_venta_seleccionada(self, event=None):
        sel = self.tree_ventas.selection()
        if not sel:
            return
        id_str = sel[0]
        try:
            id_v = int(id_str)
            self._mostrar_detalle_folio(id_v)
        except ValueError:
            pass

    def _mostrar_detalle_folio(self, id_venta: int):
        venta = VentaDAO.obtener_por_id(id_venta)
        for item in self.tree_rep.get_children():
            self.tree_rep.delete(item)

        if not venta:
            self.lbl_rep_cabecera.configure(text=f"Folio #{id_venta} no encontrado.")
            self.lbl_rep_total.configure(text="")
            return

        trabajadores_map = {t.id_trabajador: f"{t.nombre} ({t.rol})" for t in TrabajadorDAO.listar()}

        for idx, d in enumerate(venta.detalles, 1):
            cajero_str = trabajadores_map.get(d.id_trabajador, f"ID #{d.id_trabajador}")
            self.tree_rep.insert(
                '', 'end',
                values=(
                    idx,
                    d.tipo_item.capitalize(),
                    d.descripcion,
                    d.cantidad,
                    f"${d.precio_unitario:,.0f}",
                    f"${d.subtotal:,.0f}",
                    cajero_str
                )
            )

        rut_nom = f"{venta.cliente.nombre} (RUT: {venta.cliente.rut}, {venta.cliente.edad} años)" if venta.cliente else "Público General"
        self.lbl_rep_cabecera.configure(
            text=f"📄 Detalle del Folio #{venta.id_venta}  ·  Fecha: {venta.fecha_hora}  ·  Cliente: {rut_nom}"
        )
        self.lbl_rep_total.configure(
            text=f"FOLIO #{venta.id_venta}  ·  Líneas: {len(venta.detalles)}  ·  TOTAL PAGADO: ${venta.total:,.0f} CLP",
            fg=COLORS['accent_gold']
        )

    def _buscar_y_seleccionar_folio(self):
        f_str = self.var_folio_busq.get().strip().replace("#", "")
        if not f_str.isdigit():
            messagebox.showwarning("Atención", "Ingrese un número de folio a buscar.", parent=self)
            return

        id_v = int(f_str)
        iid = str(id_v)
        if self.tree_ventas.exists(iid):
            self.tree_ventas.selection_set(iid)
            self.tree_ventas.focus(iid)
            self.tree_ventas.see(iid)
            self._mostrar_detalle_folio(id_v)
        else:
            venta = VentaDAO.obtener_por_id(id_v)
            if venta:
                self._refrescar_ventas_reporte()
                if self.tree_ventas.exists(iid):
                    self.tree_ventas.selection_set(iid)
                    self.tree_ventas.focus(iid)
                    self.tree_ventas.see(iid)
                self._mostrar_detalle_folio(id_v)
            else:
                messagebox.showinfo("No Encontrado", f"No se encontró ninguna venta registrada con el Folio #{id_v}.", parent=self)

    # =========================================================================
    # TAB 5: DÓLAR EN TIEMPO REAL
    # =========================================================================
    def _build_tab_dolar(self):
        pane = self.tab_dolar

        card = tk.Frame(pane, bg=COLORS['bg_panel'], padx=30, pady=24, highlightbackground=COLORS['accent_gold'], highlightthickness=2)
        card.place(relx=0.5, rely=0.4, anchor='center', width=540, height=280)

        tk.Label(card, text="💵 TIPO DE CAMBIO EN TIEMPO REAL", font=FONTS['title'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(pady=(0, 6))
        tk.Label(card, text="Integración oficial con Banco Central de Chile vía mindicador.cl", font=FONTS['small'], bg=COLORS['bg_panel'], fg=COLORS['text_muted']).pack(pady=(0, 14))

        self.lbl_dolar_big = tk.Label(card, text=f"${self._tasa_dolar:,.2f} CLP", font=('Helvetica', 34, 'bold'), bg=COLORS['bg_panel'], fg='white')
        self.lbl_dolar_big.pack(pady=6)

        self.lbl_dolar_info = tk.Label(card, text="Cotización oficial obtenida exitosamente.", font=FONTS['body'], bg=COLORS['bg_panel'], fg='#88ff88')
        self.lbl_dolar_info.pack(pady=(0, 14))

        tk.Button(
            card, text="🔄 ACTUALIZAR VALOR DESDE LA API", font=FONTS['btn'], bg=COLORS['accent_red'],
            fg='white', relief='flat', padx=18, pady=8, cursor='hand2', command=self._consultar_dolar_api
        ).pack()

    def _consultar_dolar_api(self):
        try:
            tc = TipoCambioService.obtener_dolar_dia()
            self._tasa_dolar = tc.valor
            self.lbl_dolar_big.configure(text=f"${tc.valor:,.2f} CLP")
            self.lbl_dolar_info.configure(text=f"Actualizado hoy ({tc.fecha}) vía {tc.fuente}", fg='#88ff88')
            self._refrescar_productos()
            messagebox.showinfo("Dólar Actualizado", f"Tipo de cambio oficial: ${tc.valor:,.2f} CLP", parent=self)
        except ReglaNegocioException as e:
            self.lbl_dolar_info.configure(text=f"Aviso de red: {e}", fg='#ffaa00')
            messagebox.showwarning("Aviso de Conexión", str(e), parent=self)
