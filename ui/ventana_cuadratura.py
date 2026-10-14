"""
Modal visual para consulta de cuadratura de caja por trabajador.
"""
import tkinter as tk
from tkinter import ttk
from ui.estilos import COLORS, FONTS
from dao.venta_dao import VentaDAO
from model.trabajador import Trabajador


class VentanaCuadratura(tk.Toplevel):
    def __init__(self, parent, trabajador: Trabajador):
        super().__init__(parent)
        self.trabajador = trabajador
        self.title(f"Cuadratura de Caja — {trabajador.nombre}")
        self.geometry("540x520")
        self.resizable(False, False)
        self.configure(bg=COLORS['bg_main'])
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Cabecera
        hdr = tk.Frame(self, bg=COLORS['header_bg'], height=60, highlightbackground=COLORS['border'], highlightthickness=1)
        hdr.pack(fill='x')
        tk.Label(hdr, text="📊 CUADRATURA DE CAJA", font=FONTS['title'], bg=COLORS['header_bg'], fg=COLORS['accent_gold']).pack(pady=(10, 2))
        tk.Label(hdr, text=f"Operador: {self.trabajador.nombre} · Rol: {self.trabajador.rol.upper()}", font=FONTS['small'], bg=COLORS['header_bg'], fg=COLORS['text_muted']).pack()

        # Datos de la cuadratura
        cuad = VentaDAO.obtener_cuadratura_trabajador(self.trabajador.id_trabajador)

        cards = tk.Frame(self, bg=COLORS['bg_main'], pady=12)
        cards.pack(fill='x', padx=20)

        # Resumen superior
        c1 = tk.Frame(cards, bg=COLORS['bg_panel'], padx=12, pady=10, highlightbackground=COLORS['border'], highlightthickness=1)
        c1.pack(side='left', fill='both', expand=True, padx=4)
        tk.Label(c1, text="Total Recaudado", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_muted']).pack()
        tk.Label(c1, text=f"${cuad['total_recaudado']:,.0f}", font=FONTS['amount'], bg=COLORS['bg_panel'], fg=COLORS['accent_gold']).pack(pady=4)
        tk.Label(c1, text="Pesos Chilenos (CLP)", font=FONTS['small'], bg=COLORS['bg_panel'], fg=COLORS['text_muted']).pack()

        c2 = tk.Frame(cards, bg=COLORS['bg_panel'], padx=12, pady=10, highlightbackground=COLORS['border'], highlightthickness=1)
        c2.pack(side='left', fill='both', expand=True, padx=4)
        tk.Label(c2, text="Operaciones", font=FONTS['small_b'], bg=COLORS['bg_panel'], fg=COLORS['text_muted']).pack()
        if self.trabajador.rol == "boletero":
            tk.Label(c2, text=f"{cuad['total_entradas']} boletos", font=FONTS['price'], bg=COLORS['bg_panel'], fg='#88ff88').pack(pady=4)
        else:
            tk.Label(c2, text=f"{cuad['total_productos']} snacks", font=FONTS['price'], bg=COLORS['bg_panel'], fg='#88ff88').pack(pady=4)
        tk.Label(c2, text=f"{cuad['transacciones']} transacciones", font=FONTS['small'], bg=COLORS['bg_panel'], fg=COLORS['text_muted']).pack()

        # Tabla de desglose
        tk.Label(self, text="Desglose por Concepto / Producto:", font=FONTS['body_b'], bg=COLORS['bg_main'], fg=COLORS['text_light']).pack(anchor='w', padx=20, pady=(6, 4))

        tree_f = tk.Frame(self, bg=COLORS['bg_main'])
        tree_f.pack(fill='both', expand=True, padx=20, pady=(0, 10))

        cols = ('Concepto', 'Cant.', 'Subtotal')
        tree = ttk.Treeview(tree_f, columns=cols, show='headings', style='Cine.Treeview', height=6)
        tree.heading('Concepto', text='Concepto / Artículo')
        tree.heading('Cant.', text='Cant.')
        tree.heading('Subtotal', text='Subtotal')
        tree.column('Concepto', width=260)
        tree.column('Cant.', width=60, anchor='center')
        tree.column('Subtotal', width=120, anchor='e')

        sb = ttk.Scrollbar(tree_f, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        for d in cuad.get('desglose', []):
            tree.insert('', 'end', values=(d['descripcion'], d['cantidad_total'], f"${d['subtotal_total']:,.0f}"))

        # Botón Cerrar
        btn_f = tk.Frame(self, bg=COLORS['bg_main'], pady=10)
        btn_f.pack(fill='x', padx=20)
        tk.Button(
            btn_f, text="Cerrar Cuadratura", font=FONTS['btn'], bg=COLORS['btn_gray'], fg='white',
            relief='flat', padx=20, pady=8, cursor='hand2', command=self.destroy
        ).pack(side='right')
