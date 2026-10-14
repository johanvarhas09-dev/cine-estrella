# 📑 CATÁLOGO Y TRAZABILIDAD DE COMENTARIOS TÉCNICOS EN EL CÓDIGO
## CINE ESTRELLA — SISTEMA INTEGRAL DE GESTIÓN (VERSIÓN 4.0)

**Asignatura:** Programación Orientada a Objetos Segura  
**Institución:** INACAP — Sede Puente Alto (2026)  
**Proyecto:** CINE ESTRELLA (Caso de Negocio 11)  
**Fecha:** Octubre 2026  

---

## 1. Introducción y Criterios de Documentación

Con el fin de garantizar una alta mantenibilidad, facilitar auditorías de código y asegurar el cumplimiento riguroso de los lineamientos formativos de INACAP, cada archivo del sistema ha sido enriquecido con comentarios y *docstrings* explicativos. 

Estos comentarios han sido diseñados bajo los siguientes principios:
1. **Inocuidad en tiempo de ejecución:** No alteran la lógica, los tipos de retorno ni el rendimiento del sistema.
2. **Estandarización de Etiquetas:** Se emplean identificadores normalizados para localizar rápidamente cada regla de negocio:
   * `[FUNCIONALIDAD: ...]` — Describe el requerimiento funcional implementado.
   * `[REGLA DE NEGOCIO: ...]` — Detalla la política o restricción del cine aplicada.
   * `[SEGURIDAD: ...]` — Explica los controles de seguridad criptográfica, validación o prevención de inyecciones.
   * `[Caso Pxx]` — Vincula directamente la sección de código con la **Matriz de Pruebas de Aceptación (Guión P01 al P19)**.

---

## 2. Matriz de Trazabilidad por Archivo y Componente

### A. Capa de Dominio (`model/`)

| Archivo | Elemento / Método Comentado | Etiqueta / Propósito | Regla de Negocio / Caso |
| :--- | :--- | :--- | :--- |
| [`model/cliente.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/cliente.py) | `validar_rut()` | `[FUNCIONALIDAD: VALIDACIÓN DE RUT CHILENO - ALGORITMO MÓDULO 11]` | Casos P07 y P08: Ponderación de serie 2 a 7, residuo `% 11`, cálculo de dígito verificador ('0', 'K' o dígito). |
| [`model/cliente.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/cliente.py) | `limpiar_rut()`, `formatear_rut()` | `[UTILIDAD: SANITIZACIÓN]` y `[FORMATO CANÓNICO]` | Limpieza de caracteres no alfanuméricos y estandarización a `12345678-K`. |
| [`model/cliente.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/cliente.py) | `validar_edad()` | `[FUNCIONALIDAD: CONTROL DE EDAD MÍNIMA]` | Caso P15: Comparación booleana de edad del cliente vs requerimiento etario de la función. |
| [`model/pelicula.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/pelicula.py) | `clasificacion_edad` (setter) | `[VALIDACIÓN DE CLASIFICACIÓN ETARIA]` | Validación de números enteros no negativos (0 para Todo Espectador, 14, 18). |
| [`model/pelicula.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/pelicula.py) | `es_apta()` | `[FUNCIONALIDAD: RESTRICCIÓN DE EDAD]` | Caso P15: Determina si el cliente tiene la edad necesaria para la película. |
| [`model/funcion.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/funcion.py) | `reservar_asientos()` | `[CONTROL DE CAPACIDAD Y SOBREVENTA]` | Caso P14: Lanza `SinAsientosException` si la cantidad solicitada supera los asientos disponibles. |
| [`model/funcion.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/funcion.py) | `calcular_precio()` | `[POLIMORFISMO: BASE]` | Caso P09: Método polimórfico base que entrega el precio de entrada de la función. |
| [`model/funcion_2d.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/funcion_2d.py) | `calcular_precio()` | `[POLIMORFISMO: FUNCIÓN 2D]` | Caso P09: Proyección estándar, retorna directamente el precio base asignado. |
| [`model/funcion_3d.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/funcion_3d.py) | `calcular_precio()`, `recargo_3d` | `[POLIMORFISMO: FUNCIÓN 3D]` | Caso P10: Retorna precio base + recargo tecnológico tridimensional. |
| [`model/funcion_vip.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/funcion_vip.py) | `CAPACIDAD_MAX_VIP`, `recargo_vip` | `[REGLA DE NEGOCIO: SALA VIP]` | Caso P11: Capacidad restringida estrictamente a un máximo de 30 asientos y adición de recargo premium. |
| [`model/producto.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/producto.py) | `calcular_precio()` | `[POLIMORFISMO: BASE PRODUCTO]` | Método polimórfico base para cálculo de precio de confitería. |
| [`model/producto_nacional.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/producto_nacional.py) | `calcular_precio()` | `[PRODUCTO NACIONAL]` | Retorna el precio base fijo expresado en pesos chilenos (CLP). |
| [`model/producto_importado.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/producto_importado.py) | `calcular_precio()` | `[FUNCIONALIDAD: CONVERSIÓN DINÁMICA DE DÓLAR A PESOS CHILENOS]` | Caso P16: Multiplica el precio en USD por la tasa oficial del día de `mindicador.cl` con redondeo entero. |
| [`model/trabajador.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/trabajador.py) | `generar_hash()` | `[SEGURIDAD CRIPTOGRÁFICA: HASHING CON SALT Y SHA-256]` | Generación de salt aleatorio (16 bytes) con `os.urandom(16)` y digest SHA-256 (`salt$hash`) evitando contraseñas en texto plano. |
| [`model/trabajador.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/trabajador.py) | `verificar_password()` | `[AUTENTICACIÓN SEGURA]` | Extracción de salt, cómputo del hash candidato y verificación segura de credenciales. |
| [`model/trabajador.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/trabajador.py) | `puede_vender_entradas()`, `puede_vender_productos()` | `[CONTROL DE ACCESO BASADO EN ROLES (RBAC)]` | Matriz de permisos exclusiva entre roles Boletero y Encargado de Dulcería. |
| [`model/boletero.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/boletero.py) | Subtipo `Boletero` | `[ROL EXCLUSIVO: BOLETERÍA]` | Permiso exclusivo para vender entradas (`True`) e inhabilidad para dulcería (`False`). |
| [`model/encargado_dulceria.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/encargado_dulceria.py) | Subtipo `EncargadoDulceria` | `[ROL EXCLUSIVO: CONFITERÍA]` | Permiso exclusivo para confitería (`True`) e inhabilidad para entradas (`False`). |
| [`model/venta.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/venta.py) | `Venta` y `DetalleVenta` | `[COMPOSICIÓN: VENTA UNIFICADA]` | Casos P12 y P13: Soporte para agrupar múltiples entradas y productos bajo un mismo folio fiscal. |
| [`model/detalle_venta.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/detalle_venta.py) | `id_trabajador` | `[ATRIBUCIÓN DE TRABAJADOR POR ÍTEM]` | Identificación del empleado responsable de cada línea para cuadratura de caja individual. |
| [`model/excepciones.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/model/excepciones.py) | Clases de Excepción | `[JERARQUÍA DE EXCEPCIONES DE DOMINIO]` | `SinAsientosException`, `RestriccionEdadException`, `ReglaNegocioException`. |

---

### B. Capa de Servicios (`service/`)

| Archivo | Elemento / Método Comentado | Etiqueta / Propósito | Regla de Negocio / Caso |
| :--- | :--- | :--- | :--- |
| [`service/tipo_cambio_service.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/service/tipo_cambio_service.py) | `obtener_dolar_dia()` | `[FUNCIONALIDAD: CONSULTA OFICIAL DEL DÓLAR OBSERVADO]` | Casos P16 y P17: Petición HTTP a `mindicador.cl` con timeout de 5 segundos, registro en tabla de auditoría y captura de fallos de red. |
| [`service/tipo_cambio_service.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/service/tipo_cambio_service.py) | Bloques `except` | `[TOLERANCIA A FALLOS SIN CAÍDA]` | Caso P17: Captura `Timeout` y `ConnectionError`, emitiendo advertencia amigable sin detener el programa ni simular tasas en silencio. |
| [`service/venta_service.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/service/venta_service.py) | `validar_cliente_para_funcion()` | `[FUNCIONALIDAD: VALIDACIÓN COMBINADA DE COMPRADOR Y CLASIFICACIÓN]` | Casos P07, P08 y P15: Valida formato/dígito verificador de RUT y restringe el acceso de menores a películas +14 o +18. |
| [`service/venta_service.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/service/venta_service.py) | `crear_detalle_entrada()` | `[FUNCIONALIDAD: EMISIÓN DE BOLETO Y CONTROL DE CUPOS]` | Casos P09, P10, P11 y P14: Control de capacidad, cálculo polimórfico y validación de permisos de boletero. |
| [`service/venta_service.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/service/venta_service.py) | `crear_detalle_producto()` | `[FUNCIONALIDAD: VENTA DE CONFITERÍA Y CONVERSIÓN DE DIVISAS]` | Casos P12, P16 y P17: Conversión USD→CLP para importados o precio fijo para nacionales, validando permisos de confitería. |
| [`service/venta_service.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/service/venta_service.py) | `concretar_venta()` | `[FUNCIONALIDAD: TRANSACCIÓN ATÓMICA DE VENTA COMPARTIDA]` | Casos P12 y P13: Registro consolidado en base de datos bajo garantías ACID. |
| [`service/venta_service.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/service/venta_service.py) | `generar_grafico_asientos_texto()` | `[REPRESENTACIÓN GRÁFICA DE SALA]` | Representación visual textual con barra de ocupación (`###---`) y cálculo porcentual. |
| [`service/auth_service.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/service/auth_service.py) | `iniciar_sesion()`, `sesion_actual` | `[GESTIÓN DE SESIÓN ACTIVA]` | Control de usuario logueado en memoria y cierre seguro de sesión. |

---

### C. Capa de Acceso a Datos (`dao/`)

| Archivo | Elemento / Método Comentado | Etiqueta / Propósito | Regla de Negocio / Caso |
| :--- | :--- | :--- | :--- |
| [`dao/conexion.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/dao/conexion.py) | `obtener_conexion()` | `[INTEGRIDAD REFERENCIAL Y MAPEO RELACIONAL]` | Activa `PRAGMA foreign_keys = ON;` en SQLite y asigna `sqlite3.Row` para acceso por nombres de columna. |
| [`dao/db_init.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/dao/db_init.py) | `inicializar_bd()` | `[DDL Y SIEMBRA INICIAL SEGURA]` | Creación de tablas (`peliculas`, `funciones`, `productos`, `trabajadores`, `ventas`, `detalle_ventas`, `clientes`) y siembra de usuarios con salt SHA-256. |
| [`dao/cliente_dao.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/dao/cliente_dao.py) | `guardar_o_actualizar()` | `[PERSISTENCIA SEGURA: UPSERT]` | Inserta o actualiza mediante `ON CONFLICT(rut)` utilizando marcadores de posición `?` contra SQL Injection. |
| [`dao/cliente_dao.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/dao/cliente_dao.py) | `obtener_por_rut()` | `[BÚSQUEDA PARAMETRIZADA POR RUT]` | Consulta segura normalizada con formato canónico de RUT. |
| [`dao/venta_dao.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/dao/venta_dao.py) | `registrar_venta()` | `[FUNCIONALIDAD: TRANSACCIÓN ATÓMICA DE VENTA COMPARTIDA]` | Casos P12, P13 y P14: Transacción atómica SQLite con `conn.rollback()` ante cualquier error o falta de cupo. |
| [`dao/venta_dao.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/dao/venta_dao.py) | `obtener_cuadratura_trabajador()` | `[CUADRATURA INDIVIDUAL DE CAJA]` | Agrupación `SUM(subtotal)` filtrada por `id_trabajador` garantizando cuadratura exacta independientemente de ventas compartidas. |
| [`dao/pelicula_dao.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/dao/pelicula_dao.py) | `eliminar()` | `[PROTECCIÓN DE INTEGRIDAD REFERENCIAL]` | Caso P06: Impide eliminar una película si posee funciones programadas activas (`ReglaNegocioException`). |
| [`dao/funcion_dao.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/dao/funcion_dao.py) | `obtener_por_id()`, `listar_todas()` | `[RECONSTRUCCIÓN POLIMÓRFICA]` | Instancia dinámicamente objetos `Funcion2D`, `Funcion3D` o `FuncionVIP` según la columna `tipo` en la BD. |
| [`dao/trabajador_dao.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/dao/trabajador_dao.py) | `autenticar()` | `[AUTENTICACIÓN CRIPTOGRÁFICA]` | Valida credenciales delegando la verificación de salt y hash al modelo `Trabajador`. |

---

### D. Capa de Presentación e Interfaz (`ui/` y `main.py`)

| Archivo | Elemento / Método Comentado | Etiqueta / Propósito | Regla de Negocio / Caso |
| :--- | :--- | :--- | :--- |
| [`ui/ventana_login.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/ui/ventana_login.py) | `VentanaLogin` | `[AUTENTICACIÓN VISUAL Y SELECCIÓN DE ROL]` | Pantalla de bienvenida cinemática; deriva a `VentanaAdmin`, `VentanaBoleteria` o `VentanaDulceria` según el rol autenticado. |
| [`ui/ventana_boleteria.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/ui/ventana_boleteria.py) | `_agregar_al_carrito()` | `[FUNCIONALIDAD: RESTRICCIÓN ETARIA Y VALIDACIÓN DE RUT EN LA INTERFAZ]` | Casos P07, P08 y P15: Diálogos modales amigables sin abortar el flujo ante fallas de edad o RUT. |
| [`ui/ventana_boleteria.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/ui/ventana_boleteria.py) | `_construir_mapa_asientos()` | `[MAPA INTERACTIVO DE BUTACAS]` | Selector gráfico de asientos con diferenciación de colores (Disponibles, Ocupados, VIP). |
| [`ui/ventana_dulceria.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/ui/ventana_dulceria.py) | `_cargar_dolar()` | `[FUNCIONALIDAD: CARGA DINÁMICA DE DÓLAR EN TIEMPO REAL]` | Casos P16 y P17: Actualización de divisas vía API con respaldo referencial en modo offline si se pierde conectividad. |
| [`ui/ventana_cuadratura.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/ui/ventana_cuadratura.py) | `VentanaCuadratura` | `[CUADRATURA VISUAL DE CAJA]` | Reporte desglosado de ingresos por entradas y confitería para cierre de turno. |
| [`ui/fondos.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/ui/fondos.py) | `FondoDinamico`, `generar_fondo()` | `[FONDOS DINÁMICOS CINEMATOGRÁFICOS]` | Carga y escalado dinámico de imágenes `.jpg` desde `./fondos/` con Pillow; generación algorítmica en memoria ante ausencia de archivo. |
| [`main.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/main.py) | `leer_entero()`, `leer_flotante()` | `[UTILIDADES ROBUSTAS DE ENTRADA POR CONSOLA]` | Caso P19: Captura de `ValueError` ante entradas con letras (`abc`) o caracteres no numéricos sin cerrar la aplicación. |
| [`main.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/main.py) | `ejecutar_aplicacion()` | `[MANEJO DE OPCIÓN INEXISTENTE]` | Caso P18: Validación de opciones de menú fuera de rango sin desbordar el flujo. |
| [`main.py`](file:///c:/TRABAJO/00%20-%20PROYECTOS/CINE/version4/main.py) | `ejecutar_gui()` | `[LANZAMIENTO HÍBRIDO GUI/CLI]` | Lanza la interfaz gráfica por defecto con opción de alternancia a consola mediante `--consola` o `--cli`. |

---

## 3. Síntesis de Cobertura de Requisitos de la Rúbrica

El sistema garantiza que cada requerimiento evaluado se encuentre respaldado tanto en su implementación como en sus comentarios:

1. **Herencia y Polimorfismo:** Evidenciado en la jerarquía `Funcion` (`2D`, `3D`, `VIP`), `Producto` (`Nacional`, `Importado`) y `Trabajador` (`Boletero`, `EncargadoDulceria`).
2. **Encapsulamiento Estricto:** Todos los atributos de dominio son privados (`_atributo`) con acceso controlado vía `@property` y validadores en setters.
3. **Seguridad y Criptografía:** Ninguna clave se almacena en texto plano; se implementa `os.urandom(16)` + `SHA-256`.
4. **Validación de Identidad:** Implementación completa del algoritmo Módulo 11 con manejo de dígitos `0` a `9` y `K`.
5. **Consumo de APIs y Tolerancia a Fallos:** Manejo controlado con timeout de 5s a `mindicador.cl` y operación resiliente sin internet.
6. **Integridad Transaccional:** Composición de venta compartida con atomicidad SQLite (`BEGIN`, `COMMIT`, `ROLLBACK`).

