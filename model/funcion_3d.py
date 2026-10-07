from datetime import datetime

from model.funcion import Funcion
from model.pelicula import Pelicula
from model.validacion import entero_en_rango


class Funcion3D(Funcion):
    """Función en 3D: al precio base se suma el recargo por la tecnología 3D."""

    def __init__(self, pelicula: Pelicula, fecha_hora: datetime, precio_base: int, asientos_totales: int,
                 recargo_3d: int, asientos_vendidos: int = 0, id: int | None = None):
        super().__init__(pelicula, fecha_hora, precio_base, asientos_totales, asientos_vendidos, id)
        self.recargo_3d = recargo_3d

    @property
    def recargo_3d(self) -> int:
        return self.__recargo_3d

    @recargo_3d.setter
    def recargo_3d(self, valor: int) -> None:
        self.__recargo_3d = entero_en_rango(valor, 0, 50000, "El recargo 3D")

    def calcular_precio(self) -> int:
        return self.precio_base + self.__recargo_3d
