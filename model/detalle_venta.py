from model.item_venta import ItemVenta
from model.trabajador import Trabajador
from model.validacion import entero_en_rango


class DetalleVenta:
    """Línea de una venta. Guarda el precio unitario del momento, porque el dólar cambia a diario."""

    def __init__(self, item: ItemVenta, cantidad: int, precio_unitario: int, vendedor: Trabajador):
        if not isinstance(item, ItemVenta):
            raise ValueError("El ítem de la línea debe ser una entrada o un producto de dulcería.")
        if not isinstance(vendedor, Trabajador):
            raise ValueError("La línea debe indicar el trabajador que la vendió.")
        self.__item = item
        self.__vendedor = vendedor
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    @property
    def item(self) -> ItemVenta:
        return self.__item

    @property
    def vendedor(self) -> Trabajador:
        return self.__vendedor

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        self.__cantidad = entero_en_rango(valor, 1, 50, "La cantidad")

    @property
    def precio_unitario(self) -> int:
        return self.__precio_unitario

    @precio_unitario.setter
    def precio_unitario(self, valor: int) -> None:
        self.__precio_unitario = entero_en_rango(valor, 0, 10_000_000, "El precio unitario")

    def calcular_subtotal(self) -> int:
        return self.__cantidad * self.__precio_unitario
