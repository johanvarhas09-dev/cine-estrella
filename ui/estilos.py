"""
Configuración visual centralizada para CINE ESTRELLA.
Paleta corporativa cinematográfica: vino tinto oscuro, dorado brillante y negro noche.
"""
import tkinter as tk
from pathlib import Path
from tkinter import ttk

# Raíz del proyecto (carpeta que contiene main.py). Todas las rutas parten de aquí,
# por eso equivalen a "./fondos", "./imagenes", etc., se ejecute desde donde se ejecute.
RAIZ = Path(__file__).resolve().parent.parent
RUTA_FONDOS = RAIZ / 'fondos'          # ./fondos
RUTA_IMAGENES = RAIZ / 'imagenes'      # ./imagenes

FUENTE = 'Segoe UI'                    # Windows; si no existe, Tk usa una similar

COLORS = {
    'bg_main':    '#0c0204',       # Fondo principal oscuro
    'bg_panel':   '#18060a',       # Paneles laterales y tarjetas
    'bg_card':    '#240a10',       # Contenedor de elementos y tarjetas
    'bg_card_hover': '#321018',   # Hover en tarjetas
    'bg_input':   '#280b12',       # Campos de texto y entradas destacados
    'border_input': '#9e2b40',     # Borde visible de campos de entrada
    'accent_red': '#b30000',       # Rojo corporativo estrella
    'accent_red_hover': '#d90404',# Hover botón rojo
    'accent_gold':'#ffd700',       # Dorado marquesina y títulos
    'accent_gold_dark': '#c8aa00',# Dorado oscuro
    'text_white': '#ffffff',       # Texto principal
    'text_light': '#f0e6e6',       # Texto secundario claro
    'text_muted': '#ab9191',       # Texto atenuado/labels
    'btn_red':    '#b30000',       # Botón principal
    'btn_green':  '#00802b',       # Botón confirmar / éxito
    'btn_green_hover': '#00a337',
    'btn_gray':   '#44383a',       # Botón secundario
    'border':     '#521822',       # Bordes elegantes
    'border_focus': '#ffd700',     # Borde activo dorado
    'seat_avail': '#00aa44',       # Asiento disponible
    'seat_taken': '#b30000',       # Asiento ocupado
    'seat_vip':   '#ffd700',       # Asiento VIP disponible
    'header_bg':  '#070102',       # Fondo de marquesina
    'glass_tint': '#1a050e',       # Tinte de los paneles de vidrio
    'gold_soft':  '#e8c872',       # Dorado suave para detalles
}

def estilizar_entry(entry: tk.Entry):
    """Aplica contraste elevado y borde destacado visible a los campos de entrada."""
    entry.configure(
        bg='#280b12',
        fg='#ffffff',
        insertbackground='#ffd700',
        relief='solid',
        bd=1,
        highlightbackground='#9e2b40',
        highlightcolor='#ffd700',
        highlightthickness=2,
        font=FONTS['body']
    )

FONTS = {
    'marquee':  (FUENTE, 24, 'bold'),
    'title':    (FUENTE, 16, 'bold'),
    'subtitle': (FUENTE, 13, 'bold'),
    'body':     (FUENTE, 10),
    'body_b':   (FUENTE, 10, 'bold'),
    'small':    (FUENTE, 9),
    'small_b':  (FUENTE, 9, 'bold'),
    'price':    (FUENTE, 14, 'bold'),
    'amount':   (FUENTE, 18, 'bold'),
    'btn':      (FUENTE, 10, 'bold'),
    'tag':      (FUENTE, 8, 'bold'),
    'hero':       (FUENTE, 34, 'bold'),
    'card_title': (FUENTE, 17, 'bold'),
    'card_desc':  (FUENTE, 11),
    'btn_big':    (FUENTE, 12, 'bold'),
    'emoji':      ('Segoe UI Emoji', 54),
    'clock':      (FUENTE, 12, 'bold'),
}

TYPE_COLORS = {
    '2D':  '#1a4cb0',
    '3D':  '#0b7547',
    'VIP': '#b8860b',
}

CLASIF_COLORS = {
    0:  '#236b23',
    7:  '#236b23',
    14: '#b86200',
    18: '#b30000',
}

CLASIF_LABELS = {
    0:  'TE · TODO ESPECTADOR',
    7:  '+7 · MAYORES DE 7',
    14: '+14 · MAYORES DE 14',
    18: '+18 · ADULTOS',
}


def aplicar_estilos_ttk(root: tk.Tk):
    """Configura el tema de widgets ttk (Treeview, Notebook, Combobox, Scrollbar)."""
    style = ttk.Style(root)
    style.theme_use('clam')

    # Treeview oscuro con cabecera en rojo corporativo
    style.configure(
        'Cine.Treeview',
        background=COLORS['bg_card'],
        foreground=COLORS['text_white'],
        fieldbackground=COLORS['bg_card'],
        rowheight=28,
        font=FONTS['body'],
        borderwidth=0
    )
    style.configure(
        'Cine.Treeview.Heading',
        background=COLORS['accent_red'],
        foreground='white',
        font=FONTS['body_b'],
        relief='flat',
        padding=6
    )
    style.map(
        'Cine.Treeview',
        background=[('selected', '#52121e')],
        foreground=[('selected', COLORS['accent_gold'])]
    )

    # Notebook (Pestañas)
    style.configure(
        'Cine.TNotebook',
        background=COLORS['bg_main'],
        borderwidth=0
    )
    style.configure(
        'Cine.TNotebook.Tab',
        background=COLORS['bg_panel'],
        foreground=COLORS['text_muted'],
        font=FONTS['body_b'],
        padding=[18, 8],
        relief='flat'
    )
    style.map(
        'Cine.TNotebook.Tab',
        background=[('selected', COLORS['accent_red'])],
        foreground=[('selected', 'white')]
    )

    # Combobox oscuro
    style.configure(
        'Cine.TCombobox',
        fieldbackground=COLORS['bg_input'],
        background=COLORS['bg_card'],
        foreground='white',
        arrowcolor=COLORS['accent_gold'],
        padding=5
    )
