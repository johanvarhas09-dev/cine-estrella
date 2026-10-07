from datetime import datetime

from model.funcion import Funcion
from model.pelicula import Pelicula
from model.validacion import entero_en_rango


class FuncionVIP(Funcion):
    """Función VIP: tiene recargo propio y un cupo limitado de asientos VIP."""

    def __init__(self, pelicula: Pelicula, fecha_hora: datetime, precio_base: int, asientos_totales: int,
                 recargo_vip: int, asientos_vip: int, asientos_vendidos: int = 0, id: int | None = None):
        super().__init__(pelicula, fecha_hora, precio_base, asientos_totales, asientos_vendidos, id)
        self.recargo_vip = recargo_vip
        self.asientos_vip = asientos_vip

    @property
    def recargo_vip(self) -> int:
        return self.__recargo_vip

    @recargo_vip.setter
    def recargo_vip(self, valor: int) -> None:
        self.__recargo_vip = entero_en_rango(valor, 0, 50000, "El recargo VIP")

    @property
    def asientos_vip(self) -> int:
        return self.__asientos_vip

    @asientos_vip.setter
    def asientos_vip(self, valor: int) -> None:
        entero_en_rango(valor, 1, self.asientos_totales, "Los asientos VIP")
        if valor < self.asientos_vendidos:
            raise ValueError(f"No se puede bajar el cupo VIP a {valor}: ya hay {self.asientos_vendidos} vendidos.")
        self.__asientos_vip = valor

    def calcular_precio(self) -> int:
        return self.precio_base + self.__recargo_vip

    def asientos_disponibles(self) -> int:
        # La función VIP no vende toda la sala: solo su cupo limitado de asientos VIP
        return min(self.asientos_totales, self.__asientos_vip) - self.asientos_vendidos
