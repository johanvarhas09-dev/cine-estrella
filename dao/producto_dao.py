from dao.dao import DAO
from model.producto_dulceria import ProductoDulceria


class ProductoDAO(DAO):
    def crear_tabla(self) -> None:
        with self.conexion:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS producto_dulceria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descripcion TEXT NOT NULL,
                    precio_base REAL NOT NULL CHECK (precio_base > 0),
                    importado INTEGER NOT NULL CHECK (importado IN (0, 1))
                )
            """)

    @staticmethod
    def __crear_objeto(fila: tuple) -> ProductoDulceria:
        # SQLite guarda el booleano como 0/1; se convierte de vuelta a bool
        return ProductoDulceria(fila[1], fila[2], bool(fila[3]), fila[0])

    def insertar(self, producto: ProductoDulceria) -> None:
        with self.conexion:
            self.cursor.execute("INSERT INTO producto_dulceria (descripcion, precio_base, importado) VALUES (?, ?, ?)",
                                (producto.descripcion, producto.precio_base, int(producto.importado)))
        producto.id = self.cursor.lastrowid

    def buscar(self, id: int) -> ProductoDulceria | None:
        self.cursor.execute("SELECT id, descripcion, precio_base, importado FROM producto_dulceria WHERE id = ?",
                            (id,))
        fila = self.cursor.fetchone()
        if fila is None:
            return None
        return self.__crear_objeto(fila)

    def listar(self) -> list[ProductoDulceria]:
        self.cursor.execute("SELECT id, descripcion, precio_base, importado FROM producto_dulceria ORDER BY id")
        return [self.__crear_objeto(fila) for fila in self.cursor.fetchall()]

    def actualizar(self, producto: ProductoDulceria) -> bool:
        with self.conexion:
            self.cursor.execute("""
                UPDATE producto_dulceria SET descripcion = ?, precio_base = ?, importado = ? WHERE id = ?
            """, (producto.descripcion, producto.precio_base, int(producto.importado), producto.id))
        return self.cursor.rowcount > 0

    def eliminar(self, id: int) -> bool:
        # Si el producto aparece en alguna venta, la clave foránea lo impide (sqlite3.IntegrityError)
        with self.conexion:
            self.cursor.execute("DELETE FROM producto_dulceria WHERE id = ?", (id,))
        return self.cursor.rowcount > 0
