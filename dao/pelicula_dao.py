"""
DAO para la entidad Pelicula.
Implementa operaciones CRUD y protege la integridad referencial (no borra registros asociados).
"""
from dao.conexion import obtener_conexion
from model.pelicula import Pelicula
from model.excepciones import ReglaNegocioException


class PeliculaDAO:
    @staticmethod
    def crear(pelicula: Pelicula) -> Pelicula:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO peliculas (titulo, clasificacion_edad, duracion_minutos)
            VALUES (?, ?, ?)
            """,
            (pelicula.titulo, pelicula.clasificacion_edad, pelicula.duracion_minutos)
        )
        pelicula.id_pelicula = cursor.lastrowid
        conn.commit()
        conn.close()
        return pelicula

    @staticmethod
    def listar() -> list[Pelicula]:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id_pelicula, titulo, clasificacion_edad, duracion_minutos FROM peliculas ORDER BY id_pelicula")
        rows = cursor.fetchall()
        conn.close()
        return [
            Pelicula(
                id_pelicula=r["id_pelicula"],
                titulo=r["titulo"],
                clasificacion_edad=r["clasificacion_edad"],
                duracion_minutos=r["duracion_minutos"]
            )
            for r in rows
        ]

    @staticmethod
    def obtener_por_id(id_pelicula: int) -> Pelicula | None:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_pelicula, titulo, clasificacion_edad, duracion_minutos FROM peliculas WHERE id_pelicula = ?",
            (id_pelicula,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return Pelicula(
                id_pelicula=row["id_pelicula"],
                titulo=row["titulo"],
                clasificacion_edad=row["clasificacion_edad"],
                duracion_minutos=row["duracion_minutos"]
            )
        return None

    @staticmethod
    def modificar(pelicula: Pelicula) -> bool:
        if not pelicula.id_pelicula:
            raise ValueError("La película a modificar debe tener un ID válido.")
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE peliculas
            SET titulo = ?, clasificacion_edad = ?, duracion_minutos = ?
            WHERE id_pelicula = ?
            """,
            (pelicula.titulo, pelicula.clasificacion_edad, pelicula.duracion_minutos, pelicula.id_pelicula)
        )
        modificados = cursor.rowcount
        conn.commit()
        conn.close()
        return modificados > 0

    @staticmethod
    def eliminar(id_pelicula: int) -> bool:
        """
        Elimina una película. Si tiene funciones asociadas, impide la eliminación
        para mantener la integridad de los datos según las pautas de evaluación.
        """
        conn = obtener_conexion()
        cursor = conn.cursor()

        # Verificar si tiene funciones asociadas
        cursor.execute("SELECT COUNT(*) FROM funciones WHERE id_pelicula = ?", (id_pelicula,))
        conteo = cursor.fetchone()[0]
        if conteo > 0:
            conn.close()
            raise ReglaNegocioException(
                f"No se puede eliminar la película (ID {id_pelicula}) porque tiene {conteo} función(es) programada(s)."
            )

        cursor.execute("DELETE FROM peliculas WHERE id_pelicula = ?", (id_pelicula,))
        eliminados = cursor.rowcount
        conn.commit()
        conn.close()
        return eliminados > 0
