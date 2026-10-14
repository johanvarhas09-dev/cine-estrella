"""
Servicio central de reglas de negocio para la venta de entradas y confitería.
Orquesta validaciones de edad, RUT, asientos, conversión de divisas y persistencia unificada.
"""
from dao.funcion_dao import FuncionDAO
from dao.producto_dao import ProductoDAO
from dao.venta_dao import VentaDAO
from dao.cliente_dao import ClienteDAO
from model.cliente import Cliente
from model.venta import Venta
from model.detalle_venta import DetalleVenta
from model.trabajador import Trabajador
from model.producto_importado import ProductoImportado
from model.excepciones import SinAsientosException, RestriccionEdadException, ReglaNegocioException
from service.tipo_cambio_service import TipoCambioService


class VentaService:
    @staticmethod
    def validar_cliente_para_funcion(funcion_id: int, rut: str, nombre: str, edad: int) -> Cliente:
        """
        [FUNCIONALIDAD: VALIDACIÓN COMBINADA DE COMPRADOR Y CLASIFICACIÓN - Casos P07, P08 y P15]
        Ejecuta las dos validaciones críticas previas a la venta de entradas:
        1. Validación de RUT chileno (P07 válido, P08 inválido): Aplica Módulo 11. Si falla, lanza ReglaNegocioException.
        2. Control de edad mínima (P15): Si la película tiene clasificación (+14, +18) y el comprador
           no alcanza la edad requerida, lanza RestriccionEdadException impidiendo la venta.
        Retorna la instancia validada de Cliente para asociarla a la venta.
        """
        # Validación de formato y dígito verificador de RUT chileno (P07 / P08)
        if not Cliente.validar_rut(rut):
            raise ReglaNegocioException(
                f"El RUT '{rut}' tiene un formato o dígito verificador incorrecto. Verifique e intente nuevamente."
            )

        # Validación de edad contra la clasificación de la película (P15)
        funcion = FuncionDAO.obtener_por_id(funcion_id)
        if not funcion:
            raise ReglaNegocioException(f"La función con ID {funcion_id} no existe.")

        if not funcion.pelicula.es_apta(edad):
            raise RestriccionEdadException(
                f"Venta denegada: La película '{funcion.pelicula.titulo}' tiene clasificación "
                f"+{funcion.pelicula.clasificacion_edad} años y el comprador tiene {edad} años."
            )

        cliente = Cliente(rut=rut, nombre=nombre, edad=edad)
        return cliente

    @staticmethod
    def crear_detalle_entrada(
        funcion_id: int,
        cantidad: int,
        trabajador: Trabajador
    ) -> DetalleVenta:
        """
        [FUNCIONALIDAD: EMISIÓN DE BOLETO Y CONTROL DE CUPOS - Casos P09, P10, P11 y P14]
        1. Verifica que el trabajador tenga rol con permiso de boletería (Boletero o Admin).
        2. Control de capacidad (Caso P14): Impide sobreventa lanzando SinAsientosException si
           la cantidad solicitada supera los asientos disponibles en la sala.
        3. Invoca calcular_precio() polimórfico (2D base, 3D con recargo, VIP con recargo premium).
        4. Retorna el DetalleVenta asignando el id_trabajador emisor para trazabilidad en cuadratura.
        """
        if not trabajador.puede_vender_entradas():
            raise ReglaNegocioException("El trabajador no tiene permisos para vender entradas de cine.")

        if cantidad <= 0:
            raise ReglaNegocioException("La cantidad de entradas debe ser al menos 1.")

        funcion = FuncionDAO.obtener_por_id(funcion_id)
        if not funcion:
            raise ReglaNegocioException(f"La función con ID {funcion_id} no fue encontrada.")

        # Control estricto de cupos disponibles (P14)
        if not funcion.hay_asientos(cantidad):
            raise SinAsientosException(
                f"No hay suficientes asientos disponibles para la función [{funcion.tipo}] '{funcion.pelicula.titulo}'. "
                f"Disponibles: {funcion.asientos_disponibles} de {funcion.capacidad}."
            )

        precio_unitario = funcion.calcular_precio()
        descripcion = f"Entrada [{funcion.tipo}] {funcion.pelicula.titulo} ({funcion.fecha_hora})"

        return DetalleVenta(
            id_detalle=None,
            id_venta=None,
            tipo_item="entrada",
            id_item=funcion.id_funcion,
            descripcion=descripcion,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            id_trabajador=trabajador.id_trabajador
        )

    @staticmethod
    def crear_detalle_producto(
        producto_id: int,
        cantidad: int,
        trabajador: Trabajador
    ) -> DetalleVenta:
        """
        [FUNCIONALIDAD: VENTA DE CONFITERÍA Y CONVERSIÓN DE DIVISAS - Casos P12, P16 y P17]
        1. Valida permisos del trabajador (Encargado de Dulcería o Admin).
        2. Si el producto es de tipo Importado, invoca TipoCambioService.obtener_dolar_dia() para obtener
           el valor del dólar del día y calcular el precio final en CLP.
        3. Si el producto es Nacional, utiliza el precio fijo directo en CLP.
        4. Si falla la conexión a internet, se propaga ReglaNegocioException amigablemente sin caer el sistema.
        """
        if not trabajador.puede_vender_productos():
            raise ReglaNegocioException("El trabajador no tiene permisos para vender productos de confitería.")

        if cantidad <= 0:
            raise ReglaNegocioException("La cantidad de productos debe ser al menos 1.")

        producto = ProductoDAO.obtener_por_id(producto_id)
        if not producto:
            raise ReglaNegocioException(f"El producto con ID {producto_id} no existe.")

        if isinstance(producto, ProductoImportado):
            # Obtener tipo de cambio en tiempo real desde la API del Banco Central (P16, P17)
            tipo_cambio = TipoCambioService.obtener_dolar_dia()
            precio_unitario = producto.calcular_precio(tipo_cambio.valor)
            descripcion = f"{producto.nombre} (Importado - USD ${producto.precio_usd:.2f} @ ${tipo_cambio.valor:,.0f} CLP)"
        else:
            precio_unitario = producto.calcular_precio()
            descripcion = f"{producto.nombre} (Nacional)"

        return DetalleVenta(
            id_detalle=None,
            id_venta=None,
            tipo_item="producto",
            id_item=producto.id_producto,
            descripcion=descripcion,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            id_trabajador=trabajador.id_trabajador
        )

    @staticmethod
    def concretar_venta(venta: Venta, descontar_asientos: bool = True) -> Venta:
        """
        [FUNCIONALIDAD: TRANSACCIÓN ATÓMICA DE VENTA COMPARTIDA - Casos P12 y P13]
        Registra la venta unificada en la base de datos bajo un único folio fiscal.
        Permite que una misma venta contenga entradas (emitidas por Boletero) y confitería
        (emitida por Encargado Dulcería), garantizando la consistencia ACID de inventario y caja.
        """
        return VentaDAO.registrar_venta(venta, descontar_asientos=descontar_asientos)

    @staticmethod
    def generar_grafico_asientos_texto(id_funcion: int) -> str:
        """
        Genera un gráfico textual amigable de entradas vendidas y asientos restantes (Caso de Boletería).
        """
        funcion = FuncionDAO.obtener_por_id(id_funcion)
        if not funcion:
            return "Función no encontrada."

        total = funcion.capacidad
        disponibles = funcion.asientos_disponibles
        vendidos = funcion.asientos_vendidos

        pct_vendido = (vendidos / total) * 100 if total > 0 else 0
        largo_barra = 30
        llenos = int((vendidos / total) * largo_barra) if total > 0 else 0
        vacios = largo_barra - llenos

        barra = "#" * llenos + "-" * vacios

        reporte = (
            f"=== OCUPACIÓN DE SALA: [{funcion.tipo}] {funcion.pelicula.titulo} ===\n"
            f"Horario: {funcion.fecha_hora}\n"
            f"Capacidad Total:      {total} asientos\n"
            f"Asientos Vendidos:    {vendidos} [[VENDIDO]]\n"
            f"Asientos Disponibles: {disponibles} [[DISP]]\n"
            f"Ocupación: [{barra}] {pct_vendido:.1f}%\n"
        )
        return reporte
