import sqlite3
from pathlib import Path

# La base de datos queda junto a main.py, sin importar desde qué carpeta se ejecute el programa
RUTA_BD = Path(__file__).resolve().parent.parent / "cine.db"


def crear_conexion(ruta: Path | str = RUTA_BD) -> sqlite3.Connection:
    conexion = sqlite3.connect(ruta)
    # Sin esta instrucción SQLite no hace respetar las claves foráneas
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion
