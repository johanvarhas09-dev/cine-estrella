"""
Pruebas unitarias para la capa DAO y transaccionalidad de SQLite.
Cubre creación, persistencia, modificación, eliminación protegida y transacciones atómicas (P02-P06, P12, P13).
"""
import unittest
import os
import tempfile

from dao.conexion import set_db_path
from dao.db_init import inicializar_bd
from dao.pelicula_dao import PeliculaDAO
from dao.funcion_dao import FuncionDAO
from dao.producto_dao import ProductoDAO
from dao.trabajador_dao import TrabajadorDAO
from dao.venta_dao import VentaDAO
from model.pelicula import Pelicula
from model.funcion_2d import Funcion2D
from model.funcion_vip import FuncionVIP
from model.producto_nacional import ProductoNacional
from model.producto_importado import ProductoImportado
from model.boletero import Boletero
from model.encargado_dulceria import EncargadoDulceria
from model.cliente import Cliente
from model.venta import Venta
from model.detalle_venta import DetalleVenta
from model.excepciones import ReglaNegocioException, SinAsientosException


class TestDAO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Crear base de datos temporal aislada para pruebas
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_path = os.path.join(cls.temp_dir.name, "test_cine.db")
        set_db_path(cls.db_path)
        inicializar_bd()

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_crud_pelicula_p02_p03_p04_p06(self):
        """
        P02: Crear película
        P03: Listar película
        P04: Modificar película
        P06: Eliminar película
        """
        # P02: Crear
        peli = Pelicula(id_pelicula=None, titulo="Estreno Especial", clasificacion_edad=14, duracion_minutos=120)
        peli_guardada = PeliculaDAO.crear(peli)
        self.assertIsNotNone(peli_guardada.id_pelicula)

        # P03: Listar
        peliculas = PeliculaDAO.listar()
        self.assertTrue(any(p.id_pelicula == peli_guardada.id_pelicula for p in peliculas))

        # P04: Modificar
        peli_guardada.clasificacion_edad = 18
        peli_guardada.titulo = "Estreno Especial (Modificada)"
        modificado = PeliculaDAO.modificar(peli_guardada)
        self.assertTrue(modificado)

        peli_obtenida = PeliculaDAO.obtener_por_id(peli_guardada.id_pelicula)
        self.assertEqual(peli_obtenida.clasificacion_edad, 18)
        self.assertEqual(peli_obtenida.titulo, "Estreno Especial (Modificada)")

        # P06: Eliminar
        eliminado = PeliculaDAO.eliminar(peli_guardada.id_pelicula)
        self.assertTrue(eliminado)
        self.assertIsNone(PeliculaDAO.obtener_por_id(peli_guardada.id_pelicula))

    def test_integridad_no_eliminar_pelicula_con_funciones(self):
        """No borra registros asociados ni datos inesperados al eliminar."""
        peli = PeliculaDAO.crear(Pelicula(id_pelicula=None, titulo="Pelicula con Funcion", clasificacion_edad=0))
        f = Funcion2D(id_funcion=None, pelicula=peli, fecha_hora="2026-10-10 16:00", precio_base=4000.0, capacidad=50)
        f_guardada = FuncionDAO.crear(f)

        # Intentar eliminar película debe fallar con ReglaNegocioException
        with self.assertRaises(ReglaNegocioException):
            PeliculaDAO.eliminar(peli.id_pelicula)

        # Al eliminar la función primero, luego sí se puede eliminar la película
        FuncionDAO.eliminar(f_guardada.id_funcion)
        self.assertTrue(PeliculaDAO.eliminar(peli.id_pelicula))

    def test_venta_unificada_atomica_p12_p13(self):
        """
        Caso P12: Registrar 2 entradas y productos en la misma venta.
        Caso P13: Ver todas las líneas de detalle asociadas.
        """
        # Crear datos previos
        peli = PeliculaDAO.crear(Pelicula(id_pelicula=None, titulo="Cine Aventura", clasificacion_edad=0))
        func = FuncionDAO.crear(Funcion2D(
            id_funcion=None, pelicula=peli, fecha_hora="2026-10-10 19:00",
            precio_base=4500.0, capacidad=20
        ))
        prod = ProductoDAO.crear(ProductoNacional(id_producto=None, nombre="Bebida Cola", precio_base=1800.0))

        hash_t = Boletero.generar_hash("pass")
        boletero = TrabajadorDAO.crear(Boletero(id_trabajador=None, nombre="Boletero Test", username="bol_test", password_hash=hash_t))
        dulcero = TrabajadorDAO.crear(EncargadoDulceria(id_trabajador=None, nombre="Dulcero Test", username="dul_test", password_hash=hash_t))

        cliente = Cliente(rut="12.345.678-5", nombre="Cliente Prueba", edad=30)

        # Crear venta compartida
        venta = Venta(id_venta=None, cliente=cliente)
        d_entrada = DetalleVenta(
            id_detalle=None, id_venta=None, tipo_item="entrada", id_item=func.id_funcion,
            descripcion=f"Entrada 2D - {peli.titulo}", cantidad=2, precio_unitario=4500.0,
            id_trabajador=boletero.id_trabajador
        )
        d_producto = DetalleVenta(
            id_detalle=None, id_venta=None, tipo_item="producto", id_item=prod.id_producto,
            descripcion="Bebida Cola", cantidad=3, precio_unitario=1800.0,
            id_trabajador=dulcero.id_trabajador
        )
        venta.agregar_detalle(d_entrada)
        venta.agregar_detalle(d_producto)

        # P12: Persistir como un solo registro de venta atómico
        venta_registrada = VentaDAO.registrar_venta(venta)
        self.assertIsNotNone(venta_registrada.id_venta)

        # P13: Consultar el registro y validar líneas de detalle
        venta_recuperada = VentaDAO.obtener_por_id(venta_registrada.id_venta)
        self.assertIsNotNone(venta_recuperada)
        self.assertEqual(len(venta_recuperada.detalles), 2)
        self.assertEqual(venta_recuperada.total, (2 * 4500.0) + (3 * 1800.0))  # 9000 + 5400 = 14400.0

        # Verificar que los asientos se descontaron (capacidad 20 - 2 vendidas = 18)
        func_actualizada = FuncionDAO.obtener_por_id(func.id_funcion)
        self.assertEqual(func_actualizada.asientos_disponibles, 18)

        # Probar cuadratura de caja
        cuadratura_bol = VentaDAO.obtener_cuadratura_trabajador(boletero.id_trabajador)
        self.assertEqual(cuadratura_bol["total_entradas"], 2)
        self.assertEqual(cuadratura_bol["total_recaudado"], 9000.0)

        cuadratura_dul = VentaDAO.obtener_cuadratura_trabajador(dulcero.id_trabajador)
        self.assertEqual(cuadratura_dul["total_productos"], 3)
        self.assertEqual(cuadratura_dul["total_recaudado"], 5400.0)

    def test_transaccion_atomica_rollback_sin_asientos(self):
        """Si no hay asientos suficientes, la transacción debe hacer rollback total."""
        peli = PeliculaDAO.crear(Pelicula(id_pelicula=None, titulo="VIP Exclusivo", clasificacion_edad=0))
        func_vip = FuncionDAO.crear(FuncionVIP(
            id_funcion=None, pelicula=peli, fecha_hora="2026-10-10 21:00",
            precio_base=6000.0, capacidad=1
        ))

        venta = Venta(id_venta=None)
        # Intentar comprar 2 entradas cuando solo queda 1
        d = DetalleVenta(
            id_detalle=None, id_venta=None, tipo_item="entrada", id_item=func_vip.id_funcion,
            descripcion="VIP Ticket", cantidad=2, precio_unitario=9000.0, id_trabajador=1
        )
        venta.agregar_detalle(d)

        with self.assertRaises(SinAsientosException):
            VentaDAO.registrar_venta(venta)

        # Comprobar que no se creó ninguna venta huérfana
        func_db = FuncionDAO.obtener_por_id(func_vip.id_funcion)
        self.assertEqual(func_db.asientos_disponibles, 1)

    def test_proteccion_usuario_admin_no_se_puede_eliminar(self):
        """Verifica que el usuario admin (funcionalidad del sistema) no pueda ser eliminado."""
        admin = TrabajadorDAO.obtener_por_username("admin")
        self.assertIsNotNone(admin)
        with self.assertRaises(ReglaNegocioException):
            TrabajadorDAO.eliminar(admin.id_trabajador)

        # Verificar que no se pueda crear otro usuario llamado 'admin'
        with self.assertRaises(ReglaNegocioException):
            TrabajadorDAO.crear(Boletero(id_trabajador=None, nombre="Falso Admin", username="admin", password_hash="xxx"))


if __name__ == "__main__":
    unittest.main()
