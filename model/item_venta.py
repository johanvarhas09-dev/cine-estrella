from abc import ABC, abstractmethod

from model.validacion import texto_no_vacio


class ItemVenta(ABC):
    """Todo lo que puede ir en una línea de venta: una entrada o un producto de dulcería."""

    def __init__(self, descripcion: str):
        self.descripcion = descripcion

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        self.__descripcion = texto_no_vacio(valor, 100, "La descripción")

    @abstractmethod
    def calcular_precio(self) -> int:
        """Precio unitario en pesos chilenos."""
