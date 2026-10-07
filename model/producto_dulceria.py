from model.indicador_dolar import IndicadorDolar
from model.item_venta import ItemVenta
from model.validacion import decimal_en_rango, id_valido


class ProductoDulceria(ItemVenta):
    """Producto de dulcería. Si es importado, su precio base está en dólares y se cotiza con el dólar del día."""

    def __init__(self, descripcion: str, precio_base: float, importado: bool, id: int | None = None):
        super().__init__(descripcion)
        self.id = id
        self.importado = importado
        self.precio_base = precio_base
        self.__indicador = None

    @property
    def id(self) -> int | None:
        return self.__id

    @id.setter
    def id(self, valor: int | None) -> None:
        self.__id = id_valido(valor)

    @property
    def importado(self) -> bool:
        return self.__importado

    @importado.setter
    def importado(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ValueError("Importado debe ser verdadero o falso.")
        self.__importado = valor

    @property
    def precio_base(self) -> float:
        """En pesos si el producto es nacional; en dólares (USD) si es importado."""
        return self.__precio_base

    @precio_base.setter
    def precio_base(self, valor: float) -> None:
        self.__precio_base = decimal_en_rango(valor, 0.1, 100000, "El precio base")

    @property
    def indicador(self) -> IndicadorDolar | None:
        return self.__indicador

    @indicador.setter
    def indicador(self, valor: IndicadorDolar | None) -> None:
        if valor is not None and not isinstance(valor, IndicadorDolar):
            raise ValueError("El indicador debe ser un IndicadorDolar.")
        self.__indicador = valor

    def calcular_precio(self) -> int:
        if not self.__importado:
            return round(self.__precio_base)
        if self.__indicador is None:
            raise ValueError(f"'{self.descripcion}' es importado y no hay valor del dólar para calcular su precio.")
        return self.__indicador.convertir_a_pesos(self.__precio_base)
