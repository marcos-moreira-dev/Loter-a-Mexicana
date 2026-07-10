"""Modelo de dominio para una carta de la Lotería Mexicana."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(eq=False)
class Carta:
    """Representa una carta individual del mazo."""

    id: int
    nombre: str
    imagen_path: str
    descripcion: str | None = None
    cantada: bool = False

    def marcar_cantada(self) -> None:
        """Marca la carta como cantada."""

        self.cantada = True

    def reiniciar(self) -> None:
        """Restablece la carta a su estado inicial."""

        self.cantada = False

    def __str__(self) -> str:
        return f"{self.id}: {self.nombre}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Carta):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
