"""Diálogo de reporte histórico."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import wx

from infrastructure.ui.branding import apply_window_icon
from infrastructure.ui.colors import AppColors
from infrastructure.ui.fonts import get_display_font, get_playful_font
from model.reportes import RegistroPartida, RepositorioReportes


class ReportDialog(wx.Dialog):
    """Muestra el historial de partidas guardadas."""

    def __init__(self, parent: wx.Window, repositorio: RepositorioReportes) -> None:
        super().__init__(parent, title="Reporte", size=(840, 560))
        self.repositorio = repositorio
        self.listado: Optional[wx.ListCtrl] = None
        self.lbl_vacio: Optional[wx.StaticText] = None
        self.btn_eliminar: Optional[wx.Button] = None
        self.SetBackgroundColour(AppColors.BACKGROUND)
        self._init_ui()
        apply_window_icon(self)
        self.Centre()

    def _init_ui(self) -> None:
        panel = wx.Panel(self)
        panel.SetBackgroundColour(AppColors.BACKGROUND)
        sizer = wx.BoxSizer(wx.VERTICAL)

        titulo = wx.StaticText(panel, label="Reporte de partidas")
        titulo.SetFont(get_display_font("title"))
        titulo.SetForegroundColour(AppColors.PRIMARY)
        sizer.Add(titulo, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 18)

        subtitulo = wx.StaticText(
            panel,
            label="Fecha, duración, ganador, participantes y alineación de cada partida.",
        )
        subtitulo.SetFont(get_playful_font("normal"))
        subtitulo.SetForegroundColour(AppColors.TEXT_PRIMARY)
        sizer.Add(subtitulo, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.listado = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.BORDER_SIMPLE | wx.LC_SINGLE_SEL,
        )
        self.listado.SetFont(get_playful_font("small"))
        self.listado.AppendColumn("Fecha", width=170)
        self.listado.AppendColumn("Ganador", width=160)
        self.listado.AppendColumn("Duración", width=90)
        self.listado.AppendColumn("Participantes", width=100)
        self.listado.AppendColumn("Alineación", width=200)
        self.listado.AppendColumn("Cartas", width=70)
        sizer.Add(self.listado, 1, wx.ALL | wx.EXPAND, 12)

        self.lbl_vacio = wx.StaticText(panel, label="Todavía no hay partidas registradas.")
        self.lbl_vacio.SetFont(get_playful_font("normal"))
        self.lbl_vacio.SetForegroundColour(AppColors.TEXT_SECONDARY)
        sizer.Add(self.lbl_vacio, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 4)

        botones = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_eliminar = wx.Button(panel, label="Eliminar registros", size=(170, 42), style=wx.BORDER_NONE)
        self.btn_eliminar.SetFont(get_playful_font("normal", bold=True))
        self.btn_eliminar.SetBackgroundColour(AppColors.PRIMARY)
        self.btn_eliminar.SetForegroundColour(AppColors.TEXT_LIGHT)
        self.btn_eliminar.Bind(wx.EVT_BUTTON, self._on_eliminar_registros)
        botones.Add(self.btn_eliminar, 0, wx.RIGHT, 10)

        btn_cerrar = wx.Button(panel, label="Cerrar", size=(140, 42), style=wx.BORDER_NONE)
        btn_cerrar.SetFont(get_playful_font("normal", bold=True))
        btn_cerrar.SetBackgroundColour(AppColors.SECONDARY)
        btn_cerrar.SetForegroundColour(AppColors.TEXT_LIGHT)
        btn_cerrar.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_OK))
        botones.Add(btn_cerrar, 0)

        sizer.Add(botones, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 14)

        panel.SetSizer(sizer)
        self._recargar_registros()

    def _recargar_registros(self) -> None:
        registros = self.repositorio.cargar()
        self._cargar_registros(registros)

        hay_registros = bool(registros)
        if self.lbl_vacio:
            self.lbl_vacio.Show(not hay_registros)
        if self.btn_eliminar:
            self.btn_eliminar.Enable(hay_registros)
        self.Layout()

    def _cargar_registros(self, registros: List[RegistroPartida]) -> None:
        if self.listado is None:
            return

        self.listado.DeleteAllItems()
        for registro in reversed(registros):
            fecha = self._formatear_fecha(registro.fecha_iso)
            indice = self.listado.InsertItem(self.listado.GetItemCount(), fecha)
            self.listado.SetItem(indice, 1, registro.ganador or "Sin ganador")
            self.listado.SetItem(indice, 2, f"{registro.duracion_segundos}s")
            self.listado.SetItem(indice, 3, str(registro.participantes))
            self.listado.SetItem(indice, 4, registro.descripcion_alineacion)
            self.listado.SetItem(indice, 5, str(registro.cartas_cantadas))

    def _on_eliminar_registros(self, event: wx.Event) -> None:
        respuesta = wx.MessageBox(
            "Se eliminarán todos los registros guardados. Esta acción no se puede deshacer.\n\n¿Quieres continuar?",
            "Eliminar registros",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
        )
        if respuesta != wx.YES:
            return

        self.repositorio.eliminar_todos()
        self._recargar_registros()

    def _formatear_fecha(self, fecha_iso: str) -> str:
        try:
            fecha = datetime.fromisoformat(fecha_iso)
            return fecha.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return fecha_iso or "-"
