"""
Gestión de conexión SQLite con soporte para llaves foráneas y row factory.
"""
import sqlite3
import os

_DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cine.db')
_CURRENT_DB_PATH = _DEFAULT_DB_PATH


def set_db_path(path: str):
    """Permite redefinir la base de datos (útil para pruebas unitarias aisladas)."""
    global _CURRENT_DB_PATH
    _CURRENT_DB_PATH = path


def get_db_path() -> str:
    return _CURRENT_DB_PATH


def obtener_conexion() -> sqlite3.Connection:
    """
    Crea y retorna una nueva conexión SQLite con llaves foráneas activadas.
    """
    conn = sqlite3.connect(_CURRENT_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
