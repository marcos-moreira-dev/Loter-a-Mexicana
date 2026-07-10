"""Utilidades de fuentes con escalado compatible con DPI."""

from __future__ import annotations

import platform
from typing import Optional

import wx

from infrastructure.paths import asset_path
from infrastructure.platform import get_dpi_scale_factor


class FontManager:
    """Gestiona fuentes privadas y tamaños escalados."""

    SIZE_SMALL = 9
    SIZE_NORMAL = 11
    SIZE_MEDIUM = 13
    SIZE_LARGE = 16
    SIZE_XLARGE = 20
    SIZE_TITLE = 28
    SIZE_HUGE = 36

    _base_family: Optional[int] = None
    _custom_fonts_loaded = False
    _custom_font_faces = {
        "display": "Lilita One",
        "playful": "Balsamiq Sans",
    }
    _custom_font_files = (
        asset_path("fonts", "LilitaOne-Regular.ttf"),
        asset_path("fonts", "BalsamiqSans-Regular.ttf"),
        asset_path("fonts", "BalsamiqSans-Bold.ttf"),
    )

    @classmethod
    def get_scaled_font(
        cls,
        size_category: str = "normal",
        weight: int = wx.FONTWEIGHT_NORMAL,
        style: int = wx.FONTSTYLE_NORMAL,
        family: Optional[int] = None,
        face_name: str = "",
    ) -> wx.Font:
        """Crea una fuente escalada según el DPI del sistema."""

        base_sizes = {
            "small": cls.SIZE_SMALL,
            "normal": cls.SIZE_NORMAL,
            "medium": cls.SIZE_MEDIUM,
            "large": cls.SIZE_LARGE,
            "xlarge": cls.SIZE_XLARGE,
            "title": cls.SIZE_TITLE,
            "huge": cls.SIZE_HUGE,
        }

        base_size = base_sizes.get(size_category, cls.SIZE_NORMAL)
        scaled_size = max(int(base_size * get_dpi_scale_factor()), 8)

        cls._ensure_custom_fonts_loaded()
        if family is None:
            family = cls._get_base_family()

        return wx.Font(
            scaled_size,
            family,
            style,
            weight,
            faceName=face_name,
        )

    @classmethod
    def _ensure_custom_fonts_loaded(cls) -> None:
        if cls._custom_fonts_loaded:
            return

        for path in cls._custom_font_files:
            if not path.exists():
                continue
            try:
                wx.Font.AddPrivateFont(str(path))
            except Exception:
                continue
        cls._custom_fonts_loaded = True

    @classmethod
    def get_custom_face(cls, role: str) -> str:
        """Retorna la fuente privada asociada a un rol visual."""

        return cls._custom_font_faces.get(role, "")

    @classmethod
    def _get_base_family(cls) -> int:
        """Obtiene la familia base recomendada por plataforma."""

        if cls._base_family is None:
            cls._base_family = (
                wx.FONTFAMILY_SWISS
                if platform.system() == "Windows"
                else wx.FONTFAMILY_DEFAULT
            )
        return cls._base_family

    @classmethod
    def get_system_font(cls) -> wx.Font:
        """Obtiene la fuente normal del sistema."""

        return cls.get_scaled_font("normal")

    @classmethod
    def get_bold_font(cls, size_category: str = "normal") -> wx.Font:
        """Obtiene una fuente en negrita escalada."""

        return cls.get_scaled_font(size_category, weight=wx.FONTWEIGHT_BOLD)


def get_font(
    size: str = "normal",
    bold: bool = False,
    italic: bool = False,
    face: str = "",
) -> wx.Font:
    """Obtiene una fuente escalada de forma conveniente."""

    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    style = wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL
    return FontManager.get_scaled_font(size, weight=weight, style=style, face_name=face)


def get_display_font(size: str = "normal") -> wx.Font:
    """Obtiene la fuente decorativa principal."""

    return get_font(size=size, face=FontManager.get_custom_face("display"))


def get_playful_font(size: str = "normal", bold: bool = False) -> wx.Font:
    """Obtiene la fuente secundaria de apoyo."""

    return get_font(size=size, bold=bold, face=FontManager.get_custom_face("playful"))
