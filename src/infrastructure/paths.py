"""Helpers de rutas del proyecto y del ejecutable congelado."""

from __future__ import annotations

import sys
from pathlib import Path


def get_project_root() -> Path:
    """Retorna la raíz efectiva del proyecto o del ejecutable."""

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def asset_path(*parts: str) -> Path:
    """Construye una ruta dentro de la carpeta de assets."""

    return get_project_root().joinpath("assets", *parts)


def data_path(*parts: str) -> Path:
    """Construye una ruta dentro de la carpeta de datos."""

    return get_project_root().joinpath("data", *parts)


def resolve_project_path(path_like: str | Path) -> Path:
    """Resuelve una ruta absoluta o relativa a la raíz del proyecto."""

    path = Path(path_like)
    return path if path.is_absolute() else get_project_root() / path
