"""
Subtipo Boletero: Empleado especializado y autorizado exclusivamente para vender entradas.
Aplica herencia de Trabajador y restricción estricta de caja.
"""
from model.trabajador import Trabajador


class Boletero(Trabajador):
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
            rol="boletero",
            password_plano=password_plano
        )

    def puede_vender_entradas(self) -> bool:
        """El boletero tiene permiso para vender entradas."""
        return True

    def puede_vender_productos(self) -> bool:
        """El boletero NO tiene permiso para vender productos de confitería."""
        return False
