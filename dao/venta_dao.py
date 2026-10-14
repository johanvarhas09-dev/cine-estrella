"""
DAO para transacciones atómicas de Venta y DetalleVenta.
Garantiza que ventas compuestas (entradas + confitería) se persistan íntegramente
bajo un único folio atómico (Casos P12 y P13), gestionando los cupos de las salas.
"""
from dao.conexion import obtener_conexion
from dao.cliente_dao import ClienteDAO
from model.venta import Venta
from model.detalle_venta import DetalleVenta
from model.excepciones import SinAsientosException


class VentaDAO:
    @staticmethod
    def registrar_venta(venta: Venta, descontar_asientos: bool = True) -> Venta:
        """
        [FUNCIONALIDAD: TRANSACCIÓN ATÓMICA DE VENTA COMPARTIDA - Casos P12 y P13]
        Registra la cabecera de la venta y todas sus líneas de detalle bajo una sola transacción SQLite.
        Garantías ACID implementadas:
        1. Atomicidad: Si falla cualquier inserción o falta cupo en una sala, se ejecuta conn.rollback(),
           evitando folios huérfanos o ventas a medio registrar.
        2. Control de Concurrencia de Cupos (Caso P14): Verifica disponibilidad de asientos en la misma
           transacción y descuenta con UPDATE atómico.
        3. Trazabilidad por Empleado: Cada detalle almacena 'id_trabajador', permitiendo que una misma
           venta fiscal contenga entradas emitidas por el Boletero y snacks del Encargado de Dulcería.
        """
        if not venta.detalles:
            raise ValueError("No se puede registrar una venta sin líneas de detalle.")

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            # 1. Asegurar persistencia del cliente si está presente
            rut_cliente = None
            if venta.cliente:
                rut_cliente = venta.cliente.rut
                cursor.execute(
                    """
                    INSERT INTO clientes (rut, nombre, edad)
                    VALUES (?, ?, ?)
                    ON CONFLICT(rut) DO UPDATE SET
                        nombre = excluded.nombre,
                        edad = excluded.edad
                    """,
                    (venta.cliente.rut, venta.cliente.nombre, venta.cliente.edad)
                )

            # 2. Insertar cabecera de venta
            cursor.execute(
                """
                INSERT INTO ventas (rut_cliente, fecha_hora, total)
                VALUES (?, ?, ?)
                """,
                (rut_cliente, venta.fecha_hora, venta.total)
            )
            id_venta = cursor.lastrowid
            venta.id_venta = id_venta

            # 3. Procesar cada línea de detalle
            for detalle in venta.detalles:
                detalle.id_venta = id_venta

                # Si es una entrada y se solicita descontar asientos en esta fase
                if detalle.tipo_item == "entrada" and descontar_asientos:
                    cursor.execute(
                        "SELECT asientos_disponibles, capacidad FROM funciones WHERE id_funcion = ?",
                        (detalle.id_item,)
                    )
                    row_f = cursor.fetchone()
                    if not row_f:
                        raise ValueError(f"La función con ID {detalle.id_item} no existe.")

                    disp_actual = row_f["asientos_disponibles"]
                    if disp_actual < detalle.cantidad:
                        raise SinAsientosException(
                            f"Asientos insuficientes para la función ID {detalle.id_item}. "
                            f"Disponibles: {disp_actual}, solicitados: {detalle.cantidad}."
                        )

                    # Descontar asientos
                    cursor.execute(
                        "UPDATE funciones SET asientos_disponibles = asientos_disponibles - ? WHERE id_funcion = ?",
                        (detalle.cantidad, detalle.id_item)
                    )

                # Insertar línea de detalle
                cursor.execute(
                    """
                    INSERT INTO detalle_ventas (
                        id_venta, tipo_item, id_item, descripcion,
                        cantidad, precio_unitario, subtotal, id_trabajador
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        id_venta,
                        detalle.tipo_item,
                        detalle.id_item,
                        detalle.descripcion,
                        detalle.cantidad,
                        detalle.precio_unitario,
                        detalle.subtotal,
                        detalle.id_trabajador
                    )
                )
                detalle.id_detalle = cursor.lastrowid

            conn.commit()
            return venta

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(id_venta: int) -> Venta | None:
        """
        Obtiene la venta y reconstruye la lista completa de sus líneas de detalle (Caso P13).
        """
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("SELECT id_venta, rut_cliente, fecha_hora, total FROM ventas WHERE id_venta = ?", (id_venta,))
        row_v = cursor.fetchone()
        if not row_v:
            conn.close()
            return None

        cliente = None
        if row_v["rut_cliente"]:
            cliente = ClienteDAO.obtener_por_rut(row_v["rut_cliente"])

        cursor.execute(
            """
            SELECT id_detalle, id_venta, tipo_item, id_item, descripcion,
                   cantidad, precio_unitario, subtotal, id_trabajador
            FROM detalle_ventas
            WHERE id_venta = ?
            ORDER BY id_detalle
            """,
            (id_venta,)
        )
        rows_d = cursor.fetchall()
        conn.close()

        detalles = [
            DetalleVenta(
                id_detalle=r["id_detalle"],
                id_venta=r["id_venta"],
                tipo_item=r["tipo_item"],
                id_item=r["id_item"],
                descripcion=r["descripcion"],
                cantidad=r["cantidad"],
                precio_unitario=r["precio_unitario"],
                id_trabajador=r["id_trabajador"],
                subtotal=r["subtotal"]
            )
            for r in rows_d
        ]

        return Venta(
            id_venta=row_v["id_venta"],
            cliente=cliente,
            fecha_hora=row_v["fecha_hora"],
            detalles=detalles
        )

    @staticmethod
    def listar_todas() -> list[Venta]:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id_venta FROM ventas ORDER BY id_venta DESC")
        rows = cursor.fetchall()
        conn.close()
        return [VentaDAO.obtener_por_id(r["id_venta"]) for r in rows if r["id_venta"]]

    @staticmethod
    def obtener_ventas_por_funcion(id_funcion: int) -> list[dict]:
        """Consulta el detalle de ventas asociadas a una función específica."""
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT d.id_detalle, d.id_venta, v.fecha_hora, d.cantidad,
                   d.precio_unitario, d.subtotal, t.nombre AS trabajador
            FROM detalle_ventas d
            JOIN ventas v ON d.id_venta = v.id_venta
            JOIN trabajadores t ON d.id_trabajador = t.id_trabajador
            WHERE d.tipo_item = 'entrada' AND d.id_item = ?
            ORDER BY v.fecha_hora DESC
            """,
            (id_funcion,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def obtener_cuadratura_trabajador(id_trabajador: int) -> dict:
        """
        Calcula la recaudación y desglose de operaciones realizadas por un trabajador.
        Permite a boleteros y encargados de dulcería ver su cuadratura de caja.
        """
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(DISTINCT id_venta) AS transacciones,
                COALESCE(SUM(subtotal), 0.0) AS total_recaudado,
                COALESCE(SUM(CASE WHEN tipo_item = 'entrada' THEN cantidad ELSE 0 END), 0) AS total_entradas,
                COALESCE(SUM(CASE WHEN tipo_item = 'producto' THEN cantidad ELSE 0 END), 0) AS total_productos
            FROM detalle_ventas
            WHERE id_trabajador = ?
            """,
            (id_trabajador,)
        )
        resumen = dict(cursor.fetchone())

        cursor.execute(
            """
            SELECT descripcion, tipo_item, SUM(cantidad) AS cantidad_total, SUM(subtotal) AS subtotal_total
            FROM detalle_ventas
            WHERE id_trabajador = ?
            GROUP BY descripcion, tipo_item
            ORDER BY subtotal_total DESC
            """,
            (id_trabajador,)
        )
        desglose = [dict(r) for r in cursor.fetchall()]
        conn.close()

        resumen["desglose"] = desglose
        return resumen
