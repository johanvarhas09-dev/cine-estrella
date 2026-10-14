"""
Subtipo Funcion3D: Proyección tridimensional con tecnología especial.
Aplica polimorfismo mediante recargo sobre el precio base (Caso P10).
"""
from model.funcion import Funcion
from model.pelicula import Pelicula


class Funcion3D(Funcion):
    RECARGO_3D_DEFAULT = 1500.0

    def __init__(
        self,
        id_funcion: int | None,
        pelicula: Pelicula,
        fecha_hora: str,
        precio_base: float,
        capacidad: int = 80,
        asientos_disponibles: int | None = None,
        recargo_3d: float = RECARGO_3D_DEFAULT
    ):
        super().__init__(
            id_funcion=id_funcion,
            pelicula=pelicula,
            tipo="3D",
            fecha_hora=fecha_hora,
            precio_base=precio_base,
            capacidad=capacidad,
            asientos_disponibles=asientos_disponibles
        )
        self._recargo_3d = recargo_3d

    @property
    def recargo_3d(self) -> float:
        return self._recargo_3d

    @recargo_3d.setter
    def recargo_3d(self, valor: float):
        try:
            val_flt = float(valor)
        except (ValueError, TypeError):
            raise ValueError("El recargo 3D debe ser un valor numérico.")
        if val_flt < 0:
            raise ValueError("El recargo 3D no puede ser negativo.")
        self._recargo_3d = val_flt

    def calcular_precio(self) -> float:
        """La función 3D suma su recargo tecnológico al precio base."""
        return self._precio_base + self._recargo_3d
