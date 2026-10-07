from model.funcion import Funcion
from model.item_venta import ItemVenta
from model.validacion import id_valido


class Entrada(ItemVenta):
    """Ticket de acceso a una función. Su precio es el que calcula el subtipo de la función."""

    def __init__(self, funcion: Funcion, numero: int | None = None):
        if not isinstance(funcion, Funcion):
            raise ValueError("La entrada debe pertenecer a una función válida.")
        super().__init__(f"Entrada {type(funcion).__name__} - {funcion.pelicula.titulo} "
                         f"({funcion.fecha_hora:%d-%m-%Y %H:%M})")
        self.__funcion = funcion
        self.numero = numero

    @property
    def numero(self) -> int | None:
        return self.__numero

    @numero.setter
    def numero(self, valor: int | None) -> None:
        # El número lo asigna la base de datos al guardar la venta
        self.__numero = id_valido(valor)

    @property
    def funcion(self) -> Funcion:
        return self.__funcion

    def calcular_precio(self) -> int:
        # Polimorfismo: Funcion2D, Funcion3D y FuncionVIP responden distinto al mismo mensaje
        return self.__funcion.calcular_precio()
