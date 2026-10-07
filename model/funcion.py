from abc import ABC, abstractmethod
from datetime import datetime

from model.pelicula import Pelicula
from model.sin_asientos_error import SinAsientosError
from model.validacion import entero_en_rango, id_valido


class Funcion(ABC):
    """Exhibición de una película en una fecha y hora. Es abstracta: el precio lo define cada subtipo."""

    def __init__(self, pelicula: Pelicula, fecha_hora: datetime, precio_base: int,
                 asientos_totales: int, asientos_vendidos: int = 0, id: int | None = None):
        if not isinstance(pelicula, Pelicula):
            raise ValueError("La función debe exhibir una película válida.")
        self.__pelicula = pelicula
        self.id = id
        self.fecha_hora = fecha_hora
        self.precio_base = precio_base
        self.__asientos_vendidos = 0
        self.asientos_totales = asientos_totales
        # asientos_vendidos no tiene setter público: solo cambia con reservar_asiento().
        # Aquí se valida el valor que llega al reconstruir la función desde la base de datos.
        self.__asientos_vendidos = entero_en_rango(asientos_vendidos, 0, self.__asientos_totales,
                                                   "Los asientos vendidos")

    @property
    def id(self) -> int | None:
        return self.__id

    @id.setter
    def id(self, valor: int | None) -> None:
        self.__id = id_valido(valor)

    @property
    def pelicula(self) -> Pelicula:
        return self.__pelicula

    @property
    def fecha_hora(self) -> datetime:
        return self.__fecha_hora

    @fecha_hora.setter
    def fecha_hora(self, valor: datetime) -> None:
        if not isinstance(valor, datetime):
            raise ValueError("La fecha y hora de la función no es válida.")
        self.__fecha_hora = valor

    @property
    def precio_base(self) -> int:
        return self.__precio_base

    @precio_base.setter
    def precio_base(self, valor: int) -> None:
        self.__precio_base = entero_en_rango(valor, 500, 100000, "El precio base")

    @property
    def asientos_totales(self) -> int:
        return self.__asientos_totales

    @asientos_totales.setter
    def asientos_totales(self, valor: int) -> None:
        entero_en_rango(valor, 1, 500, "Los asientos totales")
        if valor < self.__asientos_vendidos:
            raise ValueError(f"No se puede dejar la sala con {valor} asientos: "
                             f"ya hay {self.__asientos_vendidos} vendidos.")
        self.__asientos_totales = valor

    @property
    def asientos_vendidos(self) -> int:
        return self.__asientos_vendidos

    @abstractmethod
    def calcular_precio(self) -> int:
        """Precio de una entrada para esta función. Cada subtipo lo calcula a su manera."""

    def asientos_disponibles(self) -> int:
        return self.__asientos_totales - self.__asientos_vendidos

    def hay_asientos(self) -> bool:
        return self.asientos_disponibles() > 0

    def reservar_asiento(self) -> None:
        """Ocupa un asiento. Lanza SinAsientosError si la función ya no tiene asientos disponibles."""
        if not self.hay_asientos():
            raise SinAsientosError(self.__id)
        self.__asientos_vendidos += 1
