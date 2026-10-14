"""
Entidad Entrada: Representa un boleto emitido para una función de cine determinada.
"""
from model.funcion import Funcion


class Entrada:
    def __init__(self, id_entrada: int | None, funcion: Funcion, numero_asiento: int, precio: float | None = None):
        self._id_entrada = None
        self._funcion = None
        self._numero_asiento = None
        self._precio = None

        self.id_entrada = id_entrada
        self.funcion = funcion
        self.numero_asiento = numero_asiento
        self.precio = funcion.calcular_precio() if precio is None else precio

    @property
    def id_entrada(self) -> int | None:
        return self._id_entrada

    @id_entrada.setter
    def id_entrada(self, valor: int | None):
        if valor is not None:
            if not isinstance(valor, int) or valor <= 0:
                raise ValueError("El ID de entrada debe ser un entero positivo.")
        self._id_entrada = valor

    @property
    def funcion(self) -> Funcion:
        return self._funcion

    @funcion.setter
    def funcion(self, valor: Funcion):
        if not isinstance(valor, Funcion):
            raise TypeError("La función asociada a la entrada debe ser una instancia de Funcion.")
        self._funcion = valor

    @property
    def numero_asiento(self) -> int:
        return self._numero_asiento

    @numero_asiento.setter
    def numero_asiento(self, valor: int):
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("El número de asiento debe ser un entero.")
        if val_int <= 0:
            raise ValueError("El número de asiento debe ser mayor a cero.")
        self._numero_asiento = val_int

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, valor: float):
        try:
            val_flt = float(valor)
        except (ValueError, TypeError):
            raise ValueError("El precio de la entrada debe ser un valor numérico.")
        if val_flt < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._precio = val_flt

    def __str__(self) -> str:
        return (
            f"Entrada #{self._id_entrada or 'N/A'} - {self._funcion.pelicula.titulo} "
            f"[{self._funcion.tipo}] Asiento: {self._numero_asiento} | ${self._precio:,.0f}"
        )
