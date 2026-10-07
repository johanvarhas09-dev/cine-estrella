from datetime import datetime

from model.funcion import Funcion
from model.pelicula import Pelicula


class Funcion2D(Funcion):
    """Función normal: la entrada cuesta el precio base."""

    def __init__(self, pelicula: Pelicula, fecha_hora: datetime, precio_base: int,
                 asientos_totales: int, asientos_vendidos: int = 0, id: int | None = None):
        super().__init__(pelicula, fecha_hora, precio_base, asientos_totales, asientos_vendidos, id)

    def calcular_precio(self) -> int:
        return self.precio_base
