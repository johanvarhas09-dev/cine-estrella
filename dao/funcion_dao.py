from datetime import datetime

from dao.dao import DAO
from model.funcion import Funcion
from model.funcion_2d import Funcion2D
from model.funcion_3d import Funcion3D
from model.funcion_vip import FuncionVIP
from model.pelicula import Pelicula

# Consultas de lectura: traen la función junto con su película, en el orden que espera __crear_objeto()
SQL_BUSCAR = """
    SELECT f.id, f.tipo, f.fecha_hora, f.precio_base, f.asientos_totales, f.asientos_vendidos,
           f.recargo, f.asientos_vip, p.id, p.titulo, p.duracion_min, p.edad_minima
    FROM funcion f JOIN pelicula p ON p.id = f.pelicula_id
    WHERE f.id = ?
"""
SQL_LISTAR = """
    SELECT f.id, f.tipo, f.fecha_hora, f.precio_base, f.asientos_totales, f.asientos_vendidos,
           f.recargo, f.asientos_vip, p.id, p.titulo, p.duracion_min, p.edad_minima
    FROM funcion f JOIN pelicula p ON p.id = f.pelicula_id
    ORDER BY f.fecha_hora, f.id
"""


class FuncionDAO(DAO):
    def crear_tabla(self) -> None:
        with self.conexion:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS funcion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL CHECK (tipo IN ('2D', '3D', 'VIP')),
                    pelicula_id INTEGER NOT NULL,
                    fecha_hora TEXT NOT NULL,
                    precio_base INTEGER NOT NULL CHECK (precio_base > 0),
                    asientos_totales INTEGER NOT NULL CHECK (asientos_totales > 0),
                    asientos_vendidos INTEGER NOT NULL DEFAULT 0
                        CHECK (asientos_vendidos BETWEEN 0 AND asientos_totales),
                    recargo INTEGER,
                    asientos_vip INTEGER,
                    FOREIGN KEY (pelicula_id) REFERENCES pelicula(id)
                )
            """)

    @staticmethod
    def __datos_subtipo(funcion: Funcion) -> tuple:
        # Solo el DAO necesita conocer el subtipo, para guardar sus columnas propias.
        # El precio nunca se calcula aquí: eso lo resuelve cada subtipo con calcular_precio().
        if isinstance(funcion, Funcion3D):
            return "3D", funcion.recargo_3d, None
        if isinstance(funcion, FuncionVIP):
            return "VIP", funcion.recargo_vip, funcion.asientos_vip
        return "2D", None, None

    @staticmethod
    def __crear_objeto(fila: tuple) -> Funcion:
        (id, tipo, fecha_hora, precio_base, asientos_totales, asientos_vendidos,
         recargo, asientos_vip, pelicula_id, titulo, duracion_min, edad_minima) = fila
        pelicula = Pelicula(titulo, duracion_min, edad_minima, pelicula_id)
        fecha = datetime.fromisoformat(fecha_hora)
        # La columna "tipo" indica qué subclase reconstruir a partir de la fila
        if tipo == "3D":
            return Funcion3D(pelicula, fecha, precio_base, asientos_totales, recargo, asientos_vendidos, id)
        if tipo == "VIP":
            return FuncionVIP(pelicula, fecha, precio_base, asientos_totales, recargo, asientos_vip,
                              asientos_vendidos, id)
        return Funcion2D(pelicula, fecha, precio_base, asientos_totales, asientos_vendidos, id)

    def insertar(self, funcion: Funcion) -> None:
        tipo, recargo, asientos_vip = self.__datos_subtipo(funcion)
        with self.conexion:
            self.cursor.execute("""
                INSERT INTO funcion (tipo, pelicula_id, fecha_hora, precio_base, asientos_totales,
                                     asientos_vendidos, recargo, asientos_vip)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (tipo, funcion.pelicula.id, funcion.fecha_hora.isoformat(sep=" ", timespec="minutes"),
                  funcion.precio_base, funcion.asientos_totales, funcion.asientos_vendidos, recargo, asientos_vip))
        funcion.id = self.cursor.lastrowid

    def buscar(self, id: int) -> Funcion | None:
        self.cursor.execute(SQL_BUSCAR, (id,))
        fila = self.cursor.fetchone()
        if fila is None:
            return None
        return self.__crear_objeto(fila)

    def listar(self) -> list[Funcion]:
        self.cursor.execute(SQL_LISTAR)
        return [self.__crear_objeto(fila) for fila in self.cursor.fetchall()]

    def actualizar(self, funcion: Funcion) -> bool:
        # asientos_vendidos no se edita aquí: solo cambia al guardar una venta (VentaDAO)
        tipo, recargo, asientos_vip = self.__datos_subtipo(funcion)
        with self.conexion:
            self.cursor.execute("""
                UPDATE funcion SET pelicula_id = ?, fecha_hora = ?, precio_base = ?, asientos_totales = ?,
                                   recargo = ?, asientos_vip = ?
                WHERE id = ? AND tipo = ?
            """, (funcion.pelicula.id, funcion.fecha_hora.isoformat(sep=" ", timespec="minutes"),
                  funcion.precio_base, funcion.asientos_totales, recargo, asientos_vip, funcion.id, tipo))
        return self.cursor.rowcount > 0

    def eliminar(self, id: int) -> bool:
        # Si la función ya tiene entradas vendidas, la clave foránea lo impide (sqlite3.IntegrityError)
        with self.conexion:
            self.cursor.execute("DELETE FROM funcion WHERE id = ?", (id,))
        return self.cursor.rowcount > 0
