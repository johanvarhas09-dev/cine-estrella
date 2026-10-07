from datetime import date

from model.validacion import decimal_en_rango


class IndicadorDolar:
    """Valor del dólar observado de un día. Lo entrega la API de mindicador.cl."""

    def __init__(self, fecha: date, valor_dolar: float):
        self.fecha = fecha
        self.valor_dolar = valor_dolar

    @property
    def fecha(self) -> date:
        return self.__fecha

    @fecha.setter
    def fecha(self, valor: date) -> None:
        if not isinstance(valor, date):
            raise ValueError("La fecha del indicador no es válida.")
        self.__fecha = valor

    @property
    def valor_dolar(self) -> float:
        return self.__valor_dolar

    @valor_dolar.setter
    def valor_dolar(self, valor: float) -> None:
        # Rango amplio, solo para descartar respuestas absurdas (0, negativos, etc.)
        self.__valor_dolar = decimal_en_rango(valor, 100, 5000, "El valor del dólar")

    def convertir_a_pesos(self, monto_usd: float) -> int:
        return round(monto_usd * self.__valor_dolar)
