from datetime import datetime

from model.cliente import Cliente
from model.detalle_venta import DetalleVenta
from model.validacion import id_valido


class Venta:
    """Transacción de un cliente. Se compone de una o más líneas de detalle (entradas y productos)."""

    def __init__(self, cliente: Cliente, fecha: datetime | None = None, numero: int | None = None):
        if not isinstance(cliente, Cliente):
            raise ValueError("La venta debe tener un cliente válido.")
        if fecha is not None and not isinstance(fecha, datetime):
            raise ValueError("La fecha de la venta no es válida.")
        self.__cliente = cliente
        self.__fecha = fecha if fecha is not None else datetime.now().replace(microsecond=0)
        self.__detalles: list[DetalleVenta] = []
        self.numero = numero

    @property
    def numero(self) -> int | None:
        return self.__numero

    @numero.setter
    def numero(self, valor: int | None) -> None:
        # El número lo asigna la base de datos al guardar la venta
        self.__numero = id_valido(valor)

    @property
    def fecha(self) -> datetime:
        return self.__fecha

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def detalles(self) -> list[DetalleVenta]:
        # Se entrega una copia para que nadie modifique la lista sin pasar por agregar_detalle()
        return list(self.__detalles)

    def agregar_detalle(self, detalle: DetalleVenta) -> None:
        if not isinstance(detalle, DetalleVenta):
            raise ValueError("Solo se pueden agregar líneas de detalle a la venta.")
        self.__detalles.append(detalle)

    def calcular_total(self) -> int:
        return sum(detalle.calcular_subtotal() for detalle in self.__detalles)
