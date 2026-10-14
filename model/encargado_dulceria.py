"""
Subtipo EncargadoDulceria: Empleado especializado en la confitería del cine.
Aplica herencia de Trabajador y restricción estricta de caja.
"""
from model.trabajador import Trabajador


class EncargadoDulceria(Trabajador):
    def __init__(
        self,
        id_trabajador: int | None,
        nombre: str,
        username: str,
        password_hash: str,
        password_plano: str = ""
    ):
        super().__init__(
            id_trabajador=id_trabajador,
            nombre=nombre,
            username=username,
            password_hash=password_hash,
            rol="dulceria",
            password_plano=password_plano
        )

    def puede_vender_entradas(self) -> bool:
        """El encargado de dulcería NO puede vender entradas de cine."""
        return False

    def puede_vender_productos(self) -> bool:
        """El encargado de dulcería tiene permiso para vender snacks y bebidas."""
        return True
