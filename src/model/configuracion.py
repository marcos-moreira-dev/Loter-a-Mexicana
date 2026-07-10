"""Configuracion de la partida de Loteria Mexicana."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from model.reglas import Alineacion


class ModoPartida(Enum):
    """Modos disponibles de la partida."""

    SOLO_HUMANO = "SOLO_HUMANO"
    HUMANO_VS_COMPUTADORA = "HUMANO_VS_COMPUTADORA"
    COMPUTADORA_VS_COMPUTADORA = "COMPUTADORA_VS_COMPUTADORA"


@dataclass(slots=True)
class ConfiguracionPartida:
    """Agrupa la configuracion editable de una partida."""

    nombre_jugador: str = "Jugador 1"
    modo_partida: ModoPartida = ModoPartida.HUMANO_VS_COMPUTADORA
    mostrar_cartas_oponente: bool = False
    intervalo_canto_ms: int = 6000
    nombre_oponente: str = "Computadora"
    alineacion_preferida: Alineacion | None = None

    def __post_init__(self) -> None:
        self.nombre_jugador = self.nombre_jugador.strip() or "Jugador 1"
        self.nombre_oponente = self.nombre_oponente.strip() or "Computadora"

        if self.intervalo_canto_ms < 1000:
            raise ValueError("El intervalo de canto debe ser de al menos 1000 ms")

    @property
    def incluir_oponente_automatico(self) -> bool:
        """Indica si existe un segundo jugador automatico."""

        return self.modo_partida != ModoPartida.SOLO_HUMANO

    @property
    def permite_interaccion_humana(self) -> bool:
        """Indica si la partida admite acciones manuales del usuario."""

        return self.modo_partida != ModoPartida.COMPUTADORA_VS_COMPUTADORA

    @property
    def primer_jugador_es_automatico(self) -> bool:
        """Indica si el primer carton pertenece a una computadora."""

        return self.modo_partida == ModoPartida.COMPUTADORA_VS_COMPUTADORA

    @property
    def cantidad_participantes(self) -> int:
        """Cantidad total de jugadores presentes en la partida."""

        return 2 if self.incluir_oponente_automatico else 1
