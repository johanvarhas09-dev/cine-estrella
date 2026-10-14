"""
Entidad Pelicula: Representa una obra cinematográfica en el catálogo del cine.
Permite validar si un espectador tiene edad suficiente para ingresar (Caso P15).
"""


class Pelicula:
    def __init__(self, id_pelicula: int | None, titulo: str, clasificacion_edad: int, duracion_minutos: int = 90):
        self._id_pelicula = None
        self._titulo = None
        self._clasificacion_edad = None
        self._duracion_minutos = None

        self.id_pelicula = id_pelicula
        self.titulo = titulo
        self.clasificacion_edad = clasificacion_edad
        self.duracion_minutos = duracion_minutos

    @property
    def id_pelicula(self) -> int | None:
        return self._id_pelicula

    @id_pelicula.setter
    def id_pelicula(self, valor: int | None):
        if valor is not None:
            if not isinstance(valor, int) or valor <= 0:
                raise ValueError("El ID de la película debe ser un entero positivo.")
        self._id_pelicula = valor

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 1:
            raise ValueError("El título de la película no puede estar vacío.")
        self._titulo = valor.strip()

    @property
    def clasificacion_edad(self) -> int:
        return self._clasificacion_edad

    @clasificacion_edad.setter
    def clasificacion_edad(self, valor: int):
        """
        [VALIDACIÓN DE CLASIFICACIÓN ETARIA]
        Asigna la edad mínima requerida por la película:
        - 0: Todo Espectador (TE)
        - 14: Mayores de 14 años (+14)
        - 18: Mayores de 18 años (+18 adultos)
        """
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("La clasificación de edad debe ser un número entero (ej: 0, 7, 14, 18).")
        if val_int < 0:
            raise ValueError("La clasificación de edad no puede ser negativa.")
        self._clasificacion_edad = val_int

    @property
    def duracion_minutos(self) -> int:
        return self._duracion_minutos

    @duracion_minutos.setter
    def duracion_minutos(self, valor: int):
        try:
            val_int = int(valor)
        except (ValueError, TypeError):
            raise ValueError("La duración debe ser un número entero de minutos.")
        if val_int <= 0:
            raise ValueError("La duración debe ser mayor a cero minutos.")
        self._duracion_minutos = val_int

    def es_apta(self, edad: int) -> bool:
        """
        [FUNCIONALIDAD: RESTRICCIÓN DE EDAD - Caso P15]
        Evalúa si la edad del cliente es mayor o igual a la clasificación de la película.
        Si la película es TE (0), cualquier edad es apta.
        Si es +18 y el cliente tiene 15 años, retorna False para que el servicio lance RestriccionEdadException.
        """
        return edad >= self._clasificacion_edad

    def __str__(self) -> str:
        clasif = f"+{self._clasificacion_edad}" if self._clasificacion_edad > 0 else "TE (Todo Espectador)"
        return f"{self._titulo} ({clasif}, {self._duracion_minutos} min)"
