import re


class Cliente:
    """Persona que compra en el cine. Su RUT y su edad se validan en los setters."""

    def __init__(self, rut: str, nombre: str, edad: int):
        # Se asigna a través de las propiedades para que pase por la validación de cada setter
        self.rut = rut
        self.nombre = nombre
        self.edad = edad

    @staticmethod
    def validar_rut(rut: str) -> bool:
        """Revisa el formato y el dígito verificador (módulo 11) de un RUT chileno.

        Acepta 12.345.678-5, 12345678-5 o 123456785.
        """
        if not isinstance(rut, str):
            return False
        limpio = rut.replace(".", "").replace("-", "").strip().upper()
        if not re.fullmatch(r"\d{7,8}[0-9K]", limpio):
            return False
        cuerpo, digito_verificador = limpio[:-1], limpio[-1]

        # Cada dígito, de derecha a izquierda, se multiplica por la serie 2, 3, 4, 5, 6, 7, 2, 3...
        suma = 0
        factor = 2
        for digito in reversed(cuerpo):
            suma += int(digito) * factor
            factor = 2 if factor == 7 else factor + 1
        resto = 11 - (suma % 11)
        if resto == 11:
            esperado = "0"
        elif resto == 10:
            esperado = "K"
        else:
            esperado = str(resto)
        return digito_verificador == esperado

    @property
    def rut(self) -> str:
        return self.__rut

    @rut.setter
    def rut(self, valor: str) -> None:
        if not Cliente.validar_rut(valor):
            raise ValueError(f"RUT inválido: '{valor}'. Debe tener el formato 12345678-5 "
                             "y un dígito verificador correcto.")
        limpio = valor.replace(".", "").replace("-", "").strip().upper()
        # Se guarda siempre con el mismo formato: cuerpo, guion y dígito (ej. 12345678-5)
        self.__rut = f"{limpio[:-1]}-{limpio[-1]}"

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValueError("El nombre debe ser texto.")
        valor = valor.strip()
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü' .-]{2,60}", valor):
            raise ValueError("El nombre debe tener entre 2 y 60 letras (se permiten espacios, punto y guion).")
        self.__nombre = valor

    @property
    def edad(self) -> int:
        return self.__edad

    @edad.setter
    def edad(self, valor: int) -> None:
        # bool es subclase de int en Python, por eso se excluye de forma explícita
        if not isinstance(valor, int) or isinstance(valor, bool):
            raise ValueError("La edad debe ser un número entero.")
        if not 0 <= valor <= 120:
            raise ValueError("La edad debe estar entre 0 y 120 años.")
        self.__edad = valor
