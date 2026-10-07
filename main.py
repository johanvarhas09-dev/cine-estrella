"""Cine Estrella - Sistema de venta de entradas y dulcería.

Evaluación Sumativa N°2 - Programación Orientada a Objeto Seguro (TI3V21, sección 114-2A-F2).
Ejecutar con:  python main.py
"""
import sqlite3

import validaciones as v
from dao.cliente_dao import ClienteDAO
from dao.conexion import crear_conexion
from dao.funcion_dao import FuncionDAO
from dao.pelicula_dao import PeliculaDAO
from dao.producto_dao import ProductoDAO
from dao.trabajador_dao import TrabajadorDAO
from dao.venta_dao import VentaDAO
from datos_ejemplo import base_vacia, cargar_datos_ejemplo
from model.boletero import Boletero
from model.cliente import Cliente
from model.edad_no_permitida_error import EdadNoPermitidaError
from model.encargado_dulceria import EncargadoDulceria
from model.funcion import Funcion
from model.funcion_2d import Funcion2D
from model.funcion_3d import Funcion3D
from model.funcion_vip import FuncionVIP
from model.indicador_dolar import IndicadorDolar
from model.pelicula import Pelicula
from model.producto_dulceria import ProductoDulceria
from model.sin_asientos_error import SinAsientosError
from model.trabajador import VENDER_ENTRADA, VENDER_PRODUCTO, Trabajador
from model.venta import Venta
from servicios.mindicador import IndicadorNoDisponibleError, ServicioMindicador

# Dirección IP privada que nunca responde. Sirve para mostrar en la demostración qué hace el programa
# cuando la API no contesta: la consulta espera el tiempo máximo (timeout) y se informa el error.
URL_API_SIN_RESPUESTA = "http://10.255.255.1/api/"
ID_MAXIMO = 10**9


# ----------------------------------------------------------------------------- utilidades de pantalla

def pesos(monto: float) -> str:
    return "$" + f"{round(monto):,}".replace(",", ".")


def dolares(valor: float) -> str:
    return f"${valor:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")


def encabezado(texto: str) -> None:
    print("\n" + "-" * 90)
    print(texto)
    print("-" * 90)


def ejecutar(accion) -> None:
    """Ejecuta una opción del menú. Si falla por un dato inválido o por la base de datos, informa y sigue."""
    try:
        accion()
    except ValueError as error:
        print(f"[ERROR] {error}")
    except sqlite3.IntegrityError:
        print("[ERROR] La base de datos rechazó la operación: el registro ya existe o está en uso.")
    except sqlite3.Error as error:
        print(f"[ERROR] Problema con la base de datos: {error}")


def pedir_por_id(dao, nombre: str):
    """Pide un ID y devuelve el objeto que entrega el DAO, o None si se cancela o no existe."""
    id_buscado = v.leer_entero(f"ID de {nombre} (0 = cancelar): ", 0, ID_MAXIMO)
    if id_buscado == 0:
        return None
    objeto = dao.buscar(id_buscado)
    if objeto is None:
        print(f"[AVISO] No hay {nombre} con ID {id_buscado}.")
    return objeto


def mantenedor(nombre: str, crear, listar, buscar, modificar, eliminar) -> None:
    acciones = {"1": crear, "2": listar, "3": buscar, "4": modificar, "5": eliminar}
    while True:
        encabezado(f"MANTENEDOR DE {nombre}")
        print("1. Crear   2. Listar   3. Buscar   4. Modificar   5. Eliminar   0. Volver")
        opcion = v.leer_opcion("Seleccione una opción: ", ("0", "1", "2", "3", "4", "5"))
        if opcion == "0":
            return
        ejecutar(acciones[opcion])


# ----------------------------------------------------------------------------- clientes

def mostrar_clientes(clientes: list[Cliente]) -> None:
    print(f"{'RUT':<11} | {'NOMBRE':<30} | EDAD")
    for cliente in clientes:
        print(f"{cliente.rut:<11} | {cliente.nombre:<30} | {cliente.edad}")


def registrar_cliente(dao: ClienteDAO, rut: str) -> Cliente:
    nombre = v.leer_texto("Nombre: ")
    edad = v.leer_entero("Edad: ", 0, 120)
    cliente = Cliente(rut, nombre, edad)  # los setters vuelven a validar cada dato
    dao.insertar(cliente)
    print(f"[OK] Cliente {cliente.nombre} ({cliente.rut}) registrado.")
    return cliente


def crear_cliente(dao: ClienteDAO) -> None:
    rut = v.leer_rut("RUT (ej. 12345678-5): ")
    if dao.buscar(rut) is not None:
        print(f"[ERROR] Ya existe un cliente con RUT {rut}.")
        return
    registrar_cliente(dao, rut)


def listar_clientes(dao: ClienteDAO) -> None:
    clientes = dao.listar()
    if clientes:
        mostrar_clientes(clientes)
    else:
        print("No hay clientes registrados.")


def pedir_cliente(dao: ClienteDAO) -> Cliente | None:
    rut = v.leer_rut("RUT del cliente (Enter = cancelar): ", permitir_vacio=True)
    if not rut:
        return None
    cliente = dao.buscar(rut)
    if cliente is None:
        print(f"[AVISO] No hay un cliente con RUT {rut}.")
    return cliente


def buscar_cliente(dao: ClienteDAO) -> None:
    cliente = pedir_cliente(dao)
    if cliente is not None:
        mostrar_clientes([cliente])


def modificar_cliente(dao: ClienteDAO) -> None:
    cliente = pedir_cliente(dao)
    if cliente is None:
        return
    print("Presione Enter para conservar el valor actual. El RUT no se modifica.")
    cliente.nombre = v.leer_texto(f"Nombre [{cliente.nombre}]: ", por_defecto=cliente.nombre)
    cliente.edad = v.leer_entero(f"Edad [{cliente.edad}]: ", 0, 120, por_defecto=cliente.edad)
    if dao.actualizar(cliente):
        print("[OK] Cliente actualizado.")


def eliminar_cliente(dao: ClienteDAO) -> None:
    cliente = pedir_cliente(dao)
    if cliente is None or not v.leer_si_no(f"¿Eliminar a {cliente.nombre}?"):
        return
    try:
        dao.eliminar(cliente.rut)
        print("[OK] Cliente eliminado.")
    except sqlite3.IntegrityError:
        print("[ERROR] No se puede eliminar: el cliente tiene ventas registradas.")


# ----------------------------------------------------------------------------- películas

def mostrar_peliculas(peliculas: list[Pelicula]) -> None:
    print(f"{'ID':<4} | {'TÍTULO':<32} | {'DURACIÓN':<8} | CLASIFICACIÓN")
    for pelicula in peliculas:
        clasificacion = f"{pelicula.edad_minima}+" if pelicula.es_restringida() else "Todo espectador"
        print(f"{pelicula.id:<4} | {pelicula.titulo[:32]:<32} | {pelicula.duracion_min:>4} min | {clasificacion}")


def crear_pelicula(dao: PeliculaDAO) -> None:
    titulo = v.leer_texto("Título: ", 80)
    duracion = v.leer_entero("Duración en minutos (1-400): ", 1, 400)
    edad_minima = v.leer_entero("Edad mínima (0 = todo espectador, máximo 18): ", 0, 18)
    pelicula = Pelicula(titulo, duracion, edad_minima)
    dao.insertar(pelicula)
    print(f"[OK] Película '{pelicula.titulo}' creada con ID {pelicula.id}.")


def listar_peliculas(dao: PeliculaDAO) -> None:
    peliculas = dao.listar()
    if peliculas:
        mostrar_peliculas(peliculas)
    else:
        print("No hay películas registradas.")


def buscar_pelicula(dao: PeliculaDAO) -> None:
    pelicula = pedir_por_id(dao, "película")
    if pelicula is not None:
        mostrar_peliculas([pelicula])


def modificar_pelicula(dao: PeliculaDAO) -> None:
    pelicula = pedir_por_id(dao, "película")
    if pelicula is None:
        return
    print("Presione Enter para conservar el valor actual.")
    pelicula.titulo = v.leer_texto(f"Título [{pelicula.titulo}]: ", 80, pelicula.titulo)
    pelicula.duracion_min = v.leer_entero(f"Duración [{pelicula.duracion_min}]: ", 1, 400, pelicula.duracion_min)
    pelicula.edad_minima = v.leer_entero(f"Edad mínima [{pelicula.edad_minima}]: ", 0, 18, pelicula.edad_minima)
    if dao.actualizar(pelicula):
        print("[OK] Película actualizada.")


def eliminar_pelicula(dao: PeliculaDAO) -> None:
    pelicula = pedir_por_id(dao, "película")
    if pelicula is None or not v.leer_si_no(f"¿Eliminar '{pelicula.titulo}'?"):
        return
    try:
        dao.eliminar(pelicula.id)
        print("[OK] Película eliminada.")
    except sqlite3.IntegrityError:
        print("[ERROR] No se puede eliminar: la película tiene funciones programadas.")


# ----------------------------------------------------------------------------- funciones

def formato(funcion: Funcion) -> str:
    # Solo para mostrar: "Funcion2D" -> "2D". El precio nunca depende de este texto.
    return type(funcion).__name__.replace("Funcion", "")


def mostrar_funciones(funciones: list[Funcion]) -> None:
    print(f"{'ID':<4} | {'FORMATO':<7} | {'PELÍCULA':<28} | {'EDAD':<4} | {'FECHA Y HORA':<16} | "
          f"{'ENTRADA':>8} | DISPONIBLES")
    for funcion in funciones:
        edad = f"{funcion.pelicula.edad_minima}+" if funcion.pelicula.es_restringida() else "TE"
        # calcular_precio() y asientos_disponibles() son polimórficos: cada subtipo responde a su manera
        print(f"{funcion.id:<4} | {formato(funcion):<7} | {funcion.pelicula.titulo[:28]:<28} | {edad:<4} | "
              f"{funcion.fecha_hora:%d-%m-%Y %H:%M} | {pesos(funcion.calcular_precio()):>8} | "
              f"{funcion.asientos_disponibles()}")


def crear_funcion(funcion_dao: FuncionDAO, pelicula_dao: PeliculaDAO) -> None:
    peliculas = pelicula_dao.listar()
    if not peliculas:
        print("[AVISO] Primero debe crear una película.")
        return
    mostrar_peliculas(peliculas)
    pelicula = pedir_por_id(pelicula_dao, "película")
    if pelicula is None:
        return
    print("Formato: 1. 2D   2. 3D   3. VIP")
    opcion = v.leer_opcion("Seleccione el formato: ", ("1", "2", "3"))
    fecha_hora = v.leer_fecha_hora("Fecha y hora (dd-mm-aaaa hh:mm): ")
    precio_base = v.leer_entero("Precio base en pesos (500-100000): ", 500, 100000)
    asientos = v.leer_entero("Asientos de la sala (1-500): ", 1, 500)
    # Se crea el subtipo que eligió el usuario; desde aquí en adelante el objeto sabe calcular su precio
    if opcion == "1":
        funcion = Funcion2D(pelicula, fecha_hora, precio_base, asientos)
    elif opcion == "2":
        recargo = v.leer_entero("Recargo 3D en pesos (0-50000): ", 0, 50000)
        funcion = Funcion3D(pelicula, fecha_hora, precio_base, asientos, recargo)
    else:
        recargo = v.leer_entero("Recargo VIP en pesos (0-50000): ", 0, 50000)
        cupo_vip = v.leer_entero(f"Cupo de asientos VIP (1-{asientos}): ", 1, asientos)
        funcion = FuncionVIP(pelicula, fecha_hora, precio_base, asientos, recargo, cupo_vip)
    funcion_dao.insertar(funcion)
    print(f"[OK] Función {formato(funcion)} creada con ID {funcion.id}. "
          f"Precio de la entrada: {pesos(funcion.calcular_precio())}.")


def listar_funciones(dao: FuncionDAO) -> None:
    funciones = dao.listar()
    if funciones:
        mostrar_funciones(funciones)
    else:
        print("No hay funciones programadas.")


def buscar_funcion(dao: FuncionDAO) -> None:
    funcion = pedir_por_id(dao, "función")
    if funcion is not None:
        mostrar_funciones([funcion])
        print(f"Asientos de la sala: {funcion.asientos_totales} | Vendidos: {funcion.asientos_vendidos}")


def modificar_funcion(dao: FuncionDAO) -> None:
    funcion = pedir_por_id(dao, "función")
    if funcion is None:
        return
    print("Presione Enter para conservar el valor actual. El formato y la película no se modifican.")
    funcion.fecha_hora = v.leer_fecha_hora(f"Fecha y hora [{funcion.fecha_hora:%d-%m-%Y %H:%M}]: ",
                                           funcion.fecha_hora)
    funcion.precio_base = v.leer_entero(f"Precio base [{funcion.precio_base}]: ", 500, 100000, funcion.precio_base)
    funcion.asientos_totales = v.leer_entero(f"Asientos de la sala [{funcion.asientos_totales}]: ", 1, 500,
                                             funcion.asientos_totales)
    if dao.actualizar(funcion):
        print(f"[OK] Función actualizada. Precio de la entrada: {pesos(funcion.calcular_precio())}.")


def eliminar_funcion(dao: FuncionDAO) -> None:
    funcion = pedir_por_id(dao, "función")
    if funcion is None or not v.leer_si_no(f"¿Eliminar la función {funcion.id} de '{funcion.pelicula.titulo}'?"):
        return
    try:
        dao.eliminar(funcion.id)
        print("[OK] Función eliminada.")
    except sqlite3.IntegrityError:
        print("[ERROR] No se puede eliminar: la función ya tiene entradas vendidas.")


# ----------------------------------------------------------------------------- productos de dulcería

def precio_base_texto(producto: ProductoDulceria) -> str:
    return f"USD {producto.precio_base:.2f}" if producto.importado else pesos(producto.precio_base)


def mostrar_productos(productos: list[ProductoDulceria]) -> None:
    print(f"{'ID':<4} | {'DESCRIPCIÓN':<30} | {'ORIGEN':<9} | PRECIO BASE")
    for producto in productos:
        origen = "Importado" if producto.importado else "Nacional"
        print(f"{producto.id:<4} | {producto.descripcion[:30]:<30} | {origen:<9} | {precio_base_texto(producto)}")


def crear_producto(dao: ProductoDAO) -> None:
    descripcion = v.leer_texto("Descripción: ", 60)
    importado = v.leer_si_no("¿Es importado?")
    if importado:
        precio = v.leer_decimal("Precio base en dólares (0.1 - 1000): ", 0.1, 1000)
    else:
        precio = v.leer_entero("Precio en pesos (100 - 100000): ", 100, 100000)
    producto = ProductoDulceria(descripcion, precio, importado)
    dao.insertar(producto)
    print(f"[OK] Producto '{producto.descripcion}' creado con ID {producto.id}.")


def listar_productos(dao: ProductoDAO) -> None:
    productos = dao.listar()
    if productos:
        mostrar_productos(productos)
    else:
        print("No hay productos registrados.")


def buscar_producto(dao: ProductoDAO) -> None:
    producto = pedir_por_id(dao, "producto")
    if producto is not None:
        mostrar_productos([producto])


def modificar_producto(dao: ProductoDAO) -> None:
    producto = pedir_por_id(dao, "producto")
    if producto is None:
        return
    print("Presione Enter para conservar el valor actual.")
    producto.descripcion = v.leer_texto(f"Descripción [{producto.descripcion}]: ", 60, producto.descripcion)
    importado = v.leer_si_no(f"¿Es importado? (actual: {'Sí' if producto.importado else 'No'})")
    # Si cambia el origen, cambia la moneda del precio base, así que no se ofrece el valor anterior
    mismo_origen = importado == producto.importado
    if importado:
        actual = producto.precio_base if mismo_origen else None
        precio = v.leer_decimal(f"Precio base en dólares [{actual if actual else '-'}]: ", 0.1, 1000, actual)
    else:
        actual = round(producto.precio_base) if mismo_origen else None
        precio = v.leer_entero(f"Precio en pesos [{actual if actual else '-'}]: ", 100, 100000, actual)
    producto.importado = importado
    producto.precio_base = precio
    if dao.actualizar(producto):
        print("[OK] Producto actualizado.")


def eliminar_producto(dao: ProductoDAO) -> None:
    producto = pedir_por_id(dao, "producto")
    if producto is None or not v.leer_si_no(f"¿Eliminar '{producto.descripcion}'?"):
        return
    try:
        dao.eliminar(producto.id)
        print("[OK] Producto eliminado.")
    except sqlite3.IntegrityError:
        print("[ERROR] No se puede eliminar: el producto aparece en ventas registradas.")


# ----------------------------------------------------------------------------- trabajadores

def cargo(trabajador: Trabajador) -> str:
    return type(trabajador).__name__


def mostrar_trabajadores(trabajadores: list[Trabajador]) -> None:
    print(f"{'ID':<4} | {'NOMBRE':<25} | {'CARGO':<17} | {'CAJA':<4} | PUEDE VENDER")
    for trabajador in trabajadores:
        # tiene_permiso() es polimórfico: cada subtipo define qué puede vender
        permisos = [texto for operacion, texto in ((VENDER_ENTRADA, "entradas"), (VENDER_PRODUCTO, "dulcería"))
                    if trabajador.tiene_permiso(operacion)]
        print(f"{trabajador.id:<4} | {trabajador.nombre[:25]:<25} | {cargo(trabajador):<17} | "
              f"{trabajador.caja:<4} | {', '.join(permisos)}")


def crear_trabajador(dao: TrabajadorDAO) -> None:
    nombre = v.leer_texto("Nombre: ", 60)
    caja = v.leer_entero("Número de caja (1-20): ", 1, 20)
    print("Cargo: 1. Boletero   2. Encargado de dulcería")
    if v.leer_opcion("Seleccione el cargo: ", ("1", "2")) == "1":
        trabajador = Boletero(nombre, caja)
    else:
        trabajador = EncargadoDulceria(nombre, caja)
    dao.insertar(trabajador)
    print(f"[OK] {cargo(trabajador)} {trabajador.nombre} creado con ID {trabajador.id}.")


def listar_trabajadores(dao: TrabajadorDAO) -> None:
    trabajadores = dao.listar()
    if trabajadores:
        mostrar_trabajadores(trabajadores)
    else:
        print("No hay trabajadores registrados.")


def buscar_trabajador(dao: TrabajadorDAO) -> None:
    trabajador = pedir_por_id(dao, "trabajador")
    if trabajador is not None:
        mostrar_trabajadores([trabajador])


def modificar_trabajador(dao: TrabajadorDAO) -> None:
    trabajador = pedir_por_id(dao, "trabajador")
    if trabajador is None:
        return
    print("Presione Enter para conservar el valor actual. El cargo no se modifica.")
    trabajador.nombre = v.leer_texto(f"Nombre [{trabajador.nombre}]: ", 60, trabajador.nombre)
    trabajador.caja = v.leer_entero(f"Caja [{trabajador.caja}]: ", 1, 20, trabajador.caja)
    if dao.actualizar(trabajador):
        print("[OK] Trabajador actualizado.")


def eliminar_trabajador(dao: TrabajadorDAO) -> None:
    trabajador = pedir_por_id(dao, "trabajador")
    if trabajador is None or not v.leer_si_no(f"¿Eliminar a {trabajador.nombre}?"):
        return
    try:
        dao.eliminar(trabajador.id)
        print("[OK] Trabajador eliminado.")
    except sqlite3.IntegrityError:
        print("[ERROR] No se puede eliminar: el trabajador ya registró ventas.")


# ----------------------------------------------------------------------------- dólar y dulcería

def obtener_indicador(servicio: ServicioMindicador) -> IndicadorDolar | None:
    """Consulta el dólar del día. Si la API falla, informa el motivo y devuelve None: el programa sigue."""
    print("Consultando el dólar del día en mindicador.cl ...")
    try:
        indicador = servicio.obtener_dolar()
    except IndicadorNoDisponibleError as error:
        print(f"[AVISO] No se pudo obtener el dólar: {error}")
        print("        El programa sigue funcionando: los productos nacionales se venden con normalidad,")
        print("        pero los importados no se pueden cotizar hasta que la API vuelva a responder.")
        return None
    print(f"[OK] Dólar observado del {indicador.fecha:%d-%m-%Y}: {dolares(indicador.valor_dolar)}")
    return indicador


def mostrar_cotizacion(productos: list[ProductoDulceria], indicador: IndicadorDolar | None) -> None:
    print(f"{'ID':<4} | {'DESCRIPCIÓN':<30} | {'ORIGEN':<9} | {'PRECIO BASE':<12} | PRECIO DE VENTA")
    for producto in productos:
        producto.indicador = indicador
        origen = "Importado" if producto.importado else "Nacional"
        if producto.importado and indicador is None:
            precio_venta = "no disponible (falta el dólar)"
        else:
            precio_venta = pesos(producto.calcular_precio())
            if producto.importado:
                precio_venta += f"  (USD {producto.precio_base:.2f} x {dolares(indicador.valor_dolar)})"
        print(f"{producto.id:<4} | {producto.descripcion[:30]:<30} | {origen:<9} | "
              f"{precio_base_texto(producto):<12} | {precio_venta}")


def cotizar_dulceria(producto_dao: ProductoDAO, servicio: ServicioMindicador) -> None:
    encabezado("COTIZACIÓN DE DULCERÍA CON EL DÓLAR DEL DÍA")
    productos = producto_dao.listar()
    if not productos:
        print("No hay productos registrados.")
        return
    mostrar_cotizacion(productos, obtener_indicador(servicio))


# ----------------------------------------------------------------------------- ventas

def mostrar_detalle(venta: Venta) -> None:
    numero = venta.numero if venta.numero is not None else "(sin guardar)"
    print(f"Venta N° {numero} | {venta.fecha:%d-%m-%Y %H:%M} | Cliente: {venta.cliente.nombre} "
          f"({venta.cliente.rut}, {venta.cliente.edad} años)")
    print(f"{'#':<3} | {'DESCRIPCIÓN':<62} | {'VENDIÓ':<14} | {'CANT':>4} | {'P. UNIT':>8} | {'SUBTOTAL':>9}")
    for posicion, detalle in enumerate(venta.detalles, start=1):
        # Cada línea muestra quién la vendió: boletería y dulcería son cajas separadas
        vendedor = f"{detalle.vendedor.nombre.split()[0][:6]} (caja {detalle.vendedor.caja})"
        print(f"{posicion:<3} | {detalle.item.descripcion[:62]:<62} | {vendedor:<14} | {detalle.cantidad:>4} | "
              f"{pesos(detalle.precio_unitario):>8} | {pesos(detalle.calcular_subtotal()):>9}")
    print(f"{'TOTAL':>106} {pesos(venta.calcular_total()):>9}")


def elegir_trabajador(dao: TrabajadorDAO, operacion: str, texto_operacion: str) -> Trabajador | None:
    habilitados = [trabajador for trabajador in dao.listar() if trabajador.tiene_permiso(operacion)]
    if not habilitados:
        print(f"[AVISO] No hay trabajadores habilitados para {texto_operacion}.")
        return None
    print(f"Trabajadores habilitados para {texto_operacion}:")
    mostrar_trabajadores(habilitados)
    trabajador = pedir_por_id(dao, "trabajador")
    if trabajador is not None and not trabajador.tiene_permiso(operacion):
        print(f"[ERROR] {trabajador.nombre} ({cargo(trabajador)}) no tiene permiso para {texto_operacion}: "
              "boletería y dulcería son cajas separadas.")
        return None
    return trabajador


def agregar_entradas(venta: Venta, boletero: Boletero, funcion_dao: FuncionDAO,
                     funciones_en_venta: dict[int, Funcion]) -> None:
    funciones = funcion_dao.listar()
    if not funciones:
        print("[AVISO] No hay funciones programadas.")
        return
    # Si una función ya se usó en esta venta, se usa ese mismo objeto para que cuente lo ya reservado
    funciones = [funciones_en_venta.get(funcion.id, funcion) for funcion in funciones]
    mostrar_funciones(funciones)
    id_funcion = v.leer_entero("ID de la función (0 = cancelar): ", 0, ID_MAXIMO)
    if id_funcion == 0:
        return
    funcion = next((funcion for funcion in funciones if funcion.id == id_funcion), None)
    if funcion is None:
        print(f"[AVISO] No hay función con ID {id_funcion}.")
        return
    funciones_en_venta[funcion.id] = funcion
    cantidad = v.leer_entero("Cantidad de entradas (1-10): ", 1, 10)
    vendidas = 0
    try:
        for _ in range(cantidad):
            boletero.vender_entrada(venta, funcion)
            vendidas += 1
    except EdadNoPermitidaError as error:
        print(f"[REGLA] Venta bloqueada por edad: {error}")
    except SinAsientosError as error:
        print(f"[REGLA] Venta bloqueada por falta de asientos: {error}")
    if vendidas:
        print(f"[OK] {vendidas} entrada(s) para '{funcion.pelicula.titulo}' ({formato(funcion)}) "
              f"agregada(s) a {pesos(funcion.calcular_precio())} c/u.")
    if vendidas < cantidad:
        print(f"[AVISO] Se agregaron {vendidas} de las {cantidad} entradas pedidas.")


def agregar_productos(venta: Venta, encargado: EncargadoDulceria, producto_dao: ProductoDAO,
                      servicio: ServicioMindicador, indicador: IndicadorDolar | None) -> IndicadorDolar | None:
    """Agrega una línea de dulcería. Devuelve el indicador del dólar para reutilizarlo en la misma venta."""
    productos = producto_dao.listar()
    if not productos:
        print("[AVISO] No hay productos registrados.")
        return indicador
    if indicador is None and any(producto.importado for producto in productos):
        indicador = obtener_indicador(servicio)
    mostrar_cotizacion(productos, indicador)
    id_producto = v.leer_entero("ID del producto (0 = cancelar): ", 0, ID_MAXIMO)
    if id_producto == 0:
        return indicador
    producto = next((producto for producto in productos if producto.id == id_producto), None)
    if producto is None:
        print(f"[AVISO] No hay producto con ID {id_producto}.")
        return indicador
    if producto.importado and indicador is None:
        print("[AVISO] No se puede vender un producto importado sin el dólar del día. "
              "Elija un producto nacional o intente más tarde.")
        return indicador
    cantidad = v.leer_entero("Cantidad (1-20): ", 1, 20)
    detalle = encargado.vender_producto(venta, producto, cantidad)
    print(f"[OK] {cantidad} x {producto.descripcion} a {pesos(detalle.precio_unitario)} c/u. "
          f"Subtotal {pesos(detalle.calcular_subtotal())}.")
    return indicador


def nueva_venta(cliente_dao: ClienteDAO, trabajador_dao: TrabajadorDAO, funcion_dao: FuncionDAO,
                producto_dao: ProductoDAO, venta_dao: VentaDAO, servicio: ServicioMindicador) -> None:
    encabezado("NUEVA VENTA")
    rut = v.leer_rut("RUT del cliente (Enter = cancelar): ", permitir_vacio=True)
    if not rut:
        return
    cliente = cliente_dao.buscar(rut)
    if cliente is None:
        print(f"[AVISO] El RUT {rut} no está registrado.")
        if not v.leer_si_no("¿Registrar al cliente ahora?"):
            return
        cliente = registrar_cliente(cliente_dao, rut)

    venta = Venta(cliente)
    funciones_en_venta: dict[int, Funcion] = {}
    boletero = None
    encargado = None
    indicador = None
    while True:
        encabezado(f"VENTA EN CURSO | Cliente: {cliente.nombre} ({cliente.edad} años) | "
                   f"{len(venta.detalles)} línea(s) | Total {pesos(venta.calcular_total())}")
        print("1. Agregar entradas (boletería)")
        print("2. Agregar productos (dulcería)")
        print("3. Ver detalle de la venta")
        print("4. Confirmar y guardar la venta")
        print("0. Cancelar la venta")
        opcion = v.leer_opcion("Seleccione una opción: ", ("0", "1", "2", "3", "4"))
        if opcion == "1":
            if boletero is None:
                boletero = elegir_trabajador(trabajador_dao, VENDER_ENTRADA, "vender entradas")
            if boletero is not None:
                agregar_entradas(venta, boletero, funcion_dao, funciones_en_venta)
        elif opcion == "2":
            if encargado is None:
                encargado = elegir_trabajador(trabajador_dao, VENDER_PRODUCTO, "vender productos de dulcería")
            if encargado is not None:
                indicador = agregar_productos(venta, encargado, producto_dao, servicio, indicador)
        elif opcion == "3":
            mostrar_detalle(venta)
        elif opcion == "4":
            if not venta.detalles:
                print("[ERROR] La venta debe tener al menos una línea de detalle.")
                continue
            venta_dao.insertar(venta)
            print(f"[OK] Venta N° {venta.numero} guardada en la base de datos con {len(venta.detalles)} línea(s).")
            mostrar_detalle(venta)
            return
        elif v.leer_si_no("¿Cancelar la venta? Se perderán las líneas agregadas"):
            print("Venta cancelada: no se guardó nada.")
            return


def ver_ventas(venta_dao: VentaDAO) -> None:
    encabezado("VENTAS REGISTRADAS")
    ventas = venta_dao.listar()
    if not ventas:
        print("No hay ventas registradas.")
        return
    print(f"{'N°':<4} | {'FECHA':<16} | {'CLIENTE':<25} | {'LÍNEAS':>6} | {'TOTAL':>10}")
    for venta in ventas:
        print(f"{venta.numero:<4} | {venta.fecha:%d-%m-%Y %H:%M} | {venta.cliente.nombre[:25]:<25} | "
              f"{len(venta.detalles):>6} | {pesos(venta.calcular_total()):>10}")
    numero = v.leer_entero("N° de venta para ver su detalle (0 = volver): ", 0, ID_MAXIMO)
    if numero == 0:
        return
    venta = venta_dao.buscar(numero)
    if venta is None:
        print(f"[AVISO] No hay venta N° {numero}.")
    else:
        mostrar_detalle(venta)


# ----------------------------------------------------------------------------- programa principal

def menu_principal(simulando_caida: bool) -> str:
    encabezado("CINE ESTRELLA - Venta de entradas y dulcería")
    print("1. Clientes")
    print("2. Películas")
    print("3. Funciones")
    print("4. Productos de dulcería")
    print("5. Trabajadores")
    print("6. Nueva venta")
    print("7. Ver ventas registradas")
    print("8. Cotizar dulcería con el dólar del día")
    print(f"9. Simular API sin respuesta (demostración) [{'ACTIVADA' if simulando_caida else 'desactivada'}]")
    print("0. Salir")
    return v.leer_opcion("Seleccione una opción: ", ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"))


def main() -> None:
    try:
        conexion = crear_conexion()
        cliente_dao = ClienteDAO(conexion)
        pelicula_dao = PeliculaDAO(conexion)
        funcion_dao = FuncionDAO(conexion)
        producto_dao = ProductoDAO(conexion)
        trabajador_dao = TrabajadorDAO(conexion)
        venta_dao = VentaDAO(conexion)
        # El programa crea las tablas si no existen
        for dao in (cliente_dao, pelicula_dao, funcion_dao, producto_dao, trabajador_dao, venta_dao):
            dao.crear_tabla()
    except sqlite3.Error as error:
        print(f"[ERROR] No se pudo preparar la base de datos: {error}")
        return

    servicio = ServicioMindicador()
    simulando_caida = False
    try:
        if base_vacia(conexion) and v.leer_si_no("La base de datos está vacía. ¿Cargar datos de ejemplo?"):
            cargar_datos_ejemplo(conexion)
            print("[OK] Datos de ejemplo cargados.")

        while True:
            opcion = menu_principal(simulando_caida)
            if opcion == "1":
                mantenedor("CLIENTES", lambda: crear_cliente(cliente_dao), lambda: listar_clientes(cliente_dao),
                           lambda: buscar_cliente(cliente_dao), lambda: modificar_cliente(cliente_dao),
                           lambda: eliminar_cliente(cliente_dao))
            elif opcion == "2":
                mantenedor("PELÍCULAS", lambda: crear_pelicula(pelicula_dao), lambda: listar_peliculas(pelicula_dao),
                           lambda: buscar_pelicula(pelicula_dao), lambda: modificar_pelicula(pelicula_dao),
                           lambda: eliminar_pelicula(pelicula_dao))
            elif opcion == "3":
                mantenedor("FUNCIONES", lambda: crear_funcion(funcion_dao, pelicula_dao),
                           lambda: listar_funciones(funcion_dao), lambda: buscar_funcion(funcion_dao),
                           lambda: modificar_funcion(funcion_dao), lambda: eliminar_funcion(funcion_dao))
            elif opcion == "4":
                mantenedor("PRODUCTOS DE DULCERÍA", lambda: crear_producto(producto_dao),
                           lambda: listar_productos(producto_dao), lambda: buscar_producto(producto_dao),
                           lambda: modificar_producto(producto_dao), lambda: eliminar_producto(producto_dao))
            elif opcion == "5":
                mantenedor("TRABAJADORES", lambda: crear_trabajador(trabajador_dao),
                           lambda: listar_trabajadores(trabajador_dao), lambda: buscar_trabajador(trabajador_dao),
                           lambda: modificar_trabajador(trabajador_dao), lambda: eliminar_trabajador(trabajador_dao))
            elif opcion == "6":
                ejecutar(lambda: nueva_venta(cliente_dao, trabajador_dao, funcion_dao, producto_dao,
                                             venta_dao, servicio))
            elif opcion == "7":
                ejecutar(lambda: ver_ventas(venta_dao))
            elif opcion == "8":
                ejecutar(lambda: cotizar_dulceria(producto_dao, servicio))
            elif opcion == "9":
                simulando_caida = not simulando_caida
                if simulando_caida:
                    servicio = ServicioMindicador(URL_API_SIN_RESPUESTA, timeout=3)
                    print("[AVISO] Simulación ACTIVADA: la API apunta a una dirección que no responde "
                          "(tiempo máximo de espera: 3 s).")
                else:
                    servicio = ServicioMindicador()
                    print("[OK] Simulación desactivada: se vuelve a consultar https://mindicador.cl.")
            else:
                break
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma interrumpido por el usuario.")
    finally:
        conexion.close()
        print("Sistema cerrado. ¡Hasta luego!")


if __name__ == "__main__":
    main()
