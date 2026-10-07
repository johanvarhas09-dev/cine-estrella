from abc import ABC, abstractmethod

from model.validacion import entero_en_rango, id_valido, texto_no_vacio

# Operaciones que se controlan con tiene_permiso()
VENDER_ENTRADA = "vender_entrada"
VENDER_PRODUCTO = "vender_producto"


class Trabajador(ABC):
    """Empleado que atiende una caja del cine. Cada subtipo define qué operaciones puede hacer."""

    def __init__(self, nombre: str, caja: int, id: int | None = None):
        self.id = id
        self.nombre = nombre
        self.caja = caja

    @property
    def id(self) -> int | None:
        return self.__id

    @id.setter
    def id(self, valor: int | None) -> None:
        self.__id = id_valido(valor)

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre = texto_no_vacio(valor, 60, "El nombre del trabajador")

    @property
    def caja(self) -> int:
        return self.__caja

    @caja.setter
    def caja(self, valor: int) -> None:
        self.__caja = entero_en_rango(valor, 1, 20, "El número de caja")

    @abstractmethod
    def tiene_permiso(self, operacion: str) -> bool:
        """Indica si este trabajador puede realizar la operación indicada."""
