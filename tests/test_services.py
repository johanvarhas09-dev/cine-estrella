"""
Pruebas unitarias para la capa de servicios con simulación de API externa (sin depender de internet).
"""
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os

from dao.conexion import set_db_path
from dao.db_init import inicializar_bd
from dao.pelicula_dao import PeliculaDAO
from dao.funcion_dao import FuncionDAO
from dao.producto_dao import ProductoDAO
from dao.trabajador_dao import TrabajadorDAO
from model.pelicula import Pelicula
from model.funcion_2d import Funcion2D
from model.funcion_vip import FuncionVIP
from model.producto_nacional import ProductoNacional
from model.producto_importado import ProductoImportado
from model.boletero import Boletero
from model.encargado_dulceria import EncargadoDulceria
from model.excepciones import ReglaNegocioException, RestriccionEdadException, SinAsientosException
from service.auth_service import AuthService
from service.tipo_cambio_service import TipoCambioService
from service.venta_service import VentaService


class TestServices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_path = os.path.join(cls.temp_dir.name, "test_services.db")
        set_db_path(cls.db_path)
        inicializar_bd()

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_auth_service(self):
        """Valida inicio de sesión seguro y rechazo de contraseñas incorrectas."""
        auth = AuthService()
        # Usuario demo admin inicial
        admin = auth.autenticar("admin", "admin")
        self.assertIsNotNone(admin)
        self.assertEqual(admin.rol, "admin")
        self.assertTrue(auth.esta_autenticado())

        # Contraseña errónea
        fallo = auth.autenticar("admin", "clave_invalida")
        self.assertIsNone(fallo)

        # Usuario inexistente
        inexistente = auth.autenticar("no_existe", "admin")
        self.assertIsNone(inexistente)

    @patch("requests.get")
    def test_tipo_cambio_exitoso_p16(self, mock_get):
        """Caso P16: Simula respuesta exitosa de mindicador.cl sin conectar a internet."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "serie": [{"fecha": "2026-10-04T03:00:00.000Z", "valor": 950.5}]
        }
        mock_get.return_value = mock_response

        tc = TipoCambioService.obtener_dolar_dia()
        self.assertEqual(tc.valor, 950.5)
        self.assertEqual(tc.fecha, "2026-10-04")

    @patch("requests.get")
    def test_tipo_cambio_sin_internet_p17(self, mock_get):
        """Caso P17: Simula caída de conexión y verifica que lance ReglaNegocioException sin caerse."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Fallo de red")

        with self.assertRaises(ReglaNegocioException) as cm:
            TipoCambioService.obtener_dolar_dia()
        self.assertIn("Sin conexión a internet", str(cm.exception))

    def test_validar_cliente_edad_y_rut(self):
        """Valida que un menor de 18 años sea rechazado para película +18 (P15)."""
        peli18 = PeliculaDAO.crear(Pelicula(id_pelicula=None, titulo="Terror +18", clasificacion_edad=18))
        func = FuncionDAO.crear(Funcion2D(id_funcion=None, pelicula=peli18, fecha_hora="2026-10-10 22:00", precio_base=5000.0, capacidad=50))

        # Menor de 15 años debe ser rechazado
        with self.assertRaises(RestriccionEdadException):
            VentaService.validar_cliente_para_funcion(func.id_funcion, "12.345.678-5", "Menor", 15)

        # Mayor de 18 años debe ser aceptado
        cli = VentaService.validar_cliente_para_funcion(func.id_funcion, "12.345.678-5", "Mayor", 20)
        self.assertEqual(cli.edad, 20)

        # RUT incorrecto debe ser rechazado (P08)
        with self.assertRaises(ReglaNegocioException):
            VentaService.validar_cliente_para_funcion(func.id_funcion, "12.345.678-9", "Juan", 25)

    def test_permisos_y_cupos_en_lineas_detalle(self):
        """Valida que un cajero solo pueda vender lo permitido por su rol y control de cupos."""
        peli = PeliculaDAO.crear(Pelicula(id_pelicula=None, titulo="Familiar", clasificacion_edad=0))
        func = FuncionDAO.crear(FuncionVIP(id_funcion=None, pelicula=peli, fecha_hora="2026-10-10 18:00", precio_base=6000.0, capacidad=2))
        prod = ProductoDAO.crear(ProductoNacional(id_producto=None, nombre="Popcorn", precio_base=2500.0))

        hash_p = Boletero.generar_hash("123")
        boletero = Boletero(id_trabajador=1, nombre="Boletero", username="b1", password_hash=hash_p)
        dulcero = EncargadoDulceria(id_trabajador=2, nombre="Dulcero", username="d1", password_hash=hash_p)

        # Boletero no puede vender confites
        with self.assertRaises(ReglaNegocioException):
            VentaService.crear_detalle_producto(prod.id_producto, 1, boletero)

        # Dulcero no puede vender entradas
        with self.assertRaises(ReglaNegocioException):
            VentaService.crear_detalle_entrada(func.id_funcion, 1, dulcero)

        # Boletero vende 2 entradas correctamente
        det1 = VentaService.crear_detalle_entrada(func.id_funcion, 2, boletero)
        self.assertEqual(det1.cantidad, 2)

        # Si se piden 3 entradas cuando solo caben 2, lanza SinAsientosException (P14)
        with self.assertRaises(SinAsientosException):
            VentaService.crear_detalle_entrada(func.id_funcion, 3, boletero)


if __name__ == "__main__":
    unittest.main()
