import sqlite3
from datetime import datetime

from dao.cliente_dao import ClienteDAO
from dao.dao import DAO
from dao.funcion_dao import FuncionDAO
from dao.producto_dao import ProductoDAO
from dao.trabajador_dao import TrabajadorDAO
from model.detalle_venta import DetalleVenta
from model.entrada import Entrada
from model.venta import Venta


class VentaDAO(DAO):
    """Guarda y lee las ventas junto con sus líneas de detalle."""

    def __init__(self, conexion: sqlite3.Connection):
        super().__init__(conexion)
        # Para reconstruir una venta se necesitan sus clientes, trabajadores, funciones y productos
        self.__clientes = ClienteDAO(conexion)
        self.__trabajadores = TrabajadorDAO(conexion)
        self.__funciones = FuncionDAO(conexion)
        self.__productos = ProductoDAO(conexion)

    def crear_tabla(self) -> None:
        with self.conexion:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS venta (
                    numero INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    cliente_rut TEXT NOT NULL,
                    total INTEGER NOT NULL CHECK (total >= 0),
                    FOREIGN KEY (cliente_rut) REFERENCES cliente(rut)
                )
            """)
            # ON DELETE CASCADE refleja la composición: las líneas no existen sin su venta
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS detalle_venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_numero INTEGER NOT NULL,
                    trabajador_id INTEGER NOT NULL,
                    tipo_item TEXT NOT NULL CHECK (tipo_item IN ('ENTRADA', 'PRODUCTO')),
                    funcion_id INTEGER,
                    producto_id INTEGER,
                    descripcion TEXT NOT NULL,
                    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                    precio_unitario INTEGER NOT NULL CHECK (precio_unitario >= 0),
                    FOREIGN KEY (venta_numero) REFERENCES venta(numero) ON DELETE CASCADE,
                    FOREIGN KEY (trabajador_id) REFERENCES trabajador(id),
                    FOREIGN KEY (funcion_id) REFERENCES funcion(id),
                    FOREIGN KEY (producto_id) REFERENCES producto_dulceria(id),
                    CHECK ((tipo_item = 'ENTRADA' AND funcion_id IS NOT NULL AND producto_id IS NULL)
                        OR (tipo_item = 'PRODUCTO' AND producto_id IS NOT NULL AND funcion_id IS NULL))
                )
            """)

    def insertar(self, venta: Venta) -> None:
        """Guarda la venta y todas sus líneas en una sola transacción: se guarda todo o nada."""
        if not venta.detalles:
            raise ValueError("Una venta debe tener al menos una línea de detalle.")
        with self.conexion:
            self.cursor.execute("INSERT INTO venta (fecha, cliente_rut, total) VALUES (?, ?, ?)",
                                (venta.fecha.isoformat(sep=" "), venta.cliente.rut, venta.calcular_total()))
            numero_venta = self.cursor.lastrowid
            funciones_vendidas = {}
            for detalle in venta.detalles:
                item = detalle.item
                # El DAO necesita saber qué tipo de ítem es para llenar la columna correcta
                if isinstance(item, Entrada):
                    tipo_item, funcion_id, producto_id = "ENTRADA", item.funcion.id, None
                    funciones_vendidas[item.funcion.id] = item.funcion
                else:
                    tipo_item, funcion_id, producto_id = "PRODUCTO", None, item.id
                self.cursor.execute("""
                    INSERT INTO detalle_venta (venta_numero, trabajador_id, tipo_item, funcion_id, producto_id,
                                               descripcion, cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (numero_venta, detalle.vendedor.id, tipo_item, funcion_id, producto_id,
                      item.descripcion, detalle.cantidad, detalle.precio_unitario))
                if isinstance(item, Entrada):
                    item.numero = self.cursor.lastrowid
            # Los asientos vendidos quedan tal como los dejó el modelo al reservar cada entrada
            for funcion in funciones_vendidas.values():
                self.cursor.execute("UPDATE funcion SET asientos_vendidos = ? WHERE id = ?",
                                    (funcion.asientos_vendidos, funcion.id))
        venta.numero = numero_venta

    def __armar_venta(self, numero: int, fecha: str, cliente_rut: str) -> Venta:
        venta = Venta(self.__clientes.buscar(cliente_rut), datetime.fromisoformat(fecha), numero)
        self.cursor.execute("""
            SELECT id, trabajador_id, tipo_item, funcion_id, producto_id, cantidad, precio_unitario
            FROM detalle_venta WHERE venta_numero = ? ORDER BY id
        """, (numero,))
        for (id_linea, trabajador_id, tipo_item, funcion_id, producto_id,
             cantidad, precio_unitario) in self.cursor.fetchall():
            if tipo_item == "ENTRADA":
                item = Entrada(self.__funciones.buscar(funcion_id), id_linea)
            else:
                item = self.__productos.buscar(producto_id)
            # Se usa el precio guardado, no el de hoy: el dólar pudo cambiar desde la venta
            venta.agregar_detalle(DetalleVenta(item, cantidad, precio_unitario,
                                               self.__trabajadores.buscar(trabajador_id)))
        return venta

    def buscar(self, numero: int) -> Venta | None:
        self.cursor.execute("SELECT numero, fecha, cliente_rut FROM venta WHERE numero = ?", (numero,))
        fila = self.cursor.fetchone()
        if fila is None:
            return None
        return self.__armar_venta(fila[0], fila[1], fila[2])

    def listar(self) -> list[Venta]:
        self.cursor.execute("SELECT numero, fecha, cliente_rut FROM venta ORDER BY numero")
        return [self.__armar_venta(fila[0], fila[1], fila[2]) for fila in self.cursor.fetchall()]
