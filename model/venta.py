"""
Entidad Venta: Representa una transacción unificada de compra en el cine.
Implementa una relación de composición con DetalleVenta (Venta ♦── 1..* DetalleVenta).
Permite agrupar entradas y productos en un mismo folio fiscal (Casos P12 y P13).
"""
from datetime import datetime
from model.cliente import Cliente
from model.detalle_venta import DetalleVenta


class Venta:
    def __init__(
        self,
        id_venta: int | None,
        cliente: Cliente | None = None,
        fecha_hora: str | None = None,
        detalles: list[DetalleVenta] | None = None
    ):
        self._id_venta = None
        self._cliente = None
        self._fecha_hora = None
        self._detalles: list[DetalleVenta] = []
        self._total = 0.0

        self.id_venta = id_venta
        self.cliente = cliente
        self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if fecha_hora is None else fecha_hora

        if detalles:
            for d in detalles:
                self.agregar_detalle(d)

    @property
    def id_venta(self) -> int | None:
        return self._id_venta

    @id_venta.setter
    def id_venta(self, valor: int | None):
        if valor is not None and (not isinstance(valor, int) or valor <= 0):
            raise ValueError("El ID de la venta debe ser un entero positivo.")
        self._id_venta = valor

    @property
    def cliente(self) -> Cliente | None:
        return self._cliente

    @cliente.setter
    def cliente(self, valor: Cliente | None):
        if valor is not None and not isinstance(valor, Cliente):
            raise TypeError("El cliente asociado debe ser una instancia de la clase Cliente o None.")
        self._cliente = valor

    @property
    def fecha_hora(self) -> str:
        return self._fecha_hora

    @fecha_hora.setter
    def fecha_hora(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ValueError("La fecha y hora de la venta no puede estar vacía.")
        self._fecha_hora = valor.strip()

    @property
    def detalles(self) -> list[DetalleVenta]:
        return list(self._detalles)

    @property
    def total(self) -> float:
        return self._total

    def agregar_detalle(self, detalle: DetalleVenta):
        """Agrega una línea de detalle asegurando la composición de la venta."""
        if not isinstance(detalle, DetalleVenta):
            raise TypeError("El detalle debe ser una instancia de DetalleVenta.")
        self._detalles.append(detalle)
        self.calcular_total()

    def quitar_detalle(self, indice: int) -> DetalleVenta | None:
        """Elimina una línea de detalle por su índice y actualiza el total."""
        if 0 <= indice < len(self._detalles):
            removido = self._detalles.pop(indice)
            self.calcular_total()
            return removido
        return None

    def limpiar_detalles(self):
        """Elimina todas las líneas de detalle y reinicia el total a 0."""
        self._detalles.clear()
        self._total = 0.0

    def calcular_total(self) -> float:
        """Calcula y actualiza la sumatoria de todas las líneas de detalle."""
        self._total = sum(d.subtotal for d in self._detalles)
        return self._total

    def tiene_entradas(self) -> bool:
        return any(d.tipo_item == "entrada" for d in self._detalles)

    def tiene_productos(self) -> bool:
        return any(d.tipo_item == "producto" for d in self._detalles)

    def __str__(self) -> str:
        rut = self._cliente.rut if self._cliente else "General"
        return f"Venta #{self._id_venta or 'N/A'} [{self._fecha_hora}] - Cliente: {rut} - Total: ${self._total:,.0f}"
