"""Pruebas de alineaciones oficiales."""

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from model.carta import Carta
from model.carton import Carton
from model.reglas import Alineacion, verificar_carton


def crear_carton_base() -> Carton:
    cartas = [
        Carta(id=indice + 1, nombre=f"CARTA {indice + 1}", imagen_path=f"{indice + 1}.png")
        for indice in range(16)
    ]
    return Carton(cartas)


class ReglasOficialesTest(unittest.TestCase):
    def marcar_indices(self, carton: Carton, indices: tuple[int, ...]) -> None:
        for indice in indices:
            casilla = carton.obtener_casilla_por_indice(indice)
            assert casilla is not None
            casilla.marcar()

    def test_fila_horizontal_es_valida(self) -> None:
        carton = crear_carton_base()
        self.marcar_indices(carton, (4, 5, 6, 7))
        self.assertTrue(verificar_carton(carton, Alineacion.FILA))

    def test_columna_vertical_es_valida(self) -> None:
        carton = crear_carton_base()
        self.marcar_indices(carton, (2, 6, 10, 14))
        self.assertTrue(verificar_carton(carton, Alineacion.COLUMNA))

    def test_cuatro_esquinas_es_valida(self) -> None:
        carton = crear_carton_base()
        self.marcar_indices(carton, (0, 3, 12, 15))
        self.assertTrue(verificar_carton(carton, Alineacion.ESQUINA))

    def test_bloque_en_esquina_es_valido(self) -> None:
        carton = crear_carton_base()
        self.marcar_indices(carton, (10, 11, 14, 15))
        self.assertTrue(verificar_carton(carton, Alineacion.JUNTASCUALQUIERESQUINA))

    def test_inside_es_valido(self) -> None:
        carton = crear_carton_base()
        self.marcar_indices(carton, (5, 6, 9, 10))
        self.assertTrue(verificar_carton(carton, Alineacion.INSIDE))

    def test_carton_completo_es_valido(self) -> None:
        carton = crear_carton_base()
        self.marcar_indices(carton, tuple(range(16)))
        self.assertTrue(verificar_carton(carton, Alineacion.COMPLETO))


if __name__ == "__main__":
    unittest.main()
