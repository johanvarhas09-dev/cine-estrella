"""
Servicio de autenticación y sesiones para Cine Estrella.
Verifica credenciales contra hashes seguros en SQLite.
"""
from dao.trabajador_dao import TrabajadorDAO
from model.trabajador import Trabajador


class AuthService:
    def __init__(self):
        self._usuario_actual: Trabajador | None = None

    @property
    def usuario_actual(self) -> Trabajador | None:
        return self._usuario_actual

    def autenticar(self, username: str, password_plano: str) -> Trabajador | None:
        """
        Valida las credenciales ingresadas.
        Retorna la instancia del trabajador si son correctas, o None si fallan.
        """
        if not username or not password_plano:
            return None

        trabajador = TrabajadorDAO.obtener_por_username(username)
        if not trabajador:
            return None

        if trabajador.verificar_password(password_plano):
            self._usuario_actual = trabajador
            return trabajador

        return None

    def cerrar_sesion(self):
        self._usuario_actual = None

    def esta_autenticado(self) -> bool:
        return self._usuario_actual is not None
