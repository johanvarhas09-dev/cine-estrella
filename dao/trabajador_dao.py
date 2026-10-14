"""
DAO para Trabajador y sus subtipos Boletero y EncargadoDulceria.
"""
from dao.conexion import obtener_conexion
from model.trabajador import Trabajador
from model.boletero import Boletero
from model.encargado_dulceria import EncargadoDulceria
from model.excepciones import ReglaNegocioException


class TrabajadorDAO:
    @staticmethod
    def _instanciar(row) -> Trabajador:
        rol = row["rol"].lower()
        pwd_plano = row["password_plano"] if "password_plano" in row.keys() and row["password_plano"] else ""
        kwargs = {
            "id_trabajador": row["id_trabajador"],
            "nombre": row["nombre"],
            "username": row["username"],
            "password_hash": row["password_hash"],
            "password_plano": pwd_plano
        }
        if rol == "boletero":
            return Boletero(**kwargs)
        elif rol == "dulceria":
            return EncargadoDulceria(**kwargs)
        else:
            return Trabajador(rol=rol, **kwargs)

    @staticmethod
    def crear(trabajador: Trabajador) -> Trabajador:
        if trabajador.username.strip().lower() == "admin":
            raise ReglaNegocioException("El usuario 'admin' es una funcionalidad reservada del sistema.")

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO trabajadores (nombre, username, password_hash, rol, password_plano)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                trabajador.nombre,
                trabajador.username,
                trabajador.password_hash,
                trabajador.rol,
                getattr(trabajador, 'password_plano', '')
            )
        )
        trabajador.id_trabajador = cursor.lastrowid
        conn.commit()
        conn.close()
        return trabajador

    @staticmethod
    def listar() -> list[Trabajador]:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id_trabajador, nombre, username, password_hash, rol, password_plano FROM trabajadores ORDER BY id_trabajador")
        rows = cursor.fetchall()
        conn.close()
        return [TrabajadorDAO._instanciar(r) for r in rows]

    @staticmethod
    def obtener_por_id(id_trabajador: int) -> Trabajador | None:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_trabajador, nombre, username, password_hash, rol, password_plano FROM trabajadores WHERE id_trabajador = ?",
            (id_trabajador,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return TrabajadorDAO._instanciar(row)
        return None

    @staticmethod
    def obtener_por_username(username: str) -> Trabajador | None:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_trabajador, nombre, username, password_hash, rol, password_plano FROM trabajadores WHERE username = ?",
            (username.strip().lower(),)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return TrabajadorDAO._instanciar(row)
        return None

    @staticmethod
    def modificar(trabajador: Trabajador) -> bool:
        if not trabajador.id_trabajador:
            raise ValueError("El trabajador a modificar debe tener un ID válido.")
        conn = obtener_conexion()
        cursor = conn.cursor()

        # Si el trabajador actual en base de datos es admin, no permitir cambiar su username ni rol
        cursor.execute("SELECT username, rol FROM trabajadores WHERE id_trabajador = ?", (trabajador.id_trabajador,))
        orig = cursor.fetchone()
        if orig and (orig["username"].strip().lower() == "admin" or orig["rol"].strip().lower() == "admin"):
            trabajador.username = "admin"
            trabajador.rol = "admin"

        cursor.execute(
            """
            UPDATE trabajadores
            SET nombre = ?, username = ?, password_hash = ?, rol = ?, password_plano = ?
            WHERE id_trabajador = ?
            """,
            (
                trabajador.nombre,
                trabajador.username,
                trabajador.password_hash,
                trabajador.rol,
                getattr(trabajador, 'password_plano', ''),
                trabajador.id_trabajador
            )
        )
        modificados = cursor.rowcount
        conn.commit()
        conn.close()
        return modificados > 0

    @staticmethod
    def eliminar(id_trabajador: int) -> bool:
        """Impide la eliminación de la cuenta de administración y de trabajadores con ventas."""
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("SELECT username, rol FROM trabajadores WHERE id_trabajador = ?", (id_trabajador,))
        row_t = cursor.fetchone()
        if not row_t:
            conn.close()
            return False

        if row_t["username"].strip().lower() == "admin" or row_t["rol"].strip().lower() == "admin":
            conn.close()
            raise ReglaNegocioException(
                "La cuenta del Administrador ('admin') es una funcionalidad reservada del sistema y no puede ser eliminada."
            )

        cursor.execute("SELECT COUNT(*) FROM detalle_ventas WHERE id_trabajador = ?", (id_trabajador,))
        ventas_asociadas = cursor.fetchone()[0]
        if ventas_asociadas > 0:
            conn.close()
            raise ReglaNegocioException(
                f"No se puede eliminar el trabajador (ID {id_trabajador}) porque registra {ventas_asociadas} transacción(es) en ventas."
            )

        cursor.execute("DELETE FROM trabajadores WHERE id_trabajador = ?", (id_trabajador,))
        eliminados = cursor.rowcount
        conn.commit()
        conn.close()
        return eliminados > 0
