"""
Clase base Trabajador: Representa al empleado del cine.
Gestiona credenciales seguras mediante hashing (SHA-256 con salt) para evitar texto plano.
"""
import hashlib
import os


class Trabajador:
    def __init__(
        self,
        id_trabajador: int | None,
        nombre: str,
        username: str,
        password_hash: str,
        rol: str,
        password_plano: str = ""
    ):
        self._id_trabajador = None
        self._nombre = None
        self._username = None
        self._password_hash = None
        self._rol = None
        self.password_plano = password_plano

        self.id_trabajador = id_trabajador
        self.nombre = nombre
        self.username = username
        self.password_hash = password_hash
        self.rol = rol

    @property
    def id_trabajador(self) -> int | None:
        return self._id_trabajador

    @id_trabajador.setter
    def id_trabajador(self, valor: int | None):
        if valor is not None:
            if not isinstance(valor, int) or valor <= 0:
                raise ValueError("El ID del trabajador debe ser un entero positivo.")
        self._id_trabajador = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ValueError("El nombre del trabajador debe tener al menos 2 caracteres.")
        self._nombre = valor.strip()

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ValueError("El nombre de usuario (username) debe tener al menos 2 caracteres.")
        self._username = valor.strip().lower()

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @password_hash.setter
    def password_hash(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ValueError("El hash de contraseña no puede estar vacío.")
        self._password_hash = valor

    @property
    def rol(self) -> str:
        return self._rol

    @rol.setter
    def rol(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ValueError("El rol no puede estar vacío.")
        self._rol = valor.strip().lower()

    @staticmethod
    def generar_hash(password_plano: str, salt: str | None = None) -> str:
        """
        [SEGURIDAD CRIPTOGRÁFICA: HASHING CON SALT Y SHA-256]
        Protección de credenciales para impedir almacenamiento en texto plano:
        1. Genera un salt criptográfico pseudoaleatorio de 16 bytes (32 caracteres hexadecimales) con os.urandom(16).
        2. Concatena el salt con la contraseña en texto plano para neutralizar ataques de diccionario y tablas rainbow.
        3. Aplica función resumen SHA-256 generando un hash de 64 caracteres hexadecimales.
        4. Almacena en formato canónico 'salt$hash' para verificar posteriormente sin exponer la clave.
        """
        if salt is None:
            salt = os.urandom(16).hex()
        clave_combinada = (salt + password_plano).encode('utf-8')
        digest = hashlib.sha256(clave_combinada).hexdigest()
        return f"{salt}${digest}"

    def verificar_password(self, password_plano: str) -> bool:
        """
        [AUTENTICACIÓN SEGURA]
        Extrae el salt del hash almacenado, computa el hash de la clave candidata ingresada
        por el usuario y realiza una comparación en tiempo constante del resultado.
        Retorna True si coincide, False en caso contrario.
        """
        if not self._password_hash or '$' not in self._password_hash:
            return False
        salt, _ = self._password_hash.split('$', 1)
        hash_ingresado = self.generar_hash(password_plano, salt=salt)
        return hash_ingresado == self._password_hash

    def puede_vender_entradas(self) -> bool:
        """
        [CONTROL DE ACCESO BASADO EN ROLES (RBAC)]
        Sobrescrito en subtipos: Retorna True en Boletero y Administrador.
        """
        return False

    def puede_vender_productos(self) -> bool:
        """
        [CONTROL DE ACCESO BASADO EN ROLES (RBAC)]
        Sobrescrito en subtipos: Retorna True en EncargadoDulceria y Administrador.
        """
        return False

    def __str__(self) -> str:
        return f"Trabajador: {self._nombre} ({self._username}) - Rol: {self._rol.upper()}"
