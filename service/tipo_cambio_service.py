"""
Servicio de integración con la API de indicadores económicos (mindicador.cl).
Consulta el valor oficial del dólar observado en tiempo real con timeout y manejo robusto de errores.
No inventa tasas simuladas ni oculta fallos de conectividad (Casos P16 y P17).
"""
import requests
from dao.conexion import obtener_conexion
from model.tipo_cambio import TipoCambio
from model.excepciones import ReglaNegocioException


class TipoCambioService:
    API_URL = "https://mindicador.cl/api/dolar"
    TIMEOUT_SEGUNDOS = 5

    @classmethod
    def obtener_dolar_dia(cls) -> TipoCambio:
        """
        [FUNCIONALIDAD: CONSULTA OFICIAL DEL DÓLAR OBSERVADO - Casos P16 y P17]
        Realiza una petición HTTP GET a la API REST pública de https://mindicador.cl/api/dolar.
        Características de diseño:
        1. Timeout estricto de 5 segundos para impedir que la interfaz gráfica o consola se congele.
        2. Extracción del último valor de la serie histórica y formateo de fecha ISO (YYYY-MM-DD).
        3. Persistencia en tabla de auditoría 'tipo_cambio_log' para trazabilidad histórica.
        4. Tolerancia a Fallos (Caso P17): Captura Timeout, ConnectionError y errores de deserialización JSON,
           traduciéndolos a ReglaNegocioException con mensajes amigables para el usuario.
           NO se inventan tasas ficticias ni se cae el sistema si falla el internet.
        """
        try:
            # Petición GET con control estricto de tiempo de respuesta
            respuesta = requests.get(cls.API_URL, timeout=cls.TIMEOUT_SEGUNDOS)
            if respuesta.status_code != 200:
                raise ReglaNegocioException(
                    f"La API de mindicador.cl respondió con código de estado HTTP {respuesta.status_code}."
                )

            datos = respuesta.json()
            if "serie" not in datos or not datos["serie"]:
                raise ReglaNegocioException(
                    "La respuesta de la API no contiene la serie histórica del dólar."
                )

            # Extracción del valor más reciente publicado
            ultimo_registro = datos["serie"][0]
            valor = float(ultimo_registro["valor"])
            fecha_iso = str(ultimo_registro["fecha"])
            fecha_corta = fecha_iso[:10]  # YYYY-MM-DD

            tipo_cambio = TipoCambio(valor=valor, fecha=fecha_corta, fuente="mindicador.cl")

            # Auditoría: Registrar en log de tipo de cambio de la BD local
            cls._guardar_log(tipo_cambio)

            return tipo_cambio

        except requests.exceptions.Timeout:
            # Caso P17: Manejo de corte o latencia de red sin abortar el programa
            raise ReglaNegocioException(
                "Tiempo de espera agotado (timeout) al conectar con https://mindicador.cl/api/dolar."
            )
        except requests.exceptions.ConnectionError:
            # Caso P17: Manejo de ausencia de internet o falla DNS sin abortar el programa
            raise ReglaNegocioException(
                "Sin conexión a internet o no se pudo resolver el host mindicador.cl."
            )
        except requests.exceptions.RequestException as e:
            raise ReglaNegocioException(
                f"Error en la petición HTTP a la API de tipo de cambio: {str(e)}"
            )
        except (ValueError, KeyError, TypeError) as e:
            raise ReglaNegocioException(
                f"Formato de respuesta inesperado desde la API: {str(e)}"
            )

    @classmethod
    def _guardar_log(cls, tipo_cambio: TipoCambio):
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tipo_cambio_log (valor, fecha, fuente) VALUES (?, ?, ?)",
                (tipo_cambio.valor, tipo_cambio.fecha, tipo_cambio.fuente)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass  # Si falla el log secundario, no bloquea el cálculo del dólar
