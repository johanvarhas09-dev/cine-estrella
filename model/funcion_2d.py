"""
Subtipo Funcion2D: Proyección estándar de cine.
Sobrescribe calcular_precio() retornando el precio base directamente (Caso P09).
"""
from model.funcion import Funcion
from model.pelicula import Pelicula


class Funcion2D(Funcion):
    def __init__(
        self,
        id_funcion: int | None,
        pelicula: Pelicula,
        fecha_hora: str,
        precio_base: float,
        capacidad: int = 100,
        asientos_disponibles: int | None = None
    ):
        super().__init__(
            id_funcion=id_funcion,
            pelicula=pelicula,
            tipo="2D",
            fecha_hora=fecha_hora,
            precio_base=precio_base,
            capacidad=capacidad,
            asientos_disponibles=asientos_disponibles
        )

    def calcular_precio(self) -> float:
        """La función 2D utiliza directamente el precio base fijado."""
        return self._precio_base
