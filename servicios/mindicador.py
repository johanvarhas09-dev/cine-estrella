from datetime import date

import requests

from model.indicador_dolar import IndicadorDolar


class IndicadorNoDisponibleError(Exception):
    """La API no respondió o respondió algo que no se puede usar para calcular precios."""


class ServicioMindicador:
    """Consulta el dólar observado del día en la API pública https://mindicador.cl."""

    URL_BASE = "https://mindicador.cl/api/"

    def __init__(self, url_base: str = URL_BASE, timeout: float = 10):
        self.__url_base = url_base
        # Tiempo máximo de espera en segundos: si la API no responde, el programa no queda colgado
        self.__timeout = timeout

    @property
    def url_base(self) -> str:
        return self.__url_base

    def obtener_dolar(self) -> IndicadorDolar:
        """Devuelve el dólar del día o lanza IndicadorNoDisponibleError explicando qué falló."""
        url = self.__url_base + "dolar"
        try:
            respuesta = requests.get(url, timeout=self.__timeout)
            respuesta.raise_for_status()
            datos = respuesta.json()
            ultimo = datos["serie"][0]
            return IndicadorDolar(date.fromisoformat(ultimo["fecha"][:10]), float(ultimo["valor"]))
        except requests.exceptions.Timeout:
            raise IndicadorNoDisponibleError(
                f"la API no respondió en {self.__timeout} segundos (tiempo máximo de espera).") from None
        except requests.exceptions.ConnectionError:
            raise IndicadorNoDisponibleError(
                "no se pudo conectar con la API (sin internet o servidor caído).") from None
        except requests.exceptions.HTTPError as error:
            raise IndicadorNoDisponibleError(
                f"la API respondió con el error HTTP {error.response.status_code}.") from None
        except (ValueError, KeyError, IndexError, TypeError):
            # JSON inválido, sin la serie esperada o con un valor que no es un número razonable
            raise IndicadorNoDisponibleError("la API respondió datos con un formato inesperado.") from None
        except requests.exceptions.RequestException as error:
            raise IndicadorNoDisponibleError(f"error al consultar la API: {error}") from None
