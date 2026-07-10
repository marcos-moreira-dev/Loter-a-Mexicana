"""Diálogo de configuración."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

import wx

from infrastructure.paths import asset_path
from infrastructure.ui.branding import apply_window_icon
from infrastructure.ui.colors import AppColors
from infrastructure.ui.fonts import get_display_font, get_playful_font
from model.configuracion import ModoPartida
from model.reglas import Alineacion, obtener_definicion, obtener_todas

if TYPE_CHECKING:
    from controller.app_controller import AppController

class SettingsDialog(wx.Dialog):
    """Diálogo de configuración alineado con la lógica del juego."""

    PREVIEW_SIZE = (180, 180)

    def __init__(self, parent: wx.Window, controller: "AppController") -> None:
        super().__init__(parent, title="Configuración", size=(700, 780))
        self.controller = controller
        self._cache_bitmaps: Dict[Tuple[str, int, int], wx.Bitmap] = {}
        self._opciones_alineacion: List[Tuple[str, Optional[Alineacion]]] = []
        self._opciones_modo: List[Tuple[str, ModoPartida]] = []
        self.preview_cells: List[wx.Panel] = []

        self.lbl_nombre: Optional[wx.StaticText] = None
        self.txt_nombre: Optional[wx.TextCtrl] = None
        self.choice_alineacion: Optional[wx.Choice] = None
        self.choice_modo: Optional[wx.Choice] = None
        self.chk_mostrar_oponente: Optional[wx.ToggleButton] = None
        self.spin_intervalo_segundos: Optional[wx.SpinCtrl] = None
        self.chk_musica_fondo: Optional[wx.CheckBox] = None
        self.slider_volumen_musica: Optional[wx.Slider] = None
        self.lbl_volumen_musica: Optional[wx.StaticText] = None
        self.preview_bitmap: Optional[wx.StaticBitmap] = None
        self.preview_title_label: Optional[wx.StaticText] = None
        self.preview_desc_label: Optional[wx.StaticText] = None

        self.SetBackgroundColour(AppColors.BACKGROUND)
        self.SetMinSize((650, 720))
        self._init_ui()
        apply_window_icon(self)
        self.Centre()

    def _init_ui(self) -> None:
        root_sizer = wx.BoxSizer(wx.VERTICAL)

        titulo = wx.StaticText(self, label="Configuración de la partida")
        titulo.SetFont(get_display_font("xlarge"))
        titulo.SetForegroundColour(AppColors.PRIMARY)
        root_sizer.Add(titulo, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 18)

        scroll = wx.ScrolledWindow(self, style=wx.VSCROLL | wx.BORDER_NONE)
        scroll.SetBackgroundColour(AppColors.BACKGROUND)
        scroll.SetScrollRate(0, 12)
        scroll.EnableScrolling(False, True)

        panel = wx.Panel(scroll)
        panel.SetBackgroundColour(AppColors.BACKGROUND)
        panel.SetDoubleBuffered(True)
        content_sizer = wx.BoxSizer(wx.VERTICAL)

        self.lbl_nombre = wx.StaticText(panel, label="Nombre del jugador")
        self.lbl_nombre.SetFont(get_playful_font("normal", bold=True))
        content_sizer.Add(self.lbl_nombre, 0, wx.LEFT | wx.RIGHT | wx.TOP, 18)

        self.txt_nombre = wx.TextCtrl(panel, value=self.controller.nombre_jugador)
        self._estilizar_control(self.txt_nombre, min_height=40)
        content_sizer.Add(self.txt_nombre, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 8)

        lbl_modo = wx.StaticText(panel, label="Modo de partida")
        lbl_modo.SetFont(get_playful_font("normal", bold=True))
        content_sizer.Add(lbl_modo, 0, wx.LEFT | wx.RIGHT | wx.TOP, 18)

        self._opciones_modo = self._crear_opciones_modo()
        self.choice_modo = wx.Choice(panel, choices=[label for label, _ in self._opciones_modo])
        self._estilizar_control(self.choice_modo, min_height=42)
        self.choice_modo.Bind(wx.EVT_CHOICE, self._on_modo_cambiado)
        content_sizer.Add(self.choice_modo, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 8)

        lbl_tipo = wx.StaticText(panel, label="Tipo de juego")
        lbl_tipo.SetFont(get_playful_font("normal", bold=True))
        content_sizer.Add(lbl_tipo, 0, wx.LEFT | wx.RIGHT | wx.TOP, 18)

        self._opciones_alineacion = self._crear_opciones_alineacion()
        self.choice_alineacion = wx.Choice(
            panel,
            choices=[label for label, _ in self._opciones_alineacion],
        )
        self._estilizar_control(self.choice_alineacion, min_height=42)
        self.choice_alineacion.Bind(wx.EVT_CHOICE, self._on_alineacion_cambiada)
        content_sizer.Add(self.choice_alineacion, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 8)

        preview_panel = self._crear_preview_panel(panel)
        content_sizer.Add(preview_panel, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 18)

        lbl_intervalo = wx.StaticText(panel, label="Cambio de carta (segundos)")
        lbl_intervalo.SetFont(get_playful_font("normal", bold=True))
        content_sizer.Add(lbl_intervalo, 0, wx.LEFT | wx.RIGHT | wx.TOP, 18)

        self.spin_intervalo_segundos = wx.SpinCtrl(panel, min=1, max=60, initial=max(1, self.controller.intervalo_canto_ms // 1000))
        self._estilizar_control(self.spin_intervalo_segundos, min_height=42)
        content_sizer.Add(self.spin_intervalo_segundos, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 8)

        lbl_visibilidad = wx.StaticText(panel, label="Visibilidad del rival")
        lbl_visibilidad.SetFont(get_playful_font("normal", bold=True))
        content_sizer.Add(lbl_visibilidad, 0, wx.LEFT | wx.RIGHT | wx.TOP, 18)

        toggle_row = wx.BoxSizer(wx.HORIZONTAL)
        self.chk_mostrar_oponente = wx.ToggleButton(panel, label="")
        self.chk_mostrar_oponente.SetValue(self.controller.mostrar_cartas_oponente)
        self.chk_mostrar_oponente.SetFont(get_playful_font("small", bold=True))
        self.chk_mostrar_oponente.SetMinSize((220, 40))
        self.chk_mostrar_oponente.Bind(wx.EVT_TOGGLEBUTTON, self._on_toggle_oponente)
        toggle_row.Add(self.chk_mostrar_oponente, 0, wx.RIGHT, 12)

        lbl_toggle_hint = wx.StaticText(panel, label="Solo aplica cuando existe un segundo jugador.")
        lbl_toggle_hint.SetFont(get_playful_font("small"))
        lbl_toggle_hint.SetForegroundColour(AppColors.TEXT_SECONDARY)
        toggle_row.Add(lbl_toggle_hint, 1, wx.ALIGN_CENTER_VERTICAL)
        content_sizer.Add(toggle_row, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 8)

        lbl_audio = wx.StaticText(panel, label="Música de fondo")
        lbl_audio.SetFont(get_playful_font("normal", bold=True))
        content_sizer.Add(lbl_audio, 0, wx.LEFT | wx.RIGHT | wx.TOP, 18)

        self.chk_musica_fondo = wx.CheckBox(panel, label="Reproducir música ambiental")
        self.chk_musica_fondo.SetValue(self.controller.musica_fondo_habilitada)
        self.chk_musica_fondo.SetFont(get_playful_font("normal"))
        self.chk_musica_fondo.Bind(wx.EVT_CHECKBOX, self._on_musica_fondo_cambiada)
        content_sizer.Add(self.chk_musica_fondo, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)

        volumen_row = wx.BoxSizer(wx.HORIZONTAL)
        self.slider_volumen_musica = wx.Slider(
            panel,
            value=round(self.controller.volumen_musica * 100),
            minValue=0,
            maxValue=100,
            style=wx.SL_HORIZONTAL,
        )
        self.slider_volumen_musica.SetMinSize((380, -1))
        self.slider_volumen_musica.Bind(wx.EVT_SLIDER, self._on_volumen_musica_cambiado)
        volumen_row.Add(self.slider_volumen_musica, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 12)

        self.lbl_volumen_musica = wx.StaticText(
            panel,
            label=f"{round(self.controller.volumen_musica * 100)}%",
        )
        self.lbl_volumen_musica.SetFont(get_playful_font("small", bold=True))
        self.lbl_volumen_musica.SetMinSize((64, -1))
        volumen_row.Add(self.lbl_volumen_musica, 0, wx.ALIGN_CENTER_VERTICAL)
        content_sizer.Add(volumen_row, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 8)

        self._sincronizar_controles_audio()

        panel.SetSizer(content_sizer)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll_sizer.Add(panel, 1, wx.EXPAND)
        scroll.SetSizer(scroll_sizer)
        scroll.FitInside()
        root_sizer.Add(scroll, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        botones = wx.BoxSizer(wx.HORIZONTAL)
        btn_guardar = wx.Button(self, label="Guardar", size=(140, 42), style=wx.BORDER_NONE)
        btn_guardar.SetFont(get_playful_font("normal", bold=True))
        btn_guardar.SetBackgroundColour(AppColors.SECONDARY)
        btn_guardar.SetForegroundColour(AppColors.TEXT_LIGHT)
        btn_guardar.Bind(wx.EVT_BUTTON, self._on_guardar)
        botones.Add(btn_guardar, 0, wx.RIGHT, 8)

        btn_cancelar = wx.Button(self, label="Cancelar", size=(140, 42), style=wx.BORDER_NONE)
        btn_cancelar.SetFont(get_playful_font("normal", bold=True))
        btn_cancelar.SetBackgroundColour(wx.Colour(149, 165, 166))
        btn_cancelar.SetForegroundColour(AppColors.TEXT_LIGHT)
        btn_cancelar.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CANCEL))
        botones.Add(btn_cancelar, 0)
        root_sizer.Add(botones, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 12)

        self.SetSizer(root_sizer)
        self._establecer_modo_inicial()
        self._establecer_alineacion_inicial()
        self._sincronizar_controles()
        self._actualizar_toggle_oponente()
        self._actualizar_preview_alineacion()

    def _crear_opciones_modo(self) -> List[Tuple[str, ModoPartida]]:
        return [
            ("Solo humano", ModoPartida.SOLO_HUMANO),
            ("Humano vs computadora", ModoPartida.HUMANO_VS_COMPUTADORA),
            ("Computadora vs computadora", ModoPartida.COMPUTADORA_VS_COMPUTADORA),
        ]

    def _crear_opciones_alineacion(self) -> List[Tuple[str, Optional[Alineacion]]]:
        opciones: List[Tuple[str, Optional[Alineacion]]] = [("Aleatoria", None)]
        for alineacion in obtener_todas():
            definicion = obtener_definicion(alineacion)
            opciones.append((definicion.nombre, alineacion))
        return opciones

    def _crear_preview_panel(self, panel: wx.Window) -> wx.Panel:
        preview_panel = wx.Panel(panel)
        preview_panel.SetBackgroundColour(wx.Colour(255, 249, 240))
        preview_sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_preview = wx.StaticText(preview_panel, label="Vista previa")
        lbl_preview.SetFont(get_display_font("medium"))
        lbl_preview.SetForegroundColour(AppColors.TEXT_PRIMARY)
        preview_sizer.Add(lbl_preview, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 18)

        self.preview_title_label = wx.StaticText(preview_panel, label="")
        self.preview_title_label.SetFont(get_playful_font("medium", bold=True))
        self.preview_title_label.SetForegroundColour(AppColors.SECONDARY)
        preview_sizer.Add(self.preview_title_label, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 10)

        visual_row = wx.BoxSizer(wx.HORIZONTAL)
        self.preview_bitmap = wx.StaticBitmap(
            preview_panel,
            bitmap=self._crear_bitmap_patron((), self.PREVIEW_SIZE),
        )
        visual_row.Add(self.preview_bitmap, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 18)

        pattern_grid = wx.GridSizer(4, 4, 4, 4)
        for _ in range(16):
            cell = wx.Panel(preview_panel, size=(18, 18))
            cell.SetBackgroundColour(wx.WHITE)
            self.preview_cells.append(cell)
            pattern_grid.Add(cell, 0, wx.EXPAND)
        visual_row.Add(pattern_grid, 0, wx.ALIGN_CENTER_VERTICAL)
        preview_sizer.Add(visual_row, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 16)

        self.preview_desc_label = wx.StaticText(preview_panel, label="")
        self.preview_desc_label.SetFont(get_playful_font("small"))
        self.preview_desc_label.SetForegroundColour(AppColors.TEXT_PRIMARY)
        self.preview_desc_label.Wrap(500)
        preview_sizer.Add(self.preview_desc_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 18)

        nota = wx.StaticText(
            preview_panel,
            label=(
                "Puedes dejar la alineación aleatoria o fijar manualmente "
                "el patrón que quieres jugar."
            ),
        )
        nota.SetFont(get_playful_font("small"))
        nota.SetForegroundColour(AppColors.TEXT_SECONDARY)
        nota.Wrap(500)
        preview_sizer.Add(nota, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 18)

        preview_panel.SetSizer(preview_sizer)
        return preview_panel

    def _establecer_modo_inicial(self) -> None:
        if self.choice_modo is None:
            return

        seleccion = 0
        for indice, (_, modo) in enumerate(self._opciones_modo):
            if modo == self.controller.modo_partida:
                seleccion = indice
                break
        self.choice_modo.SetSelection(seleccion)

    def _establecer_alineacion_inicial(self) -> None:
        if self.choice_alineacion is None:
            return

        seleccion = 0
        for indice, (_, alineacion) in enumerate(self._opciones_alineacion):
            if alineacion == self.controller.alineacion_preferida:
                seleccion = indice
                break
        self.choice_alineacion.SetSelection(seleccion)

    def _obtener_modo_seleccionado(self) -> ModoPartida:
        if self.choice_modo is None:
            return ModoPartida.HUMANO_VS_COMPUTADORA

        indice = self.choice_modo.GetSelection()
        if indice == wx.NOT_FOUND:
            return ModoPartida.HUMANO_VS_COMPUTADORA
        return self._opciones_modo[indice][1]

    def _obtener_alineacion_seleccionada(self) -> Optional[Alineacion]:
        if self.choice_alineacion is None:
            return None

        indice = self.choice_alineacion.GetSelection()
        if indice == wx.NOT_FOUND:
            return None
        return self._opciones_alineacion[indice][1]

    def _sincronizar_controles(self) -> None:
        modo = self._obtener_modo_seleccionado()
        hay_humano = modo != ModoPartida.COMPUTADORA_VS_COMPUTADORA
        hay_segundo_jugador = modo != ModoPartida.SOLO_HUMANO

        if self.lbl_nombre is not None:
            self.lbl_nombre.Enable(hay_humano)
        if self.txt_nombre is not None:
            self.txt_nombre.Enable(hay_humano)
        if self.chk_mostrar_oponente is not None:
            self.chk_mostrar_oponente.Enable(hay_segundo_jugador)
            if not hay_segundo_jugador:
                self.chk_mostrar_oponente.SetValue(False)
            self._actualizar_toggle_oponente()

    def _actualizar_preview_alineacion(self) -> None:
        if self.preview_bitmap is None or self.preview_title_label is None or self.preview_desc_label is None:
            return

        alineacion = self._obtener_alineacion_seleccionada()
        if alineacion is None:
            self.preview_title_label.SetLabel("Aleatoria")
            self.preview_desc_label.SetLabel(
                "La partida elegirá una de las cinco alineaciones oficiales cada vez "
                "que empieces un juego nuevo."
            )
            self.preview_bitmap.SetBitmap(self._crear_bitmap_patron((), self.PREVIEW_SIZE))
            self._render_patron_preview(())
            self.Layout()
            return

        definicion = obtener_definicion(alineacion)
        self.preview_title_label.SetLabel(definicion.nombre)
        self.preview_desc_label.SetLabel(definicion.descripcion)
        self.preview_bitmap.SetBitmap(
            self._obtener_bitmap_alineacion(alineacion, definicion.patron_referencia)
        )
        self._render_patron_preview(definicion.patron_referencia)
        self.Layout()

    def _obtener_bitmap_alineacion(
        self,
        alineacion: Alineacion,
        patron_referencia: Tuple[int, ...],
    ) -> wx.Bitmap:
        definicion = obtener_definicion(alineacion)
        if definicion.imagen_referencia:
            ruta = asset_path("alignments", definicion.imagen_referencia)
            bitmap = self._cargar_bitmap(ruta, self.PREVIEW_SIZE)
            if bitmap is not None:
                return bitmap
        return self._crear_bitmap_patron(patron_referencia, self.PREVIEW_SIZE)

    def _render_patron_preview(self, indices_activos: Tuple[int, ...]) -> None:
        activos = set(indices_activos)
        for indice, cell in enumerate(self.preview_cells):
            cell.SetBackgroundColour(AppColors.ACCENT if indice in activos else wx.WHITE)
            cell.Refresh()

    def _cargar_bitmap(self, ruta: Path, size: Tuple[int, int]) -> Optional[wx.Bitmap]:
        clave = (str(ruta), size[0], size[1])
        if clave in self._cache_bitmaps:
            return self._cache_bitmaps[clave]

        if not ruta.exists():
            return None

        imagen = wx.Image(str(ruta), wx.BITMAP_TYPE_ANY)
        if not imagen.IsOk():
            return None

        bitmap = imagen.Scale(size[0], size[1], wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self._cache_bitmaps[clave] = bitmap
        return bitmap

    def _crear_bitmap_patron(self, indices_activos: Tuple[int, ...], size: Tuple[int, int]) -> wx.Bitmap:
        clave = (f"pattern:{','.join(map(str, indices_activos))}", size[0], size[1])
        if clave in self._cache_bitmaps:
            return self._cache_bitmaps[clave]

        bitmap = wx.Bitmap(size[0], size[1])
        dc = wx.MemoryDC()
        dc.SelectObject(bitmap)
        dc.SetBackground(wx.Brush(wx.WHITE))
        dc.Clear()

        margen = 14
        separacion = 8
        celda_ancho = (size[0] - (2 * margen) - (3 * separacion)) // 4
        celda_alto = (size[1] - (2 * margen) - (3 * separacion)) // 4
        activos = set(indices_activos)

        for indice in range(16):
            fila = indice // 4
            columna = indice % 4
            x = margen + columna * (celda_ancho + separacion)
            y = margen + fila * (celda_alto + separacion)
            color = AppColors.ACCENT if indice in activos else wx.Colour(236, 240, 241)
            dc.SetBrush(wx.Brush(color))
            dc.SetPen(wx.Pen(wx.Colour(189, 195, 199), 1))
            dc.DrawRectangle(x, y, celda_ancho, celda_alto)

        dc.SelectObject(wx.NullBitmap)
        self._cache_bitmaps[clave] = bitmap
        return bitmap

    def _on_modo_cambiado(self, event: wx.Event) -> None:
        self._sincronizar_controles()
        event.Skip()

    def _on_toggle_oponente(self, event: wx.Event) -> None:
        self._actualizar_toggle_oponente()
        event.Skip()

    def _on_alineacion_cambiada(self, event: wx.Event) -> None:
        self._actualizar_preview_alineacion()
        event.Skip()

    def _on_musica_fondo_cambiada(self, event: wx.Event) -> None:
        self._sincronizar_controles_audio()
        event.Skip()

    def _on_volumen_musica_cambiado(self, event: wx.Event) -> None:
        if self.slider_volumen_musica is not None and self.lbl_volumen_musica is not None:
            self.lbl_volumen_musica.SetLabel(f"{self.slider_volumen_musica.GetValue()}%")
        event.Skip()

    def _sincronizar_controles_audio(self) -> None:
        habilitada = (
            self.chk_musica_fondo.GetValue()
            if self.chk_musica_fondo is not None
            else self.controller.musica_fondo_habilitada
        )
        if self.slider_volumen_musica is not None:
            self.slider_volumen_musica.Enable(habilitada)
        if self.lbl_volumen_musica is not None:
            self.lbl_volumen_musica.Enable(habilitada)

    def _estilizar_control(self, control: wx.Control, *, min_height: int) -> None:
        control.SetFont(get_playful_font("normal"))
        control.SetMinSize((-1, min_height))
        try:
            control.SetBackgroundColour(wx.Colour(255, 250, 241))
            control.SetForegroundColour(AppColors.TEXT_PRIMARY)
        except Exception:
            return

    def _actualizar_toggle_oponente(self) -> None:
        if self.chk_mostrar_oponente is None:
            return

        if not self.chk_mostrar_oponente.IsEnabled():
            self.chk_mostrar_oponente.SetLabel("No disponible")
            self.chk_mostrar_oponente.SetBackgroundColour(wx.Colour(176, 182, 181))
            self.chk_mostrar_oponente.SetForegroundColour(AppColors.TEXT_LIGHT)
            return

        visible = self.chk_mostrar_oponente.GetValue()
        self.chk_mostrar_oponente.SetLabel("Cartón visible" if visible else "Cartón oculto")
        self.chk_mostrar_oponente.SetBackgroundColour(
            AppColors.SECONDARY if visible else wx.Colour(149, 165, 166)
        )
        self.chk_mostrar_oponente.SetForegroundColour(AppColors.TEXT_LIGHT)

    def _on_guardar(self, event: wx.Event) -> None:
        nombre = self.txt_nombre.GetValue().strip() if self.txt_nombre is not None else "Jugador 1"
        modo = self._obtener_modo_seleccionado()
        if modo != ModoPartida.COMPUTADORA_VS_COMPUTADORA and not nombre:
            wx.MessageBox("Debes ingresar un nombre para continuar.", "Error", wx.OK | wx.ICON_ERROR)
            return

        mostrar_oponente = (
            self.chk_mostrar_oponente.GetValue()
            if self.chk_mostrar_oponente is not None and modo != ModoPartida.SOLO_HUMANO
            else False
        )
        intervalo_segundos = (
            self.spin_intervalo_segundos.GetValue()
            if self.spin_intervalo_segundos is not None
            else 6
        )

        self.controller.actualizar_configuracion(
            nombre=nombre or self.controller.nombre_jugador,
            mostrar_cartas_oponente=mostrar_oponente,
            intervalo_canto_ms=max(1, intervalo_segundos) * 1000,
            alineacion_preferida=self._obtener_alineacion_seleccionada(),
            modo_partida=modo,
            musica_fondo_habilitada=(
                self.chk_musica_fondo.GetValue()
                if self.chk_musica_fondo is not None
                else self.controller.musica_fondo_habilitada
            ),
            volumen_musica=(
                self.slider_volumen_musica.GetValue() / 100.0
                if self.slider_volumen_musica is not None
                else self.controller.volumen_musica
            ),
        )
        self.EndModal(wx.ID_OK)
