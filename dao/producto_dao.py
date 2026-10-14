"""
DAO para la entidad Producto y sus subtipos ProductoNacional y ProductoImportado.
"""
from dao.conexion import obtener_conexion
from model.producto import Producto
from model.producto_nacional import ProductoNacional
from model.producto_importado import ProductoImportado
from model.excepciones import ReglaNegocioException


class ProductoDAO:
    @staticmethod
    def _instanciar(row) -> Producto:
        tipo = row["tipo"].lower()
        if tipo == "importado":
            return ProductoImportado(
                id_producto=row["id_producto"],
                nombre=row["nombre"],
                precio_base_usd=row["precio_base"]
            )
        else:
            return ProductoNacional(
                id_producto=row["id_producto"],
                nombre=row["nombre"],
                precio_base=row["precio_base"]
            )

    @staticmethod
    def crear(producto: Producto) -> Producto:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO productos (nombre, precio_base, tipo)
            VALUES (?, ?, ?)
            """,
            (producto.nombre, producto.precio_base, producto.tipo)
        )
        producto.id_producto = cursor.lastrowid
        conn.commit()
        conn.close()
        return producto

    @staticmethod
    def listar() -> list[Producto]:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id_producto, nombre, precio_base, tipo FROM productos ORDER BY id_producto")
        rows = cursor.fetchall()
        conn.close()
        return [ProductoDAO._instanciar(r) for r in rows]

    @staticmethod
    def obtener_por_id(id_producto: int) -> Producto | None:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_producto, nombre, precio_base, tipo FROM productos WHERE id_producto = ?",
            (id_producto,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return ProductoDAO._instanciar(row)
        return None

    @staticmethod
    def modificar(producto: Producto) -> bool:
        if not producto.id_producto:
            raise ValueError("El producto a modificar debe tener un ID válido.")
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE productos
            SET nombre = ?, precio_base = ?, tipo = ?
            WHERE id_producto = ?
            """,
            (producto.nombre, producto.precio_base, producto.tipo, producto.id_producto)
        )
        modificados = cursor.rowcount
        conn.commit()
        conn.close()
        return modificados > 0

    @staticmethod
    def eliminar(id_producto: int) -> bool:
        """Impide la eliminación si el producto tiene ventas asociadas."""
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM detalle_ventas WHERE tipo_item = 'producto' AND id_item = ?",
            (id_producto,)
        )
        conteo = cursor.fetchone()[0]
        if conteo > 0:
            conn.close()
            raise ReglaNegocioException(
                f"No se puede eliminar el producto (ID {id_producto}) porque ya registra {conteo} venta(s) asociada(s)."
            )

        cursor.execute("DELETE FROM productos WHERE id_producto = ?", (id_producto,))
        eliminados = cursor.rowcount
        conn.commit()
        conn.close()
        return eliminados > 0
