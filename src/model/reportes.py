"""Persistencia simple de reportes de partidas."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from infrastructure.paths import data_path


@dataclass(slots=True)
class RegistroPartida:
    """Representa el resumen persistido de una partida terminada."""

    fecha_iso: str
    ganador: Optional[str]
    alineacion: str
    descripcion_alineacion: str
    duracion_segundos: int
    cartas_cantadas: int
    participantes: int


class RepositorioReportes:
    """Guarda y recupera historiales de partidas en JSON."""

    def __init__(self, ruta: Optional[Path] = None) -> None:
        self._ruta = ruta or data_path("reportes_partidas.json")

    @property
    def ruta(self) -> Path:
        """Ruta del archivo de reportes."""

        return self._ruta

    def cargar(self) -> List[RegistroPartida]:
        """Carga todos los reportes conocidos."""

        if not self._ruta.exists():
            return []

        try:
            with self._ruta.open("r", encoding="utf-8") as archivo:
                contenido = json.load(archivo)
        except (json.JSONDecodeError, OSError):
            return []

        if not isinstance(contenido, list):
            return []

        registros: List[RegistroPartida] = []
        for item in contenido:
            if not isinstance(item, dict):
                continue
            registros.append(
                RegistroPartida(
                    fecha_iso=str(item.get("fecha_iso", "")),
                    ganador=item.get("ganador"),
                    alineacion=str(item.get("alineacion", "")),
                    descripcion_alineacion=str(item.get("descripcion_alineacion", "")),
                    duracion_segundos=int(item.get("duracion_segundos", 0)),
                    cartas_cantadas=int(item.get("cartas_cantadas", 0)),
                    participantes=int(item.get("participantes", 1)),
                )
            )

        return registros

    def guardar(self, registro: RegistroPartida) -> None:
        """Agrega un nuevo registro al historial."""

        registros = self.cargar()
        registros.append(registro)

        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        with self._ruta.open("w", encoding="utf-8") as archivo:
            json.dump(
                [asdict(item) for item in registros],
                archivo,
                indent=2,
                ensure_ascii=False,
            )

    def eliminar_todos(self) -> None:
        """Elimina el historial persistido de partidas."""

        try:
            self._ruta.unlink()
        except FileNotFoundError:
            return
        except OSError:
            self._ruta.parent.mkdir(parents=True, exist_ok=True)
            with self._ruta.open("w", encoding="utf-8") as archivo:
                json.dump([], archivo, indent=2, ensure_ascii=False)
