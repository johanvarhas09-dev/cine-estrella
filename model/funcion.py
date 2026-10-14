"""
Clase base Funcion: Representa la proyección programada de una película en una sala.
Sirve de clase padre para Funcion2D, Funcion3D y FuncionVIP aplicando polimorfismo.
"""
from model.pelicula import Pelicula
from model.excepciones import SinAsientosException


class Funcion:
    def __init__(
        self,
        id_funcion: int | None,
        pelicula: Pelicula,
        tipo: str,
        fecha_hora: str,
        precio_base: float,
        capacidad: int,
        asientos_disponibles: int | None = None
    ):
        self._id_funcion = None
        self._pelicula = None
        self._tipo = None
        self._fecha_hora = None
        self._precio_base = None
        self._capacidad = None
        self._asientos_disponibles = None

        self.id_funcion = id_funcion
        self.pelicula = pelicula
        self.tipo = tipo
        self.fecha_hora = fecha_hora
        self.precio_base = precio_base
        self.capacidad = capacidad
        self.asientos_disponibles = capacidad if asientos_disponibles is None else asientos_disponibles

    @property
    def id_funcion(self) -> int | None:
        return self._id_funcion

    @id_funcion.setter
    def id_funcion(self, valor: int | None):
        if valor is not None:
            if not isinstance(valor, int) or valor <= 0:
                raise ValueError("El ID de función debe ser un entero positivo.")
        self._id_funcion = valor

    @property
    def pelicula(self) -> Pelicula:
        return self._pelicula

    @pelicula.setter
    def pelicula(self, valor: Pelicula):
        if not isinstance(valor, Pelicula):
            raise TypeError("La película asociada debe ser una instancia de la clase Pelicula.")
        self._pelicula = valor

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ValueError("El tipo de función no puede estar vacío.")
        self._tipo = valor.strip().upper()

    @property
    def fecha_hora(self) -> str:
        return self._fecha_hora

    @fecha_hora.setter
    def fecha_hora(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 5:
            raise ValueError("La fecha y hora debe tener un formato válido (ej: '2026-10-05 18:00').")
        self._fecha_hora = valor.strip()

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @precio_base.setter
    def precio_base(self, valor: float):
        try:
            val_flt = float(valor)
        except (ValueError, TypeError):
            raise ValueError("El precio base debe ser un valor numérico.")
        if val_flt < 0:
            raise ValueError("El precio base no puede ser negativo.")
        self._precio_base = val_flt

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor: int):
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("La capacidad debe ser un número entero.")
        if val_int <= 0:
            raise ValueError("La capacidad de la sala debe ser mayor a cero.")
        self._capacidad = val_int

    @property
    def asientos_disponibles(self) -> int:
        return self._asientos_disponibles

    @asientos_disponibles.setter
    def asientos_disponibles(self, valor: int):
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("Los asientos disponibles deben ser un número entero.")
        if val_int < 0:
            raise ValueError("Los asientos disponibles no pueden ser negativos.")
        if self._capacidad is not None and val_int > self._capacidad:
            raise ValueError("Los asientos disponibles no pueden superar la capacidad de la sala.")
        self._asientos_disponibles = val_int

    @property
    def asientos_vendidos(self) -> int:
        return self._capacidad - self._asientos_disponibles

    def calcular_precio(self) -> float:
        """Método polimórfico base que calcula el precio de la entrada."""
        return self._precio_base

    def hay_asientos(self, cantidad: int = 1) -> bool:
        """Comprueba si hay al menos la cantidad requerida de asientos disponibles."""
        return self._asientos_disponibles >= cantidad

    def reservar_asientos(self, cantidad: int = 1):
        """
        Descuenta los asientos vendidos. Lanza SinAsientosException si excede la capacidad.
        Asegura el cumplimiento de la regla de no vender más que la capacidad.
        """
        if not self.hay_asientos(cantidad):
            raise SinAsientosException(
                f"No es posible vender {cantidad} entrada(s). "
                f"Disponibles: {self._asientos_disponibles} de {self._capacidad}."
            )
        self._asientos_disponibles -= cantidad

    def liberar_asientos(self, cantidad: int = 1):
        """Devuelve asientos en caso de anulación de proceso."""
        if self._asientos_disponibles + cantidad > self._capacidad:
            self._asientos_disponibles = self._capacidad
        else:
            self._asientos_disponibles += cantidad

    def __str__(self) -> str:
        return (
            f"[{self._tipo}] {self._pelicula.titulo} - {self._fecha_hora} | "
            f"Precio: ${self.calcular_precio():,.0f} | Disp: {self._asientos_disponibles}/{self._capacidad}"
        )
