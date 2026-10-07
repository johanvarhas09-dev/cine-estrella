from dao.dao import DAO
from model.pelicula import Pelicula


class PeliculaDAO(DAO):
    def crear_tabla(self) -> None:
        with self.conexion:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pelicula (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    duracion_min INTEGER NOT NULL CHECK (duracion_min > 0),
                    edad_minima INTEGER NOT NULL CHECK (edad_minima BETWEEN 0 AND 18)
                )
            """)

    def insertar(self, pelicula: Pelicula) -> None:
        with self.conexion:
            self.cursor.execute("INSERT INTO pelicula (titulo, duracion_min, edad_minima) VALUES (?, ?, ?)",
                                (pelicula.titulo, pelicula.duracion_min, pelicula.edad_minima))
        pelicula.id = self.cursor.lastrowid

    def buscar(self, id: int) -> Pelicula | None:
        self.cursor.execute("SELECT titulo, duracion_min, edad_minima, id FROM pelicula WHERE id = ?", (id,))
        fila = self.cursor.fetchone()
        if fila is None:
            return None
        return Pelicula(fila[0], fila[1], fila[2], fila[3])

    def listar(self) -> list[Pelicula]:
        self.cursor.execute("SELECT titulo, duracion_min, edad_minima, id FROM pelicula ORDER BY id")
        return [Pelicula(fila[0], fila[1], fila[2], fila[3]) for fila in self.cursor.fetchall()]

    def actualizar(self, pelicula: Pelicula) -> bool:
        with self.conexion:
            self.cursor.execute("UPDATE pelicula SET titulo = ?, duracion_min = ?, edad_minima = ? WHERE id = ?",
                                (pelicula.titulo, pelicula.duracion_min, pelicula.edad_minima, pelicula.id))
        return self.cursor.rowcount > 0

    def eliminar(self, id: int) -> bool:
        # Si la película tiene funciones, la clave foránea lo impide (sqlite3.IntegrityError)
        with self.conexion:
            self.cursor.execute("DELETE FROM pelicula WHERE id = ?", (id,))
        return self.cursor.rowcount > 0
