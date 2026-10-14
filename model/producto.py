"""
Clase base Producto: Representa cualquier artículo ofrecido en la confitería del cine.
Define el método polimórfico calcular_precio(tasa_dolar) implementado en sus subtipos.
"""


class Producto:
    def __init__(
        self,
        id_producto: int | None,
        nombre: str,
        precio_base: float,
        tipo: str
    ):
        self._id_producto = None
        self._nombre = None
        self._precio_base = None
        self._tipo = None

        self.id_producto = id_producto
        self.nombre = nombre
        self.precio_base = precio_base
        self.tipo = tipo

    @property
    def id_producto(self) -> int | None:
        return self._id_producto

    @id_producto.setter
    def id_producto(self, valor: int | None):
        if valor is not None:
            if not isinstance(valor, int) or valor <= 0:
                raise ValueError("El ID del producto debe ser un entero positivo.")
        self._id_producto = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 1:
            raise ValueError("El nombre del producto no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @precio_base.setter
    def precio_base(self, valor: float):
        try:
            val_flt = float(valor)
        except (ValueError, TypeError):
            raise ValueError("El precio base debe ser un número.")
        if val_flt < 0:
            raise ValueError("El precio base no puede ser negativo.")
        self._precio_base = val_flt

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ValueError("El tipo de producto no puede estar vacío.")
        self._tipo = valor.strip().lower()

    def calcular_precio(self, tasa_dolar: float = 1.0) -> float:
        """Método polimórfico que calcula el precio de venta final en CLP."""
        return self._precio_base

    def __str__(self) -> str:
        return f"[{self._tipo.capitalize()}] {self._nombre} - Base: {self._precio_base}"
