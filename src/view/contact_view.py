"""Ventana de contacto del autor."""

from __future__ import annotations

from pathlib import Path

import wx

from infrastructure.paths import asset_path
from infrastructure.ui.colors import AppColors
from infrastructure.ui.fonts import get_display_font, get_playful_font


class ContactDialog(wx.Dialog):
    """Muestra informacion de contacto del autor."""

    IMAGE_SIZE = (132, 132)

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(
            parent,
            title="Contacto",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.SetBackgroundColour(AppColors.BACKGROUND)
        self.SetMinSize((520, 420))
        self._init_ui()
        self.CentreOnParent()

    def _init_ui(self) -> None:
        root = wx.BoxSizer(wx.VERTICAL)

        titulo = wx.StaticText(self, label="Contacto del autor")
        titulo.SetFont(get_display_font("xlarge"))
        titulo.SetForegroundColour(AppColors.PRIMARY)
        root.Add(titulo, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 18)

        cuerpo = wx.BoxSizer(wx.HORIZONTAL)

        imagen = wx.StaticBitmap(self, bitmap=self._load_contact_bitmap())
        cuerpo.Add(imagen, 0, wx.RIGHT | wx.ALIGN_TOP, 22)

        datos = wx.BoxSizer(wx.VERTICAL)

        subtitulo = wx.StaticText(self, label="Marcos Moreira")
        subtitulo.SetFont(get_playful_font("large", bold=True))
        subtitulo.SetForegroundColour(AppColors.TEXT_PRIMARY)
        datos.Add(subtitulo, 0, wx.BOTTOM, 14)

        for etiqueta, valor in (
            ("Gmail", "marcos.moreira.ec.dev@gmail.com"),
            ("Outlook", "marcos_moreira_dev@outlook.com"),
            ("Twitter", "@marcosmdev26"),
        ):
            datos.Add(self._crear_linea_dato(etiqueta, valor), 0, wx.BOTTOM | wx.EXPAND, 10)

        nota = wx.StaticText(
            self,
            label="Puedes usar cualquiera de estos canales para consultas, colaboraciones o contacto profesional.",
        )
        nota.SetFont(get_playful_font("normal"))
        nota.SetForegroundColour(AppColors.TEXT_SECONDARY)
        nota.Wrap(290)
        datos.Add(nota, 0, wx.TOP | wx.EXPAND, 12)

        cuerpo.Add(datos, 1, wx.EXPAND)
        root.Add(cuerpo, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 24)

        botones = self.CreateStdDialogButtonSizer(wx.OK)
        if botones:
            root.Add(botones, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, 18)

        self.SetSizerAndFit(root)

    def _crear_linea_dato(self, etiqueta: str, valor: str) -> wx.Sizer:
        fila = wx.BoxSizer(wx.VERTICAL)

        titulo = wx.StaticText(self, label=etiqueta)
        titulo.SetFont(get_playful_font("small", bold=True))
        titulo.SetForegroundColour(AppColors.SECONDARY)
        fila.Add(titulo, 0, wx.BOTTOM, 2)

        contenido = wx.TextCtrl(
            self,
            value=valor,
            style=wx.TE_READONLY | wx.BORDER_NONE,
        )
        contenido.SetBackgroundColour(wx.Colour(255, 250, 240))
        contenido.SetForegroundColour(AppColors.TEXT_PRIMARY)
        contenido.SetFont(get_playful_font("normal"))
        fila.Add(contenido, 0, wx.EXPAND)
        return fila

    def _load_contact_bitmap(self) -> wx.Bitmap:
        path = asset_path("contact", "cara.png")
        if not path.exists():
            return wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_OTHER, self.IMAGE_SIZE)

        image = wx.Image(str(Path(path)))
        if not image.IsOk():
            return wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_OTHER, self.IMAGE_SIZE)

        image = image.Scale(self.IMAGE_SIZE[0], self.IMAGE_SIZE[1], wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(image)
