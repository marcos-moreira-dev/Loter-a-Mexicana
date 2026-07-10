"""Diálogo de ayuda."""

from __future__ import annotations

import wx

from infrastructure.ui.branding import apply_window_icon
from infrastructure.ui.colors import AppColors
from infrastructure.ui.fonts import get_display_font, get_playful_font


class HelpDialog(wx.Dialog):
    """Muestra las instrucciones del modo de juego oficial."""

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, title="Ayuda", size=(640, 680))
        self.SetBackgroundColour(AppColors.BACKGROUND)
        self._init_ui()
        apply_window_icon(self)
        self.Centre()

    def _init_ui(self) -> None:
        panel = wx.Panel(self)
        panel.SetBackgroundColour(AppColors.BACKGROUND)
        sizer = wx.BoxSizer(wx.VERTICAL)

        titulo = wx.StaticText(panel, label="Cómo jugar")
        titulo.SetFont(get_display_font("title"))
        titulo.SetForegroundColour(AppColors.PRIMARY)
        sizer.Add(titulo, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 14)

        scroll = wx.ScrolledWindow(panel)
        scroll.SetBackgroundColour(AppColors.BACKGROUND)
        scroll.SetScrollRate(5, 5)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        secciones = [
            (
                "Resumen",
                "El juego usa una alineación oficial, cambio automático de cartas, "
                "modos solo, humano vs computadora o computadora vs computadora, "
                "y marcado válido solo para la carta actual cuando hay interacción humana.",
            ),
            (
                "Flujo de partida",
                "1. Inicia una partida nueva.\n"
                "2. El sistema usa la alineación configurada o elige una oficial al azar.\n"
                "3. La carta actual cambia automáticamente cada 6 segundos.\n"
                "4. Haz clic únicamente sobre la carta actual si está en tu cartón.\n"
                "5. Cuando completes la alineación, presiona 'Cantar lotería'.",
            ),
            (
                "Alineaciones oficiales",
                "Las alineaciones posibles son:\n"
                "- Cualquier fila\n"
                "- Cualquier columna\n"
                "- Cuatro esquinas\n"
                "- Cuatro juntas en cualquier esquina\n"
                "- Inside (bloque central de 2x2)",
            ),
            (
                "Computadora",
                "En los modos con computadora, las cartas se marcan automáticamente cuando "
                "coinciden con la carta actual. Si eliges computadora vs computadora, "
                "la partida se resuelve sola y el tablero queda solo para observación.",
            ),
            (
                "Consejo importante",
                "El mazo no repite cartas y las marcas equivocadas muestran la carta virada "
                "por un momento para avisarte del error antes de restaurar la imagen.",
            ),
        ]

        for titulo_seccion, contenido in secciones:
            scroll_sizer.Add(self._crear_seccion(scroll, titulo_seccion, contenido), 0, wx.EXPAND | wx.ALL, 8)

        scroll.SetSizer(scroll_sizer)
        sizer.Add(scroll, 1, wx.EXPAND | wx.ALL, 10)

        btn_cerrar = wx.Button(panel, label="Cerrar", size=(140, 42), style=wx.BORDER_NONE)
        btn_cerrar.SetFont(get_playful_font("normal", bold=True))
        btn_cerrar.SetBackgroundColour(AppColors.SECONDARY)
        btn_cerrar.SetForegroundColour(AppColors.TEXT_LIGHT)
        btn_cerrar.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_OK))
        sizer.Add(btn_cerrar, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 14)

        panel.SetSizer(sizer)

    def _crear_seccion(self, parent: wx.Window, titulo: str, contenido: str) -> wx.Panel:
        panel = wx.Panel(parent)
        panel.SetBackgroundColour(AppColors.ACCENT)

        borde = wx.BoxSizer(wx.VERTICAL)
        interior = wx.Panel(panel)
        interior.SetBackgroundColour(wx.WHITE)
        interior_sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_titulo = wx.StaticText(interior, label=titulo)
        lbl_titulo.SetFont(get_display_font("medium"))
        lbl_titulo.SetForegroundColour(AppColors.PRIMARY)
        interior_sizer.Add(lbl_titulo, 0, wx.ALL, 10)

        lbl_contenido = wx.StaticText(interior, label=contenido)
        lbl_contenido.SetFont(get_playful_font("small"))
        lbl_contenido.SetForegroundColour(AppColors.TEXT_PRIMARY)
        lbl_contenido.Wrap(540)
        interior_sizer.Add(lbl_contenido, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        interior.SetSizer(interior_sizer)
        borde.Add(interior, 1, wx.EXPAND | wx.ALL, 3)
        panel.SetSizer(borde)
        return panel
