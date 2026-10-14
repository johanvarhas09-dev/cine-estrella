"""
Inicializador de esquema DDL y datos semilla para Cine Estrella.
Crea las tablas si no existen y asegura la cuenta inicial 'admin' / 'admin' protegida con hash.
"""
from dao.conexion import obtener_conexion
from model.trabajador import Trabajador


def inicializar_bd():
    """Ejecuta el DDL de creación de tablas y siembra datos iniciales seguros."""
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Detección de esquema obsoleto de Fase 1 para actualización limpia a Fase 2
    cursor.execute("PRAGMA table_info(trabajadores)")
    cols_trab = [r[1] for r in cursor.fetchall()]
    if cols_trab and "username" not in cols_trab:
        # Desactivar temporalmente llaves foráneas para reconstrucción limpia
        cursor.execute("PRAGMA foreign_keys = OFF;")
        tablas_viejas = [
            "detalle_ventas", "ventas", "funciones", "productos",
            "clientes", "trabajadores", "peliculas", "tipo_cambio_dolar"
        ]
        for t in tablas_viejas:
            cursor.execute(f"DROP TABLE IF EXISTS {t};")
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS peliculas (
            id_pelicula INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            clasificacion_edad INTEGER NOT NULL DEFAULT 0,
            duracion_minutos INTEGER NOT NULL DEFAULT 90
        );

        CREATE TABLE IF NOT EXISTS funciones (
            id_funcion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pelicula INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            fecha_hora TEXT NOT NULL,
            precio_base REAL NOT NULL,
            capacidad INTEGER NOT NULL,
            asientos_disponibles INTEGER NOT NULL,
            recargo REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula)
        );

        CREATE TABLE IF NOT EXISTS trabajadores (
            id_trabajador INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL,
            password_plano TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio_base REAL NOT NULL,
            tipo TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS clientes (
            rut TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            rut_cliente TEXT,
            fecha_hora TEXT NOT NULL,
            total REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (rut_cliente) REFERENCES clientes(rut)
        );

        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER NOT NULL,
            tipo_item TEXT NOT NULL,
            id_item INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            id_trabajador INTEGER NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE RESTRICT,
            FOREIGN KEY (id_trabajador) REFERENCES trabajadores(id_trabajador)
        );

        CREATE TABLE IF NOT EXISTS tipo_cambio_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL NOT NULL,
            fecha TEXT NOT NULL,
            fuente TEXT NOT NULL
        );
    """)

    # Asegurar columna password_plano en esquemas existentes
    cursor.execute("PRAGMA table_info(trabajadores)")
    cols_actuales = [r[1] for r in cursor.fetchall()]
    if "password_plano" not in cols_actuales:
        cursor.execute("ALTER TABLE trabajadores ADD COLUMN password_plano TEXT DEFAULT ''")
        cursor.execute("UPDATE trabajadores SET password_plano = 'admin' WHERE username = 'admin'")
        cursor.execute("UPDATE trabajadores SET password_plano = '1234' WHERE username IN ('boletero1', 'dulceria1')")
        conn.commit()

    # Sembrar usuario 'admin' / 'admin' de demostración con contraseña cifrada (hash seguro)
    cursor.execute("SELECT COUNT(*) FROM trabajadores WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        hash_admin = Trabajador.generar_hash("admin")
        cursor.execute(
            "INSERT INTO trabajadores (nombre, username, password_hash, rol, password_plano) VALUES (?, ?, ?, ?, ?)",
            ("Administrador General", "admin", hash_admin, "admin", "admin")
        )
    else:
        cursor.execute("UPDATE trabajadores SET password_plano = 'admin' WHERE username = 'admin' AND (password_plano IS NULL OR password_plano = '')")

    # Sembrar trabajadores de prueba si no existen
    cursor.execute("SELECT COUNT(*) FROM trabajadores WHERE rol IN ('boletero', 'dulceria')")
    if cursor.fetchone()[0] == 0:
        hash_demo = Trabajador.generar_hash("1234")
        cursor.execute(
            "INSERT INTO trabajadores (nombre, username, password_hash, rol, password_plano) VALUES (?, ?, ?, ?, ?)",
            ("Carlos Boletero", "boletero1", hash_demo, "boletero", "1234")
        )
        cursor.execute(
            "INSERT INTO trabajadores (nombre, username, password_hash, rol, password_plano) VALUES (?, ?, ?, ?, ?)",
            ("Ana Dulcería", "dulceria1", hash_demo, "dulceria", "1234")
        )
    else:
        cursor.execute("UPDATE trabajadores SET password_plano = '1234' WHERE username IN ('boletero1', 'dulceria1') AND (password_plano IS NULL OR password_plano = '')")
    cursor.execute("UPDATE trabajadores SET password_plano = '1234' WHERE password_plano IS NULL OR password_plano = ''")

    # Sembrar películas iniciales si no hay ninguna
    cursor.execute("SELECT COUNT(*) FROM peliculas")
    if cursor.fetchone()[0] == 0:
        peliculas_demo = [
            ("Galaxy Wars", 0, 130),
            ("Haunted Night", 18, 95),
            ("Action Chase", 14, 110),
            ("Los Pitufos", 0, 80)
        ]
        cursor.executemany(
            "INSERT INTO peliculas (titulo, clasificacion_edad, duracion_minutos) VALUES (?, ?, ?)",
            peliculas_demo
        )

    # Sembrar productos iniciales si no hay ninguno
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos_demo = [
            ("Popcorn Grande", 3500.0, "nacional"),
            ("Bebida 500ml", 1800.0, "nacional"),
            ("Agua Mineral", 1500.0, "nacional"),
            ("Hot Dog", 2500.0, "nacional"),
            ("Nachos con Queso", 3.5, "importado"),
            ("Chocolatina Importada", 2.0, "importado"),
            ("Gomitas Especiales", 2.5, "importado"),
            ("Combo Dulce Importado", 5.0, "importado")
        ]
        cursor.executemany(
            "INSERT INTO productos (nombre, precio_base, tipo) VALUES (?, ?, ?)",
            productos_demo
        )

    conn.commit()
    conn.close()
