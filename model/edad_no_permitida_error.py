class EdadNoPermitidaError(Exception):
    """Regla 2 del negocio: no se vende una entrada a quien no cumple la edad mínima de la película."""

    def __init__(self, edad: int, edad_minima: int):
        super().__init__(f"El cliente tiene {edad} años y la película exige como mínimo {edad_minima}.")
