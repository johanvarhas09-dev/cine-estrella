"""
Entidad TipoCambio: Almacena la cotización oficial del dólar obtenida desde la API externa.
"""


class TipoCambio:
    def __init__(self, valor: float, fecha: str, fuente: str = "mindicador.cl"):
        self._valor = None
        self._fecha = None
        self._fuente = None

        self.valor = valor
        self.fecha = fecha
        self.fuente = fuente

    @property
    def valor(self) -> float:
        return self._valor

    @valor.setter
    def valor(self, val: float):
        try:
            val_flt = float(val)
        except (ValueError, TypeError):
            raise ValueError("El valor del dólar debe ser numérico.")
        if val_flt <= 0:
            raise ValueError("El valor del dólar debe ser mayor a cero.")
        self._valor = val_flt

    @property
    def fecha(self) -> str:
        return self._fecha

    @fecha.setter
    def fecha(self, val: str):
        if not val or not isinstance(val, str):
            raise ValueError("La fecha del tipo de cambio no puede estar vacía.")
        self._fecha = val.strip()

    @property
    def fuente(self) -> str:
        return self._fuente

    @fuente.setter
    def fuente(self, val: str):
        self._fuente = str(val).strip()

    def __str__(self) -> str:
        return f"Dólar Observado: ${self._valor:,.2f} CLP ({self._fecha}) - Fuente: {self._fuente}"
