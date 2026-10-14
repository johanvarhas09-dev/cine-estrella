"""
Entidad DetalleVenta: Representa una línea específica dentro de una transacción de venta.
Permite registrar tanto entradas como confites, atribuyendo cada ítem al trabajador que lo registró.
"""


class DetalleVenta:
    def __init__(
        self,
        id_detalle: int | None,
        id_venta: int | None,
        tipo_item: str,         # 'entrada' o 'producto'
        id_item: int,           # id_funcion (si entrada) o id_producto (si producto)
        descripcion: str,
        cantidad: int,
        precio_unitario: float,
        id_trabajador: int,     # ID del trabajador que registró la línea
        subtotal: float | None = None
    ):
        self._id_detalle = None
        self._id_venta = None
        self._tipo_item = None
        self._id_item = None
        self._descripcion = None
        self._cantidad = None
        self._precio_unitario = None
        self._id_trabajador = None
        self._subtotal = None

        self.id_detalle = id_detalle
        self.id_venta = id_venta
        self.tipo_item = tipo_item
        self.id_item = id_item
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.id_trabajador = id_trabajador
        self.subtotal = (cantidad * precio_unitario) if subtotal is None else subtotal

    @property
    def id_detalle(self) -> int | None:
        return self._id_detalle

    @id_detalle.setter
    def id_detalle(self, valor: int | None):
        if valor is not None and (not isinstance(valor, int) or valor <= 0):
            raise ValueError("El ID del detalle debe ser un entero positivo.")
        self._id_detalle = valor

    @property
    def id_venta(self) -> int | None:
        return self._id_venta

    @id_venta.setter
    def id_venta(self, valor: int | None):
        if valor is not None and (not isinstance(valor, int) or valor <= 0):
            raise ValueError("El ID de la venta debe ser un entero positivo.")
        self._id_venta = valor

    @property
    def tipo_item(self) -> str:
        return self._tipo_item

    @tipo_item.setter
    def tipo_item(self, valor: str):
        if not valor or valor.lower() not in ("entrada", "producto"):
            raise ValueError("El tipo de ítem debe ser 'entrada' o 'producto'.")
        self._tipo_item = valor.lower()

    @property
    def id_item(self) -> int:
        return self._id_item

    @id_item.setter
    def id_item(self, valor: int):
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("El ID del ítem referenciado debe ser un entero.")
        if val_int <= 0:
            raise ValueError("El ID del ítem debe ser mayor a cero.")
        self._id_item = val_int

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ValueError("La descripción no puede estar vacía.")
        self._descripcion = valor.strip()

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int):
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("La cantidad debe ser un número entero.")
        if val_int <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        self._cantidad = val_int

    @property
    def precio_unitario(self) -> float:
        return self._precio_unitario

    @precio_unitario.setter
    def precio_unitario(self, valor: float):
        try:
            val_flt = float(valor)
        except (ValueError, TypeError):
            raise ValueError("El precio unitario debe ser numérico.")
        if val_flt < 0:
            raise ValueError("El precio unitario no puede ser negativo.")
        self._precio_unitario = val_flt

    @property
    def id_trabajador(self) -> int:
        return self._id_trabajador

    @id_trabajador.setter
    def id_trabajador(self, valor: int):
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("El ID del trabajador debe ser un entero.")
        if val_int <= 0:
            raise ValueError("El ID del trabajador debe ser mayor a cero.")
        self._id_trabajador = val_int

    @property
    def subtotal(self) -> float:
        return self._subtotal

    @subtotal.setter
    def subtotal(self, valor: float):
        try:
            val_flt = float(valor)
        except (ValueError, TypeError):
            raise ValueError("El subtotal debe ser numérico.")
        if val_flt < 0:
            raise ValueError("El subtotal no puede ser negativo.")
        self._subtotal = val_flt

    def calcular_subtotal(self) -> float:
        self._subtotal = self._cantidad * self._precio_unitario
        return self._subtotal

    def __str__(self) -> str:
        return f"{self._descripcion} x{self._cantidad} @ ${self._precio_unitario:,.0f} = ${self._subtotal:,.0f}"
