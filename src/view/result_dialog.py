"""Diálogo final de resultados."""

from __future__ import annotations

from typing import TYPE_CHECKING

import wx

from infrastructure.ui.branding import apply_window_icon
from infrastructure.ui.colors import AppColors
from infrastructure.ui.fonts import get_display_font, get_playful_font
from model.partida import Partida

if TYPE_CHECKING:
    from controller.app_controller import AppController


class ResultDialog(wx.Dialog):
    """Diálogo mostrado al terminar una partida."""

    def __init__(self, parent: wx.Window, partida: Partida, controller: "AppController") -> None:
        super().__init__(parent, title="Resultado de la partida", size=(500, 360))
        self.partida = partida
        self.controller = controller
        self.SetBackgroundColour(AppColors.BACKGROUND)
        self._init_ui()
        apply_window_icon(self)
        self.Centre()

    def _init_ui(self) -> None:
        panel = wx.Panel(self)
        panel.SetBackgroundColour(AppColors.BACKGROUND)
        sizer = wx.BoxSizer(wx.VERTICAL)

        victoria = self.partida.ganador is not None
        titulo = "Partida finalizada"
        mensaje = (
            f"Ganador: {self.partida.ganador.nombre}"
            if victoria
            else "El mazo terminó sin ganador."
        )
        color = AppColors.SUCCESS if victoria else AppColors.PRIMARY

        lbl_titulo = wx.StaticText(panel, label=titulo)
        lbl_titulo.SetFont(get_display_font("title"))
        lbl_titulo.SetForegroundColour(color)
        sizer.Add(lbl_titulo, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 16)

        lbl_mensaje = wx.StaticText(panel, label=mensaje)
        lbl_mensaje.SetFont(get_playful_font("large", bold=True))
        lbl_mensaje.SetForegroundColour(AppColors.TEXT_PRIMARY)
        sizer.Add(lbl_mensaje, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)

        resumen = (
            f"Alineación: {self.partida.nombre_alineacion}\n"
            f"Cartas cantadas: {len(self.partida.historial_cartas)}\n"
            f"Duración: {self.partida.duracion_segundos} segundos\n"
            f"Participantes: {self.partida.configuracion.cantidad_participantes}"
        )
        lbl_resumen = wx.StaticText(panel, label=resumen)
        lbl_resumen.SetFont(get_playful_font("normal"))
        lbl_resumen.SetForegroundColour(AppColors.TEXT_PRIMARY)
        sizer.Add(lbl_resumen, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 12)

        botones = wx.BoxSizer(wx.HORIZONTAL)
        btn_reiniciar = wx.Button(panel, label="Jugar de nuevo", size=(150, 44), style=wx.BORDER_NONE)
        btn_reiniciar.SetFont(get_playful_font("normal", bold=True))
        btn_reiniciar.SetBackgroundColour(AppColors.SECONDARY)
        btn_reiniciar.SetForegroundColour(AppColors.TEXT_LIGHT)
        btn_reiniciar.Bind(wx.EVT_BUTTON, self._on_reiniciar)
        botones.Add(btn_reiniciar, 0, wx.RIGHT, 8)

        btn_menu = wx.Button(panel, label="Menú principal", size=(150, 44), style=wx.BORDER_NONE)
        btn_menu.SetFont(get_playful_font("normal", bold=True))
        btn_menu.SetBackgroundColour(wx.Colour(149, 165, 166))
        btn_menu.SetForegroundColour(AppColors.TEXT_LIGHT)
        btn_menu.Bind(wx.EVT_BUTTON, self._on_menu)
        botones.Add(btn_menu, 0)
        sizer.Add(botones, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 18)

        panel.SetSizer(sizer)

    def _on_reiniciar(self, event: wx.Event) -> None:
        self.EndModal(wx.ID_OK)
        self.controller.iniciar_nueva_partida()

    def _on_menu(self, event: wx.Event) -> None:
        self.EndModal(wx.ID_OK)
        self.controller.mostrar_menu_principal()
