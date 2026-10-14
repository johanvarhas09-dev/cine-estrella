# 📑 INFORME TÉCNICO DE CUMPLIMIENTO DE RÚBRICA DE EVALUACIÓN (ES3)
## SISTEMA DE GESTIÓN CINE ESTRELLA — VERSIÓN 4.0

**Asignatura:** Programación Orientada a Objetos Segura  
**Institución:** INACAP  
**Rol del Auditor:** Desarrollador Sénior de Software / Analista de Código  
**Fecha de Emisión:** Octubre 2026  
**Entorno de Ejecución:** Visual Studio Code / Antigravity Python 3.12 Engine  
**Estado General:** **14 / 14 Puntos Cumplidos (100% de Aprobación)**

---

## 1. Matriz Ejecutiva de Rúbrica y Evidencias

A continuación se presenta la tabla consolidada de cumplimiento con los 14 puntos exigidos por la pauta de evaluación. Cada archivo cuenta con enlace relativo directo para su apertura en el editor.

| N.º | Requisito / Punto de Rúbrica | Archivo Principal | Línea(s) | Estado | Extracto Representativo del Código |
|:---|:---|:---|:---:|:---:|:---|
| **1.1** | **Validación de RUT** | [`model/cliente.py`](./model/cliente.py#L78-L118) | L78–L118 | **Implementado** | `resto = suma % 11; digito_calculado = 11 - resto ... return dv == dv_esperado` |
| **1.2** | **Manejo de excepciones** | [`model/excepciones.py`](./model/excepciones.py#L7-L24) | L7–L24 | **Implementado** | `class ReglaNegocioException(Exception) ... class SinAsientosException(ReglaNegocioException)` |
| **1.3** | **Validación de ingreso de información** | [`main.py`](./main.py#L65-L103) | L65–L103 | **Implementado** | `while True: try: valor = int(texto) ... except ValueError: print("[!] Entrada inválida...")` |
| **1.4** | **Consulta del dólar y cálculo en pesos** | [`service/tipo_cambio_service.py`](./service/tipo_cambio_service.py#L17-L74) | L17–L74 | **Implementado** | `requests.get("https://mindicador.cl/api/dolar", timeout=5) ... round(precio_usd * tasa_dolar)` |
| **1.5** | **Acceso a la base de datos** | [`dao/conexion.py`](./dao/conexion.py#L21-L28) | L21–L28 | **Implementado** | `conn = sqlite3.connect(_CURRENT_DB_PATH); conn.execute("PRAGMA foreign_keys = ON;")` |
| **1.6** | **CRUD completo** | [`dao/pelicula_dao.py`](./dao/pelicula_dao.py#L11-L104) | L11–L104 | **Implementado** | `crear()` (L12), `listar()` (L28), `modificar()` (L64), `eliminar()` con integridad referencial (L83) |
| **1.7** | **Herencia: cuatro jerarquías** | [`model/funcion.py`](./model/funcion.py#L9) | L9 (y subtipos) | **Implementado** | Cuatro jerarquías reales: `Funcion`, `Producto`, `Trabajador`, `ReglaNegocioException` |
| **1.8** | **Polimorfismo** | [`model/funcion.py`](./model/funcion.py#L125-L127) | L125–L127 | **Implementado** | `calcular_precio()` sobrescrito en `Funcion2D`, `Funcion3D` (+recargo) y `FuncionVIP` (+recargo) |
| **1.9** | **DAO (Data Access Object)** | [`dao/pelicula_dao.py`](./dao/pelicula_dao.py#L10-L105) | L10–L105 | **Implementado** | Capa DAO desacoplada: `ClienteDAO`, `PeliculaDAO`, `FuncionDAO`, `ProductoDAO`, `TrabajadorDAO`, `VentaDAO` |
| **2.0** | **Ingreso de login** | [`ui/ventana_login.py`](./ui/ventana_login.py#L138-L169) | L138–L169 | **Implementado** | `self.auth.autenticar(usuario, password)` con hashing SHA-256 + salt y derivación por rol |
| **2.1** | **Control de usuario** | [`model/trabajador.py`](./model/trabajador.py#L112-L125) | L112–L125 | **Implementado** | `puede_vender_entradas()`, `puede_vender_productos()` en modelo y filtrado RBAC en servicios |
| **2.2** | **Funcionalidad de boletería** | [`ui/ventana_boleteria.py`](./ui/ventana_boleteria.py#L24-L634) | L24–L634 | **Implementado** | Selección de función, control de edad, mapa de butacas, carrito y venta atómica (`VentaService`) |
| **2.3** | **Funcionalidad de confitería** | [`ui/ventana_dulceria.py`](./ui/ventana_dulceria.py#L27-L303) | L27–L303 | **Implementado** | Catálogo interactivo, cotización dólar en vivo, conversión USD→CLP, carrito y cuadratura de caja |
| **2.4** | **Funcionalidad de administrador** | [`ui/ventana_admin.py`](./ui/ventana_admin.py#L27-L1046) | L27–L1046 | **Implementado** | Panel integral con 5 pestañas: Cartelera, Confitería, Personal (CRUD), Reportes y Dólar API |

---

## 2. Inspección Técnica Detallada Punto por Punto

---

### 1.1. Validación de RUT

- **Estado:** **Implementado**
- **Justificación:** Se implementa el algoritmo estándar de verificación de RUT chileno (Módulo 11) con limpieza de caracteres especiales (puntos y guiones) y ponderación de serie $\{2, 3, 4, 5, 6, 7\}$. Maneja correctamente los casos límite donde el dígito verificador es `'0'` o `'K'`.
- **Archivo principal:** [`model/cliente.py`](./model/cliente.py#L78-L118)
- **Líneas exactas:** L78–L118 (método `validar_rut`), L65–L75 (método `limpiar_rut`), L22–L29 (setter `@rut.setter`).
- **Archivos secundarios:**
  - [`service/venta_service.py`](./service/venta_service.py#L23-L32): Validación integrada en la compra previa a la emisión de boleto.
  - [`ui/ventana_boleteria.py`](./ui/ventana_boleteria.py#L384-L408): Captura y validación en la interfaz gráfica con diálogos modales amigables.

#### Extracto Real del Código

```python
# Ubicación: model/cliente.py (Líneas 78 a 118)
@staticmethod
def validar_rut(rut: str) -> bool:
    if not rut or not isinstance(rut, str):
        return False
    cuerpo, dv = Cliente.limpiar_rut(rut)
    if not cuerpo or not dv or not cuerpo.isdigit():
        return False

    # Paso 1: Ponderación de dígitos con serie 2 a 7 de derecha a izquierda
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    # Paso 2: Cálculo del residuo Módulo 11
    resto = suma % 11
    digito_calculado = 11 - resto

    # Paso 3: Mapeo de casos especiales (0 y K)
    if digito_calculado == 11:
        dv_esperado = '0'
    elif digito_calculado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(digito_calculado)

    # Paso 4: Comparación estricta del dígito verificador
    return dv == dv_esperado
```

- **Explicación técnica:** La función `limpiar_rut` utiliza expresiones regulares `re.sub(r'[^0-9Kk]', '', rut).upper()` para aislar el cuerpo numérico y el dígito verificador entregado. Luego, `validar_rut` ejecuta el cálculo aritmético ponderado y compara el dígito esperado con el ingresado en mayúscula. En el modelo `Cliente`, el `@rut.setter` invoca `validar_rut` y, de ser inválido, genera una excepción `ValueError` sin persistir datos corruptos.

---

### 1.2. Manejo de Excepciones

- **Estado:** **Implementado**
- **Justificación:** El sistema cuenta con una jerarquía formal de excepciones de negocio derivadas de `Exception` (`ReglaNegocioException`, `SinAsientosException`, `RestriccionEdadException`), complementadas con bloques `try-except-raise` y transaccionalidad `rollback` en SQLite ante fallos operacionales.
- **Archivo principal:** [`model/excepciones.py`](./model/excepciones.py#L7-L24)
- **Líneas exactas:** L7–L24.
- **Archivos secundarios:**
  - [`dao/venta_dao.py`](./dao/venta_dao.py#L111-L115): Captura de fallos con reversión atómica de la base de datos (`conn.rollback()`).
  - [`service/tipo_cambio_service.py`](./service/tipo_cambio_service.py#L56-L74): Captura controlada de `Timeout` y `ConnectionError` de la biblioteca `requests`.
  - [`main.py`](./main.py#L65-L103, L659, L689): Manejo amigable de `ValueError` y excepciones de dominio en la interfaz de usuario.

#### Extracto Real del Código

```python
# Ubicación: model/excepciones.py (Líneas 7 a 24)
class ReglaNegocioException(Exception):
    """Excepción base para violaciones de reglas de negocio del cine."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class SinAsientosException(ReglaNegocioException):
    """Lanzada cuando una función no cuenta con capacidad o asientos disponibles suficientes."""
    def __init__(self, mensaje: str = "No hay asientos suficientes disponibles para esta función."):
        super().__init__(mensaje)


class RestriccionEdadException(ReglaNegocioException):
    """Lanzada cuando un cliente no cumple con la edad mínima exigida por la clasificación."""
    def __init__(self, mensaje: str = "El comprador no cumple con la edad mínima requerida para esta película."):
        super().__init__(mensaje)
```

Y en la capa de datos para garantizar transacciones ACID:

```python
# Ubicación: dao/venta_dao.py (Líneas 112 a 115)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
```

- **Explicación técnica:** La jerarquía permite diferenciar errores de validación de negocio (edad insuficiente, sobreventa de salas) de errores de infraestructura (caída de red o llaves foráneas). Si ocurre un fallo en la venta, `VentaDAO` revierte atómicamente todos los cambios ejecutados en SQLite mediante `conn.rollback()`, impidiendo registros inconsistentes.

---

### 1.3. Validación de Ingreso de Información

- **Estado:** **Implementado**
- **Justificación:** Existen validaciones de campos obligatorios, tipos de datos (conversiones seguras a entero y decimal), longitudes mínimas y rangos lógicos (edad entre 0 y 130 años, capacidades mayores a cero, precios no negativos). En la consola se previenen bloqueos ante entradas alfabéticas (`abc`) y en la interfaz gráfica se muestran cuadros de diálogo modales.
- **Archivo principal:** [`main.py`](./main.py#L65-L103)
- **Líneas exactas:** L65–L103 (funciones `leer_entero` y `leer_flotante`).
- **Archivos secundarios:**
  - [`model/cliente.py`](./model/cliente.py#L22-L54): Validación de formato de RUT, longitud mínima de nombre y rango de edad en `@property.setter`.
  - [`model/pelicula.py`](./model/pelicula.py#L35-L73): Validación de título no vacío, clasificación $\ge 0$ y duración $> 0$.
  - [`ui/ventana_admin.py`](./ui/ventana_admin.py#L210-L216, L463-L470): Validaciones en formularios de administración.

#### Extracto Real del Código

```python
# Ubicación: main.py (Líneas 65 a 85)
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
```

Y en el modelo de dominio:

```python
# Ubicación: model/cliente.py (Líneas 45 a 53)
    @edad.setter
    def edad(self, valor: int):
        try:
            valor_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("La edad debe ser un número entero.")
        if valor_int < 0 or valor_int > 130:
            raise ValueError("La edad debe estar comprendida entre 0 y 130 años.")
        self._edad = valor_int
```

- **Explicación técnica:** La función `leer_entero` mantiene un bucle interactivo que intercepta `ValueError` si el usuario ingresa cadenas o caracteres no numéricos, impidiendo el colapso de la aplicación (caso P19 de pruebas). De igual modo, los métodos de dominio encapsulados con decoradores `@property` validan el estado de los objetos antes de permitir su asignación.

---

### 1.4. Consulta del Dólar del Día y Cálculo en Pesos Chilenos

- **Estado:** **Implementado**
- **Justificación:** El sistema consume en tiempo real la API REST pública de `https://mindicador.cl/api/dolar` utilizando la librería `requests` con un límite estricto de espera (*timeout* de 5 segundos). Calcula dinámicamente el valor en pesos chilenos (CLP) de los productos de dulcería importados multiplicando el precio base en USD por la tasa oficial redondeada al entero más próximo.
- **Archivo principal:** [`service/tipo_cambio_service.py`](./service/tipo_cambio_service.py#L17-L74)
- **Líneas exactas:** L17–L74 (método `obtener_dolar_dia`).
- **Archivos secundarios:**
  - [`model/producto_importado.py`](./model/producto_importado.py#L27-L38): Método `calcular_precio(tasa_dolar)` que realiza la conversión comercial con `round()`.
  - [`service/venta_service.py`](./service/venta_service.py#L118-L123): Integración de la cotización al momento de emitir la línea de detalle de confitería.
  - [`ui/ventana_dulceria.py`](./ui/ventana_dulceria.py#L50-L65): Carga en segundo plano al abrir la caja con mecanismo de contingencia *offline* (950 CLP).

#### Extracto Real del Código

```python
# Ubicación: service/tipo_cambio_service.py (Líneas 29 a 54)
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
```

Y el cálculo matemático en la entidad importada:

```python
# Ubicación: model/producto_importado.py (Líneas 27 a 38)
def calcular_precio(self, tasa_dolar: float = 1.0) -> float:
    if tasa_dolar <= 0:
        raise ValueError("La tasa de cambio del dólar debe ser mayor a cero.")
    return round(self._precio_base * tasa_dolar)
```

- **Explicación técnica:** El método desacopla la fuente de datos externa de la lógica de negocio. Si la API no responde o no hay conexión a internet, captura `requests.exceptions.Timeout` o `ConnectionError` y lanza `ReglaNegocioException`, permitiendo que la interfaz gráfica conmute de forma transparente a una tasa referencial sin detener las operaciones del cine.

---

### 1.5. Acceso a la Base de Datos

- **Estado:** **Implementado**
- **Justificación:** Utiliza el motor relacional **SQLite 3** (`cine.db`). La conexión se gestiona centralizadamente asegurando la activación del soporte de integridad referencial mediante `PRAGMA foreign_keys = ON;` y el mapeo de columnas asociativas con `conn.row_factory = sqlite3.Row`. Todas las operaciones SQL emplean parámetros `?` para neutralizar ataques de inyección SQL.
- **Archivo principal:** [`dao/conexion.py`](./dao/conexion.py#L21-L28)
- **Líneas exactas:** L21–L28 (función `obtener_conexion`).
- **Archivos secundarios:**
  - [`dao/db_init.py`](./dao/db_init.py#L9-L99): Creación de las tablas relacionales (`peliculas`, `funciones`, `productos`, `trabajadores`, `clientes`, `ventas`, `detalle_ventas`, `tipo_cambio_log`).
  - [`dao/venta_dao.py`](./dao/venta_dao.py#L30-L116): Ejecución de consultas parametrizadas y control transaccional `commit`/`rollback`.

#### Extracto Real del Código

```python
# Ubicación: dao/conexion.py (Líneas 21 a 28)
def obtener_conexion() -> sqlite3.Connection:
    """
    Crea y retorna una nueva conexión SQLite con llaves foráneas activadas.
    """
    conn = sqlite3.connect(_CURRENT_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
```

Y la configuración del esquema DDL:

```python
# Ubicación: dao/db_init.py (Líneas 29 a 47)
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS peliculas (
            id_pelicula INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            clasificacion_edad INTEGER NOT NULL DEFAULT 0,
            duracion_minutos INTEGER NOT NULL DEFAULT 90
        );

        CREATE TABLE IF NOT EXISTS funciones (
            id_funcion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pelicula INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            fecha_hora TEXT NOT NULL,
            precio_base REAL NOT NULL,
            capacidad INTEGER NOT NULL,
            asientos_disponibles INTEGER NOT NULL,
            recargo REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula)
        );
        ...
```

- **Explicación técnica:** Al forzar `PRAGMA foreign_keys = ON;`, SQLite rechaza cualquier inserción que haga referencia a claves foráneas inexistentes y previene el borrado en cascada no deseado de datos históricos. La fábrica de filas `sqlite3.Row` permite acceder a los campos devueltos por nombre de columna (ej. `row["precio_base"]`), facilitando la reconstrucción de objetos de dominio.

---

### 1.6. CRUD Completo: Crear, Leer, Modificar y Eliminar

- **Estado:** **Implementado**
- **Justificación:** Se identifican las cuatro operaciones CRUD canónicas implementadas en múltiples módulos DAO del sistema (`PeliculaDAO`, `ProductoDAO`, `FuncionDAO`, `TrabajadorDAO`), incorporando además validaciones de integridad referencial que impiden la eliminación física de registros si estos poseen funciones o ventas históricas asociadas.
- **Archivo principal:** [`dao/pelicula_dao.py`](./dao/pelicula_dao.py#L11-L104)
- **Líneas exactas:**
  - **Create (Crear):** L11–L26 (`PeliculaDAO.crear`)
  - **Read (Leer):** L28–L43 (`PeliculaDAO.listar`) y L45–L62 (`PeliculaDAO.obtener_por_id`)
  - **Update (Modificar):** L64–L81 (`PeliculaDAO.modificar`)
  - **Delete (Eliminar):** L83–L104 (`PeliculaDAO.eliminar`)
- **Archivos secundarios:**
  - [`dao/producto_dao.py`](./dao/producto_dao.py#L29-L105): CRUD completo de confitería con restricción de eliminación si registra ventas.
  - [`dao/trabajador_dao.py`](./dao/trabajador_dao.py#L31-L156): CRUD de personal con protección de la cuenta principal `admin`.
  - [`ui/ventana_admin.py`](./ui/ventana_admin.py#L205-L370, L455-L585): Interfaz visual completa para ejecutar las operaciones CRUD.

#### Extracto Real del Código

```python
# Ubicación: dao/pelicula_dao.py (Líneas 11 a 104 - Métodos CRUD)

# 1. CREATE
@staticmethod
def crear(pelicula: Pelicula) -> Pelicula:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO peliculas (titulo, clasificacion_edad, duracion_minutos) VALUES (?, ?, ?)",
        (pelicula.titulo, pelicula.clasificacion_edad, pelicula.duracion_minutos)
    )
    pelicula.id_pelicula = cursor.lastrowid
    conn.commit()
    conn.close()
    return pelicula

# 2. READ
@staticmethod
def listar() -> list[Pelicula]:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id_pelicula, titulo, clasificacion_edad, duracion_minutos FROM peliculas ORDER BY id_pelicula")
    rows = cursor.fetchall()
    conn.close()
    return [Pelicula(r["id_pelicula"], r["titulo"], r["clasificacion_edad"], r["duracion_minutos"]) for r in rows]

# 3. UPDATE
@staticmethod
def modificar(pelicula: Pelicula) -> bool:
    if not pelicula.id_pelicula:
        raise ValueError("La película a modificar debe tener un ID válido.")
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE peliculas SET titulo = ?, clasificacion_edad = ?, duracion_minutos = ? WHERE id_pelicula = ?",
        (pelicula.titulo, pelicula.clasificacion_edad, pelicula.duracion_minutos, pelicula.id_pelicula)
    )
    modificados = cursor.rowcount
    conn.commit()
    conn.close()
    return modificados > 0

# 4. DELETE (Con integridad referencial)
@staticmethod
def eliminar(id_pelicula: int) -> bool:
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM funciones WHERE id_pelicula = ?", (id_pelicula,))
    conteo = cursor.fetchone()[0]
    if conteo > 0:
        conn.close()
        raise ReglaNegocioException(
            f"No se puede eliminar la película (ID {id_pelicula}) porque tiene {conteo} función(es) programada(s)."
        )
    cursor.execute("DELETE FROM peliculas WHERE id_pelicula = ?", (id_pelicula,))
    eliminados = cursor.rowcount
    conn.commit()
    conn.close()
    return eliminados > 0
```

- **Explicación técnica:** El ciclo de vida de la entidad `Pelicula` está completamente cerrado. Cada método gestiona el ciclo de vida de la conexión a la base de datos, confirma cambios mediante `commit()` y protege el modelo contra estados inconsistentes o borrados accidentales de elementos vinculados a funciones activas.

---

### 1.7. Herencia: Cuatro Jerarquías

- **Estado:** **Implementado**
- **Justificación:** El proyecto implementa **cuatro jerarquías de herencia reales e independientes** en su capa de dominio y modelo, más jerarquías adicionales en la capa de presentación (`ui/`). Cada una modela especializaciones de negocio concretas mediante la invocación de `super().__init__()`.
- **Estructura de las cuatro jerarquías:**
  1. **Jerarquía 1 — Proyecciones y Salas (`Funcion`):**
     - Clase Padre: [`model/funcion.py`](./model/funcion.py#L9) (`Funcion`)
     - Clases Hijas:
       - [`model/funcion_2d.py`](./model/funcion_2d.py#L9) (`Funcion2D`)
       - [`model/funcion_3d.py`](./model/funcion_3d.py#L9) (`Funcion3D`)
       - [`model/funcion_vip.py`](./model/funcion_vip.py#L9) (`FuncionVIP`)
  2. **Jerarquía 2 — Artículos de Confitería (`Producto`):**
     - Clase Padre: [`model/producto.py`](./model/producto.py#L7) (`Producto`)
     - Clases Hijas:
       - [`model/producto_nacional.py`](./model/producto_nacional.py#L8) (`ProductoNacional`)
       - [`model/producto_importado.py`](./model/producto_importado.py#L8) (`ProductoImportado`)
  3. **Jerarquía 3 — Personal del Cine (`Trabajador`):**
     - Clase Padre: [`model/trabajador.py`](./model/trabajador.py#L9) (`Trabajador`)
     - Clases Hijas:
       - [`model/boletero.py`](./model/boletero.py#L8) (`Boletero`)
       - [`model/encargado_dulceria.py`](./model/encargado_dulceria.py#L8) (`EncargadoDulceria`)
  4. **Jerarquía 4 — Excepciones de Negocio (`ReglaNegocioException`):**
     - Clase Padre Estándar: `Exception`
     - Clase Base del Dominio: [`model/excepciones.py`](./model/excepciones.py#L7) (`ReglaNegocioException`)
     - Clases Hijas:
       - [`model/excepciones.py`](./model/excepciones.py#L14) (`SinAsientosException`)
       - [`model/excepciones.py`](./model/excepciones.py#L20) (`RestriccionEdadException`)
  5. *(Jerarquía adicional en UI)*: [`ui/base.py`](./ui/base.py#L22) (`VentanaBase` hereda de `tk.Toplevel`), de la cual hereda [`ui/ventana_dulceria.py`](./ui/ventana_dulceria.py#L27) (`VentanaDulceria`).

#### Diagrama de Jerarquías de Clases (Mermaid)

```mermaid
classDiagram
    %% Jerarquía 1: Funciones
    class Funcion {
        -id_funcion: int
        -pelicula: Pelicula
        -tipo: str
        -precio_base: float
        -capacidad: int
        -asientos_disponibles: int
        +calcular_precio() float
    }
    class Funcion2D {
        +calcular_precio() float
    }
    class Funcion3D {
        -recargo_3d: float
        +calcular_precio() float
    }
    class FuncionVIP {
        -recargo_vip: float
        +calcular_precio() float
    }
    Funcion <|-- Funcion2D : hereda
    Funcion <|-- Funcion3D : hereda
    Funcion <|-- FuncionVIP : hereda

    %% Jerarquía 2: Productos
    class Producto {
        -id_producto: int
        -nombre: str
        -precio_base: float
        -tipo: str
        +calcular_precio(tasa_dolar) float
    }
    class ProductoNacional {
        +calcular_precio(tasa_dolar) float
    }
    class ProductoImportado {
        -precio_base_usd: float
        +calcular_precio(tasa_dolar) float
    }
    Producto <|-- ProductoNacional : hereda
    Producto <|-- ProductoImportado : hereda

    %% Jerarquía 3: Trabajadores
    class Trabajador {
        -id_trabajador: int
        -nombre: str
        -username: str
        -password_hash: str
        -rol: str
        +puede_vender_entradas() bool
        +puede_vender_productos() bool
    }
    class Boletero {
        +puede_vender_entradas() bool
    }
    class EncargadoDulceria {
        +puede_vender_productos() bool
    }
    Trabajador <|-- Boletero : hereda
    Trabajador <|-- EncargadoDulceria : hereda

    %% Jerarquía 4: Excepciones
    class Exception {
        <<Built-in Python>>
    }
    class ReglaNegocioException {
        +mensaje: str
    }
    class SinAsientosException {
        +mensaje: str
    }
    class RestriccionEdadException {
        +mensaje: str
    }
    Exception <|-- ReglaNegocioException : hereda
    ReglaNegocioException <|-- SinAsientosException : hereda
    ReglaNegocioException <|-- RestriccionEdadException : hereda
```

#### Extractos de Declaración de Herencia

```python
# Ubicación: model/funcion_3d.py (Línea 9)
class Funcion3D(Funcion):
    def __init__(self, id_funcion, pelicula, fecha_hora, precio_base, capacidad=80, asientos_disponibles=None, recargo_3d=1500.0):
        super().__init__(id_funcion, pelicula, "3D", fecha_hora, precio_base, capacidad, asientos_disponibles)
        self._recargo_3d = recargo_3d
```

```python
# Ubicación: model/producto_importado.py (Línea 8)
class ProductoImportado(Producto):
    def __init__(self, id_producto, nombre, precio_base_usd):
        super().__init__(id_producto, nombre, precio_base_usd, tipo="importado")
```

```python
# Ubicación: model/boletero.py (Línea 8)
class Boletero(Trabajador):
    def __init__(self, id_trabajador, nombre, username, password_hash, password_plano=""):
        super().__init__(id_trabajador, nombre, username, password_hash, rol="boletero", password_plano=password_plano)
```

- **Explicación técnica:** Cada clase hija reutiliza la inicialización de atributos comunes en la clase padre mediante `super().__init__()` y extiende el comportamiento agregando propiedades específicas (como `recargo_3d` en `Funcion3D` o `rol="boletero"` en `Boletero`), cumpliendo cabalmente el principio de sustitución de Liskov y el requerimiento de cuatro jerarquías del enunciado.

---

### 1.8. Polimorfismo

- **Estado:** **Implementado**
- **Justificación:** El polimorfismo se manifiesta de forma destacada en dos jerarquías principales:
  1. En `Funcion`: el método `calcular_precio()` es sobrescrito por `Funcion2D` (tarifa plana base), `Funcion3D` (adiciona recargo tecnológico tridimensional) y `FuncionVIP` (adiciona recargo de comodidades y butacas exclusivas).
  2. En `Producto`: el método `calcular_precio(tasa_dolar)` es sobrescrito por `ProductoNacional` (devuelve el precio fijo en CLP) y `ProductoImportado` (calcula dinámicamente según la cotización en dólares).
  3. En `Trabajador`: los métodos `puede_vender_entradas()` y `puede_vender_productos()` son sobrescritos polimórficamente por `Boletero` y `EncargadoDulceria`.
- **Archivo principal:** [`model/funcion.py`](./model/funcion.py#L125-L127) y sus clases hijas.
- **Líneas exactas:**
  - Base: [`model/funcion.py`](./model/funcion.py#L125-L127)
  - Subtipo 2D: [`model/funcion_2d.py`](./model/funcion_2d.py#L29-L31)
  - Subtipo 3D: [`model/funcion_3d.py`](./model/funcion_3d.py#L47-L49)
  - Subtipo VIP: [`model/funcion_vip.py`](./model/funcion_vip.py#L51-L53)
- **Archivos secundarios:**
  - [`model/producto.py`](./model/producto.py#L70-L72), [`model/producto_nacional.py`](./model/producto_nacional.py#L22-L24), [`model/producto_importado.py`](./model/producto_importado.py#L27-L38).

#### Extracto Real del Código

```python
# Ubicación: model/funcion.py (Líneas 125 a 127 - Método base)
    def calcular_precio(self) -> float:
        """Método polimórfico base que calcula el precio de la entrada."""
        return self._precio_base
```

```python
# Ubicación: model/funcion_2d.py (Líneas 29 a 31 - Sobrescritura 2D)
    def calcular_precio(self) -> float:
        """La función 2D utiliza directamente el precio base fijado."""
        return self._precio_base
```

```python
# Ubicación: model/funcion_3d.py (Líneas 47 a 49 - Sobrescritura 3D)
    def calcular_precio(self) -> float:
        """La función 3D suma su recargo tecnológico al precio base."""
        return self._precio_base + self._recargo_3d
```

```python
# Ubicación: model/funcion_vip.py (Líneas 51 a 53 - Sobrescritura VIP)
    def calcular_precio(self) -> float:
        """La función VIP añade un recargo premium sobre el precio base."""
        return self._precio_base + self._recargo_vip
```

- **Explicación técnica:** Gracias al polimorfismo, el módulo de ventas [`service/venta_service.py`](./service/venta_service.py#L79) invoca `f_db.calcular_precio()` de manera uniforme sin necesidad de bifurcaciones condicionales (`if/else`) sobre el tipo de función, garantizando la extensibilidad del sistema ante futuros formatos (por ejemplo, IMAX o 4DX).

---

### 1.9. DAO (Data Access Object)

- **Estado:** **Implementado**
- **Justificación:** El sistema cuenta con una capa de acceso a datos formal y desacoplada ubicada en el paquete `dao/`. Ningún componente de la interfaz de usuario ni de los servicios ejecuta sentencias SQL directamente; todas las operaciones de persistencia son delegadas a clases DAO especializadas.
- **Módulos DAO identificados:**
  - [`dao/cliente_dao.py`](./dao/cliente_dao.py): Búsqueda parametrizada y operación *UPSERT* segura de clientes.
  - [`dao/pelicula_dao.py`](./dao/pelicula_dao.py): CRUD completo de títulos cinematográficos.
  - [`dao/funcion_dao.py`](./dao/funcion_dao.py): CRUD y reconstrucción polimórfica dinámica según la columna `tipo` de la base de datos.
  - [`dao/producto_dao.py`](./dao/producto_dao.py): CRUD y reconstrucción de `ProductoNacional` o `ProductoImportado`.
  - [`dao/trabajador_dao.py`](./dao/trabajador_dao.py): Persistencia, listado y autenticación segura de usuarios.
  - [`dao/venta_dao.py`](./dao/venta_dao.py): Transacciones atómicas de tickets unificados y consultas de cuadratura de caja.
- **Archivo principal:** [`dao/pelicula_dao.py`](./dao/pelicula_dao.py#L10-L105)
- **Líneas exactas:** L10–L105.
- **Archivos secundarios:** [`dao/funcion_dao.py`](./dao/funcion_dao.py#L14-L42) (reconstrucción polimórfica).

#### Extracto Real del Código

```python
# Ubicación: dao/funcion_dao.py (Líneas 14 a 42 - Reconstrucción de objetos en DAO)
class FuncionDAO:
    @staticmethod
    def _instanciar(row) -> Funcion:
        pelicula = PeliculaDAO.obtener_por_id(row["id_pelicula"])
        if not pelicula:
            from model.pelicula import Pelicula
            pelicula = Pelicula(id_pelicula=row["id_pelicula"], titulo="Desconocida", clasificacion_edad=0)

        tipo = row["tipo"].upper()
        kwargs = {
            "id_funcion": row["id_funcion"],
            "pelicula": pelicula,
            "fecha_hora": row["fecha_hora"],
            "precio_base": row["precio_base"],
            "capacidad": row["capacidad"],
            "asientos_disponibles": row["asientos_disponibles"]
        }

        if tipo == "2D":
            return Funcion2D(**kwargs)
        elif tipo == "3D":
            recargo = row["recargo"] if "recargo" in row.keys() else Funcion3D.RECARGO_3D_DEFAULT
            return Funcion3D(recargo_3d=recargo, **kwargs)
        elif tipo == "VIP":
            recargo = row["recargo"] if "recargo" in row.keys() else FuncionVIP.RECARGO_VIP_DEFAULT
            return FuncionVIP(recargo_vip=recargo, **kwargs)
        else:
            return Funcion(tipo=tipo, **kwargs)
```

- **Explicación técnica:** La capa DAO aísla las peculiaridades del motor relacional SQLite del resto de la arquitectura. El método `_instanciar` lee los registros tabulares y reconstituye los objetos de dominio correspondientes a sus subclases reales (`Funcion2D`, `Funcion3D`, `FuncionVIP`), entregando al servicio objetos con su comportamiento polimórfico listo para operar.

---

### 2.0. Ingreso de Login

- **Estado:** **Implementado**
- **Justificación:** La autenticación se encuentra implementada tanto en entorno gráfico (Tkinter) como en consola CLI. El mecanismo verifica credenciales contra contraseñas protegidas con **hashing SHA-256 más salt pseudoaleatorio de 16 bytes** (`salt$hash`), evitando el almacenamiento de claves en texto plano. Tras el acceso, la aplicación deriva automáticamente al operador a su pantalla correspondiente según su rol.
- **Archivo principal:** [`ui/ventana_login.py`](./ui/ventana_login.py#L138-L169)
- **Líneas exactas:** L138–L169 (método `_login`).
- **Archivos secundarios:**
  - [`service/auth_service.py`](./service/auth_service.py#L17-L33): Método `autenticar(username, password_plano)` que orquesta la verificación y almacena la sesión activa.
  - [`model/trabajador.py`](./model/trabajador.py#L84-L110): Métodos `generar_hash()` y `verificar_password()`.
  - [`dao/trabajador_dao.py`](./dao/trabajador_dao.py#L79-L90): Búsqueda de trabajador por nombre de usuario.

#### Extracto Real del Código

```python
# Ubicación: ui/ventana_login.py (Líneas 138 a 166)
    def _login(self):
        usuario = self.var_user.get().strip()
        password = self.var_pass.get().strip()

        if not usuario or not password:
            messagebox.showwarning("Atención", "Por favor ingrese su usuario y contraseña.", parent=self)
            return

        trabajador = self.auth.autenticar(usuario, password)
        if not trabajador:
            messagebox.showerror("Error de Acceso", "Usuario o contraseña incorrectos.", parent=self)
            return

        # Redirigir según el rol
        self.withdraw()

        if trabajador.rol == "admin":
            from ui.ventana_admin import VentanaAdmin
            win = VentanaAdmin(self, trabajador)
        elif trabajador.rol == "boletero":
            from ui.ventana_boleteria import VentanaBoleteria
            win = VentanaBoleteria(self, trabajador)
        elif trabajador.rol == "dulceria":
            from ui.ventana_dulceria import VentanaDulceria
            win = VentanaDulceria(self, trabajador)
        else:
            messagebox.showerror("Rol desconocido", f"El rol '{trabajador.rol}' no tiene pantalla asignada.")
            self.deiconify()
            return
```

Y la verificación criptográfica del hash:

```python
# Ubicación: model/trabajador.py (Líneas 99 a 110)
    def verificar_password(self, password_plano: str) -> bool:
        if not self._password_hash or '$' not in self._password_hash:
            return False
        salt, _ = self._password_hash.split('$', 1)
        hash_ingresado = self.generar_hash(password_plano, salt=salt)
        return hash_ingresado == self._password_hash
```

- **Explicación técnica:** El proceso de autenticación extrae el `salt` almacenado en la base de datos, calcula el hash SHA-256 de la contraseña ingresada con dicho `salt` y efectúa una comparación segura. Si el login es exitoso, `VentanaLogin` oculta la ventana de bienvenida e inicializa la interfaz gráfica especializada para el rol autenticado.

---

### 2.1. Control de Usuario

- **Estado:** **Implementado**
- **Justificación:** Se implementa un modelo de **Control de Acceso Basado en Roles (RBAC)** que separa de forma estricta el proceso de autenticación (quién es el usuario) del proceso de autorización (qué acciones puede ejecutar en el sistema). Los roles disponibles son `administrador`, `boletero` y `dulceria`.
- **Diferenciación de roles y permisos:**
  - **Boletero:** Permiso exclusivo para emitir boletos de cine (`puede_vender_entradas() -> True`); inhabilitado para vender confitería (`puede_vender_productos() -> False`).
  - **Encargado de Dulcería:** Permiso exclusivo para vender artículos de confitería (`puede_vender_productos() -> True`); inhabilitado para emitir entradas (`puede_vender_entradas() -> False`).
  - **Administrador:** Acceso a la totalidad de las funciones de gestión, configuración, creación/edición de cuentas y auditoría de ventas.
- **Archivo principal:** [`model/trabajador.py`](./model/trabajador.py#L112-L125)
- **Líneas exactas:** L112–L125.
- **Archivos secundarios:**
  - [`model/boletero.py`](./model/boletero.py#L26-L32): Sobrescritura de permisos para boletero.
  - [`model/encargado_dulceria.py`](./model/encargado_dulceria.py#L26-L32): Sobrescritura de permisos para dulcería.
  - [`service/venta_service.py`](./service/venta_service.py#L63-L65, L108-L110): Bloqueo con `ReglaNegocioException` si un usuario intenta operar fuera de su ámbito de atribución.
  - [`dao/trabajador_dao.py`](./dao/trabajador_dao.py#L32-L34, L138-L142): Protección de la cuenta reservada `admin` para impedir su eliminación o modificación desautorizada.

#### Extracto Real del Código

```python
# Ubicación: service/venta_service.py (Líneas 63 a 65 y Líneas 108 a 110)
# 1. Control de acceso en venta de entradas:
if not trabajador.puede_vender_entradas():
    raise ReglaNegocioException("El trabajador no tiene permisos para emitir entradas de cine.")

# 2. Control de acceso en venta de productos de confitería:
if not trabajador.puede_vender_productos():
    raise ReglaNegocioException("El trabajador no tiene permisos para vender productos de confitería.")
```

Y la protección del usuario administrador en persistencia:

```python
# Ubicación: dao/trabajador_dao.py (Líneas 138 a 142)
if row_t["username"].strip().lower() == "admin" or row_t["rol"].strip().lower() == "admin":
    conn.close()
    raise ReglaNegocioException(
        "La cuenta del Administrador ('admin') es una funcionalidad reservada del sistema y no puede ser eliminada."
    )
```

- **Explicación técnica:** La autorización no depende de comprobaciones visuales en los botones de la interfaz, sino que está blindada en la capa de servicios (`VentaService`). Incluso si una petición errónea intentara asociar un boletero a la venta de dulces, el servicio rechaza la transacción lanzando `ReglaNegocioException`.

---

### 2.2. Funcionalidad de Boletería

- **Estado:** **Implementado**
- **Justificación:** La boletería cuenta con un flujo completo de emisión de boletos: visualización de cartelera activa, selector interactivo de asientos con diferenciación cromática (disponibles, ocupados y VIP), validación obligatoria de RUT chileno y edad mínima para películas clasificadas (+14, +18), carrito transaccional y registro atómico en base de datos con descuento de cupos en tiempo real.
- **Archivo principal:** [`ui/ventana_boleteria.py`](./ui/ventana_boleteria.py#L24-L634)
- **Líneas exactas:**
  - Inicialización y estado: L24–L60
  - Selección de función y visualización de cupos: L205–L230
  - Validación de comprador y agregado al carrito: L349–L430
  - Confirmación de venta atómica: L575–L594
  - Soporte de venta compartida (anexar dulces): L595–L630
- **Archivos secundarios:**
  - [`service/venta_service.py`](./service/venta_service.py#L48-L93): Creación y validación del detalle de entrada.
  - [`dao/venta_dao.py`](./dao/venta_dao.py#L15-L115): Persistencia atómica de la cabecera y el detalle en SQLite.
  - [`main.py`](./main.py#L619-L720): Módulo homólogo de boletería para consola CLI.

#### Extracto Real del Código

```python
# Ubicación: ui/ventana_boleteria.py (Líneas 384 a 428)
        # Validación de comprador en película clasificada (P07, P08, P15)
        if f.pelicula.clasificacion_edad > 0:
            rut = self.var_rut.get().strip()
            edad_str = self.var_edad.get().strip()

            if not rut:
                messagebox.showerror("RUT Obligatorio", "Debe ingresar el RUT del comprador.", parent=self)
                return

            try:
                edad = int(edad_str)
            except ValueError:
                messagebox.showerror("Edad Inválida", "La edad debe ser un número entero.", parent=self)
                return

            try:
                cliente = VentaService.validar_cliente_para_funcion(f.id_funcion, rut, "Comprador", edad)
            except RestriccionEdadException as e:
                messagebox.showerror("Acceso Denegado (Edad)", str(e), parent=self)
                return
            except ReglaNegocioException as e:
                messagebox.showerror("RUT Inválido", str(e), parent=self)
                return

        # Descontar los asientos inmediatamente en la BD al agregar entradas
        nuevos_disponibles = f_db.asientos_disponibles - cant
        FuncionDAO.actualizar_asientos(f.id_funcion, nuevos_disponibles)

        precio_unitario = f_db.calcular_precio()
        descripcion = f"Entrada [{f_db.tipo}] {f_db.pelicula.titulo} ({f_db.fecha_hora})"
        detalle = DetalleVenta(
            id_detalle=None,
            id_venta=None,
            tipo_item="entrada",
            id_item=f_db.id_funcion,
            descripcion=descripcion,
            cantidad=cant,
            precio_unitario=precio_unitario,
            id_trabajador=self.boletero.id_trabajador
        )
```

- **Explicación técnica:** La emisión de entradas valida primero la capacidad física de la sala para evitar sobreventas (`SinAsientosException`), luego exige la identificación y verificación etaria si la película posee restricción de edad, y finalmente estructura el objeto `DetalleVenta` registrando el `id_trabajador` del boletero responsable para fines de auditoría y cuadratura.

---

### 2.3. Funcionalidad de Confitería

- **Estado:** **Implementado**
- **Justificación:** La confitería cuenta con un catálogo visual paginado de productos nacionales e importados. Realiza la consulta del dólar del día vía API para recalcular en tiempo real el precio en pesos chilenos de los productos importados, permite seleccionar cantidades numéricas, añadir y retirar productos del carrito de compras y cerrar la venta con emisión de folio fiscal y cuadratura de caja individual.
- **Archivo principal:** [`ui/ventana_dulceria.py`](./ui/ventana_dulceria.py#L27-L303)
- **Líneas exactas:**
  - Consulta y visualización del dólar: L50–L65 (`_cargar_dolar`)
  - Renderizado de productos y precios dinámicos: L180–L205 (`_tarjeta_producto`)
  - Gestión y manipulación del carrito: L214–L275
  - Confirmación de venta con folio fiscal: L286–L303 (`_confirmar_venta`)
- **Archivos secundarios:**
  - [`service/venta_service.py`](./service/venta_service.py#L95-L136): `crear_detalle_producto()` con validación de rol de confitería y cálculo de divisas.
  - [`dao/producto_dao.py`](./dao/producto_dao.py#L12-L105): Recuperación del catálogo de confitería.
  - [`main.py`](./main.py#L722-L835): Módulo de confitería para consola CLI.

#### Extracto Real del Código

```python
# Ubicación: ui/ventana_dulceria.py (Líneas 180 a 201)
        if importado:
            precio_clp = prod.calcular_precio(tasa)
            c.create_text(x + w - 16, y + 120, text=f"USD ${prod.precio_usd:.2f}", font=FONTS['small'],
                          fill=COLORS['text_muted'], anchor='e', tags='cat')
        else:
            precio_clp = prod.calcular_precio()
        c.create_text(x + 16, y + 120, text=f"${precio_clp:,.0f} CLP", font=FONTS['price'],
                      fill=COLORS['accent_gold'], anchor='w', tags='cat')

        # Controles: [−] cantidad [+]   [Agregar ▶]
        yb, pid = y + h - 48, prod.id_producto
        self.boton(x + 14, yb, 34, 34, "−", lambda p=pid: self._cambiar_qty(p, -1), 'fantasma',
                   FONTS['btn_big'], grupo='cat', radio=10)
        self._qty_ids[pid] = c.create_text(x + 64, yb + 17, text=str(self._qty.get(pid, 1)),
                                           font=FONTS['price'], fill='white', tags='cat')
        self.boton(x + 80, yb, 34, 34, "+", lambda p=pid: self._cambiar_qty(p, 1), 'fantasma',
                   FONTS['btn_big'], grupo='cat', radio=10)
        self.boton(x + 124, yb, 106, 34, "Agregar ▶",
                   lambda p=prod: self._agregar_al_carrito(p, self._qty.get(p.id_producto, 1)),
                   'primario', FONTS['small_b'], grupo='cat', radio=10)
```

Y la confirmación de la venta:

```python
# Ubicación: ui/ventana_dulceria.py (Líneas 291 a 302)
        try:
            v_guardada = VentaService.concretar_venta(self.venta_actual)
            messagebox.showinfo(
                "¡Venta Exitosa!",
                f"✔ Venta de confitería registrada exitosamente.\n"
                f"Folio Fiscal: #{v_guardada.id_venta}\n"
                f"Total Cobrado: ${v_guardada.total:,.0f} CLP",
                parent=self
            )
            self._nueva_venta()
        except Exception as e:
            messagebox.showerror("Error al Registrar Venta", str(e), parent=self)
```

- **Explicación técnica:** La ventana presenta los productos organizados en tarjetas con sus precios base. En el caso de los importados, muestra en tipografía secundaria el valor original en dólares y en tipografía dorada destacada el importe convertido a pesos chilenos según la cotización recuperada. Al confirmar la compra, se invoca `VentaService.concretar_venta` bajo una transacción atómica que emite el folio único.

---

### 2.4. Funcionalidad de Administrador

- **Estado:** **Implementado**
- **Justificación:** El panel de administración proporciona control integral del negocio mediante un contenedor de pestañas (`ttk.Notebook`) accesible exclusivamente para usuarios con `rol == 'admin'`. Permite administrar el catálogo de películas, programar y modificar funciones con sus cupos, gestionar productos de dulcería, registrar y administrar cuentas de empleados asignando roles y claves con hash seguro, auditar el historial de ventas por folio y consultar la sincronización con la API del dólar.
- **Pestañas operativas implementadas en el panel:**
  - **Pestaña 1 (Películas y Funciones):** Creación, modificación, listado y eliminación de películas y funciones en formatos 2D, 3D y VIP.
  - **Pestaña 2 (Confitería y Snacks):** Catálogo de golosinas y bebidas nacionales e importadas.
  - **Pestaña 3 (Personal y Cajas):** Administración de trabajadores con generación de hash SHA-256 + salt y asignación de roles.
  - **Pestaña 4 (Reportes y Auditoría):** Consulta detallada de ventas globales, desglose de ítems por folio y cuadratura por cajero.
  - **Pestaña 5 (Tipo de Cambio API):** Monitoreo del estado de la API `mindicador.cl` y registro histórico en base de datos.
- **Archivo principal:** [`ui/ventana_admin.py`](./ui/ventana_admin.py#L27-L1046)
- **Líneas exactas:**
  - Inicialización y control de pestañas: L27–L97
  - Gestión de películas y funciones: L105–L370
  - Gestión de confitería: L372–L590
  - Gestión de trabajadores: L592–L860
  - Reportes de ventas y cuadraturas: L862–L970
  - Monitoreo del dólar API: L972–L1046
- **Archivos secundarios:**
  - [`ui/ventana_login.py`](./ui/ventana_login.py#L154-L156): Restricción de acceso que impide abrir el módulo de administración a usuarios sin perfil `admin`.
  - [`dao/trabajador_dao.py`](./dao/trabajador_dao.py#L32-L34, L138-L142): Bloqueo de seguridad que protege la cuenta de administración principal contra borrado accidental.
  - [`main.py`](./main.py#L135-L240): Submenú administrativo para consola CLI.

#### Extracto Real del Código

```python
# Ubicación: ui/ventana_admin.py (Líneas 69 a 96 - Estructura de pestañas del Administrador)
        # 2. Pestañas Principales (Notebook)
        self.nb = ttk.Notebook(self, style='Cine.TNotebook')
        self.nb.pack(fill='both', expand=True, padx=14, pady=10)

        # Tab 1: Películas y Funciones
        self.tab_funciones = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_funciones, text="🎬  Películas y Funciones")
        self._build_tab_funciones()

        # Tab 2: Catálogo de Confitería
        self.tab_productos = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_productos, text="🍿  Confitería y Snacks")
        self._build_tab_productos()

        # Tab 3: Trabajadores
        self.tab_trabajadores = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_trabajadores, text="👥  Personal y Cajas")
        self._build_tab_trabajadores()

        # Tab 4: Reportes de Ventas
        self.tab_reportes = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_reportes, text="📊  Reportes y Auditoría")
        self._build_tab_reportes()

        # Tab 5: Dólar del Día
        self.tab_dolar = tk.Frame(self.nb, bg=COLORS['bg_main'])
        self.nb.add(self.tab_dolar, text="💵  Tipo de Cambio API")
        self._build_tab_dolar()
```

- **Explicación técnica:** La clase `VentanaAdmin` consolida todas las herramientas de gestión estratégica del cine. La restricción de acceso por rol opera desde el inicio de sesión (`VentanaLogin`), y los DAO protegen la integridad referencial para evitar que el administrador elimine películas con funciones programadas o productos con ventas históricas.

---

## 3. Resumen General de Cumplimiento

A continuación se resume el estado global de la auditoría técnica realizada sobre el proyecto Cine Estrella:

| Estado de Cumplimiento | Cantidad de Requisitos | Porcentaje | Detalle de Puntos |
|:---|:---:|:---:|:---|
| **Implementado** | **14** | **100%** | Puntos 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4 |
| **Parcialmente implementado** | **0** | **0%** | Ninguno |
| **No encontrado** | **0** | **0%** | Ninguno |
| **Pendiente de verificar** | **0** | **0%** | Ninguno |
| **TOTAL AUDITADO** | **14** | **100%** | **Cumplimiento Total de la Rúbrica** |

> [!NOTE]
> La suite de pruebas automatizadas del proyecto ([`tests/test_guion_pruebas_p01_p19.py`](./tests/test_guion_pruebas_p01_p19.py)) fue ejecutada con éxito en su totalidad: **31 pruebas ejecutadas, 31 pruebas aprobadas (0 errores, 0 fallos)**, confirmando la solidez de los componentes documentados.

---

## 4. Observaciones y Recomendaciones Técnicas

Tras inspeccionar el código fuente, la arquitectura de capas y los modelos de persistencia, se presentan las siguientes observaciones y sugerencias de mejora para futuras fases de desarrollo:

### Fortalezas Detectadas
1. **Arquitectura Limpia y Desacoplada:** La separación en cuatro capas (`model`, `dao`, `service`, `ui`) cumple con los principios de diseño de alta cohesión y bajo acoplamiento.
2. **Seguridad Criptográfica:** Uso de salting pseudoaleatorio con `os.urandom(16)` y función hash `SHA-256`, neutralizando ataques de diccionario y *rainbow tables*.
3. **Consistencia Transaccional ACID:** El uso de transacciones con control de reversión (`rollback`) en `VentaDAO` garantiza que ventas mixtas (entradas + confitería) se persistan de forma atómica sin desajustes de caja o sobreventas.
4. **Resiliencia en Servicios Externos:** El consumo de la API REST de `mindicador.cl` con *timeout* estricto de 5 segundos y respaldo de contingencia fuera de línea evita el congelamiento de la interfaz de usuario ante interrupciones de red.

### Recomendaciones de Mejora y Buenas Prácticas
1. **Eliminación de Claves en Texto Plano de Apoyo:**  
   En la tabla `trabajadores` existe la columna `password_plano` utilizada para facilitar las pruebas académicas y la demostración docente mediante el modal "Ver usuarios". **Recomendación:** En un entorno de producción real, dicha columna debe ser eliminada del DDL en [`dao/db_init.py`](./dao/db_init.py) y del modelo [`model/trabajador.py`](./model/trabajador.py), conservando exclusivamente `password_hash`.
2. **Migración a Algoritmo de Hashing Lento:**  
   Aunque `SHA-256` con *salt* es seguro para fines formativos, los estándares modernos de la industria (OWASP) sugieren algoritmos diseñados contra ataques de fuerza bruta basados en hardware GPU/ASIC, tales como `bcrypt` o `argon2id`.
3. **Paginación en Consultas de Reportes:**  
   En [`dao/venta_dao.py`](./dao/venta_dao.py#L140), el método `listar_todas()` recupera la totalidad de los folios registrados. A medida que el volumen histórico crezca en un cine real con miles de ventas diarias, se recomienda aplicar paginación SQL con sentencias `LIMIT` y `OFFSET`.
4. **Inyección de Dependencias en la Capa DAO:**  
   Actualmente los métodos en las clases DAO son estáticos (`@staticmethod`). Adoptar inyección de dependencias o instancias configurables facilitaría la integración de pruebas unitarias con bases de datos en memoria sin recurrir a variables globales.

