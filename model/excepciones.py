"""
Módulo de excepciones de dominio para el negocio Cine Estrella.
Responde a las especificaciones de Fase 2 para control de cupos y clasificación.
"""


class ReglaNegocioException(Exception):
    """Excepción base para violaciones de reglas de negocio del cine."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class SinAsientosException(ReglaNegocioException):
    """Lanzada cuando una función no cuenta con capacidad o asientos disponibles suficientes."""
    def __init__(self, mensaje: str = "No hay asientos suficientes disponibles para esta función."):
        super().__init__(mensaje)


class RestriccionEdadException(ReglaNegocioException):
    """Lanzada cuando un cliente no cumple con la edad mínima exigida por la clasificación."""
    def __init__(self, mensaje: str = "El comprador no cumple con la edad mínima requerida para esta película."):
        super().__init__(mensaje)
