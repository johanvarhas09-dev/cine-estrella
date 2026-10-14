"""
Entidad Cliente: Representa al comprador en el sistema de cine.
Incluye validación estricta de RUT mediante algoritmo Módulo 11 (Casos P07 y P08).
"""
import re


class Cliente:
    def __init__(self, rut: str, nombre: str, edad: int):
        self._rut = None
        self._nombre = None
        self._edad = None

        self.rut = rut
        self.nombre = nombre
        self.edad = edad

    @property
    def rut(self) -> str:
        return self._rut

    @rut.setter
    def rut(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ValueError("El RUT no puede estar vacío y debe ser una cadena.")
        valor_limpio = valor.strip().upper()
        if not self.validar_rut(valor_limpio):
            raise ValueError(f"El RUT '{valor}' no es válido según el algoritmo de verificación.")
        self._rut = self.formatear_rut(valor_limpio)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres.")
        self._nombre = valor.strip()

    @property
    def edad(self) -> int:
        return self._edad

    @edad.setter
    def edad(self, valor: int):
        try:
            valor_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("La edad debe ser un número entero.")
        if valor_int < 0 or valor_int > 130:
            raise ValueError("La edad debe estar comprendida entre 0 y 130 años.")
        self._edad = valor_int

    def validar_edad(self, edad_minima: int) -> bool:
        """
        [FUNCIONALIDAD: CONTROL DE EDAD MÍNIMA - Caso P15]
        Verifica si el cliente cumple con la edad mínima requerida por la clasificación
        de la película antes de autorizar la emisión del boleto.
        Retorna True si cumple o supera la edad mínima, False en caso contrario.
        """
        return self._edad >= edad_minima

    @staticmethod
    def limpiar_rut(rut: str) -> tuple[str, str]:
        """
        [UTILIDAD: SANITIZACIÓN DE RUT]
        Elimina puntos, espacios y guiones mediante expresión regular, normalizando a mayúsculas.
        Retorna una tupla (cuerpo_numerico, digito_verificador).
        Ejemplo: '12.345.678-k' -> ('12345678', 'K')
        """
        rut_limpio = re.sub(r'[^0-9Kk]', '', rut).upper()
        if len(rut_limpio) < 2:
            return "", ""
        return rut_limpio[:-1], rut_limpio[-1]

    @staticmethod
    def validar_rut(rut: str) -> bool:
        """
        [FUNCIONALIDAD: VALIDACIÓN DE RUT CHILENO - ALGORITMO MÓDULO 11 - Casos P07 y P08]
        Aplica el algoritmo estándar de verificación de RUT chileno:
        1. Sanitiza el string eliminando separadores cosméticos (puntos, guiones).
        2. Recorre el cuerpo numérico de derecha a izquierda multiplicando por la secuencia [2, 3, 4, 5, 6, 7, 2, ...].
        3. Acumula la suma ponderada y calcula el residuo (suma % 11).
        4. Determina el dígito verificador esperado:
           - Si 11 - resto == 11 -> DV esperado es '0'
           - Si 11 - resto == 10 -> DV esperado es 'K'
           - En cualquier otro caso -> DV esperado es str(11 - resto)
        5. Compara el dígito calculado con el entregado por el usuario.
        Acepta formatos con y sin puntos o guion: '12.345.678-5', '12345678-5', '123456785'.
        """
        if not rut or not isinstance(rut, str):
            return False
        cuerpo, dv = Cliente.limpiar_rut(rut)
        if not cuerpo or not dv or not cuerpo.isdigit():
            return False

        # Paso 1: Ponderación de dígitos con serie 2 a 7 de derecha a izquierda
        suma = 0
        multiplicador = 2
        for digito in reversed(cuerpo):
            suma += int(digito) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1

        # Paso 2: Cálculo del residuo Módulo 11
        resto = suma % 11
        digito_calculado = 11 - resto

        # Paso 3: Mapeo de casos especiales (0 y K)
        if digito_calculado == 11:
            dv_esperado = '0'
        elif digito_calculado == 10:
            dv_esperado = 'K'
        else:
            dv_esperado = str(digito_calculado)

        # Paso 4: Comparación estricta del dígito verificador
        return dv == dv_esperado

    @staticmethod
    def formatear_rut(rut: str) -> str:
        """
        [FORMATO CANÓNICO]
        Devuelve el RUT en formato uniforme '12345678-K' para almacenamiento consistente en BD.
        """
        cuerpo, dv = Cliente.limpiar_rut(rut)
        return f"{cuerpo}-{dv}"

    def __str__(self) -> str:
        return f"Cliente: {self._nombre} (RUT: {self._rut}, Edad: {self._edad} años)"
