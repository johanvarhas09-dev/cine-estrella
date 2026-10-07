# Cine Estrella: sistema de venta de entradas y dulcería

Evaluación Sumativa N°2 · Programación Orientada a Objeto Seguro (TI3V21) · Sección 114-2A-F2 · INACAP Puente Alto

| | |
|---|---|
| **Negocio** | 11 - Cine |
| **Integrantes** | Fernando A. Durán Leiva · Johan Patrichs Vargas Catalán |
| **Docente** | Michael Arjel |

El sistema administra la venta de entradas y de productos de dulcería de un cine. Una misma venta junta
entradas (las vende el boletero) y productos (los vende el encargado de dulcería, en su propia caja).
Antes de vender una entrada se revisa que la función tenga asientos y que el cliente tenga la edad mínima
de la película. Los productos importados se cotizan con el dólar del día, que se obtiene de la API pública
de [mindicador.cl](https://mindicador.cl).

---

## 1. Instalación y ejecución

Requisitos: **Python 3.10 o superior** y conexión a internet (solo para el dólar del día).

```bash
git clone https://github.com/johanvarhas09-dev/cine-estrella.git
cd cine-estrella
python -m venv venv
venv\Scripts\activate            # Windows (en Linux o macOS: source venv/bin/activate)
pip install -r requirements.txt
python main.py
```

- Al iniciar, el programa **crea la base de datos `cine.db` y sus tablas si no existen**.
- Si la base está vacía, ofrece cargar **datos de ejemplo** para probar el programa: 3 películas, 3 funciones
  (2D, 3D y VIP con cupo de 3 asientos), 4 productos (2 importados), 1 boletero, 1 encargado de dulcería y
  2 clientes (`11.111.111-1`, 25 años, y `22.222.222-2`, 15 años).
- La base de datos no se sube al repositorio (`.gitignore`). Para partir de cero basta con borrar `cine.db`.

## 2. Estructura del proyecto

```
cine-estrella/
├── main.py              Menús de consola: CRUD, ventas, cotización y simulación de caída de la API
├── validaciones.py      Lectura validada de lo que escribe el usuario (tipo, formato y rango)
├── datos_ejemplo.py     Datos de ejemplo para probar el programa
├── requirements.txt
├── model/               Clases del diagrama, una por archivo (sin SQL)
│   ├── cliente.py, venta.py, detalle_venta.py, item_venta.py, entrada.py, producto_dulceria.py
│   ├── indicador_dolar.py, pelicula.py, funcion.py, funcion_2d.py, funcion_3d.py, funcion_vip.py
│   ├── trabajador.py, boletero.py, encargado_dulceria.py
│   ├── sin_asientos_error.py, edad_no_permitida_error.py   (excepciones de las reglas)
│   └── validacion.py    Funciones de validación que reutilizan los setters
├── dao/                 Persistencia SQLite, separada del modelo
│   ├── conexion.py, dao.py (clase base)
│   └── cliente_dao.py, pelicula_dao.py, funcion_dao.py, producto_dao.py, trabajador_dao.py, venta_dao.py
├── servicios/
│   └── mindicador.py    Consulta del dólar con requests y tiempo máximo de espera
└── docs/                Diagrama de clases corregido (.drawio y .png) e informe corregido de la ES1 (.pdf)
```

## 3. Requisitos de la ficha y dónde se cumplen

| Requisito | Implementación |
|---|---|
| Tres subtipos con un método que se comporta distinto | `Funcion` es abstracta. `Funcion2D`, `Funcion3D` y `FuncionVIP` heredan con `super().__init__()` y sobrescriben `calcular_precio()`. `FuncionVIP` también sobrescribe `asientos_disponibles()` (cupo VIP). El programa nunca pregunta por el tipo para calcular el precio. |
| Al menos un dato con validación | El RUT del cliente se valida en el setter de `Cliente` (formato y dígito verificador, módulo 11). Todos los atributos son privados y se exponen con `@property`; los setters validan tipo y rango. |
| Transacción con líneas de detalle | `Venta` se compone de una o más `DetalleVenta`. Cada línea guarda un `ItemVenta` (una `Entrada` o un `ProductoDulceria`), la cantidad, el precio unitario del momento y el trabajador que la vendió. `VentaDAO.insertar()` guarda la venta y sus líneas en una sola transacción. |
| Dos reglas que impiden una operación | `Funcion.reservar_asiento()` lanza `SinAsientosError` y `Pelicula.verificar_edad()` lanza `EdadNoPermitidaError`. Ambas se capturan con su propio `except` en `main.py`; el programa informa y sigue. |
| Precio que depende de un indicador externo | `ProductoDulceria.calcular_precio()` usa el `IndicadorDolar` del día si el producto es importado. El valor viene de `ServicioMindicador.obtener_dolar()` (`requests`, `timeout`). |
| Dos trabajadores con permisos distintos (ES1) | `Boletero` solo puede `vender_entrada()` y `EncargadoDulceria` solo `vender_producto()`. `tiene_permiso()` es polimórfico. |

**CRUD completo** (crear, listar, buscar, modificar y eliminar) de clientes, películas, funciones,
productos de dulcería y trabajadores. Las ventas se crean y se consultan, pero no se modifican ni se anulan:
el cliente lo pidió así (respuesta 7 del Anexo 3 del informe de la ES1).

## 4. Modelo: versión corregida del diagrama de la ES1

El código sigue el diagrama corregido que está en [`docs/diagrama_clases.png`](docs/diagrama_clases.png)
(editable en [`docs/diagrama_clases.drawio`](docs/diagrama_clases.drawio)). El informe corregido de la ES1, con la
explicación de cada clase y la justificación de cada relación, está en
[`docs/ES1_114-2A-F2_Cine_corregido.pdf`](docs/ES1_114-2A-F2_Cine_corregido.pdf).
Respecto de la entrega original de la ES1 se corrigió lo que indicó el docente:

- `Funcion` ya no usa `tipo_formato: str`: ahora hay herencia real (`Funcion2D`, `Funcion3D`, `FuncionVIP`) y polimorfismo.
- Se agregó `DetalleVenta` (composición `Venta 1 ◆— 1..* DetalleVenta`) y la clase abstracta `ItemVenta`.
- Se agregó `Cliente` con la validación del RUT.
- Se quitaron los objetos (`Producto_1`, `Pelicula_2`...): el diagrama es solo de clases.
- `Entrada—Funcion` y `Funcion—Pelicula` son agregaciones con línea continua y multiplicidad en ambos extremos.
- Se agregaron las dos excepciones de las reglas del negocio.

## 5. Decisiones de seguridad

### Inyección SQL
Todas las consultas usan parámetros `?`. Ningún dato del usuario se concatena ni se formatea dentro del SQL:
el texto de la consulta es siempre fijo y los valores viajan aparte.

```python
# dao/cliente_dao.py
self.cursor.execute("SELECT rut, nombre, edad FROM cliente WHERE rut = ?", (rut,))
```

Si alguien escribe `' OR '1'='1` como RUT, la validación lo rechaza; y aunque llegara al DAO, SQLite lo
trataría como un texto que se compara con la columna `rut`, nunca como parte de la consulta.

### Validación de entradas, en tres capas
1. **Antes de usar el dato** (`validaciones.py`): cada lectura revisa tipo (número entero, decimal, fecha),
   formato (RUT, `dd-mm-aaaa hh:mm`, texto imprimible) y rango (edad 0-120, caja 1-20, precio, cantidad...).
   Si el dato no sirve se muestra el motivo y se vuelve a preguntar; el programa no se cae.
2. **En el modelo**: los atributos son privados y cada setter vuelve a validar. El RUT se valida en
   `Cliente.rut` (setter) con `validar_rut()`, que calcula el dígito verificador con módulo 11. Así, ningún
   objeto puede quedar con datos inválidos, venga de donde venga el dato.
3. **En la base de datos**: claves foráneas activadas (`PRAGMA foreign_keys = ON`) y restricciones `CHECK`
   (por ejemplo, `asientos_vendidos` nunca supera `asientos_totales`). Por eso no se puede borrar una película
   con funciones ni una función con entradas vendidas.

### Transacciones
La venta, sus líneas y la actualización de asientos se guardan dentro de `with self.conexion:`. Si algo
falla a mitad de camino, SQLite deshace todo (rollback): nunca queda una venta sin sus líneas.

### Manejo de errores
- Las reglas del negocio tienen excepción propia (`SinAsientosError`, `EdadNoPermitidaError`) y se capturan
  por separado. No hay ningún `except Exception` genérico que oculte errores.
- La API tiene su propia excepción (`IndicadorNoDisponibleError`) y se distingue cada falla: tiempo de espera
  agotado, sin conexión, error HTTP y respuesta con formato inesperado.
- Si la API no responde, el programa lo informa y sigue: los productos nacionales se siguen vendiendo y los
  importados quedan bloqueados hasta que la API responda. La opción 9 del menú permite comprobarlo sin
  desconectar internet: apunta la consulta a una dirección que nunca contesta, con 3 segundos de espera.
- Si el usuario cierra la entrada (Ctrl+C), el programa cierra la base de datos de forma ordenada.

## 6. Uso de inteligencia artificial

Usamos **Claude (Anthropic)** como asistente para revisar el diagrama corregido, proponer la estructura en
capas (`model/`, `dao/`, `servicios/`) y generar el código base del proyecto. Cada propuesta la revisamos y la
probamos con el programa funcionando. Estos son ejemplos concretos de lo que adoptamos, modificamos o
descartamos, con su razón técnica:

**1. Modificado: tiempo máximo de espera de la API (5 s → 10 s).**
La primera versión del servicio usaba `timeout=5`, igual que el ejemplo de clases. Al probarlo con la API real,
una consulta tardó más de 5 segundos y el programa informó una caída que no existía (al reintentar, respondió
bien). Lo subimos a 10 segundos. Para demostrar la caída se usa una dirección que nunca responde, con 3 segundos,
para no hacer esperar.

```python
def __init__(self, url_base: str = URL_BASE, timeout: float = 10):
```

**2. Modificado: consultas armadas con f-string.**
Una versión de `FuncionDAO` armaba el `SELECT` con un f-string que insertaba una lista fija de columnas:

```python
# Antes
self.cursor.execute(f"SELECT {COLUMNAS} FROM funcion f JOIN pelicula p ON p.id = f.pelicula_id "
                    "WHERE f.id = ?", (id,))
# Después
self.cursor.execute(SQL_BUSCAR, (id,))
```

No era inyectable, porque `COLUMNAS` no contiene datos del usuario, pero dejaba una consulta armada con texto,
un patrón fácil de copiar mal en otra parte. La reemplazamos por consultas completas y constantes
(`SQL_BUSCAR`, `SQL_LISTAR`). Así ningún `execute()` del proyecto usa f-strings ni concatenación.

**3. Modificado: dónde se sobrescribe el cupo VIP.**
La propuesta inicial sobrescribía `hay_asientos()` en `FuncionVIP`. Para mostrar cuántos asientos quedan habría
sido necesario preguntar `if isinstance(funcion, FuncionVIP)` en el menú, que es el "if sobre el tipo" que
reemplaza al polimorfismo. Lo cambiamos: `FuncionVIP` sobrescribe `asientos_disponibles()` y `hay_asientos()`
queda una sola vez en `Funcion`.

**4. Adoptado: manejo separado de cada falla de la API.**
El ejemplo de clases leía `respuesta.json()["serie"][0]["valor"]` y capturaba los problemas en `main.py` con
`except Exception`. La IA propuso revisar el código HTTP con `raise_for_status()` y capturar por separado
`Timeout`, `ConnectionError`, `HTTPError` y los errores de formato, convirtiéndolos en
`IndicadorNoDisponibleError`. Lo adoptamos porque un `except` genérico oculta errores de programación y no dice
qué falló. Además, `IndicadorDolar` valida el valor recibido (un dólar en 0 o negativo se rechaza).

**5. Descartado: usar el último dólar conocido cuando la API falla.**
Se evaluó guardar el último valor obtenido y usarlo si la API no responde. Lo descartamos: vendería productos
con un dólar que no es el del día, que es lo que pidió el cliente. Preferimos informar la falla y bloquear
solo los productos importados; los nacionales se siguen vendiendo.
