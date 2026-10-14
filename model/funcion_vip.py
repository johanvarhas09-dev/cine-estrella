"""
Subtipo FuncionVIP: Sala premium con servicio de confort y asientos limitados (Caso P11).
Aplica polimorfismo mediante recargo VIP y control estricto de cupos reducidos.
"""
from model.funcion import Funcion
from model.pelicula import Pelicula


class FuncionVIP(Funcion):
    # [REGLA DE NEGOCIO: SALA VIP]
    # La capacidad máxima de una sala VIP está estrictamente acotada a 30 asientos (exigencia del cliente).
    # Posee además un recargo premium por amenidades exclusivas (reclinación, atención a la butaca).
    RECARGO_VIP_DEFAULT = 3000.0
    CAPACIDAD_MAX_VIP = 30

    def __init__(
        self,
        id_funcion: int | None,
        pelicula: Pelicula,
        fecha_hora: str,
        precio_base: float,
        capacidad: int = CAPACIDAD_MAX_VIP,
        asientos_disponibles: int | None = None,
        recargo_vip: float = RECARGO_VIP_DEFAULT
    ):
        super().__init__(
            id_funcion=id_funcion,
            pelicula=pelicula,
            tipo="VIP",
            fecha_hora=fecha_hora,
            precio_base=precio_base,
            capacidad=capacidad,
            asientos_disponibles=asientos_disponibles
        )
        self._recargo_vip = recargo_vip

    @property
    def recargo_vip(self) -> float:
        return self._recargo_vip

    @recargo_vip.setter
    def recargo_vip(self, valor: float):
        try:
            val_flt = float(valor)
        except (ValueError, TypeError):
            raise ValueError("El recargo VIP debe ser un valor numérico.")
        if val_flt < 0:
            raise ValueError("El recargo VIP no puede ser negativo.")
        self._recargo_vip = val_flt

    def calcular_precio(self) -> float:
        """La función VIP añade un recargo premium sobre el precio base."""
        return self._precio_base + self._recargo_vip
