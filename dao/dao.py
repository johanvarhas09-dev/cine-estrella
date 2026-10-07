import sqlite3


class DAO:
    """Clase base de los DAO: comparte la conexión y el cursor.

    Reglas que siguen todos los DAO del proyecto:
    - Todas las consultas usan parámetros (?) y nunca concatenan texto del usuario.
    - Las escrituras van dentro de "with self.conexion:", que confirma (commit) si todo sale bien
      y deshace (rollback) si ocurre un error.
    """

    def __init__(self, conexion: sqlite3.Connection):
        self.conexion = conexion
        self.cursor = conexion.cursor()
