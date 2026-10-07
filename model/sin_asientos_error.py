class SinAsientosError(Exception):
    """Regla 1 del negocio: no se vende una entrada si la función ya no tiene asientos."""

    def __init__(self, id_funcion: int | None):
        super().__init__(f"La función N° {id_funcion} no tiene asientos disponibles.")
