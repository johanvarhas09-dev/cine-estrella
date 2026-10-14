"""
Subtipo ProductoNacional: Producto fabricado o adquirido en Chile.
Su precio base está fijado en CLP y no varía con el dólar.
"""
from model.producto import Producto


class ProductoNacional(Producto):
    def __init__(
        self,
        id_producto: int | None,
        nombre: str,
        precio_base: float
    ):
        super().__init__(
            id_producto=id_producto,
            nombre=nombre,
            precio_base=precio_base,
            tipo="nacional"
        )

    def calcular_precio(self, tasa_dolar: float = 1.0) -> float:
        """El precio del producto nacional es fijo en pesos chilenos."""
        return self._precio_base
