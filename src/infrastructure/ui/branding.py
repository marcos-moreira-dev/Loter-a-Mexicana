"""Helpers de branding e iconografía de la aplicación."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import wx

from infrastructure.paths import asset_path


def get_logo_path() -> Path:
    """Retorna la ruta del logo principal."""

    return asset_path("branding", "logo.png")


def get_logo_icon_path() -> Path:
    """Retorna la ruta del icono para ventanas e instalador."""

    return asset_path("branding", "logo.ico")


def load_logo_bitmap(size: Optional[Tuple[int, int]] = None) -> Optional[wx.Bitmap]:
    """Carga el logo como bitmap opcionalmente escalado."""

    path = get_logo_path()
    if not path.exists():
        return None

    image = wx.Image(str(path), wx.BITMAP_TYPE_ANY)
    if not image.IsOk():
        return None

    if size is not None:
        image = image.Scale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)
    return image.ConvertToBitmap()


def load_app_icon() -> Optional[wx.Icon]:
    """Carga el icono principal de la aplicación."""

    icon_path = get_logo_icon_path()
    if icon_path.exists():
        icon = wx.Icon(str(icon_path), wx.BITMAP_TYPE_ICO)
        if icon.IsOk():
            return icon

    bitmap = load_logo_bitmap((256, 256))
    if bitmap is None or not bitmap.IsOk():
        return None

    icon = wx.Icon()
    icon.CopyFromBitmap(bitmap)
    return icon if icon.IsOk() else None


def apply_window_icon(window: wx.TopLevelWindow) -> None:
    """Aplica el icono de branding a una ventana superior."""

    icon = load_app_icon()
    if icon is not None and icon.IsOk():
        window.SetIcon(icon)
