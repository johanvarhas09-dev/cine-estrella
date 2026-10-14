"""
===============================================================================
                       CINE ESTRELLA — SISTEMA DE GESTIÓN
                    Versión 2.0 (Fase 2) — Consola Interactiva
===============================================================================
Punto de entrada principal del sistema. Implementa menús interactivos por rol,
autenticación segura, control de permisos, persistencia atómica y tolerancia
a errores y fallos de conectividad (Casos de prueba P01 a P19).
"""
import sys
import os

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dao.db_init import inicializar_bd
from dao.pelicula_dao import PeliculaDAO
from dao.funcion_dao import FuncionDAO
from dao.producto_dao import ProductoDAO
from dao.trabajador_dao import TrabajadorDAO
from dao.venta_dao import VentaDAO
from dao.cliente_dao import ClienteDAO

from model.pelicula import Pelicula
from model.funcion_2d import Funcion2D
from model.funcion_3d import Funcion3D
from model.funcion_vip import FuncionVIP
from model.producto_nacional import ProductoNacional
from model.producto_importado import ProductoImportado
from model.boletero import Boletero
from model.encargado_dulceria import EncargadoDulceria
from model.trabajador import Trabajador
from model.venta import Venta
from model.detalle_venta import DetalleVenta
from model.cliente import Cliente
from model.excepciones import (
    SinAsientosException,
    RestriccionEdadException,
    ReglaNegocioException
)

from service.auth_service import AuthService
from service.tipo_cambio_service import TipoCambioService
from service.venta_service import VentaService


# =============================================================================
# UTILIDADES ROBUSTAS DE ENTRADA POR CONSOLA (Casos P18 y P19)
# =============================================================================

def leer_texto(mensaje: str, obligatorio: bool = True) -> str:
    """Lee una cadena desde la consola asegurando que no esté vacía si es obligatoria."""
    while True:
        try:
            valor = input(mensaje).strip()
            if obligatorio and not valor:
                print("[!] El valor no puede estar vacío. Intente nuevamente.")
                continue
            return valor
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada.")
            return ""


def leer_entero(mensaje: str, minimo: int | None = None, maximo: int | None = None) -> int:
    """
    Lee un entero robustamente. Si el usuario ingresa letras ('abc'),
    captura el error sin cerrar el programa (Caso P19).
    """
    while True:
        try:
            texto = input(mensaje).strip()
            valor = int(texto)
            if minimo is not None and valor < minimo:
                print(f"[!] El número debe ser mayor o igual a {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"[!] El número debe ser menor o igual a {maximo}.")
                continue
            return valor
        except ValueError:
            print("[!] Entrada inválida: Debe ingresar un número entero válido (no letras ni símbolos).")
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada.")
            return 0


def leer_flotante(mensaje: str, minimo: float | None = None) -> float:
    """Lee un número decimal robustamente capturando entradas no numéricas (Caso P19)."""
    while True:
        try:
            texto = input(mensaje).strip().replace(",", ".")
            valor = float(texto)
            if minimo is not None and valor < minimo:
                print(f"[!] El valor debe ser mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("[!] Entrada inválida: Debe ingresar un valor numérico válido.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada.")
            return 0.0


def pausar():
    """Pausa interactiva entre pantallas."""
    try:
        input("\nPresione [Enter] para continuar...")
    except (KeyboardInterrupt, EOFError):
        pass


# =============================================================================
# MÓDULO: ADMINISTRADOR (Funcionalidad)
# =============================================================================

class MenuAdmin:
    def __init__(self, admin: Trabajador):
        self.admin = admin

    def ejecutar(self):
        while True:
            print("\n" + "=" * 65)
            print("       * PANEL DE ADMINISTRACIÓN — CINE ESTRELLA *")
            print(f" Sesión activa: {self.admin.nombre} ({self.admin.username})")
            print("=" * 65)
            print(" 1. Gestión de Películas (Crear, Listar, Modificar, Eliminar)")
            print(" 2. Gestión de Funciones (2D, 3D, VIP, Precios y Capacidad)")
            print(" 3. Gestión de Productos de Confitería (Nacionales e Importados)")
            print(" 4. Gestión de Trabajadores (Boleteros y Encargados de Dulcería)")
            print(" 5. Reporte de Ventas por Función")
            print(" 6. Reporte de Ventas por Trabajador")
            print(" 7. Consultar Detalle de una Venta (por Folio / ID)")
            print(" 8. Consultar Tipo de Cambio Oficial del Dólar (mindicador.cl)")
            print(" 0. Cerrar Sesión")
            print("=" * 65)

            opcion = leer_texto("Seleccione una opción: ")

            if opcion == "1":
                self._menu_peliculas()
            elif opcion == "2":
                self._menu_funciones()
            elif opcion == "3":
                self._menu_productos()
            elif opcion == "4":
                self._menu_trabajadores()
            elif opcion == "5":
                self._reporte_ventas_por_funcion()
            elif opcion == "6":
                self._reporte_ventas_por_trabajador()
            elif opcion == "7":
                self._consultar_venta_por_id()
            elif opcion == "8":
                self._consultar_dolar()
            elif opcion == "0":
                print("\nCerrando sesión de administrador...")
                break
            else:
                # Caso P18: Opción 99 o inexistente muestra mensaje y vuelve al menú sin caerse
                print(f"\n[!] Opción '{opcion}' no reconocida. Por favor ingrese una opción válida.")
                pausar()

    # --- CRUD PELÍCULAS (Casos P02, P03, P04, P06) ---
    def _menu_peliculas(self):
        while True:
            print("\n--- GESTIÓN DE PELÍCULAS ---")
            print("1. Listar películas (P03)")
            print("2. Crear película (P02)")
            print("3. Modificar película (P04)")
            print("4. Eliminar película (P06)")
            print("0. Volver al menú principal")

            op = leer_texto("Opción: ")
            if op == "1":
                pelis = PeliculaDAO.listar()
                if not pelis:
                    print("No hay películas registradas.")
                else:
                    print(f"\n{'ID':<5} | {'Título':<30} | {'Clasificación':<15} | {'Duración':<10}")
                    print("-" * 65)
                    for p in pelis:
                        clasif = f"+{p.clasificacion_edad}" if p.clasificacion_edad > 0 else "TE (Todo Espectador)"
                        print(f"{p.id_pelicula:<5} | {p.titulo:<30} | {clasif:<15} | {p.duracion_minutos} min")
                pausar()

            elif op == "2":
                print("\n[Crear Película]")
                titulo = leer_texto("Título de la película: ")
                print("Clasificaciones comunes: 0 (Todo Espectador), 7 (+7 años), 14 (+14 años), 18 (+18 años)")
                clasif = leer_entero("Clasificación de edad mínima: ", minimo=0, maximo=21)
                duracion = leer_entero("Duración en minutos: ", minimo=1, maximo=500)
                try:
                    peli = Pelicula(id_pelicula=None, titulo=titulo, clasificacion_edad=clasif, duracion_minutos=duracion)
                    peli_guardada = PeliculaDAO.crear(peli)
                    print(f"[OK] Película '{peli_guardada.titulo}' guardada exitosamente con ID {peli_guardada.id_pelicula}.")
                except Exception as e:
                    print(f"[ERROR] Error al crear película: {e}")
                pausar()

            elif op == "3":
                print("\n[Modificar Película]")
                id_p = leer_entero("ID de la película a modificar: ", minimo=1)
                peli = PeliculaDAO.obtener_por_id(id_p)
                if not peli:
                    print(f"[!] No existe película con ID {id_p}.")
                else:
                    print(f"Modificando: {peli.titulo} (Clasificación actual: +{peli.clasificacion_edad})")
                    nuevo_titulo = input(f"Nuevo título [{peli.titulo}]: ").strip()
                    if nuevo_titulo:
                        peli.titulo = nuevo_titulo
                    nuevo_clasif_str = input(f"Nueva clasificación [{peli.clasificacion_edad}]: ").strip()
                    if nuevo_clasif_str:
                        peli.clasificacion_edad = int(nuevo_clasif_str)
                    nueva_dur_str = input(f"Nueva duración [{peli.duracion_minutos}]: ").strip()
                    if nueva_dur_str:
                        peli.duracion_minutos = int(nueva_dur_str)

                    PeliculaDAO.modificar(peli)
                    print(f"[OK] Película ID {id_p} modificada exitosamente.")
                pausar()

            elif op == "4":
                print("\n[Eliminar Película]")
                id_p = leer_entero("ID de la película a eliminar: ", minimo=1)
                try:
                    PeliculaDAO.eliminar(id_p)
                    print(f"[OK] Película ID {id_p} eliminada.")
                except ReglaNegocioException as e:
                    print(f"[!] Operación impedida: {e}")
                except Exception as e:
                    print(f"[ERROR] Error al eliminar: {e}")
                pausar()

            elif op == "0":
                break
            else:
                print(f"[!] Opción '{op}' inválida.")

    # --- CRUD FUNCIONES (Casos P09, P10, P11) ---
    def _menu_funciones(self):
        while True:
            print("\n--- GESTIÓN DE FUNCIONES ---")
            print("1. Listar funciones")
            print("2. Crear función (2D, 3D o VIP)")
            print("3. Modificar función")
            print("4. Eliminar función")
            print("0. Volver")

            op = leer_texto("Opción: ")
            if op == "1":
                funcs = FuncionDAO.listar()
                if not funcs:
                    print("No hay funciones programadas.")
                else:
                    print(f"\n{'ID':<5} | {'Tipo':<5} | {'Película':<25} | {'Horario':<16} | {'Precio':<10} | {'Cupos (Disp/Total)':<18}")
                    print("-" * 85)
                    for f in funcs:
                        precio = f.calcular_precio()
                        print(f"{f.id_funcion:<5} | {f.tipo:<5} | {f.pelicula.titulo:<25} | {f.fecha_hora:<16} | ${precio:<9,.0f} | {f.asientos_disponibles}/{f.capacidad}")
                pausar()

            elif op == "2":
                print("\n[Crear Función]")
                pelis = PeliculaDAO.listar()
                if not pelis:
                    print("[!] Debe crear al menos una película antes de crear funciones.")
                    pausar()
                    continue

                for p in pelis:
                    print(f"  [{p.id_pelicula}] {p.titulo} (+{p.clasificacion_edad})")
                id_peli = leer_entero("Seleccione ID de película: ", minimo=1)
                pelicula = PeliculaDAO.obtener_por_id(id_peli)
                if not pelicula:
                    print("[!] Película no encontrada.")
                    pausar()
                    continue

                print("\nTipos de función disponibles:")
                print(" 1. 2D (Estándar)")
                print(" 2. 3D (Recargo tecnológico)")
                print(" 3. VIP (Premium, cupos limitados)")
                tipo_op = leer_texto("Seleccione tipo (1, 2 o 3): ")

                fecha = leer_texto("Fecha y hora (ej: 2026-10-10 19:00): ")
                precio_base = leer_flotante("Precio base en CLP: ", minimo=0.0)

                try:
                    if tipo_op == "1":
                        cap = leer_entero("Capacidad de sala [default 100]: ", minimo=1)
                        func = Funcion2D(id_funcion=None, pelicula=pelicula, fecha_hora=fecha, precio_base=precio_base, capacidad=cap)
                    elif tipo_op == "2":
                        cap = leer_entero("Capacidad de sala [default 80]: ", minimo=1)
                        recargo = leer_flotante("Recargo 3D en CLP [default 1500]: ", minimo=0.0)
                        func = Funcion3D(id_funcion=None, pelicula=pelicula, fecha_hora=fecha, precio_base=precio_base, capacidad=cap, recargo_3d=recargo)
                    elif tipo_op == "3":
                        cap = leer_entero("Capacidad limitada VIP (máximo 30 recomendado): ", minimo=1, maximo=30)
                        recargo = leer_flotante("Recargo VIP en CLP [default 3000]: ", minimo=0.0)
                        func = FuncionVIP(id_funcion=None, pelicula=pelicula, fecha_hora=fecha, precio_base=precio_base, capacidad=cap, recargo_vip=recargo)
                    else:
                        print("[!] Tipo de función inválido.")
                        pausar()
                        continue

                    func_guardada = FuncionDAO.crear(func)
                    print(f"[OK] Función [{func_guardada.tipo}] guardada exitosamente con ID {func_guardada.id_funcion}.")
                    print(f"  Precio de entrada calculado polimórficamente: ${func_guardada.calcular_precio():,.0f} CLP")
                except Exception as e:
                    print(f"[ERROR] Error al crear función: {e}")
                pausar()

            elif op == "3":
                id_f = leer_entero("ID de la función a modificar: ", minimo=1)
                func = FuncionDAO.obtener_por_id(id_f)
                if not func:
                    print(f"[!] Función ID {id_f} no encontrada.")
                else:
                    nueva_fecha = input(f"Nuevo horario [{func.fecha_hora}]: ").strip()
                    if nueva_fecha:
                        func.fecha_hora = nueva_fecha
                    nuevo_precio_str = input(f"Nuevo precio base [${func.precio_base:,.0f}]: ").strip()
                    if nuevo_precio_str:
                        func.precio_base = float(nuevo_precio_str)
                    FuncionDAO.modificar(func)
                    print(f"[OK] Función ID {id_f} modificada.")
                pausar()

            elif op == "4":
                id_f = leer_entero("ID de la función a eliminar: ", minimo=1)
                try:
                    FuncionDAO.eliminar(id_f)
                    print(f"[OK] Función ID {id_f} eliminada.")
                except ReglaNegocioException as e:
                    print(f"[!] Operación impedida: {e}")
                except Exception as e:
                    print(f"[ERROR] Error al eliminar: {e}")
                pausar()

            elif op == "0":
                break
            else:
                print(f"[!] Opción '{op}' no válida.")

    # --- CRUD PRODUCTOS ---
    def _menu_productos(self):
        while True:
            print("\n--- GESTIÓN DE PRODUCTOS DE CONFITERÍA ---")
            print("1. Listar productos")
            print("2. Crear producto (Nacional o Importado)")
            print("3. Modificar producto")
            print("4. Eliminar producto")
            print("0. Volver")

            op = leer_texto("Opción: ")
            if op == "1":
                prods = ProductoDAO.listar()
                if not prods:
                    print("No hay productos registrados.")
                else:
                    print(f"\n{'ID':<5} | {'Nombre':<28} | {'Tipo':<12} | {'Precio Base':<15}")
                    print("-" * 65)
                    for p in prods:
                        if isinstance(p, ProductoImportado):
                            base_str = f"USD ${p.precio_usd:.2f}"
                        else:
                            base_str = f"${p.precio_base:,.0f} CLP"
                        print(f"{p.id_producto:<5} | {p.nombre:<28} | {p.tipo.capitalize():<12} | {base_str:<15}")
                pausar()

            elif op == "2":
                print("\n[Crear Producto]")
                nombre = leer_texto("Nombre del producto: ")
                print("1. Nacional (precio fijo en CLP)")
                print("2. Importado (precio base en USD, cotizado al dólar del día)")
                tipo_op = leer_texto("Seleccione origen (1 o 2): ")

                try:
                    if tipo_op == "1":
                        precio_clp = leer_flotante("Precio en pesos chilenos (CLP): ", minimo=0.0)
                        prod = ProductoNacional(id_producto=None, nombre=nombre, precio_base=precio_clp)
                    elif tipo_op == "2":
                        precio_usd = leer_flotante("Precio en dólares estadounidenses (USD): ", minimo=0.0)
                        prod = ProductoImportado(id_producto=None, nombre=nombre, precio_base_usd=precio_usd)
                    else:
                        print("[!] Opción no válida.")
                        pausar()
                        continue

                    prod_guardado = ProductoDAO.crear(prod)
                    print(f"[OK] Producto '{prod_guardado.nombre}' guardado exitosamente con ID {prod_guardado.id_producto}.")
                except Exception as e:
                    print(f"[ERROR] Error al crear producto: {e}")
                pausar()

            elif op == "3":
                id_p = leer_entero("ID del producto a modificar: ", minimo=1)
                prod = ProductoDAO.obtener_por_id(id_p)
                if not prod:
                    print(f"[!] Producto ID {id_p} no encontrado.")
                else:
                    nuevo_nombre = input(f"Nuevo nombre [{prod.nombre}]: ").strip()
                    if nuevo_nombre:
                        prod.nombre = nuevo_nombre
                    nuevo_precio_str = input(f"Nuevo precio base [{prod.precio_base}]: ").strip()
                    if nuevo_precio_str:
                        prod.precio_base = float(nuevo_precio_str)
                    ProductoDAO.modificar(prod)
                    print(f"[OK] Producto ID {id_p} modificado.")
                pausar()

            elif op == "4":
                id_p = leer_entero("ID del producto a eliminar: ", minimo=1)
                try:
                    ProductoDAO.eliminar(id_p)
                    print(f"[OK] Producto ID {id_p} eliminado.")
                except ReglaNegocioException as e:
                    print(f"[!] Operación impedida: {e}")
                pausar()

            elif op == "0":
                break
            else:
                print(f"[!] Opción '{op}' no válida.")

    # --- CRUD TRABAJADORES ---
    def _menu_trabajadores(self):
        while True:
            print("\n--- GESTIÓN DE TRABAJADORES ---")
            print("1. Listar trabajadores")
            print("2. Crear trabajador (Boletero o Encargado Dulcería)")
            print("3. Eliminar trabajador")
            print("0. Volver")

            op = leer_texto("Opción: ")
            if op == "1":
                trabs = TrabajadorDAO.listar()
                print(f"\n{'ID':<5} | {'Nombre':<25} | {'Username':<15} | {'Rol / Caja':<15}")
                print("-" * 65)
                for t in trabs:
                    print(f"{t.id_trabajador:<5} | {t.nombre:<25} | {t.username:<15} | {t.rol.upper():<15}")
                pausar()

            elif op == "2":
                print("\n[Crear Trabajador]")
                nombre = leer_texto("Nombre completo: ")
                username = leer_texto("Nombre de usuario (login): ")
                password = leer_texto("Contraseña: ")
                print("1. Boletero (Caja de venta de entradas)")
                print("2. Encargado de Dulcería (Caja de confitería y bebidas)")
                rol_op = leer_texto("Seleccione rol (1 o 2): ")

                hash_pw = Trabajador.generar_hash(password)
                try:
                    if rol_op == "1":
                        t = Boletero(id_trabajador=None, nombre=nombre, username=username, password_hash=hash_pw)
                    elif rol_op == "2":
                        t = EncargadoDulceria(id_trabajador=None, nombre=nombre, username=username, password_hash=hash_pw)
                    else:
                        print("[!] Rol no válido.")
                        pausar()
                        continue

                    t_guardado = TrabajadorDAO.crear(t)
                    print(f"[OK] Trabajador '{t_guardado.nombre}' ({t_guardado.rol}) creado con ID {t_guardado.id_trabajador}.")
                except Exception as e:
                    print(f"[ERROR] Error al crear trabajador: {e}")
                pausar()

            elif op == "3":
                id_t = leer_entero("ID del trabajador a eliminar: ", minimo=1)
                try:
                    TrabajadorDAO.eliminar(id_t)
                    print(f"[OK] Trabajador ID {id_t} eliminado.")
                except ReglaNegocioException as e:
                    print(f"[!] Operación impedida: {e}")
                pausar()

            elif op == "0":
                break
            else:
                print(f"[!] Opción '{op}' no válida.")

    # --- REPORTES Y CONSULTAS ---
    def _reporte_ventas_por_funcion(self):
        print("\n--- REPORTE DE VENTAS POR FUNCIÓN ---")
        funcs = FuncionDAO.listar()
        if not funcs:
            print("No hay funciones registradas.")
            pausar()
            return

        for f in funcs:
            print(f"  [{f.id_funcion}] [{f.tipo}] {f.pelicula.titulo} ({f.fecha_hora})")
        id_f = leer_entero("Seleccione ID de función: ", minimo=1)

        ventas = VentaDAO.obtener_ventas_por_funcion(id_f)
        if not ventas:
            print(f"No se registran ventas para la función ID {id_f}.")
        else:
            print(f"\n{'Línea':<8} | {'Folio Venta':<12} | {'Fecha/Hora':<20} | {'Cant':<5} | {'Unitario':<10} | {'Subtotal':<10} | {'Cajero':<15}")
            print("-" * 90)
            total = 0.0
            entradas = 0
            for v in ventas:
                total += v["subtotal"]
                entradas += v["cantidad"]
                print(f"{v['id_detalle']:<8} | #{v['id_venta']:<11} | {v['fecha_hora']:<20} | {v['cantidad']:<5} | ${v['precio_unitario']:<9,.0f} | ${v['subtotal']:<9,.0f} | {v['trabajador']:<15}")
            print("-" * 90)
            print(f"TOTAL RECAUDADO: ${total:,.0f} CLP en {entradas} entrada(s).")
        pausar()

    def _reporte_ventas_por_trabajador(self):
        print("\n--- REPORTE DE VENTAS POR TRABAJADOR ---")
        trabs = TrabajadorDAO.listar()
        for t in trabs:
            print(f"  [{t.id_trabajador}] {t.nombre} ({t.rol})")
        id_t = leer_entero("Seleccione ID de trabajador: ", minimo=1)

        cuadratura = VentaDAO.obtener_cuadratura_trabajador(id_t)
        print("\n" + "=" * 55)
        print("          CUADRATURA DE OPERACIONES")
        print("=" * 55)
        print(f" Transacciones participadas: {cuadratura['transacciones']}")
        print(f" Total Entradas emitidas:   {cuadratura['total_entradas']}")
        print(f" Total Productos vendidos:   {cuadratura['total_productos']}")
        print(f" TOTAL RECAUDADO:            ${cuadratura['total_recaudado']:,.0f} CLP")
        print("-" * 55)
        print(" Desglose por concepto:")
        for d in cuadratura["desglose"]:
            print(f"  * {d['descripcion']:<35} x{d['cantidad_total']:<4} = ${d['subtotal_total']:,.0f}")
        print("=" * 55)
        pausar()

    def _consultar_venta_por_id(self):
        """Caso P13: Consultar el registro de venta recién creado y ver todas sus líneas."""
        print("\n--- CONSULTA DE VENTA POR FOLIO (Caso P13) ---")
        id_v = leer_entero("Ingrese el Folio / ID de la venta: ", minimo=1)
        venta = VentaDAO.obtener_por_id(id_v)
        if not venta:
            print(f"[!] La venta #{id_v} no existe en los registros.")
        else:
            rut = venta.cliente.rut if venta.cliente else "Público General"
            print("\n" + "=" * 70)
            print(f" COMPROBANTE DE VENTA FISCAL #{venta.id_venta}")
            print(f" Fecha/Hora: {venta.fecha_hora}")
            print(f" Cliente:    {rut}")
            print("=" * 70)
            print(f" {'Tipo':<10} | {'Descripción':<35} | {'Cant':<5} | {'Precio':<10} | {'Subtotal':<10}")
            print("-" * 70)
            for d in venta.detalles:
                print(f" {d.tipo_item.capitalize():<10} | {d.descripcion[:34]:<35} | {d.cantidad:<5} | ${d.precio_unitario:<9,.0f} | ${d.subtotal:<9,.0f}")
            print("=" * 70)
            print(f" TOTAL DE LA VENTA: ${venta.total:,.0f} CLP")
            print("=" * 70)
        pausar()

    def _consultar_dolar(self):
        """Consulta directa a mindicador.cl (Casos P16 y P17)."""
        print("\n--- CONSULTA DE TIPO DE CAMBIO EN TIEMPO REAL ---")
        print("Conectando con https://mindicador.cl/api/dolar ...")
        try:
            tc = TipoCambioService.obtener_dolar_dia()
            print(f"[OK] Conexión exitosa:")
            print(f"  * Dólar Observado: ${tc.valor:,.2f} CLP")
            print(f"  * Fecha oficial:   {tc.fecha}")
            print(f"  * Proveedor:       {tc.fuente}")
        except ReglaNegocioException as e:
            print(f"[!] Aviso de red / conectividad: {e}")
        pausar()


# =============================================================================
# MÓDULO: BOLETERO (Venta de Entradas y Cuadratura)
# =============================================================================

class MenuBoletero:
    def __init__(self, boletero: Boletero):
        self.boletero = boletero

    def ejecutar(self):
        while True:
            print("\n" + "=" * 65)
            print("         [BOLETERIA] CAJA DE BOLETERÍA — CINE ESTRELLA [BOLETERIA]")
            print(f" Atiende: {self.boletero.nombre} | Rol: BOLETERO")
            print("=" * 65)
            print(" 1. Ver Funciones y Mapa de Asientos (Gráfico Textual)")
            print(" 2. Vender Entradas (Venta Rápida)")
            print(" 3. Venta Compartida (Entradas + Confitería bajo un solo folio)")
            print(" 4. Consultar Mi Cuadratura de Caja")
            print(" 0. Cerrar Sesión")
            print("=" * 65)

            op = leer_texto("Seleccione una opción: ")

            if op == "1":
                self._ver_grafico_asientos()
            elif op == "2":
                self._vender_entradas()
            elif op == "3":
                self._vender_compartida()
            elif op == "4":
                self._ver_cuadratura()
            elif op == "0":
                print("\nCerrando turno de boletería...")
                break
            else:
                print(f"\n[!] Opción '{op}' no válida.")
                pausar()

    def _ver_grafico_asientos(self):
        funcs = FuncionDAO.listar()
        if not funcs:
            print("No hay funciones disponibles.")
            pausar()
            return
        print("\nFunciones disponibles:")
        for f in funcs:
            print(f" [{f.id_funcion}] [{f.tipo}] {f.pelicula.titulo} ({f.fecha_hora}) - Cupos: {f.asientos_disponibles}/{f.capacidad}")
        id_f = leer_entero("Seleccione ID de función para ver ocupación: ", minimo=1)
        grafico = VentaService.generar_grafico_asientos_texto(id_f)
        print("\n" + grafico)
        pausar()

    def _vender_entradas(self):
        """Venta de entradas con validaciones de RUT, edad y cupos (P07, P08, P14, P15)."""
        print("\n--- EMISIÓN DE ENTRADAS ---")
        funcs = FuncionDAO.listar()
        if not funcs:
            print("No hay funciones disponibles para la venta.")
            pausar()
            return

        for f in funcs:
            clasif_txt = f"+{f.pelicula.clasificacion_edad}" if f.pelicula.clasificacion_edad > 0 else "TE"
            print(f" [{f.id_funcion}] [{f.tipo}] {f.pelicula.titulo} ({clasif_txt}) - Horario: {f.fecha_hora} | ${f.calcular_precio():,.0f} | Disp: {f.asientos_disponibles}")

        id_f = leer_entero("Seleccione ID de la función: ", minimo=1)
        funcion = FuncionDAO.obtener_por_id(id_f)
        if not funcion:
            print("[!] Función no encontrada.")
            pausar()
            return

        cantidad = leer_entero("Cantidad de entradas a comprar: ", minimo=1)

        # Validación de comprador (si es clasificada exige RUT y edad)
        cliente = None
        if funcion.pelicula.clasificacion_edad > 0:
            print(f"\n[!] ATENCIÓN: La película '{funcion.pelicula.titulo}' tiene clasificación +{funcion.pelicula.clasificacion_edad}.")
            print("Por normativa, se requiere validar RUT chileno y edad del comprador.")
            rut = leer_texto("Ingrese RUT del comprador (ej: 12.345.678-5): ")
            edad = leer_entero("Ingrese edad del comprador: ", minimo=0, maximo=130)
            nombre = leer_texto("Nombre del comprador: ")

            try:
                cliente = VentaService.validar_cliente_para_funcion(id_f, rut, nombre, edad)
                print(f"[OK] Validación exitosa: Cliente {cliente.nombre} cumple con la edad requerida.")
            except (RestriccionEdadException, ReglaNegocioException) as e:
                # Caso P15 y P08: La venta se impide, el programa continúa sin caerse
                print(f"\n[DENEGADO] {e}")
                pausar()
                return
        else:
            # Opcional capturar RUT para cliente general
            opc_rut = leer_texto("¿Desea asociar un RUT de cliente? (s/n): ").lower()
            if opc_rut == "s":
                rut = leer_texto("RUT del cliente: ")
                if Cliente.validar_rut(rut):
                    nom = leer_texto("Nombre: ")
                    ed = leer_entero("Edad: ", minimo=0)
                    cliente = Cliente(rut=rut, nombre=nom, edad=ed)
                else:
                    print("[!] RUT no válido. Se emitirá a Público General.")

        try:
            detalle = VentaService.crear_detalle_entrada(id_f, cantidad, self.boletero)
            venta = Venta(id_venta=None, cliente=cliente)
            venta.agregar_detalle(detalle)

            print(f"\nResumen: {cantidad} entrada(s) [{funcion.tipo}] {funcion.pelicula.titulo} = ${venta.total:,.0f} CLP")
            confirmar = leer_texto("¿Confirmar venta y emitir boletos? (s/n): ").lower()
            if confirmar == "s":
                venta_guardada = VentaService.concretar_venta(venta)
                print(f"\n[OK] ¡VENTA #{venta_guardada.id_venta} REGISTRADA EXITOSAMENTE!")
                print(f"  Total pagado: ${venta_guardada.total:,.0f} CLP")
            else:
                print("Venta cancelada.")
        except SinAsientosException as e:
            # Caso P14: Venta impedida por falta de asientos, programa sigue activo
            print(f"\n[DENEGADO] Sin Asientos: {e}")
        except Exception as e:
            print(f"\n[ERROR] Error al procesar venta: {e}")
        pausar()

    def _vender_compartida(self):
        """Venta de entradas y confites bajo una misma venta (Caso P12)."""
        print("\n--- VENTA COMPARTIDA (ENTRADAS + CONFITERÍA EN UN SOLO FOLIO) ---")
        funcs = FuncionDAO.listar()
        if not funcs:
            print("No hay funciones disponibles.")
            pausar()
            return

        for f in funcs:
            print(f" [{f.id_funcion}] [{f.tipo}] {f.pelicula.titulo} ({f.fecha_hora}) - ${f.calcular_precio():,.0f} | Disp: {f.asientos_disponibles}")
        id_f = leer_entero("ID de la función: ", minimo=1)
        cant_ent = leer_entero("Cantidad de entradas: ", minimo=1)

        try:
            det_ent = VentaService.crear_detalle_entrada(id_f, cant_ent, self.boletero)
        except SinAsientosException as e:
            print(f"[DENEGADO] {e}")
            pausar()
            return

        # Anexar productos de confitería autorizados por encargado de dulcería
        venta = Venta(id_venta=None)
        venta.agregar_detalle(det_ent)

        prods = ProductoDAO.listar()
        print("\nAgregar confitería a la misma compra (atribuida a la caja de dulcería):")
        # Buscar el ID de un encargado de dulcería para atribuir la línea
        dulceros = [t for t in TrabajadorDAO.listar() if t.rol == "dulceria"]
        id_dulcero = dulceros[0].id_trabajador if dulceros else 1

        for p in prods:
            print(f" [{p.id_producto}] {p.nombre} ({p.tipo})")
        id_prod = leer_entero("ID de producto a agregar: ", minimo=1)
        cant_prod = leer_entero("Cantidad de productos: ", minimo=1)

        # Crear trabajador proxy para la atribución de dulcería
        proxy_dulcero = EncargadoDulceria(id_trabajador=id_dulcero, nombre="Dulcería", username="dulc", password_hash="")
        det_prod = VentaService.crear_detalle_producto(id_prod, cant_prod, proxy_dulcero)
        venta.agregar_detalle(det_prod)

        print("\n" + "=" * 60)
        print(" RESUMEN DE LA VENTA COMPUESTA (Caso P12):")
        for d in venta.detalles:
            print(f" * {d.descripcion} x{d.cantidad} = ${d.subtotal:,.0f} CLP (Cajero ID: {d.id_trabajador})")
        print(f" TOTAL COMPARTIDO: ${venta.total:,.0f} CLP")
        print("=" * 60)

        conf = leer_texto("¿Confirmar venta compuesta? (s/n): ").lower()
        if conf == "s":
            v_reg = VentaService.concretar_venta(venta)
            print(f"\n[OK] ¡Venta unificada guardada bajo el Folio Único #{v_reg.id_venta}!")
        pausar()

    def _ver_cuadratura(self):
        cuad = VentaDAO.obtener_cuadratura_trabajador(self.boletero.id_trabajador)
        print("\n" + "=" * 55)
        print(f" CUADRATURA DE CAJA — {self.boletero.nombre.upper()}")
        print("=" * 55)
        print(f" Transacciones realizadas: {cuad['transacciones']}")
        print(f" Total Entradas emitidas:   {cuad['total_entradas']}")
        print(f" TOTAL RECAUDADO EN CAJA:   ${cuad['total_recaudado']:,.0f} CLP")
        print("=" * 55)
        pausar()


# =============================================================================
# MÓDULO: ENCARGADO DE DULCERÍA (Venta de Snacks y Dólar del Día)
# =============================================================================

class MenuDulceria:
    def __init__(self, dulcero: EncargadoDulceria):
        self.dulcero = dulcero

    def ejecutar(self):
        while True:
            print("\n" + "=" * 65)
            print("        [DULCERIA] CAJA DE CONFITERÍA — CINE ESTRELLA [DULCERIA]")
            print(f" Atiende: {self.dulcero.nombre} | Rol: ENCARGADO DE DULCERÍA")
            print("=" * 65)
            print(" 1. Ver Catálogo de Confitería con Precios del Día")
            print(" 2. Vender Productos de Confitería")
            print(" 3. Consultar Mi Cuadratura de Caja")
            print(" 0. Cerrar Sesión")
            print("=" * 65)

            op = leer_texto("Seleccione una opción: ")

            if op == "1":
                self._ver_catalogo()
            elif op == "2":
                self._vender_productos()
            elif op == "3":
                self._ver_cuadratura()
            elif op == "0":
                print("\nCerrando turno de dulcería...")
                break
            else:
                print(f"\n[!] Opción '{op}' no válida.")
                pausar()

    def _ver_catalogo(self):
        """Muestra catálogo con conversión en tiempo real de productos importados (P16, P17)."""
        print("\n--- CATÁLOGO DE PRODUCTOS DE CONFITERÍA ---")
        prods = ProductoDAO.listar()
        if not prods:
            print("No hay productos en el catálogo.")
            pausar()
            return

        # Intentar obtener cotización del dólar
        tasa_dolar = None
        try:
            tc = TipoCambioService.obtener_dolar_dia()
            tasa_dolar = tc.valor
            print(f"💵 Dólar Oficial Hoy: ${tasa_dolar:,.2f} CLP ({tc.fecha} - {tc.fuente})")
        except ReglaNegocioException as e:
            # Caso P17: Sin internet informa el problema y continúa
            print(f"[!] Aviso: {e}")

        print(f"\n{'ID':<5} | {'Producto':<28} | {'Tipo':<12} | {'Precio Base':<15} | {'Precio Final (CLP)':<18}")
        print("-" * 85)
        for p in prods:
            if isinstance(p, ProductoImportado):
                base_str = f"USD ${p.precio_usd:.2f}"
                if tasa_dolar is not None:
                    final_str = f"${p.calcular_precio(tasa_dolar):,.0f} CLP"
                else:
                    final_str = "[Requiere Internet]"
            else:
                base_str = f"${p.precio_base:,.0f} CLP"
                final_str = f"${p.calcular_precio():,.0f} CLP"

            print(f"{p.id_producto:<5} | {p.nombre:<28} | {p.tipo.capitalize():<12} | {base_str:<15} | {final_str:<18}")
        pausar()

    def _vender_productos(self):
        """Venta de uno o más productos de confitería (Casos P12, P16, P17)."""
        print("\n--- REGISTRO DE VENTA DE CONFITERÍA ---")
        prods = ProductoDAO.listar()
        if not prods:
            print("No hay productos disponibles.")
            pausar()
            return

        venta = Venta(id_venta=None)

        while True:
            for p in prods:
                print(f" [{p.id_producto}] {p.nombre} ({p.tipo})")
            id_p = leer_entero("Seleccione ID de producto a agregar: ", minimo=1)
            cantidad = leer_entero("Cantidad: ", minimo=1)

            try:
                detalle = VentaService.crear_detalle_producto(id_p, cantidad, self.dulcero)
                venta.agregar_detalle(detalle)
                print(f"[OK] Agregado: {detalle.descripcion} x{cantidad} = ${detalle.subtotal:,.0f} CLP")
            except ReglaNegocioException as e:
                # Si falla internet o el producto, informa y continúa (P17)
                print(f"[!] No fue posible agregar el producto: {e}")

            mas = leer_texto("¿Desea agregar otro producto a la misma compra? (s/n): ").lower()
            if mas != "s":
                break

        if not venta.detalles:
            print("No se agregaron productos. Venta cancelada.")
            pausar()
            return

        print("\n" + "=" * 55)
        print(" RESUMEN DE COMPRA DE CONFITERÍA:")
        for d in venta.detalles:
            print(f" * {d.descripcion} x{d.cantidad} = ${d.subtotal:,.0f} CLP")
        print(f" TOTAL A COBRAR: ${venta.total:,.0f} CLP")
        print("=" * 55)

        confirmar = leer_texto("¿Confirmar venta? (s/n): ").lower()
        if confirmar == "s":
            v_guardada = VentaService.concretar_venta(venta)
            print(f"\n[OK] ¡VENTA #{v_guardada.id_venta} REGISTRADA EXITOSAMENTE!")
            print(f"  Total: ${v_guardada.total:,.0f} CLP")
        else:
            print("Venta cancelada.")
        pausar()

    def _ver_cuadratura(self):
        cuad = VentaDAO.obtener_cuadratura_trabajador(self.dulcero.id_trabajador)
        print("\n" + "=" * 55)
        print(f" CUADRATURA DE CAJA — {self.dulcero.nombre.upper()}")
        print("=" * 55)
        print(f" Transacciones realizadas:  {cuad['transacciones']}")
        print(f" Total Productos vendidos:   {cuad['total_productos']}")
        print(f" TOTAL RECAUDADO EN CAJA:    ${cuad['total_recaudado']:,.0f} CLP")
        print("-" * 55)
        print(" Desglose de confitería:")
        for d in cuad["desglose"]:
            print(f"  * {d['descripcion']:<35} x{d['cantidad_total']:<4} = ${d['subtotal_total']:,.0f}")
        print("=" * 55)
        pausar()


# =============================================================================
# APLICACIÓN PRINCIPAL (Inicio de Sesión y Control de Flujo)
# =============================================================================

def ejecutar_aplicacion():
    # Inicialización de la base de datos (DDL y semillas de demostración)
    inicializar_bd()
    auth = AuthService()

    while True:
        print("\n" + "#" * 65)
        print("            * BIENVENIDO A CINE ESTRELLA *")
        print("             Sistema de Gestión Integral")
        print("#" * 65)
        print(" Inicie sesión para acceder a su módulo de trabajo:")
        print(" (Cuenta de demostración administrador: 'admin' / 'admin')")
        print("-" * 65)

        username = leer_texto("Usuario (o 'salir' para cerrar el sistema): ")
        if username.lower() == "salir":
            print("\n¡Gracias por utilizar el sistema Cine Estrella! Hasta pronto.")
            break

        password = leer_texto("Contraseña: ")

        trabajador = auth.autenticar(username, password)
        if not trabajador:
            print("\n[ERROR] Error de autenticación: Usuario o contraseña incorrectos.")
            pausar()
            continue

        print(f"\n[OK] ¡Acceso concedido! Bienvenido, {trabajador.nombre}.")

        # Redirigir según el rol del usuario
        if trabajador.rol == "admin":
            menu_adm = MenuAdmin(trabajador)
            menu_adm.ejecutar()
        elif trabajador.rol == "boletero":
            from model.boletero import Boletero
            # Si es instancia base, adaptar a Boletero
            bol = trabajador if isinstance(trabajador, Boletero) else Boletero(
                id_trabajador=trabajador.id_trabajador, nombre=trabajador.nombre,
                username=trabajador.username, password_hash=trabajador.password_hash
            )
            menu_bol = MenuBoletero(bol)
            menu_bol.ejecutar()
        elif trabajador.rol == "dulceria":
            from model.encargado_dulceria import EncargadoDulceria
            dulc = trabajador if isinstance(trabajador, EncargadoDulceria) else EncargadoDulceria(
                id_trabajador=trabajador.id_trabajador, nombre=trabajador.nombre,
                username=trabajador.username, password_hash=trabajador.password_hash
            )
            menu_dulc = MenuDulceria(dulc)
            menu_dulc.ejecutar()
        else:
            print(f"[!] Rol '{trabajador.rol}' no tiene un módulo asignado.")
            pausar()

        auth.cerrar_sesion()


def ejecutar_gui():
    """Lanza la interfaz gráfica moderna e interactiva de Cine Estrella (Versión 3.0)."""
    inicializar_bd()
    try:
        from ui.ventana_login import VentanaLogin
        app = VentanaLogin()
        app.mainloop()
    except Exception as e:
        print(f"[ERROR] Error al inicializar interfaz gráfica: {e}")
        print("Iniciando en modo consola de respaldo...")
        ejecutar_aplicacion()


if __name__ == "__main__":
    try:
        if "--consola" in sys.argv or "--cli" in sys.argv:
            ejecutar_aplicacion()
        else:
            ejecutar_gui()
    except (KeyboardInterrupt, SystemExit):
        print("\n\nCierre ordenado del sistema Cine Estrella.")
