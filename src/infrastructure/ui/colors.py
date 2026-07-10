"""Colores y temas visuales centralizados."""

import wx


class AppColors:
    """Paleta de colores de la aplicacion."""

    # Colores base
    BACKGROUND = wx.Colour(250, 244, 228)       # Pergamino suave amarillo pastel
    PRIMARY = wx.Colour(201, 72, 52)            # Terracota
    SECONDARY = wx.Colour(43, 133, 92)          # Verde jade
    ACCENT = wx.Colour(232, 178, 43)            # Oro maiz
    BLUE = wx.Colour(63, 126, 143)              # Azul petroleo suave
    ORANGE = wx.Colour(216, 121, 44)            # Naranja calabaza
    PURPLE = wx.Colour(167, 96, 136)            # Frambuesa suave

    # Colores de texto
    TEXT_PRIMARY = wx.Colour(63, 51, 43)        # Cacao oscuro
    TEXT_SECONDARY = wx.Colour(127, 112, 96)    # Arena tostada
    TEXT_LIGHT = wx.Colour(255, 255, 255)       # Blanco

    # Estados
    SUCCESS = SECONDARY
    WARNING = ACCENT
    ERROR = PRIMARY
    INFO = BLUE

    # Carton
    CELL_NORMAL = wx.WHITE
    CELL_MARKED = wx.Colour(43, 133, 92, 220)
    CELL_HIGHLIGHTED = wx.Colour(232, 178, 43, 180)

    # Botones
    BTN_HOVER_DARKEN = 0.85


class ButtonColors:
    """Colores especificos para botones."""

    PRIMARY = AppColors.PRIMARY
    PRIMARY_HOVER = wx.Colour(170, 56, 39)

    SECONDARY = AppColors.SECONDARY
    SECONDARY_HOVER = wx.Colour(31, 108, 74)

    ACCENT = AppColors.ACCENT
    ACCENT_HOVER = wx.Colour(203, 150, 28)

    NEUTRAL = wx.Colour(144, 145, 137)
    NEUTRAL_HOVER = wx.Colour(112, 113, 107)

    PURPLE = AppColors.PURPLE
    PURPLE_HOVER = wx.Colour(138, 74, 112)
