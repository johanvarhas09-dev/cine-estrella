# 🎬 CINE ESTRELLA — SISTEMA INTEGRAL DE GESTIÓN (VERSIÓN 4.0 GUI + CLI)

**Asignatura:** Programación Orientada a Objetos Segura  
**Institución:** INACAP — Sede Puente Alto (2026)  
**Docente:** Michael Alexis Arjel Mayerovich  
**Integrantes del Equipo:**
* Fernando Durán
* Johan Vargas

**Caso de Negocio:** 11 – CINE ESTRELLA

---

## 📋 Tabla de Contenidos

1. [Descripción del Negocio](#descripción-del-negocio)
2. [Documentación y Manuales del Sistema](#-documentación-y-manuales-del-sistema)
3. [Versiones Disponibles](#versiones-disponibles)
4. [Instalación y Ejecución](#instalación-y-ejecución)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Funcionalidades](#funcionalidades)
7. [Seguridad](#seguridad)
8. [Pruebas](#pruebas)
9. [Historial de Cambios](#historial-de-cambios)

---

## 📚 Documentación y Manuales del Sistema

El proyecto cuenta con documentación técnica formal y manuales de operación organizados en el directorio [`docs/`](docs/):

* **[Manual de Usuario por Funciones](docs/manual_usuario.md):** Guía paso a paso para Administrador, Boletero y Encargado de Dulcería, con instrucciones de inicio, venta, contingencias y resolución de incidentes.
* **[Manual Técnico de Arquitectura y Código](docs/manual_tecnico_codigo.md):** Documento de arquitectura de software, patrones de diseño, modelos relacionales DDL, diagramas de clases, algoritmos clave y configuración de CI.
* **[Catálogo y Trazabilidad de Comentarios en el Código](docs/referencia_comentarios_codigo.md):** Mapeo de comentarios explicativos archivo por archivo, vinculando cada requerimiento del negocio y caso de prueba (P01–P19) con el código fuente.

---

## Descripción del Negocio

El negocio **CINE ESTRELLA** requiere un sistema informático de escritorio con interfaz gráfica moderna y temática cinematográfica (Tkinter) para la administración y venta presencial de entradas y confitería.

### Funcionalidades Clave

- **Boletería:** Venta de entradas para funciones de cine
- **Confitería:** Venta de snacks y bebidas
- **Ventas Combinadas:** Un cliente puede comprar entradas y confites en la misma transacción
- **Control de Asientos:** Stock dinámico por función
- **Validación de Edad:** Para películas clasificadas con validación de RUT Módulo 11
- **Cotización en Dólares:** Cálculo automático USD → CLP para productos importados

---

## Versiones Disponibles

El repositorio contiene **5 ramas ejecutables**, cada una representando una fase de desarrollo:

### 📌 Matriz de Versiones

| Rama | Estado | Características | Cómo Ejecutar |
|------|--------|-----------------|---------------|
| **main** | Producción (Fase 1) | Versión inicial básica, CLI interactivo | `git checkout main && python main.py --consola` |
| **version1** | Estable | Copia de main, versión de referencia | `git checkout version1 && python main.py --consola` |
| **version2** | Desarrollo Avanzado | CLI mejorado + servicios + API dólar + pruebas | `git checkout version2 && python main.py --consola` |
| **version3** | **ACTUAL (GUI)** | GUI Tkinter + reportes por folio + todas las mejoras | `git checkout version3 && python main.py` |
| **endesarrollo** | Experimental | Rama de trabajo (sincronizada con version2) | `git checkout endesarrollo && python main.py --consola` |

---

## Instalación y Ejecución

### Prerrequisitos

- Python 3.10 o superior (compatible con 3.14)
- pip (gestor de paquetes de Python)

### Paso 1: Clonar el Repositorio

```powershell
git clone https://github.com/durfe01/CINE.git
cd CINE
```

### Paso 2: Instalar Dependencias

```powershell
python -m pip install -r requirements.txt
```

### Paso 3: Elegir y Ejecutar una Versión

#### Versión 3.0 (GUI Tkinter — **RECOMENDADA**)
```powershell
git checkout version3
python main.py
```
O en Windows:
```powershell
iniciar_cine.bat
```

#### Versión 2.0 (CLI Avanzado)
```powershell
git checkout version2
python main.py --consola
```

#### Versión 1.0 (CLI Básico)
```powershell
git checkout version1
python main.py --consola
```

#### Main (Versión Inicial)
```powershell
git checkout main
python main.py --consola
```

### Credenciales de Demostración

| Rol | Usuario | Contraseña | Acceso |
|-----|---------|-----------|--------|
| Administrador | `admin` | `admin` | Gestión completa |
| Boletero | `boletero1` | `1234` | Venta de entradas |
| Dulcería | `dulceria1` | `1234` | Venta de confites |

---

## Estructura del Proyecto

```
CINE/
├── README.md                   # Este archivo (documentación)
├── main.py                     # Punto de entrada (GUI o CLI según rama)
├── requirements.txt            # Dependencias (requests)
├── iniciar_cine.bat           # Script de inicio para Windows
│
├── model/                      # CAPA DE DOMINIO
│   ├── cliente.py             # Validación RUT Módulo 11
│   ├── pelicula.py            # Clasificación de edad
│   ├── funcion.py             # Clase base abstracta
│   ├── funcion_2d.py          # Polimorfismo: tipo 2D
│   ├── funcion_3d.py          # Polimorfismo: tipo 3D
│   ├── funcion_vip.py         # Polimorfismo: tipo VIP (máx 30 asientos)
│   ├── producto.py            # Clase base de productos
│   ├── producto_nacional.py   # Precio fijo en CLP
│   ├── producto_importado.py  # Precio dinámico USD
│   ├── trabajador.py          # Hash SHA-256 + salt
│   ├── boletero.py            # Subclase: venta de entradas
│   ├── encargado_dulceria.py  # Subclase: venta de confites
│   ├── venta.py               # Cabecera de venta
│   ├── detalle_venta.py       # Línea de detalle con trabajador
│   └── excepciones.py         # Excepciones de negocio
│
├── dao/                        # CAPA DE ACCESO A DATOS
│   ├── conexion.py            # Contexto SQLite + row_factory
│   ├── db_init.py             # DDL + migración de esquema
│   ├── cliente_dao.py         # CRUD clientes
│   ├── pelicula_dao.py        # CRUD películas
│   ├── funcion_dao.py         # CRUD funciones
│   ├── producto_dao.py        # CRUD productos
│   ├── trabajador_dao.py      # CRUD + autenticación
│   └── venta_dao.py           # Transacciones atómicas
│
├── service/                    # CAPA DE LÓGICA DE NEGOCIO
│   ├── auth_service.py        # Autenticación y sesión
│   ├── tipo_cambio_service.py # API mindicador.cl (USD)
│   └── venta_service.py       # Orquestación de ventas
│
├── ui/                         # CAPA DE PRESENTACIÓN (Tkinter Moderno)
│   ├── ventana_login.py       # Pantalla de autenticación y selección de rol
│   ├── ventana_principal.py   # Dashboard principal
│   ├── ventana_admin.py       # Panel administrativo y auditoría
│   ├── ventana_boleteria.py   # Interfaz de boletería y mapa de asientos
│   ├── ventana_dulceria.py    # Interfaz de confitería y dólar en tiempo real
│   ├── ventana_cuadratura.py  # Cuadraturas por trabajador
│   ├── base.py, componentes.py# Widgets y base para ventanas
│   ├── fondos.py              # Cargador dinámico de fondos Pillow
│   └── estilos.py             # Tema corporativo (colores, fuentes)
│
├── fondos/                     # FONDOS VISUALES TEMÁTICOS (.jpg)
│   ├── fondo_principal.jpg, fondo_boleteria.jpg, fondo_confiteria.jpg, fondo_admin.jpg
│
├── tests/                      # SUITE DE PRUEBAS AUTOMATIZADAS (31/31 OK)
│   ├── test_models.py         # Herencia, polimorfismo, RUT
│   ├── test_dao.py            # CRUD, transacciones, rollback
│   ├── test_services.py       # Mocks de API externa
│   └── test_guion_pruebas_p01_p19.py # Aceptación funcional
│
├── docs/                       # MANUALES Y DOCUMENTACIÓN TÉCNICA
│   ├── manual_usuario.md      # Manual de usuario organizado por funciones
│   ├── manual_tecnico_codigo.md # Manual técnico de arquitectura y clases
│   └── referencia_comentarios_codigo.md # Matriz de comentarios en el código
│
└── .github/workflows/
    └── tests.yml              # CI/CD: Pruebas automáticas en GitHub
```

---

## Historial de Cambios

### 📍 Línea de Tiempo de Desarrollo

```
28-Sep-2026 ── Initial Commit (Repositorio vacío)
    │
04-Oct-2026 ── Primer Commit: Proyecto CINE (Versión 1 - CLI Básico)
    │          • Modelo de dominio (cliente, película, función, producto)
    │          • DAO con SQLite
    │          • Menús de consola interactivos
    │          • Validación de edad y RUT
    │
05-Oct-2026 ── Version 2 (CLI Avanzado) — Rama "endesarrollo"
    │          • feat: Modelo dominio + DAO + pruebas unitarias (02:07)
    │          • feat: Servicios de negocio + API dólar + CLI (02:15)
    │          • docs: README formal + manual de trazabilidad (02:32)
    │          • test: Suite de aceptación P01-P19 (02:37)
    │          • Se crea proyecto CINE (112e128) (02:48)
    │          ✓ 16/16 pruebas exitosas
    │
05-Oct-2026 ── Version 3 (GUI Tkinter) — Rama "version3" ⭐ ACTUAL
               • feat: GUI corporativa Tkinter (78c6dca) (04:12)
               • ci: Workflow GitHub Actions (506fb5f) (04:15)
               • feat: 14 modificaciones solicitadas (1f0463f) (05:27)
               • Se crea versión 3 (ff6a2d3) (05:34)
               • fix: Admin no eliminable + reportes por folio (a6d7c02) (06:06)
               • fix: Eliminar acceso rápido + ocultar passwords (c30d84b) (06:42)
               • docs: Actualizar README con historial versiones (2ee3cff) (15:39) ← AQUÍ ESTAMOS
```

### 🔄 Evolución de Características por Versión

| Característica | main | version1 | version2 | endesarrollo | version3 |
|---|:---:|:---:|:---:|:---:|:---:|
| Modelo de Dominio | ✓ | ✓ | ✓ | ✓ | ✓ |
| DAO + SQLite | ✓ | ✓ | ✓ | ✓ | ✓ |
| CLI Interactivo | ✓ | ✓ | ✓ | ✓ | ✗ |
| Interfaz Gráfica GUI | ✗ | ✗ | ✗ | ✗ | **✓** |
| Servicios (Auth, API) | ✗ | ✗ | ✓ | ✓ | ✓ |
| API Mindicador (USD) | ✗ | ✗ | ✓ | ✓ | ✓ |
| Pruebas Unitarias | ✗ | ✗ | ✓ | ✓ | ✓ |
| Pruebas de Aceptación | ✗ | ✗ | ✓ | ✓ | ✓ |
| Reportes por Folio | ✗ | ✗ | ✗ | ✗ | **✓** |
| Admin No Eliminable | ✗ | ✗ | ✗ | ✗ | **✓** |
| Ocultar Passwords | ✗ | ✗ | ✗ | ✗ | **✓** |
| Descuento Asientos Real | ✗ | ✗ | ✗ | ✗ | **✓** |
| CI/CD (GitHub Actions) | ✗ | ✗ | ✗ | ✗ | **✓** |

---

## Funcionalidades

### 👨‍💼 Rol: Administrador

- **Gestión de Películas:** CRUD + validación de clasificación de edad
- **Gestión de Funciones:** Crear funciones 2D, 3D o VIP (con cálculo polimórfico de precios)
- **Gestión de Productos:** Registrar artículos nacionales (CLP) e importados (USD)
- **Gestión de Trabajadores:** Crear y modificar usuarios con roles específicos
- **Reportes de Ventas:** Listado por folio con detalle automático de líneas
- **Cuadratura General:** Resumen de recaudación por trabajador
- **Consulta de Dólar:** Valor oficial en tiempo real desde mindicador.cl

### 🎫 Rol: Boletero

- **Mapa de Ocupación:** Barra ASCII con porcentaje de asientos vendidos
- **Venta de Entradas:** Con validación de edad (RUT Módulo 11) para películas clasificadas
- **Venta Compartida:** Combinar entradas + confites en una misma transacción
- **Cuadratura de Caja:** Total recaudado + cantidad de entradas emitidas

### 🍿 Rol: Encargado de Dulcería

- **Catálogo de Confitería:** Con conversión automática USD → CLP
- **Venta de Productos:** Múltiples artículos en una transacción
- **Cuadratura de Caja:** Total recaudado + cantidad de productos vendidos

---

## Seguridad

1. **Prevención de Inyección SQL:** Consultas parametrizadas en todas las DAO
2. **Hash de Contraseñas:** SHA-256 + salt criptográfico aleatorio
3. **Encapsulamiento Estricto:** Atributos privados con `@property`
4. **Integridad Referencial:** `PRAGMA foreign_keys = ON` en SQLite
5. **Transacciones Atómicas:** Ventas con ACID compliance
6. **Manejo de Errores:** Excepciones sin crash del sistema

---

## Pruebas

### Ejecución de Pruebas Automatizadas

```powershell
python -m unittest discover tests
```

**Resultado esperado:** 16/16 pruebas exitosas

### Cobertura

- Herencia y polimorfismo en funciones
- Validación de RUT (Módulo 11)
- CRUD de entidades
- Transacciones y rollback
- Integración con API externa (mocked)
- Aceptación funcional (guión P01–P19)

---

## Requisitos de Sistema

- **Lenguaje:** Python 3.10+
- **GUI:** Tkinter (incluido en Python)
- **Base de Datos:** SQLite 3 (incluido en Python)
- **Dependencia Externa:** `requests>=2.28.0`

---

## Próximas Mejoras

- [ ] Integración con sistema de pagos (WebPay, POS)
- [ ] Reportes en PDF con QR de folio
- [ ] Sincronización en la nube
- [ ] Aplicación móvil para consultas
- [ ] Multi-idioma (ES/EN)

---

## Contacto y Soporte

**Institución:** INACAP — Sede Puente Alto  
**Docente:** Michael Alexis Arjel Mayerovich  
**Asignatura:** Programación Orientada a Objetos Segura (2026)

---

**Última actualización:** 5 de Octubre de 2026
