from dao.dao import DAO
from model.boletero import Boletero
from model.encargado_dulceria import EncargadoDulceria
from model.trabajador import Trabajador


class TrabajadorDAO(DAO):
    # Traducción entre el subtipo de Python y el texto que se guarda en la columna "tipo"
    TIPO_POR_CLASE = {Boletero: "BOLETERO", EncargadoDulceria: "ENCARGADO_DULCERIA"}
    CLASE_POR_TIPO = {"BOLETERO": Boletero, "ENCARGADO_DULCERIA": EncargadoDulceria}

    def crear_tabla(self) -> None:
        with self.conexion:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS trabajador (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    caja INTEGER NOT NULL CHECK (caja BETWEEN 1 AND 20),
                    tipo TEXT NOT NULL CHECK (tipo IN ('BOLETERO', 'ENCARGADO_DULCERIA'))
                )
            """)

    def __crear_objeto(self, fila: tuple) -> Trabajador:
        clase = self.CLASE_POR_TIPO[fila[3]]
        return clase(fila[1], fila[2], fila[0])

    def insertar(self, trabajador: Trabajador) -> None:
        with self.conexion:
            self.cursor.execute("INSERT INTO trabajador (nombre, caja, tipo) VALUES (?, ?, ?)",
                                (trabajador.nombre, trabajador.caja, self.TIPO_POR_CLASE[type(trabajador)]))
        trabajador.id = self.cursor.lastrowid

    def buscar(self, id: int) -> Trabajador | None:
        self.cursor.execute("SELECT id, nombre, caja, tipo FROM trabajador WHERE id = ?", (id,))
        fila = self.cursor.fetchone()
        if fila is None:
            return None
        return self.__crear_objeto(fila)

    def listar(self) -> list[Trabajador]:
        self.cursor.execute("SELECT id, nombre, caja, tipo FROM trabajador ORDER BY id")
        return [self.__crear_objeto(fila) for fila in self.cursor.fetchall()]

    def actualizar(self, trabajador: Trabajador) -> bool:
        # El tipo no se modifica: un boletero no se convierte en encargado de dulcería
        with self.conexion:
            self.cursor.execute("UPDATE trabajador SET nombre = ?, caja = ? WHERE id = ?",
                                (trabajador.nombre, trabajador.caja, trabajador.id))
        return self.cursor.rowcount > 0

    def eliminar(self, id: int) -> bool:
        # Si el trabajador ya registró ventas, la clave foránea lo impide (sqlite3.IntegrityError)
        with self.conexion:
            self.cursor.execute("DELETE FROM trabajador WHERE id = ?", (id,))
        return self.cursor.rowcount > 0
