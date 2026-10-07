"""Lectura validada de lo que escribe el usuario en la consola.

Cada función revisa tipo, formato y rango ANTES de usar el dato. Si el dato es inválido,
muestra el motivo y vuelve a preguntar, sin detener el programa.
Si se entrega "por_defecto", presionar Enter conserva ese valor (útil al modificar).
"""
import math
from datetime import datetime, timedelta

from model.cliente import Cliente


def _error(mensaje: str) -> None:
    print(f"  [ERROR] {mensaje} Intente nuevamente.")


def leer_texto(mensaje: str, maximo: int = 60, por_defecto: str | None = None) -> str:
    while True:
        texto = input(mensaje).strip()
        if not texto and por_defecto is not None:
            return por_defecto
        if not texto:
            _error("El valor no puede quedar vacío.")
        elif len(texto) > maximo:
            _error(f"Máximo {maximo} caracteres.")
        elif not texto.isprintable():
            _error("El texto contiene caracteres no permitidos.")
        else:
            return texto


def leer_entero(mensaje: str, minimo: int, maximo: int, por_defecto: int | None = None) -> int:
    while True:
        texto = input(mensaje).strip()
        if not texto and por_defecto is not None:
            return por_defecto
        try:
            numero = int(texto)
        except ValueError:
            _error("Debe ingresar un número entero, sin puntos ni letras.")
            continue
        if minimo <= numero <= maximo:
            return numero
        _error(f"El número debe estar entre {minimo} y {maximo}.")


def leer_decimal(mensaje: str, minimo: float, maximo: float, por_defecto: float | None = None) -> float:
    while True:
        texto = input(mensaje).strip()
        if not texto and por_defecto is not None:
            return por_defecto
        try:
            numero = float(texto.replace(",", "."))
        except ValueError:
            _error("Debe ingresar un número (use punto o coma para los decimales).")
            continue
        if not math.isfinite(numero):
            _error("Debe ingresar un número válido.")
        elif minimo <= numero <= maximo:
            return numero
        else:
            _error(f"El número debe estar entre {minimo} y {maximo}.")


def leer_opcion(mensaje: str, opciones: tuple[str, ...]) -> str:
    while True:
        texto = input(mensaje).strip()
        if texto in opciones:
            return texto
        _error(f"Opción no válida. Opciones: {', '.join(opciones)}.")


def leer_si_no(mensaje: str) -> bool:
    while True:
        texto = input(mensaje + " (S/N): ").strip().upper()
        if texto in ("S", "N"):
            return texto == "S"
        _error("Responda S o N.")


def leer_fecha_hora(mensaje: str, por_defecto: datetime | None = None) -> datetime:
    """Fecha y hora con formato dd-mm-aaaa hh:mm, desde ahora y hasta un año más."""
    while True:
        texto = input(mensaje).strip()
        if not texto and por_defecto is not None:
            return por_defecto
        try:
            fecha = datetime.strptime(texto, "%d-%m-%Y %H:%M")
        except ValueError:
            _error("Use el formato dd-mm-aaaa hh:mm, por ejemplo 07-10-2026 19:30.")
            continue
        ahora = datetime.now()
        if fecha < ahora:
            _error("La fecha y hora no puede estar en el pasado.")
        elif fecha > ahora + timedelta(days=365):
            _error("La fecha no puede ser a más de un año.")
        else:
            return fecha


def leer_rut(mensaje: str, permitir_vacio: bool = False) -> str:
    """Pide un RUT hasta que el dígito verificador sea correcto y lo devuelve como 12345678-5.

    Con permitir_vacio=True, presionar Enter devuelve "" para cancelar.
    """
    while True:
        texto = input(mensaje).strip()
        if not texto and permitir_vacio:
            return ""
        # Se usa la misma regla que aplica el setter de Cliente
        if Cliente.validar_rut(texto):
            limpio = texto.replace(".", "").replace("-", "").upper()
            return f"{limpio[:-1]}-{limpio[-1]}"
        _error(f"RUT inválido: '{texto}'. Revise el formato (12345678-5) y el dígito verificador.")
