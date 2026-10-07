from model.edad_no_permitida_error import EdadNoPermitidaError
from model.validacion import entero_en_rango, id_valido, texto_no_vacio


class Pelicula:
    """Obra que exhibe el cine. Su edad mínima decide si se puede vender una entrada."""

    def __init__(self, titulo: str, duracion_min: int, edad_minima: int, id: int | None = None):
        self.id = id
        self.titulo = titulo
        self.duracion_min = duracion_min
        self.edad_minima = edad_minima

    @property
    def id(self) -> int | None:
        return self.__id

    @id.setter
    def id(self, valor: int | None) -> None:
        self.__id = id_valido(valor)

    @property
    def titulo(self) -> str:
        return self.__titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self.__titulo = texto_no_vacio(valor, 80, "El título")

    @property
    def duracion_min(self) -> int:
        return self.__duracion_min

    @duracion_min.setter
    def duracion_min(self, valor: int) -> None:
        self.__duracion_min = entero_en_rango(valor, 1, 400, "La duración en minutos")

    @property
    def edad_minima(self) -> int:
        return self.__edad_minima

    @edad_minima.setter
    def edad_minima(self, valor: int) -> None:
        # 0 significa "todo espectador"; 18 es la clasificación más alta
        self.__edad_minima = entero_en_rango(valor, 0, 18, "La edad mínima")

    def es_restringida(self) -> bool:
        return self.__edad_minima > 0

    def permite_edad(self, edad: int) -> bool:
        return edad >= self.__edad_minima

    def verificar_edad(self, edad: int) -> None:
        """Lanza EdadNoPermitidaError si la edad no alcanza la edad mínima de la película."""
        if not self.permite_edad(edad):
            raise EdadNoPermitidaError(edad, self.__edad_minima)
