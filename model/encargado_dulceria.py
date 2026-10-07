from model.detalle_venta import DetalleVenta
from model.producto_dulceria import ProductoDulceria
from model.trabajador import VENDER_PRODUCTO, Trabajador
from model.venta import Venta


class EncargadoDulceria(Trabajador):
    """Atiende la dulcería: solo puede vender productos de dulcería."""

    def __init__(self, nombre: str, caja: int, id: int | None = None):
        super().__init__(nombre, caja, id)

    def tiene_permiso(self, operacion: str) -> bool:
        return operacion == VENDER_PRODUCTO

    def vender_producto(self, venta: Venta, producto: ProductoDulceria, cantidad: int) -> DetalleVenta:
        """Agrega una línea con el producto. El precio queda fijo con el valor del dólar de hoy."""
        if not isinstance(producto, ProductoDulceria):
            raise ValueError("Solo se pueden vender productos de dulcería.")
        detalle = DetalleVenta(producto, cantidad, producto.calcular_precio(), self)
        venta.agregar_detalle(detalle)
        return detalle
