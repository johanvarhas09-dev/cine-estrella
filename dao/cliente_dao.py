"""
DAO para gestión de Clientes en base de datos.
"""
from dao.conexion import obtener_conexion
from model.cliente import Cliente


class ClienteDAO:
    @staticmethod
    def guardar_o_actualizar(cliente: Cliente) -> Cliente:
        """
        [PERSISTENCIA SEGURA: UPSERT DE CLIENTE]
        Inserta un nuevo cliente o actualiza su nombre y edad si el RUT ya existe (ON CONFLICT).
        Utiliza marcadores de posición '?' para prevenir inyección SQL.
        """
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO clientes (rut, nombre, edad)
            VALUES (?, ?, ?)
            ON CONFLICT(rut) DO UPDATE SET
                nombre = excluded.nombre,
                edad = excluded.edad
            """,
            (cliente.rut, cliente.nombre, cliente.edad)
        )
        conn.commit()
        conn.close()
        return cliente

    @staticmethod
    def obtener_por_rut(rut: str) -> Cliente | None:
        """
        [BÚSQUEDA PARAMETRIZADA POR RUT]
        Normaliza el RUT consultado a formato canónico antes de buscar en la BD.
        Retorna la entidad de dominio Cliente o None si no existe.
        """
        cuerpo, dv = Cliente.limpiar_rut(rut)
        rut_formateado = f"{cuerpo}-{dv}"
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT rut, nombre, edad FROM clientes WHERE rut = ?", (rut_formateado,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Cliente(rut=row["rut"], nombre=row["nombre"], edad=row["edad"])
        return None
