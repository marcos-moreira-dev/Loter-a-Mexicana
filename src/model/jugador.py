"""Modelo del jugador para la Loteria Mexicana."""

from dataclasses import dataclass

from model.carton import Carton


@dataclass(slots=True)
class Jugador:
    """Representa a un participante de la partida."""

    nombre: str
    carton: Carton
    es_automatico: bool = False
    ha_ganado: bool = False

    def declarar_ganador(self) -> None:
        """Marca al jugador como ganador."""

        self.ha_ganado = True

    def reiniciar(self) -> None:
        """Reinicia las marcas del jugador."""

        self.ha_ganado = False
        self.carton.reiniciar()

    def marcar_carta(self, id_carta: int) -> bool:
        """Marca una carta existente dentro de su carton."""

        return self.carton.marcar_carta(id_carta)

    def __str__(self) -> str:
        estado = "GANADOR" if self.ha_ganado else "EN JUEGO"
        return f"{self.nombre} ({estado})"
