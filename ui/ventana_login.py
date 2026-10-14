"""
Ventana de autenticación visual con diseño cinematográfico de Cine Estrella.
Permite iniciar sesión por rol; cada rol abre su propia pantalla.

Fondo: ./fondos/fondo_principal.jpg (si lo reemplazas, cambia solo, sin reiniciar).
"""
import tkinter as tk
from tkinter import ttk, messagebox

from ui import fondos
from ui.componentes import BotonCanvas, BotonModerno, rect_redondeado
from ui.estilos import (COLORS, FONTS, FUENTE, RUTA_FONDOS,
                        aplicar_estilos_ttk, estilizar_entry)
from service.auth_service import AuthService
from dao.trabajador_dao import TrabajadorDAO

if fondos.HAY_PIL:
    from PIL import Image, ImageTk


class VentanaLogin(tk.Tk):
    W, H = 960, 620
    NOMBRE_FONDO = 'fondo_principal'
    CARD = (260, 166, 700, 526)          # caja de vidrio del formulario (x0, y0, x1, y1)

    def __init__(self):
        super().__init__()
        self.title("CINE ESTRELLA — Sistema Integrado de Gestión")
        x, y = (self.winfo_screenwidth() - self.W) // 2, (self.winfo_screenheight() - self.H) // 3
        self.geometry(f"{self.W}x{self.H}+{max(0, x)}+{max(0, y)}")
        self.resizable(False, False)
        self.configure(bg=COLORS['bg_main'])

        aplicar_estilos_ttk(self)
        self.auth = AuthService()

        self.var_user = tk.StringVar()
        self.var_pass = tk.StringVar()
        self._escena, self._foto, self._focos, self._encendido = None, None, [], True

        self.canvas = tk.Canvas(self, width=self.W, height=self.H, bg=COLORS['bg_main'],
                                highlightthickness=0, bd=0)
        self.canvas.pack()
        self._build_ui()

        fondos.asegurar_fondos(RUTA_FONDOS)
        self._refrescar_fondo()
        self.vigia = fondos.FondoDinamico(self, RUTA_FONDOS, self.NOMBRE_FONDO,
                                          self._refrescar_fondo)
        self.vigia.iniciar()
        self._parpadeo()
        self.e_user.focus_set()

    # ── Diseño ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        c, W, H = self.canvas, self.W, self.H
        self._img_id = c.create_image(0, 0, anchor='nw')

        # Marquesina: foquitos que parpadean + título
        for x in range(30, W - 10, 34):
            self._focos.append(c.create_oval(x - 5, 16, x + 5, 26, fill='#ffd700', outline=''))
        c.create_text(W // 2 + 2, 74, text="★  CINE ESTRELLA  ★", fill='#000000', font=FONTS['hero'])
        c.create_text(W // 2, 72, text="★  CINE ESTRELLA  ★", fill=COLORS['accent_gold'], font=FONTS['hero'])
        c.create_text(W // 2, 116, text="Sistema de Gestión y Punto de Venta — Versión 3.0",
                      fill=COLORS['text_light'], font=FONTS['subtitle'])

        # Tarjeta de inicio de sesión
        x0, y0, x1, y1 = self.CARD
        ancho_campo = x1 - x0 - 72
        if not fondos.HAY_PIL:
            rect_redondeado(c, *self.CARD, 24, fill=COLORS['bg_panel'], outline='')
        rect_redondeado(c, *self.CARD, 24, fill='', outline=COLORS['border'], width=1)

        c.create_text(x0 + 36, y0 + 38, anchor='w', text="Iniciar Sesión",
                      font=FONTS['card_title'], fill=COLORS['accent_gold'])
        c.create_text(x0 + 36, y0 + 64, anchor='w', text="Ingrese sus credenciales de operador",
                      font=FONTS['small'], fill=COLORS['text_muted'])

        campo = (FUENTE, 12)
        c.create_text(x0 + 36, y0 + 106, anchor='w', text="Nombre de usuario",
                      font=FONTS['small_b'], fill=COLORS['text_light'])
        BotonCanvas(c, x1 - 36 - 150, y0 + 94, 150, 24, "👥 Ver usuarios", self._abrir_modal_usuarios,
                    'fantasma', fuente=FONTS['tag'], radio=10)
        self.e_user = tk.Entry(self, textvariable=self.var_user)
        estilizar_entry(self.e_user)
        self.e_user.configure(font=campo)
        c.create_window(x0 + 36, y0 + 126, anchor='nw', window=self.e_user, width=ancho_campo, height=38)

        c.create_text(x0 + 36, y0 + 190, anchor='w', text="Contraseña",
                      font=FONTS['small_b'], fill=COLORS['text_light'])
        self.e_pass = tk.Entry(self, textvariable=self.var_pass, show="•")
        estilizar_entry(self.e_pass)
        self.e_pass.configure(font=campo)
        c.create_window(x0 + 36, y0 + 210, anchor='nw', window=self.e_pass, width=ancho_campo, height=38)

        self.e_user.bind("<Return>", lambda e: self.e_pass.focus_set())
        self.e_pass.bind("<Return>", lambda e: self._login())

        BotonCanvas(c, x0 + 36, y0 + 276, ancho_campo, 52, "INGRESAR AL SISTEMA  ▶", self._login, 'primario')

        c.create_text(W // 2, H - 26, fill=COLORS['text_muted'], font=FONTS['small'],
                      text="INACAP  ·  Programación Orientada a Objetos Segura  ·  2026")

    # ── Fondo dinámico ───────────────────────────────────────────────────────

    def _componer(self):
        base = fondos.cargar_fondo(RUTA_FONDOS, self.NOMBRE_FONDO, self.W, self.H, oscurecer=0.15)
        return fondos.panel_vidrio(base, self.CARD, tinte=(26, 5, 14), opacidad=0.62)

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
        self._mostrar(Image.blend(vieja, nueva, paso / pasos))
        if paso < pasos:
            self.after(30, self._fundir, vieja, nueva, paso + 1)

    def _parpadeo(self):
        self._encendido = not self._encendido
        for i, f in enumerate(self._focos):
            self.canvas.itemconfig(f, fill='#ffd700' if (i % 2 == 0) == self._encendido else '#7a5a00')
        self.after(700, self._parpadeo)

    # ── Lógica de acceso (sin cambios) ───────────────────────────────────────

    def _login(self):
        usuario = self.var_user.get().strip()
        password = self.var_pass.get().strip()

        if not usuario or not password:
            messagebox.showwarning("Atención", "Por favor ingrese su usuario y contraseña.", parent=self)
            return

        trabajador = self.auth.autenticar(usuario, password)
        if not trabajador:
            messagebox.showerror("Error de Acceso", "Usuario o contraseña incorrectos.", parent=self)
            return

        # Redirigir según el rol
        self.withdraw()

        if trabajador.rol == "admin":
            from ui.ventana_admin import VentanaAdmin
            win = VentanaAdmin(self, trabajador)
        elif trabajador.rol == "boletero":
            from ui.ventana_boleteria import VentanaBoleteria
            win = VentanaBoleteria(self, trabajador)
        elif trabajador.rol == "dulceria":
            from ui.ventana_dulceria import VentanaDulceria
            win = VentanaDulceria(self, trabajador)
        else:
            messagebox.showerror("Rol desconocido", f"El rol '{trabajador.rol}' no tiene pantalla asignada.")
            self.deiconify()
            return

        win.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(win))

    def _on_child_close(self, win):
        win.destroy()
        self.var_pass.set("")
        self.deiconify()

    # ── Lista de usuarios (el acceso administrativo no se muestra) ───────────

    @staticmethod
    def _es_oculto(t):
        return t.rol == "admin" or t.username.strip().lower() == "admin"

    def _abrir_modal_usuarios(self):
        """Ventana modal con los usuarios operativos y sus roles (sin contraseñas)."""
        dlg = tk.Toplevel(self)
        dlg.title("Usuarios Disponibles en el Sistema")
        dlg.geometry("600x440")
        dlg.resizable(False, False)
        dlg.configure(bg=COLORS['bg_main'])
        dlg.transient(self)
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg=COLORS['header_bg'], height=56,
                       highlightbackground=COLORS['border'], highlightthickness=1)
        hdr.pack(fill='x')
        tk.Label(hdr, text="👥 USUARIOS DISPONIBLES", font=FONTS['title'],
                 bg=COLORS['header_bg'], fg=COLORS['accent_gold']).pack(pady=12)
        tk.Label(dlg, text="Haga doble clic en un usuario (o selecciónelo y pulse el botón) para autocompletar el login:",
                 font=FONTS['small'], bg=COLORS['bg_main'], fg=COLORS['text_muted']
                 ).pack(padx=16, pady=(10, 4), anchor='w')

        cols = ('ID', 'Nombre Completo', 'Usuario', 'Rol Asignado')
        tf = tk.Frame(dlg, bg=COLORS['bg_main'])
        tf.pack(fill='both', expand=True, padx=16, pady=4)
        tree = ttk.Treeview(tf, columns=cols, show='headings', style='Cine.Treeview', height=8)
        for col, w in zip(cols, [40, 220, 140, 140]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center' if col == 'ID' else 'w')
        sb = ttk.Scrollbar(tf, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        for t in TrabajadorDAO.listar():
            if not self._es_oculto(t):
                tree.insert('', 'end', values=(t.id_trabajador, t.nombre, t.username, t.rol.upper()))

        def seleccionar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Selección", "Por favor seleccione un usuario de la tabla.", parent=dlg)
                return
            self.var_user.set(tree.item(sel[0])['values'][2])
            self.var_pass.set("")
            dlg.destroy()
            self.e_pass.focus_set()

        tree.bind("<Double-1>", lambda e: seleccionar())

        barra = tk.Frame(dlg, bg=COLORS['bg_main'], pady=10)
        barra.pack(fill='x', padx=16)
        BotonModerno(barra, "✔ SELECCIONAR USUARIO", seleccionar, 'exito', ancho=230, alto=42).pack(side='right', padx=4)
        BotonModerno(barra, "Cerrar", dlg.destroy, 'fantasma', ancho=110, alto=42).pack(side='right', padx=4)
