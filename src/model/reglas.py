"""Reglas de alineación del juego."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

from model.carton import Carton


class Alineacion(Enum):
    """Alineaciones disponibles del juego."""

    FILA = "FILA"
    COLUMNA = "COLUMNA"
    ESQUINA = "ESQUINA"
    JUNTASCUALQUIERESQUINA = "JUNTASCUALQUIERESQUINA"
    INSIDE = "INSIDE"
    COMPLETO = "COMPLETO"


@dataclass(frozen=True, slots=True)
class DefinicionAlineacion:
    """Describe una alineación válida del juego."""

    alineacion: Alineacion
    nombre: str
    descripcion: str
    patrones: Tuple[Tuple[int, ...], ...]
    patron_referencia: Tuple[int, ...]
    imagen_referencia: str | None = None
    es_oficial: bool = True


_DEFINICIONES: Dict[Alineacion, DefinicionAlineacion] = {
    Alineacion.FILA: DefinicionAlineacion(
        alineacion=Alineacion.FILA,
        nombre="Línea horizontal",
        descripcion="Marca las 4 cartas de una fila horizontal completa.",
        patrones=(
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (8, 9, 10, 11),
            (12, 13, 14, 15),
        ),
        patron_referencia=(0, 1, 2, 3),
        imagen_referencia="CualquierFila.png",
    ),
    Alineacion.COLUMNA: DefinicionAlineacion(
        alineacion=Alineacion.COLUMNA,
        nombre="Cualquier columna",
        descripcion="Marca las 4 cartas de una columna vertical completa.",
        patrones=(
            (0, 4, 8, 12),
            (1, 5, 9, 13),
            (2, 6, 10, 14),
            (3, 7, 11, 15),
        ),
        patron_referencia=(0, 4, 8, 12),
        imagen_referencia="CualquierColumna.png",
    ),
    Alineacion.ESQUINA: DefinicionAlineacion(
        alineacion=Alineacion.ESQUINA,
        nombre="Cuatro esquinas",
        descripcion="Marca las cuatro esquinas del cartón.",
        patrones=((0, 3, 12, 15),),
        patron_referencia=(0, 3, 12, 15),
        imagen_referencia="4Esquinas.png",
    ),
    Alineacion.JUNTASCUALQUIERESQUINA: DefinicionAlineacion(
        alineacion=Alineacion.JUNTASCUALQUIERESQUINA,
        nombre="Cuatro juntas en cualquier esquina",
        descripcion="Marca un bloque de 2x2 ubicado en cualquiera de las cuatro esquinas.",
        patrones=(
            (0, 1, 4, 5),
            (2, 3, 6, 7),
            (8, 9, 12, 13),
            (10, 11, 14, 15),
        ),
        patron_referencia=(0, 1, 4, 5),
        imagen_referencia="4FigurasJuntasCualquierEsquina.png",
    ),
    Alineacion.INSIDE: DefinicionAlineacion(
        alineacion=Alineacion.INSIDE,
        nombre="Inside",
        descripcion="Marca el bloque central de 2x2 del cartón.",
        patrones=((5, 6, 9, 10),),
        patron_referencia=(5, 6, 9, 10),
        imagen_referencia="inside.JPG",
    ),
    Alineacion.COMPLETO: DefinicionAlineacion(
        alineacion=Alineacion.COMPLETO,
        nombre="Cartón completo",
        descripcion="Marca las 16 cartas del cartón para ganar.",
        patrones=(tuple(range(16)),),
        patron_referencia=tuple(range(16)),
        es_oficial=False,
    ),
}


def obtener_todas() -> Tuple[Alineacion, ...]:
    """Retorna todas las alineaciones disponibles para configuración."""

    return tuple(_DEFINICIONES.keys())


def obtener_oficiales() -> Tuple[Alineacion, ...]:
    """Retorna solo las alineaciones oficiales del juego."""

    return tuple(
        alineacion
        for alineacion, definicion in _DEFINICIONES.items()
        if definicion.es_oficial
    )


def obtener_definicion(alineacion: Alineacion) -> DefinicionAlineacion:
    """Obtiene la definición de una alineación."""

    return _DEFINICIONES[alineacion]


def verificar_carton(carton: Carton, alineacion: Alineacion) -> bool:
    """Verifica si un cartón satisface la alineación indicada."""

    definicion = obtener_definicion(alineacion)
    return any(carton.estan_marcados(patron) for patron in definicion.patrones)
