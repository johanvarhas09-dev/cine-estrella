from dao.dao import DAO
from model.cliente import Cliente


class ClienteDAO(DAO):
    def crear_tabla(self) -> None:
        with self.conexion:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS cliente (
                    rut TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    edad INTEGER NOT NULL CHECK (edad BETWEEN 0 AND 120)
                )
            """)

    def insertar(self, cliente: Cliente) -> None:
        with self.conexion:
            self.cursor.execute("INSERT INTO cliente (rut, nombre, edad) VALUES (?, ?, ?)",
                                (cliente.rut, cliente.nombre, cliente.edad))

    def buscar(self, rut: str) -> Cliente | None:
        self.cursor.execute("SELECT rut, nombre, edad FROM cliente WHERE rut = ?", (rut,))
        fila = self.cursor.fetchone()
        if fila is None:
            return None
        return Cliente(fila[0], fila[1], fila[2])

    def listar(self) -> list[Cliente]:
        self.cursor.execute("SELECT rut, nombre, edad FROM cliente ORDER BY nombre")
        return [Cliente(fila[0], fila[1], fila[2]) for fila in self.cursor.fetchall()]

    def actualizar(self, cliente: Cliente) -> bool:
        with self.conexion:
            self.cursor.execute("UPDATE cliente SET nombre = ?, edad = ? WHERE rut = ?",
                                (cliente.nombre, cliente.edad, cliente.rut))
        return self.cursor.rowcount > 0

    def eliminar(self, rut: str) -> bool:
        # Si el cliente tiene ventas, la clave foránea lo impide (sqlite3.IntegrityError)
        with self.conexion:
            self.cursor.execute("DELETE FROM cliente WHERE rut = ?", (rut,))
        return self.cursor.rowcount > 0
