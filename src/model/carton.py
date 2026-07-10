"""Modelo del carton para la Loteria Mexicana."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable, List, Optional, Sequence, Set, Tuple

from model.carta import Carta


@dataclass(slots=True)
class CasillaCarton:
    """Representa una casilla individual del carton."""

    carta: Carta
    marcada: bool = False

    def marcar(self) -> bool:
        """Marca la casilla si aun no lo estaba."""

        if self.marcada:
            return False
        self.marcada = True
        return True

    def desmarcar(self) -> None:
        """Elimina la marca de la casilla."""

        self.marcada = False


class Carton:
    """Representa un carton de 4x4 casillas."""

    FILAS = 4
    COLUMNAS = 4
    CASILLAS_TOTALES = FILAS * COLUMNAS

    def __init__(self, cartas: Sequence[Carta]) -> None:
        if len(cartas) != self.CASILLAS_TOTALES:
            raise ValueError(
                f"El carton debe tener {self.CASILLAS_TOTALES} cartas, "
                f"recibio {len(cartas)}"
            )

        ids = [carta.id for carta in cartas]
        if len(set(ids)) != len(ids):
            raise ValueError("El carton no puede contener cartas repetidas")

        self._casillas: List[CasillaCarton] = [CasillaCarton(carta) for carta in cartas]

    @classmethod
    def generar_aleatorio(
        cls,
        mazo_cartas: Sequence[Carta],
        rng: Optional[random.Random] = None,
    ) -> "Carton":
        """Genera un carton aleatorio con 16 cartas unicas."""

        generador = rng or random
        cartas_seleccionadas = generador.sample(list(mazo_cartas), cls.CASILLAS_TOTALES)
        return cls(cartas_seleccionadas)

    def obtener_casilla(self, fila: int, columna: int) -> Optional[CasillaCarton]:
        """Obtiene una casilla por coordenadas."""

        if not (0 <= fila < self.FILAS and 0 <= columna < self.COLUMNAS):
            return None

        indice = fila * self.COLUMNAS + columna
        return self._casillas[indice]

    def obtener_casilla_por_indice(self, indice: int) -> Optional[CasillaCarton]:
        """Obtiene una casilla por su indice lineal."""

        if not (0 <= indice < len(self._casillas)):
            return None
        return self._casillas[indice]

    def obtener_casilla_por_carta(self, id_carta: int) -> Optional[CasillaCarton]:
        """Busca la casilla asociada al id indicado."""

        for casilla in self._casillas:
            if casilla.carta.id == id_carta:
                return casilla
        return None

    def obtener_indice_por_carta(self, id_carta: int) -> Optional[int]:
        """Busca el indice de una carta dentro del carton."""

        for indice, casilla in enumerate(self._casillas):
            if casilla.carta.id == id_carta:
                return indice
        return None

    def contiene(self, id_carta: int) -> bool:
        """Indica si una carta existe dentro del carton."""

        return self.obtener_casilla_por_carta(id_carta) is not None

    def marcar_carta(self, id_carta: int) -> bool:
        """Marca una carta existente dentro del carton."""

        casilla = self.obtener_casilla_por_carta(id_carta)
        return casilla.marcar() if casilla else False

    def desmarcar_carta(self, id_carta: int) -> bool:
        """Desmarca una carta existente dentro del carton."""

        casilla = self.obtener_casilla_por_carta(id_carta)
        if casilla is None:
            return False
        casilla.desmarcar()
        return True

    def reiniciar(self) -> None:
        """Limpia todas las marcas del carton."""

        for casilla in self._casillas:
            casilla.desmarcar()

    def esta_completo(self) -> bool:
        """Indica si todas las casillas estan marcadas."""

        return all(casilla.marcada for casilla in self._casillas)

    def contar_marcadas(self) -> int:
        """Cuenta cuantas casillas ya fueron marcadas."""

        return sum(1 for casilla in self._casillas if casilla.marcada)

    def verificar_fila_completa(self, fila: int) -> bool:
        """Indica si una fila esta completamente marcada."""

        if not (0 <= fila < self.FILAS):
            return False
        indices = range(fila * self.COLUMNAS, (fila + 1) * self.COLUMNAS)
        return self.estan_marcados(indices)

    def verificar_columna_completa(self, columna: int) -> bool:
        """Indica si una columna esta completamente marcada."""

        if not (0 <= columna < self.COLUMNAS):
            return False
        indices = range(columna, self.CASILLAS_TOTALES, self.COLUMNAS)
        return self.estan_marcados(indices)

    def estan_marcados(self, indices: Iterable[int]) -> bool:
        """Verifica si un grupo de indices esta totalmente marcado."""

        for indice in indices:
            casilla = self.obtener_casilla_por_indice(indice)
            if casilla is None or not casilla.marcada:
                return False
        return True

    def obtener_cartas_faltantes(self, cartas_cantadas: Set[int]) -> List[Carta]:
        """Retorna las cartas del carton aun no cantadas."""

        return [
            casilla.carta
            for casilla in self._casillas
            if casilla.carta.id not in cartas_cantadas
        ]

    @property
    def casillas(self) -> Tuple[CasillaCarton, ...]:
        """Copia inmutable de las casillas del carton."""

        return tuple(self._casillas)

    @property
    def filas(self) -> int:
        """Cantidad de filas del carton."""

        return self.FILAS

    @property
    def columnas(self) -> int:
        """Cantidad de columnas del carton."""

        return self.COLUMNAS

    def __iter__(self):
        return iter(self._casillas)

    def __len__(self) -> int:
        return len(self._casillas)
