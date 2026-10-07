"""Funciones de validación que reutilizan los setters de las clases del modelo.

Cada función devuelve el valor ya validado o lanza ValueError con un mensaje claro.
"""


def entero_en_rango(valor: int, minimo: int, maximo: int, campo: str) -> int:
    # bool es subclase de int en Python, por eso se excluye de forma explícita
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ValueError(f"{campo} debe ser un número entero.")
    if not minimo <= valor <= maximo:
        raise ValueError(f"{campo} debe estar entre {minimo} y {maximo}.")
    return valor


def decimal_en_rango(valor: float, minimo: float, maximo: float, campo: str) -> float:
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        raise ValueError(f"{campo} debe ser un número.")
    if not minimo <= valor <= maximo:
        raise ValueError(f"{campo} debe estar entre {minimo} y {maximo}.")
    return float(valor)


def texto_no_vacio(valor: str, maximo: int, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} no puede estar vacío.")
    valor = valor.strip()
    if len(valor) > maximo:
        raise ValueError(f"{campo} admite como máximo {maximo} caracteres.")
    return valor


def id_valido(valor: int | None) -> int | None:
    # El id es None mientras el objeto todavía no se guarda en la base de datos
    if valor is None:
        return None
    return entero_en_rango(valor, 1, 10**9, "El id")
