"""Modelo de dominio de la Lotería Mexicana."""

from .carta import Carta
from .carton import Carton, CasillaCarton
from .configuracion import ConfiguracionPartida
from .configuracion import ModoPartida
from .jugador import Jugador
from .mazo import Mazo
from .partida import EstadoPartida, Partida, ResultadoLoteria, ResultadoMarcado
from .reglas import (
    Alineacion,
    DefinicionAlineacion,
    obtener_definicion,
    obtener_oficiales,
    obtener_todas,
    verificar_carton,
)
from .reportes import RegistroPartida, RepositorioReportes

__all__ = [
    "Alineacion",
    "Carta",
    "Carton",
    "CasillaCarton",
    "ConfiguracionPartida",
    "DefinicionAlineacion",
    "EstadoPartida",
    "Jugador",
    "ModoPartida",
    "Mazo",
    "Partida",
    "RegistroPartida",
    "RepositorioReportes",
    "ResultadoLoteria",
    "ResultadoMarcado",
    "obtener_definicion",
    "obtener_oficiales",
    "obtener_todas",
    "verificar_carton",
]
