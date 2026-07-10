"""Ventana principal de la aplicación."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import wx

from infrastructure.ui.branding import apply_window_icon
from infrastructure.ui.colors import AppColors

if TYPE_CHECKING:
    from controller.app_controller import AppController


class AppWindow(wx.Frame):
    """Ventana principal de la aplicación."""

    def __init__(self, title: str, controller: "AppController") -> None:
        ancho, alto = wx.GetDisplaySize()
        super().__init__(
            None,
            title=title,
            size=(ancho, alto),
            style=wx.DEFAULT_FRAME_STYLE | wx.CLIP_CHILDREN,
        )

        self.controller = controller
        self.current_view: Optional[wx.Panel] = None
        self._refresh_timer = wx.Timer(self)

        self._init_ui()
        apply_window_icon(self)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_TIMER, self._on_refresh_timer, self._refresh_timer)
        wx.CallAfter(self._activar_pantalla_completa_inicial)

    def _init_ui(self) -> None:
        self.main_panel = wx.Panel(self)
        self.main_panel.SetBackgroundColour(AppColors.BACKGROUND)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.main_sizer)

    def set_content(self, panel: wx.Panel) -> None:
        """Cambia el contenido central de la ventana."""

        panel.Hide()
        self.Freeze()
        self.main_panel.Freeze()
        if self.current_view is not None:
            previous_view = self.current_view
            self.current_view = None
            if hasattr(previous_view, "prepare_for_removal"):
                previous_view.prepare_for_removal()
            previous_view.Hide()
            self.main_sizer.Detach(previous_view)
            previous_view.Destroy()

        self.current_view = panel
        self.main_sizer.Add(self.current_view, 1, wx.EXPAND)
        self.current_view.Show()
        # El segundo Layout, ya con la vista visible, evita que wxWidgets reutilice
        # métricas de una vista anterior al encadenar varias partidas.
        self.main_panel.Layout()
        self.Layout()
        self.current_view.Layout()
        self.main_panel.Thaw()
        self.Thaw()
        # Un único refresco diferido basta una vez que la vista ya es visible.
        # Evitamos SendSizeEvent(): en vistas complejas puede encadenar EVT_SIZE
        # y provocar una tormenta de relayouts al iniciar partidas sucesivas.
        wx.CallAfter(self._refrescar_escena)
        self._solicitar_refresco_visual()

    def toggle_fullscreen(self) -> None:
        """Alterna entre pantalla completa y modo ventana."""

        self.Freeze()
        self.ShowFullScreen(not self.IsFullScreen(), wx.FULLSCREEN_ALL)
        self.Thaw()
        self._solicitar_refresco_visual()

    def _activar_pantalla_completa_inicial(self) -> None:
        if not self.IsFullScreen():
            self.Freeze()
            self.ShowFullScreen(True, wx.FULLSCREEN_ALL)
            self.Thaw()
            self._solicitar_refresco_visual()

    def _on_char_hook(self, event: wx.KeyEvent) -> None:
        tecla = event.GetKeyCode()
        if tecla == wx.WXK_F11:
            self.toggle_fullscreen()
            return

        if tecla == wx.WXK_ESCAPE and self.IsFullScreen():
            self.ShowFullScreen(False, wx.FULLSCREEN_ALL)
            self._solicitar_refresco_visual()
            return

        event.Skip()

    def _on_size(self, event: wx.SizeEvent) -> None:
        event.Skip()
        self._solicitar_refresco_visual()

    def _on_close(self, event: wx.CloseEvent) -> None:
        if self.IsFullScreen():
            self.ShowFullScreen(False, wx.FULLSCREEN_ALL)
        event.Skip()

    def _solicitar_refresco_visual(self) -> None:
        self._refresh_timer.StartOnce(30)

    def _on_refresh_timer(self, event: wx.TimerEvent) -> None:
        self._refrescar_escena()

    def _refrescar_escena(self) -> None:
        if not self:
            return

        self.Layout()
        self.main_panel.Layout()
        self.main_panel.Refresh(False)
        if self.current_view is not None:
            self.current_view.Layout()
            if hasattr(self.current_view, "refresh_visual_tree"):
                self.current_view.refresh_visual_tree()
            self.current_view.Refresh(False)
        self.Refresh(False)
