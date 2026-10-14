"""
Subtipo ProductoImportado: Snacks y dulces importados tasados en dólares estadounidenses (USD).
Su precio final en CLP se calcula dinámicamente mediante el valor del dólar del día (Casos P16 y P17).
"""
from model.producto import Producto


class ProductoImportado(Producto):
    def __init__(
        self,
        id_producto: int | None,
        nombre: str,
        precio_base_usd: float
    ):
        super().__init__(
            id_producto=id_producto,
            nombre=nombre,
            precio_base=precio_base_usd,
            tipo="importado"
        )

    @property
    def precio_usd(self) -> float:
        """Alias descriptivo para el precio base en dólares."""
        return self._precio_base

    def calcular_precio(self, tasa_dolar: float = 1.0) -> float:
        """
        [FUNCIONALIDAD: CONVERSIÓN DINÁMICA DE DÓLAR A PESOS CHILENOS - Caso P16]
        Calcula el valor en CLP multiplicando el precio base en USD por la tasa oficial del día
        obtenida desde la API del Banco Central (mindicador.cl).
        Aplica redondeo comercial entero con round().
        Si la tasa no es válida o es menor o igual a cero, lanza ValueError.
        Ejemplo: USD 3.50 * $950 CLP/USD = $3.325 CLP.
        """
        if tasa_dolar <= 0:
            raise ValueError("La tasa de cambio del dólar debe ser mayor a cero.")
        return round(self._precio_base * tasa_dolar)
