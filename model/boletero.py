from model.detalle_venta import DetalleVenta
from model.entrada import Entrada
from model.funcion import Funcion
from model.trabajador import VENDER_ENTRADA, Trabajador
from model.venta import Venta


class Boletero(Trabajador):
    """Atiende la boletería: solo puede vender entradas."""

    def __init__(self, nombre: str, caja: int, id: int | None = None):
        super().__init__(nombre, caja, id)

    def tiene_permiso(self, operacion: str) -> bool:
        return operacion == VENDER_ENTRADA

    def vender_entrada(self, venta: Venta, funcion: Funcion) -> DetalleVenta:
        """Agrega una entrada a la venta, aplicando las dos reglas del negocio.

        Lanza EdadNoPermitidaError si el cliente no cumple la edad mínima de la película,
        y SinAsientosError si la función ya no tiene asientos. En ambos casos la venta no cambia.
        """
        # Primero la edad, para no ocupar un asiento que después no se puede vender
        funcion.pelicula.verificar_edad(venta.cliente.edad)
        funcion.reservar_asiento()
        entrada = Entrada(funcion)
        detalle = DetalleVenta(entrada, 1, entrada.calcular_precio(), self)
        venta.agregar_detalle(detalle)
        return detalle
