"""
DAO para la entidad Funcion y sus subtipos (Funcion2D, Funcion3D, FuncionVIP).
Reconstruye las instancias polimórficas adecuadas e impide la eliminación si registra ventas.
"""
from dao.conexion import obtener_conexion
from dao.pelicula_dao import PeliculaDAO
from model.funcion import Funcion
from model.funcion_2d import Funcion2D
from model.funcion_3d import Funcion3D
from model.funcion_vip import FuncionVIP
from model.excepciones import ReglaNegocioException


class FuncionDAO:
    @staticmethod
    def _instanciar(row) -> Funcion:
        pelicula = PeliculaDAO.obtener_por_id(row["id_pelicula"])
        if not pelicula:
            from model.pelicula import Pelicula
            pelicula = Pelicula(id_pelicula=row["id_pelicula"], titulo="Desconocida", clasificacion_edad=0)

        tipo = row["tipo"].upper()
        kwargs = {
            "id_funcion": row["id_funcion"],
            "pelicula": pelicula,
            "fecha_hora": row["fecha_hora"],
            "precio_base": row["precio_base"],
            "capacidad": row["capacidad"],
            "asientos_disponibles": row["asientos_disponibles"]
        }

        if tipo == "2D":
            return Funcion2D(**kwargs)
        elif tipo == "3D":
            recargo = row["recargo"] if "recargo" in row.keys() else Funcion3D.RECARGO_3D_DEFAULT
            return Funcion3D(recargo_3d=recargo, **kwargs)
        elif tipo == "VIP":
            recargo = row["recargo"] if "recargo" in row.keys() else FuncionVIP.RECARGO_VIP_DEFAULT
            return FuncionVIP(recargo_vip=recargo, **kwargs)
        else:
            return Funcion(tipo=tipo, **kwargs)

    @staticmethod
    def crear(funcion: Funcion) -> Funcion:
        conn = obtener_conexion()
        cursor = conn.cursor()
        recargo = 0.0
        if isinstance(funcion, Funcion3D):
            recargo = funcion.recargo_3d
        elif isinstance(funcion, FuncionVIP):
            recargo = funcion.recargo_vip

        cursor.execute(
            """
            INSERT INTO funciones (
                id_pelicula, tipo, fecha_hora, precio_base,
                capacidad, asientos_disponibles, recargo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                funcion.pelicula.id_pelicula,
                funcion.tipo,
                funcion.fecha_hora,
                funcion.precio_base,
                funcion.capacidad,
                funcion.asientos_disponibles,
                recargo
            )
        )
        funcion.id_funcion = cursor.lastrowid
        conn.commit()
        conn.close()
        return funcion

    @staticmethod
    def listar() -> list[Funcion]:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funciones ORDER BY fecha_hora, id_funcion")
        rows = cursor.fetchall()
        conn.close()
        return [FuncionDAO._instanciar(r) for r in rows]

    @staticmethod
    def obtener_por_id(id_funcion: int) -> Funcion | None:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funciones WHERE id_funcion = ?", (id_funcion,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return FuncionDAO._instanciar(row)
        return None

    @staticmethod
    def modificar(funcion: Funcion) -> bool:
        if not funcion.id_funcion:
            raise ValueError("La función debe tener un ID válido para ser modificada.")
        conn = obtener_conexion()
        cursor = conn.cursor()
        recargo = 0.0
        if isinstance(funcion, Funcion3D):
            recargo = funcion.recargo_3d
        elif isinstance(funcion, FuncionVIP):
            recargo = funcion.recargo_vip

        cursor.execute(
            """
            UPDATE funciones
            SET id_pelicula = ?, tipo = ?, fecha_hora = ?, precio_base = ?,
                capacidad = ?, asientos_disponibles = ?, recargo = ?
            WHERE id_funcion = ?
            """,
            (
                funcion.pelicula.id_pelicula,
                funcion.tipo,
                funcion.fecha_hora,
                funcion.precio_base,
                funcion.capacidad,
                funcion.asientos_disponibles,
                recargo,
                funcion.id_funcion
            )
        )
        modificados = cursor.rowcount
        conn.commit()
        conn.close()
        return modificados > 0

    @staticmethod
    def actualizar_asientos(id_funcion: int, nuevos_asientos_disponibles: int) -> bool:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE funciones SET asientos_disponibles = ? WHERE id_funcion = ?",
            (nuevos_asientos_disponibles, id_funcion)
        )
        actualizados = cursor.rowcount
        conn.commit()
        conn.close()
        return actualizados > 0

    @staticmethod
    def eliminar(id_funcion: int) -> bool:
        """
        Impide la eliminación si la función ya posee boletos/entradas vendidas en detalle_ventas.
        """
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM detalle_ventas WHERE tipo_item = 'entrada' AND id_item = ?",
            (id_funcion,)
        )
        ventas_asociadas = cursor.fetchone()[0]
        if ventas_asociadas > 0:
            conn.close()
            raise ReglaNegocioException(
                f"No se puede eliminar la función (ID {id_funcion}) porque ya tiene {ventas_asociadas} venta(s) asociada(s)."
            )

        cursor.execute("DELETE FROM funciones WHERE id_funcion = ?", (id_funcion,))
        eliminados = cursor.rowcount
        conn.commit()
        conn.close()
        return eliminados > 0
