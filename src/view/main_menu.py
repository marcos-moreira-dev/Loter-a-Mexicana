"""Panel del menú principal."""

from __future__ import annotations

from typing import TYPE_CHECKING

import wx

from infrastructure.paths import asset_path
from infrastructure.ui.backgrounds import ImageBackgroundPanel, set_transparent_text
from infrastructure.ui.colors import AppColors, ButtonColors
from infrastructure.ui.fonts import get_display_font, get_playful_font
from shared.app_info import APP_NAME

if TYPE_CHECKING:
    from controller.app_controller import AppController


MENU_BACKGROUND = AppColors.BACKGROUND


class MainMenuPanel(ImageBackgroundPanel):
    """Panel del menú principal."""

    def __init__(self, parent: wx.Window, controller: "AppController") -> None:
        super().__init__(
            parent,
            asset_path("backgrounds", "menuprincipalbackground.png"),
            image_opacity=0.36,
            overlay_color=wx.Colour(
                MENU_BACKGROUND.Red(),
                MENU_BACKGROUND.Green(),
                MENU_BACKGROUND.Blue(),
                44,
            ),
            base_color=MENU_BACKGROUND,
        )
        self.controller = controller
        self.SetBackgroundColour(MENU_BACKGROUND)
        self._init_ui()

    def _init_ui(self) -> None:
        root = wx.BoxSizer(wx.VERTICAL)
        root.AddStretchSpacer()

        titulo = wx.StaticText(self, label=APP_NAME.upper())
        set_transparent_text(titulo)
        titulo.SetFont(get_display_font("huge"))
        titulo.SetForegroundColour(AppColors.PRIMARY)
        root.Add(titulo, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 18)

        subtitulo = wx.StaticText(
            self,
            label="Cartas, cantos y tablero para una partida con más presencia visual.",
        )
        set_transparent_text(subtitulo)
        subtitulo.SetFont(get_playful_font("medium"))
        subtitulo.SetForegroundColour(AppColors.TEXT_PRIMARY)
        root.Add(subtitulo, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 14)

        separador = wx.StaticLine(self)
        root.Add(separador, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 120)

        acciones = wx.FlexGridSizer(0, 2, 14, 18)
        acciones.AddGrowableCol(0, 1)
        acciones.AddGrowableCol(1, 1)
        acciones.Add(
            self._crear_boton_menu(
                self,
                "Nueva partida",
                wx.ART_GO_FORWARD,
                ButtonColors.PRIMARY,
                ButtonColors.PRIMARY_HOVER,
                self.on_nueva_partida,
            ),
            0,
            wx.EXPAND,
        )
        acciones.Add(
            self._crear_boton_menu(
                self,
                "Configuración",
                wx.ART_EXECUTABLE_FILE,
                ButtonColors.SECONDARY,
                ButtonColors.SECONDARY_HOVER,
                self.on_configuracion,
            ),
            0,
            wx.EXPAND,
        )
        acciones.Add(
            self._crear_boton_menu(
                self,
                "Reporte",
                wx.ART_LIST_VIEW,
                AppColors.BLUE,
                wx.Colour(47, 98, 112),
                self.on_reporte,
            ),
            0,
            wx.EXPAND,
        )
        acciones.Add(
            self._crear_boton_menu(
                self,
                "Ayuda",
                wx.ART_HELP_BOOK,
                ButtonColors.ACCENT,
                ButtonColors.ACCENT_HOVER,
                self.on_ayuda,
            ),
            0,
            wx.EXPAND,
        )
        acciones.Add(
            self._crear_boton_menu(
                self,
                "Créditos",
                wx.ART_TIP,
                ButtonColors.PURPLE,
                ButtonColors.PURPLE_HOVER,
                self.on_creditos,
            ),
            0,
            wx.EXPAND,
        )
        acciones.Add(
            self._crear_boton_menu(
                self,
                "Salir",
                wx.ART_QUIT,
                AppColors.ORANGE,
                wx.Colour(182, 92, 34),
                self.on_salir,
            ),
            0,
            wx.EXPAND,
        )
        root.Add(acciones, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 34)

        nota = wx.StaticText(
            self,
            label="Pantalla completa recomendada. F11 alterna el modo de visualización.",
        )
        set_transparent_text(nota)
        nota.SetFont(get_playful_font("small"))
        nota.SetForegroundColour(AppColors.TEXT_SECONDARY)
        root.Add(nota, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 28)

        root.AddStretchSpacer()

        contacto_row = wx.BoxSizer(wx.HORIZONTAL)
        contacto_row.AddStretchSpacer(1)
        contacto_row.Add(self._crear_boton_contacto(), 0, wx.RIGHT | wx.BOTTOM, 4)
        root.Add(contacto_row, 0, wx.EXPAND)
        self.SetSizer(root)

    def _crear_boton_menu(
        self,
        parent: wx.Window,
        label: str,
        art_id: str,
        color_fondo: wx.Colour,
        color_hover: wx.Colour,
        handler: callable,
    ) -> wx.Button:
        btn = wx.Button(parent, label=label, size=(300, 72), style=wx.BORDER_NONE)
        btn.SetFont(get_playful_font("large", bold=True))
        btn.SetBackgroundColour(color_fondo)
        btn.SetForegroundColour(AppColors.TEXT_LIGHT)
        icono = wx.ArtProvider.GetBitmap(art_id, wx.ART_BUTTON, (26, 26))
        if icono.IsOk():
            btn.SetBitmap(icono)
            btn.SetBitmapMargins(10, 0)
        btn.Bind(wx.EVT_ENTER_WINDOW, lambda event: btn.SetBackgroundColour(color_hover))
        btn.Bind(wx.EVT_LEAVE_WINDOW, lambda event: btn.SetBackgroundColour(color_fondo))
        btn.Bind(wx.EVT_BUTTON, handler)
        return btn

    def _crear_boton_contacto(self) -> wx.BitmapButton:
        bitmap = self._load_contact_icon()
        color_base = wx.Colour(214, 196, 167)
        color_hover = wx.Colour(196, 177, 147)
        btn = wx.BitmapButton(self, bitmap=bitmap, size=(34, 34), style=wx.BORDER_NONE)
        btn.SetBackgroundColour(color_base)
        btn.SetToolTip("Contacto del autor")
        btn.Bind(wx.EVT_ENTER_WINDOW, lambda event: btn.SetBackgroundColour(color_hover))
        btn.Bind(wx.EVT_LEAVE_WINDOW, lambda event: btn.SetBackgroundColour(color_base))
        btn.Bind(wx.EVT_BUTTON, self.on_contacto)
        return btn

    def _load_contact_icon(self) -> wx.Bitmap:
        return wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_BUTTON, (16, 16))

    def on_nueva_partida(self, event: wx.Event) -> None:
        if self.controller:
            self.controller.iniciar_nueva_partida()

    def on_configuracion(self, event: wx.Event) -> None:
        if self.controller:
            self.controller.mostrar_configuracion()

    def on_reporte(self, event: wx.Event) -> None:
        if self.controller:
            self.controller.mostrar_reporte()

    def on_ayuda(self, event: wx.Event) -> None:
        if self.controller:
            self.controller.mostrar_ayuda()

    def on_creditos(self, event: wx.Event) -> None:
        if self.controller:
            self.controller.mostrar_creditos()

    def on_contacto(self, event: wx.Event) -> None:
        if self.controller:
            self.controller.mostrar_contacto()

    def on_salir(self, event: wx.Event) -> None:
        if self.controller:
            self.controller.salir()
