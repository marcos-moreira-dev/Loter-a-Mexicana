"""Modelo del mazo de cartas para la Lotería Mexicana."""

from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from infrastructure.paths import resolve_project_path
from model.carta import Carta


class Mazo:
    """Representa el mazo profesional de 54 cartas sin repeticiones."""

    def __init__(
        self,
        assets_path: str = "assets/cards",
        csv_path: str = "assets/cartasloteria.csv",
    ) -> None:
        self._assets_path = self._resolver_ruta(assets_path)
        self._csv_path = self._resolver_ruta(csv_path)
        self._cartas: List[Carta] = []
        self._cartas_restantes: List[Carta] = []
        self._cartas_cantadas: List[Carta] = []
        self._inicializar_cartas()

    def _resolver_ruta(self, ruta: str) -> Path:
        return resolve_project_path(Path(ruta))

    def _inicializar_cartas(self) -> None:
        """Carga las cartas desde CSV y sus imágenes asociadas."""

        self._cartas = []
        for id_carta, nombre in self._leer_csv():
            imagen_path = self._assets_path / f"{id_carta}.png"
            self._cartas.append(
                Carta(
                    id=id_carta,
                    nombre=nombre,
                    imagen_path=str(imagen_path.resolve()),
                    descripcion=f"Carta tradicional: {nombre}",
                )
            )

        self.reiniciar()

    def _leer_csv(self) -> Sequence[Tuple[int, str]]:
        """Lee el CSV oficial o usa datos por defecto si falta."""

        cartas: List[Tuple[int, str]] = []
        try:
            with self._csv_path.open("r", encoding="utf-8") as archivo:
                reader = csv.reader(archivo)
                for row in reader:
                    if len(row) >= 2:
                        cartas.append((int(row[0].strip()), row[1].strip()))
        except (OSError, ValueError):
            cartas = list(self._datos_por_defecto())
        return cartas

    def _datos_por_defecto(self) -> Sequence[Tuple[int, str]]:
        return (
            (1, "EL GALLO"),
            (2, "EL DIABLITO"),
            (3, "LA DAMA"),
            (4, "EL CATRÍN"),
            (5, "EL PARAGUAS"),
            (6, "LA SIRENA"),
            (7, "LA ESCALERA"),
            (8, "LA BOTELLA"),
            (9, "EL BARRIL"),
            (10, "EL ÁRBOL"),
            (11, "EL MELÓN"),
            (12, "EL VALIENTE"),
            (13, "EL GORRITO"),
            (14, "LA MUERTE"),
            (15, "LA PERA"),
            (16, "LA BANDERA"),
            (17, "EL BANDOLÓN"),
            (18, "EL VIOLONCELLO"),
            (19, "LA GARZA"),
            (20, "EL PÁJARO"),
            (21, "LA MANO"),
            (22, "LA BOTA"),
            (23, "LA LUNA"),
            (24, "EL COTORRO"),
            (25, "EL BORRACHO"),
            (26, "EL NEGRITO"),
            (27, "EL CORAZÓN"),
            (28, "LA SANDÍA"),
            (29, "EL TAMBOR"),
            (30, "EL CAMARÓN"),
            (31, "LAS JARAS"),
            (32, "EL MÚSICO"),
            (33, "LA ARAÑA"),
            (34, "EL SOLDADO"),
            (35, "LA ESTRELLA"),
            (36, "EL CAZO"),
            (37, "EL MUNDO"),
            (38, "EL APACHE"),
            (39, "EL NOPAL"),
            (40, "EL ALACRÁN"),
            (41, "LA ROSA"),
            (42, "LA CALAVERA"),
            (43, "LA CAMPANA"),
            (44, "EL CANTARITO"),
            (45, "EL VENADO"),
            (46, "EL SOL"),
            (47, "LA CORONA"),
            (48, "LA CHALUPA"),
            (49, "EL PINO"),
            (50, "EL PESCADO"),
            (51, "LA PALMA"),
            (52, "LA MACETA"),
            (53, "EL ARPA"),
            (54, "LA RANA"),
        )

    def barajar(self) -> None:
        """Baraja las cartas restantes."""

        random.shuffle(self._cartas_restantes)

    def siguiente_carta(self) -> Optional[Carta]:
        """Entrega la siguiente carta del mazo."""

        if not self._cartas_restantes:
            return None

        carta = self._cartas_restantes.pop()
        carta.marcar_cantada()
        self._cartas_cantadas.append(carta)
        return carta

    def reiniciar(self) -> None:
        """Restituye el mazo completo y vuelve a barajar."""

        self._cartas_restantes = self._cartas.copy()
        self._cartas_cantadas = []
        for carta in self._cartas:
            carta.reiniciar()
        self.barajar()

    def esta_vacio(self) -> bool:
        """Indica si ya no quedan cartas por cantar."""

        return not self._cartas_restantes

    @property
    def cartas_restantes(self) -> int:
        return len(self._cartas_restantes)

    @property
    def cartas_cantadas(self) -> List[Carta]:
        return self._cartas_cantadas.copy()

    @property
    def total_cartas(self) -> int:
        return len(self._cartas)

    @property
    def cartas(self) -> List[Carta]:
        return self._cartas.copy()

    def obtener_carta_por_id(self, id_carta: int) -> Optional[Carta]:
        """Busca una carta por su identificador."""

        for carta in self._cartas:
            if carta.id == id_carta:
                return carta
        return None

    def fue_cantada(self, id_carta: int) -> bool:
        """Indica si la carta ya fue cantada."""

        carta = self.obtener_carta_por_id(id_carta)
        return carta.cantada if carta else False
