"""
Pruebas unitarias para las entidades del modelo y sus reglas de negocio.
Valida herencia, polimorfismo, encapsulamiento (@property) y excepciones de dominio.
"""
import unittest

from model.cliente import Cliente
from model.pelicula import Pelicula
from model.funcion import Funcion
from model.funcion_2d import Funcion2D
from model.funcion_3d import Funcion3D
from model.funcion_vip import FuncionVIP
from model.producto import Producto
from model.producto_nacional import ProductoNacional
from model.producto_importado import ProductoImportado
from model.trabajador import Trabajador
from model.boletero import Boletero
from model.encargado_dulceria import EncargadoDulceria
from model.venta import Venta
from model.detalle_venta import DetalleVenta
from model.excepciones import SinAsientosException, RestriccionEdadException


class TestModelos(unittest.TestCase):
    def test_rut_valido_e_invalido_p07_p08(self):
        """Caso P07: RUT válido aceptado. Caso P08: RUT inválido rechazado."""
        # P07: 12.345.678-5 debe ser válido
        self.assertTrue(Cliente.validar_rut("12.345.678-5"))
        cliente = Cliente(rut="12.345.678-5", nombre="Juan Pérez", edad=25)
        self.assertEqual(cliente.rut, "12345678-5")

        # P08: 12.345.678-9 debe ser inválido
        self.assertFalse(Cliente.validar_rut("12.345.678-9"))
        with self.assertRaises(ValueError):
            Cliente(rut="12.345.678-9", nombre="Invalido", edad=25)

    def test_pelicula_clasificacion_edad_p15(self):
        """Verifica restricción de edad de películas (Caso P15)."""
        peli_adultos = Pelicula(id_pelicula=1, titulo="Terror Nocturno", clasificacion_edad=18)
        self.assertFalse(peli_adultos.es_apta(15))
        self.assertTrue(peli_adultos.es_apta(18))
        self.assertTrue(peli_adultos.es_apta(21))

        peli_te = Pelicula(id_pelicula=2, titulo="Animación Familiar", clasificacion_edad=0)
        self.assertTrue(peli_te.es_apta(5))

    def test_polimorfismo_funciones_p09_p10_p11(self):
        """
        Casos P09, P10 y P11:
        Funcion2D, Funcion3D y FuncionVIP deben implementar calcular_precio()
        con comportamientos diferenciados mediante herencia real.
        """
        peli = Pelicula(id_pelicula=1, titulo="Galaxy Wars", clasificacion_edad=0)

        f_2d = Funcion2D(id_funcion=1, pelicula=peli, fecha_hora="2026-10-05 18:00", precio_base=4000.0)
        f_3d = Funcion3D(id_funcion=2, pelicula=peli, fecha_hora="2026-10-05 20:00", precio_base=4000.0, recargo_3d=1500.0)
        f_vip = FuncionVIP(id_funcion=3, pelicula=peli, fecha_hora="2026-10-05 22:00", precio_base=4000.0, recargo_vip=3000.0)

        # Polimorfismo: invocación sin distinguir tipos con if
        funciones: list[Funcion] = [f_2d, f_3d, f_vip]
        precios = [f.calcular_precio() for f in funciones]

        self.assertEqual(precios[0], 4000.0)         # 2D base
        self.assertEqual(precios[1], 5500.0)         # 3D con recargo 1500
        self.assertEqual(precios[2], 7000.0)         # VIP con recargo 3000

        # P11: VIP con capacidad limitada
        self.assertEqual(f_vip.capacidad, 30)

    def test_control_capacidad_y_excepcion_p14(self):
        """Caso P14: No se pueden vender más entradas que los asientos disponibles."""
        peli = Pelicula(id_pelicula=1, titulo="Estreno", clasificacion_edad=14)
        f = FuncionVIP(id_funcion=1, pelicula=peli, fecha_hora="2026-10-05 18:00", precio_base=5000.0, capacidad=3)

        self.assertEqual(f.asientos_disponibles, 3)
        f.reservar_asientos(2)
        self.assertEqual(f.asientos_disponibles, 1)

        # Intentar reservar 2 más cuando solo queda 1 debe lanzar SinAsientosException
        with self.assertRaises(SinAsientosException):
            f.reservar_asientos(2)

    def test_polimorfismo_productos_p16(self):
        """
        Caso P16: ProductoNacional mantiene precio CLP,
        ProductoImportado convierte dinámicamente con la tasa del dólar.
        """
        p_nac = ProductoNacional(id_producto=1, nombre="Popcorn Grande", precio_base=3200.0)
        p_imp = ProductoImportado(id_producto=2, nombre="Nachos Especiales", precio_base_usd=3.5)

        tasa_dolar = 950.0

        # Invocación polimórfica de calcular_precio
        productos: list[Producto] = [p_nac, p_imp]
        precios_clp = [p.calcular_precio(tasa_dolar) for p in productos]

        self.assertEqual(precios_clp[0], 3200.0)
        self.assertEqual(precios_clp[1], round(3.5 * 950.0))  # 3325.0

    def test_trabajador_hashing_y_permisos(self):
        """Valida que las contraseñas no se guarden en texto plano y los permisos por rol."""
        hash_pass = Trabajador.generar_hash("secreta123")
        self.assertNotEqual(hash_pass, "secreta123")
        self.assertIn("$", hash_pass)

        boletero = Boletero(id_trabajador=1, nombre="Carlos", username="carlos", password_hash=hash_pass)
        self.assertTrue(boletero.verificar_password("secreta123"))
        self.assertFalse(boletero.verificar_password("clave_erronea"))
        self.assertTrue(boletero.puede_vender_entradas())
        self.assertFalse(boletero.puede_vender_productos())

        dulcero = EncargadoDulceria(id_trabajador=2, nombre="Ana", username="ana", password_hash=hash_pass)
        self.assertFalse(dulcero.puede_vender_entradas())
        self.assertTrue(dulcero.puede_vender_productos())

    def test_venta_composicion_y_total_p12(self):
        """Caso P12: Composición Venta ♦── DetalleVenta calculando total correctamente."""
        venta = Venta(id_venta=1)
        d1 = DetalleVenta(
            id_detalle=1, id_venta=1, tipo_item="entrada", id_item=10,
            descripcion="Entrada 2D", cantidad=2, precio_unitario=4500.0, id_trabajador=1
        )
        d2 = DetalleVenta(
            id_detalle=2, id_venta=1, tipo_item="producto", id_item=5,
            descripcion="Popcorn", cantidad=1, precio_unitario=3000.0, id_trabajador=2
        )
        venta.agregar_detalle(d1)
        venta.agregar_detalle(d2)

        self.assertEqual(len(venta.detalles), 2)
        self.assertEqual(venta.total, 12000.0)


if __name__ == "__main__":
    unittest.main()
