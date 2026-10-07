"""Datos de ejemplo para la demostración. Se crean con las clases del modelo, así que pasan por sus validaciones."""
import sqlite3
from datetime import date, datetime, time, timedelta

from dao.cliente_dao import ClienteDAO
from dao.funcion_dao import FuncionDAO
from dao.pelicula_dao import PeliculaDAO
from dao.producto_dao import ProductoDAO
from dao.trabajador_dao import TrabajadorDAO
from model.boletero import Boletero
from model.cliente import Cliente
from model.encargado_dulceria import EncargadoDulceria
from model.funcion_2d import Funcion2D
from model.funcion_3d import Funcion3D
from model.funcion_vip import FuncionVIP
from model.pelicula import Pelicula
from model.producto_dulceria import ProductoDulceria


def base_vacia(conexion: sqlite3.Connection) -> bool:
    cursor = conexion.cursor()
    for consulta in ("SELECT COUNT(*) FROM pelicula", "SELECT COUNT(*) FROM cliente",
                     "SELECT COUNT(*) FROM producto_dulceria", "SELECT COUNT(*) FROM trabajador"):
        cursor.execute(consulta)
        if cursor.fetchone()[0] > 0:
            return False
    return True


def cargar_datos_ejemplo(conexion: sqlite3.Connection) -> None:
    peliculas = PeliculaDAO(conexion)
    minecraft = Pelicula("Minecraft: La Película", 101, 0)
    fnaf = Pelicula("Five Nights at Freddy's 2", 104, 14)
    deadpool = Pelicula("Deadpool & Wolverine", 128, 18)
    for pelicula in (minecraft, fnaf, deadpool):
        peliculas.insertar(pelicula)

    # Las funciones quedan para mañana, así siempre están en el futuro
    manana = date.today() + timedelta(days=1)
    funciones = FuncionDAO(conexion)
    funciones.insertar(Funcion2D(minecraft, datetime.combine(manana, time(15, 30)), 4500, 120))
    funciones.insertar(Funcion3D(fnaf, datetime.combine(manana, time(18, 0)), 4500, 80, 2000))
    # Cupo VIP pequeño (3) para poder mostrar la regla de asientos agotados en la demostración
    funciones.insertar(FuncionVIP(deadpool, datetime.combine(manana, time(21, 0)), 6000, 20, 5000, 3))

    productos = ProductoDAO(conexion)
    productos.insertar(ProductoDulceria("Cabritas grandes", 4500, False))
    productos.insertar(ProductoDulceria("Bebida 500 ml", 2200, False))
    productos.insertar(ProductoDulceria("Chocolates M&M importados", 3.5, True))
    productos.insertar(ProductoDulceria("Gomitas Haribo importadas", 2.8, True))

    trabajadores = TrabajadorDAO(conexion)
    trabajadores.insertar(Boletero("Ana Rojas", 1))
    trabajadores.insertar(EncargadoDulceria("Luis Pérez", 2))

    clientes = ClienteDAO(conexion)
    clientes.insertar(Cliente("11.111.111-1", "María González", 25))
    clientes.insertar(Cliente("22.222.222-2", "Diego Muñoz", 15))
