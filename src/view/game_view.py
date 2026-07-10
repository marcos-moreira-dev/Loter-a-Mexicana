"""Panel principal de juego."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

try:
    import winsound
except ImportError:  # pragma: no cover - solo aplica fuera de Windows.
    winsound = None

import wx

from infrastructure.paths import asset_path
from infrastructure.ui.backgrounds import ImageBackgroundPanel, set_transparent_text
from infrastructure.ui.colors import AppColors
from infrastructure.ui.fonts import get_display_font, get_playful_font
from model.partida import Partida, ResultadoMarcado
from model.reglas import DefinicionAlineacion, obtener_definicion

if TYPE_CHECKING:
    from controller.app_controller import GameController

class GamePanel(ImageBackgroundPanel):
    """Vista principal de la partida."""

    HUMAN_BUTTON_SIZE = (90, 90)
    OPPONENT_BUTTON_SIZE = (52, 52)
    OPPONENT_GRID_GAP = 2
    CURRENT_CARD_SIZE = (204, 240)
    PATTERN_IMAGE_SIZE = (148, 148)
    HISTORY_PANEL_SIZE = (278, 404)
    LEFT_PANEL_WIDTH = 452
    CENTER_PANEL_WIDTH = 396
    RIGHT_PANEL_WIDTH = 278
    SAFE_MARGIN_X = 24
    SAFE_MARGIN_TOP = 69
    SAFE_MARGIN_BOTTOM = 14
    LEFT_INFO_TOP_GAP = 30
    STATUS_WORKSPACE_WIDTH = 205
    PATTERN_WORKSPACE_WIDTH = 250
    HERO_COLUMNS_GAP = 32
    ACTIONS_PANEL_WIDTH = 216

    def __init__(self, parent: wx.Window, controller: "GameController") -> None:
        super().__init__(
            parent,
            asset_path("backgrounds", "juegobackground.png"),
            image_opacity=0.42,
            overlay_color=wx.Colour(
                AppColors.BACKGROUND.Red(),
                AppColors.BACKGROUND.Green(),
                AppColors.BACKGROUND.Blue(),
                36,
            ),
            base_color=AppColors.BACKGROUND,
        )
        self.controller = controller
        self.partida: Optional[Partida] = None
        self._cache_bitmaps: Dict[Tuple[str, int, int], wx.Bitmap] = {}
        self._pausado = False
        self._human_hidden_indices: set[int] = set()
        self._human_hidden_tokens: Dict[int, int] = {}
        self._aviso_token = 0
        self._ultima_carta_reproducida_id: Optional[int] = None
        self._button_state_cache: Dict[int, Tuple[object, ...]] = {}
        self._last_historial_text = ""
        self._last_status_text = ""
        self._last_pattern_key: Optional[Tuple[int, ...]] = None
        self._last_current_card_key: Optional[Tuple[Optional[int], str]] = None
        self._last_human_label = ""
        self._last_opponent_label = ""
        self._last_opponent_visible: Optional[bool] = None
        self._layout_pending = True
        self._center_sizer: Optional[wx.BoxSizer] = None
        self._active = True
        self._layout_refresh_token = 0

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self.timer)
        self.Bind(wx.EVT_SHOW, self._on_show)

        self.botones_humano: List[wx.Button] = []
        self.botones_oponente: List[wx.Button] = []
        self.pattern_cells: List[wx.Panel] = []

        self.current_card_bitmap: Optional[wx.StaticBitmap] = None
        self.current_card_label: Optional[wx.StaticText] = None
        self.status_label: Optional[wx.StaticText] = None
        self.aviso_label: Optional[wx.StaticText] = None
        self.historial_text: Optional[wx.TextCtrl] = None
        self.pattern_name_label: Optional[wx.StaticText] = None
        self.pattern_desc_label: Optional[wx.StaticText] = None
        self.pattern_bitmap: Optional[wx.StaticBitmap] = None
        self.human_label: Optional[wx.StaticText] = None
        self.opponent_label: Optional[wx.StaticText] = None
        self.btn_loteria: Optional[wx.Button] = None
        self.btn_pausa: Optional[wx.Button] = None
        self.opponent_section: Optional[wx.BoxSizer] = None

        self.back_image_path = self._resolver_recurso(
            asset_path("cards", "back_java.png"),
            asset_path("cards", "back.png"),
        )
        self.human_marker_path = self._resolver_recurso(
            asset_path("markers", "frejol.png"),
            asset_path("cards", "match.png"),
        )
        self.opponent_marker_path = self._resolver_recurso(
            asset_path("cards", "match.png"),
            asset_path("markers", "frejol.png"),
        )
        self.audio_dir = asset_path("sounds", "cartas")
        self.audio_paths: Dict[int, List[Path]] = self._indexar_audios_cartas()

        self._init_ui()
        wx.CallAfter(self._iniciar_primera_carta)

    def _init_ui(self) -> None:
        """Construye la interfaz del juego."""

        root_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self._crear_panel_izquierdo(), 0, wx.EXPAND | wx.RIGHT, 12)
        main_sizer.Add(self._crear_divisor_vertical(), 0, wx.EXPAND | wx.RIGHT, 12)
        main_sizer.Add(self._crear_panel_centro(), 0, wx.EXPAND | wx.RIGHT, 12)
        main_sizer.Add(self._crear_divisor_vertical(), 0, wx.EXPAND | wx.RIGHT, 12)
        main_sizer.Add(self._crear_panel_derecho(), 0, wx.EXPAND)

        centered_row = wx.BoxSizer(wx.HORIZONTAL)
        centered_row.AddStretchSpacer(1)
        centered_row.Add(main_sizer, 0)
        centered_row.AddStretchSpacer(1)

        root_sizer.AddSpacer(self.SAFE_MARGIN_TOP)
        root_sizer.AddStretchSpacer(1)
        root_sizer.Add(centered_row, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, self.SAFE_MARGIN_X)
        root_sizer.AddStretchSpacer(2)
        root_sizer.AddSpacer(self.SAFE_MARGIN_BOTTOM)
        self.SetSizer(root_sizer)

    def _crear_panel_izquierdo(self) -> wx.Sizer:
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.SetMinSize((self.LEFT_PANEL_WIDTH, -1))

        # El título pertenece a toda la micro-región de la carta actual.
        # Se mantiene alineado con el borde izquierdo de la imagen y se separa
        # del contenido para que funcione visualmente como encabezado.
        sizer.Add(
            self._crear_encabezado(self, "Carta actual", AppColors.PRIMARY, wx.ART_TIP, "xlarge"),
            0,
            wx.BOTTOM | wx.ALIGN_LEFT,
            26,
        )

        hero_sizer = wx.BoxSizer(wx.HORIZONTAL)

        carta_visual = wx.BoxSizer(wx.VERTICAL)

        self.current_card_bitmap = wx.StaticBitmap(self, bitmap=wx.Bitmap(*self.CURRENT_CARD_SIZE))
        carta_visual.Add(self.current_card_bitmap, 0, wx.BOTTOM | wx.ALIGN_LEFT, 10)

        self.current_card_label = wx.StaticText(self, label="Esperando primera carta...")
        set_transparent_text(self.current_card_label)
        self.current_card_label.SetFont(get_playful_font("medium", bold=True))
        self.current_card_label.SetForegroundColour(AppColors.TEXT_PRIMARY)
        carta_visual.Add(self.current_card_label, 0, wx.ALIGN_LEFT)
        hero_sizer.Add(carta_visual, 0, wx.ALIGN_TOP)
        hero_sizer.AddSpacer(self.HERO_COLUMNS_GAP)

        acciones_sizer = wx.BoxSizer(wx.VERTICAL)
        acciones_sizer.SetMinSize((self.ACTIONS_PANEL_WIDTH, -1))

        acciones_titulo = wx.StaticText(self, label="Controles de la partida")
        set_transparent_text(acciones_titulo)
        acciones_titulo.SetFont(get_display_font("medium"))
        acciones_titulo.SetForegroundColour(AppColors.BLUE)
        acciones_sizer.Add(acciones_titulo, 0, wx.BOTTOM | wx.ALIGN_LEFT, 12)

        self.btn_loteria = wx.Button(self, label="Cantar lotería", size=(self.ACTIONS_PANEL_WIDTH, 46), style=wx.BORDER_NONE)
        self.btn_loteria.SetFont(get_playful_font("medium", bold=True))
        self.btn_loteria.SetBackgroundColour(AppColors.SECONDARY)
        self.btn_loteria.SetForegroundColour(AppColors.TEXT_LIGHT)
        self.btn_loteria.Bind(wx.EVT_BUTTON, self._on_loteria)
        acciones_sizer.Add(self.btn_loteria, 0, wx.BOTTOM | wx.ALIGN_LEFT, 10)

        self.btn_pausa = wx.Button(self, label="Pausar", size=(self.ACTIONS_PANEL_WIDTH, 42), style=wx.BORDER_NONE)
        self.btn_pausa.SetFont(get_playful_font("normal", bold=True))
        self.btn_pausa.SetBackgroundColour(AppColors.BLUE)
        self.btn_pausa.SetForegroundColour(AppColors.TEXT_LIGHT)
        self.btn_pausa.Bind(wx.EVT_BUTTON, self._on_pausar)
        acciones_sizer.Add(self.btn_pausa, 0, wx.BOTTOM | wx.ALIGN_LEFT, 10)

        botones = wx.BoxSizer(wx.HORIZONTAL)
        btn_reiniciar = wx.Button(self, label="Reiniciar", size=(104, 38), style=wx.BORDER_NONE)
        btn_reiniciar.SetFont(get_playful_font("small", bold=True))
        btn_reiniciar.SetBackgroundColour(AppColors.ORANGE)
        btn_reiniciar.SetForegroundColour(AppColors.TEXT_LIGHT)
        btn_reiniciar.Bind(wx.EVT_BUTTON, self._on_reiniciar)
        botones.Add(btn_reiniciar, 0, wx.RIGHT, 8)

        btn_menu = wx.Button(self, label="Menú", size=(104, 38), style=wx.BORDER_NONE)
        btn_menu.SetFont(get_playful_font("small", bold=True))
        btn_menu.SetBackgroundColour(wx.Colour(149, 165, 166))
        btn_menu.SetForegroundColour(AppColors.TEXT_LIGHT)
        btn_menu.Bind(wx.EVT_BUTTON, self._on_menu)
        botones.Add(btn_menu, 0)
        acciones_sizer.Add(botones, 0, wx.BOTTOM | wx.ALIGN_LEFT, 12)

        self.aviso_label = wx.StaticText(self, label="")
        set_transparent_text(self.aviso_label)
        self.aviso_label.SetFont(get_playful_font("small"))
        self.aviso_label.SetForegroundColour(AppColors.PRIMARY)
        self.aviso_label.SetMinSize((self.ACTIONS_PANEL_WIDTH, -1))
        self.aviso_label.Wrap(self.ACTIONS_PANEL_WIDTH)
        acciones_sizer.Add(self.aviso_label, 0, wx.EXPAND)
        hero_sizer.Add(acciones_sizer, 1, wx.TOP | wx.EXPAND, 8)
        sizer.Add(hero_sizer, 0, wx.BOTTOM | wx.EXPAND, 18)

        # Conserva la posición actual de los micro-workspaces inferiores
        # (estado y tipo de juego), pero permite que Carta actual respire
        # más arriba sin desplazar el resto de la pantalla.
        sizer.AddSpacer(self.LEFT_INFO_TOP_GAP)

        divisor = wx.StaticLine(self)
        sizer.Add(divisor, 0, wx.BOTTOM | wx.EXPAND, 16)

        info_sizer = wx.BoxSizer(wx.HORIZONTAL)

        estado_sizer = wx.BoxSizer(wx.VERTICAL)
        estado_sizer.Add(
            self._crear_encabezado(self, "Estado de la partida", AppColors.TEXT_PRIMARY, wx.ART_INFORMATION, "medium"),
            0,
            wx.BOTTOM,
            8,
        )

        self.status_label = wx.StaticText(self, label="")
        set_transparent_text(self.status_label)
        self.status_label.SetFont(get_playful_font("normal"))
        self.status_label.SetForegroundColour(AppColors.TEXT_PRIMARY)
        self.status_label.SetMinSize((self.STATUS_WORKSPACE_WIDTH, -1))
        self.status_label.SetMaxSize((self.STATUS_WORKSPACE_WIDTH, -1))
        self.status_label.Wrap(self.STATUS_WORKSPACE_WIDTH)
        estado_sizer.Add(self.status_label, 0, wx.EXPAND)
        info_sizer.Add(estado_sizer, 1, wx.EXPAND)
        info_sizer.Add(self._crear_divisor_vertical(), 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 12)

        patron_wrapper_sizer = wx.BoxSizer(wx.VERTICAL)

        patron_wrapper_sizer.Add(
            self._crear_encabezado(self, "Tipo de juego", AppColors.TEXT_PRIMARY, wx.ART_HELP, "medium"),
            0,
            wx.BOTTOM,
            8,
        )

        self.pattern_name_label = wx.StaticText(self, label="")
        set_transparent_text(self.pattern_name_label)
        self.pattern_name_label.SetFont(get_playful_font("normal", bold=True))
        self.pattern_name_label.SetForegroundColour(AppColors.SECONDARY)
        patron_wrapper_sizer.Add(self.pattern_name_label, 0, wx.BOTTOM, 8)

        self.pattern_desc_label = wx.StaticText(self, label="")
        set_transparent_text(self.pattern_desc_label)
        self.pattern_desc_label.SetFont(get_playful_font("small"))
        self.pattern_desc_label.SetForegroundColour(AppColors.TEXT_PRIMARY)
        self.pattern_desc_label.SetMinSize((self.PATTERN_WORKSPACE_WIDTH, -1))
        self.pattern_desc_label.SetMaxSize((self.PATTERN_WORKSPACE_WIDTH, -1))
        self.pattern_desc_label.Wrap(self.PATTERN_WORKSPACE_WIDTH)
        patron_wrapper_sizer.Add(self.pattern_desc_label, 0, wx.BOTTOM | wx.EXPAND, 10)

        patron_visual = wx.BoxSizer(wx.HORIZONTAL)
        self.pattern_bitmap = wx.StaticBitmap(
            self,
            bitmap=self._crear_bitmap_patron((), self.PATTERN_IMAGE_SIZE),
        )
        patron_visual.Add(self.pattern_bitmap, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 12)

        patron_grid = wx.GridSizer(4, 4, 4, 4)
        for _ in range(16):
            cell = wx.Panel(self, size=(18, 18))
            cell.SetBackgroundColour(wx.WHITE)
            self.pattern_cells.append(cell)
            patron_grid.Add(cell, 0, wx.EXPAND)
        patron_visual.Add(patron_grid, 0, wx.ALIGN_CENTER_VERTICAL)
        patron_wrapper_sizer.Add(patron_visual, 0, wx.ALIGN_CENTER_HORIZONTAL)

        info_sizer.Add(patron_wrapper_sizer, 1, wx.EXPAND)

        sizer.Add(info_sizer, 0, wx.EXPAND)
        return sizer

    def _crear_panel_centro(self) -> wx.Sizer:
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._center_sizer = sizer
        sizer.SetMinSize((self.CENTER_PANEL_WIDTH, -1))

        self.human_label = wx.StaticText(self, label="Tu cartón")
        set_transparent_text(self.human_label)
        self.human_label.SetFont(get_display_font("large"))
        self.human_label.SetForegroundColour(AppColors.SECONDARY)
        sizer.Add(self.human_label, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 12)

        human_grid = wx.GridSizer(4, 4, 4, 4)
        for indice in range(16):
            boton = wx.Button(self, size=self.HUMAN_BUTTON_SIZE, style=wx.BORDER_NONE)
            boton.SetFont(get_playful_font("small", bold=True))
            boton.Bind(wx.EVT_BUTTON, lambda event, idx=indice: self._on_human_click(idx))
            self.botones_humano.append(boton)
            human_grid.Add(boton, 0, wx.EXPAND)
        sizer.Add(human_grid, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.opponent_section = wx.BoxSizer(wx.VERTICAL)

        self.opponent_label = wx.StaticText(self, label="Computadora")
        set_transparent_text(self.opponent_label)
        self.opponent_label.SetFont(get_display_font("medium"))
        self.opponent_label.SetForegroundColour(AppColors.ORANGE)
        self.opponent_section.Add(self.opponent_label, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 8)

        opponent_grid = wx.GridSizer(4, 4, self.OPPONENT_GRID_GAP, self.OPPONENT_GRID_GAP)
        for _ in range(16):
            boton = wx.Button(self, size=self.OPPONENT_BUTTON_SIZE, style=wx.BORDER_NONE)
            boton.Enable(False)
            boton.SetFont(get_playful_font("small"))
            self.botones_oponente.append(boton)
            opponent_grid.Add(boton, 0, wx.EXPAND)
        self.opponent_section.Add(opponent_grid, 0, wx.ALIGN_CENTER_HORIZONTAL)

        sizer.Add(self.opponent_section, 0, wx.ALIGN_CENTER_HORIZONTAL)

        return sizer

    def _crear_panel_derecho(self) -> wx.Sizer:
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.SetMinSize((self.RIGHT_PANEL_WIDTH, -1))

        sizer.Add(
            self._crear_encabezado(self, "Historial de cartas", AppColors.ORANGE, wx.ART_LIST_VIEW, "large"),
            0,
            wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL,
            12,
        )

        self.historial_text = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.BORDER_SIMPLE | wx.VSCROLL,
            size=self.HISTORY_PANEL_SIZE,
        )
        self.historial_text.SetFont(get_playful_font("normal"))
        self.historial_text.SetBackgroundColour(wx.Colour(255, 252, 246))
        self.historial_text.SetForegroundColour(AppColors.TEXT_PRIMARY)
        sizer.Add(self.historial_text, 0, wx.EXPAND)
        sizer.AddStretchSpacer(1)

        return sizer

    def _crear_divisor_vertical(self) -> wx.StaticLine:
        divisor = wx.StaticLine(self, style=wx.LI_VERTICAL)
        divisor.SetMinSize((2, -1))
        return divisor

    def render(self, partida: Partida) -> None:
        """Renderiza toda la vista segun el estado de la partida."""

        self.partida = partida
        definicion = obtener_definicion(partida.alineacion_actual) if partida.alineacion_actual else None
        layout_required = self._layout_pending
        should_freeze = self.IsShownOnScreen() and hasattr(self, "Freeze")
        if should_freeze:
            self.Freeze()

        try:
            jugador_principal = partida.jugador_principal
            if self.human_label and jugador_principal:
                prefijo = "Tu cartón" if partida.permite_interaccion_humana else "Jugador 1"
                layout_required |= self._set_label_if_changed(
                    self.human_label,
                    f"{prefijo}: {jugador_principal.nombre}",
                    "_last_human_label",
                )

            hay_oponente = partida.jugador_oponente is not None
            if self._center_sizer and self.opponent_section and hay_oponente != self._last_opponent_visible:
                self._center_sizer.Show(self.opponent_section, hay_oponente, recursive=True)
                self._last_opponent_visible = hay_oponente
                layout_required = True
            if self.opponent_label and partida.jugador_oponente:
                visibilidad = "visible" if partida.configuracion.mostrar_cartas_oponente else "oculto"
                prefijo = "Oponente" if partida.permite_interaccion_humana else "Jugador 2"
                layout_required |= self._set_label_if_changed(
                    self.opponent_label,
                    f"{prefijo}: {partida.jugador_oponente.nombre} ({visibilidad})",
                    "_last_opponent_label",
                )

            self._render_carton_humano()
            self._render_carton_oponente()
            self._render_carta_actual()
            self._render_historial()
            layout_required |= self._render_alineacion(definicion)

            if self.status_label:
                ganador = partida.ganador.nombre if partida.ganador else "Nadie"
                status_text = (
                    "Estado: "
                    f"{partida.estado.name}\n"
                    f"Modo: {self._describir_modo_partida(partida)}\n"
                    f"Tipo: {partida.nombre_alineacion}\n"
                    f"Cartas cantadas: {len(partida.historial_cartas)}/54\n"
                    f"Cartas restantes: {partida.cartas_restantes}\n"
                    f"Ganador actual: {ganador}"
                )
                if status_text != self._last_status_text:
                    self.status_label.SetLabel(status_text)
                    self.status_label.Wrap(self.STATUS_WORKSPACE_WIDTH)
                    self._last_status_text = status_text
                    layout_required = True

            if self.btn_loteria:
                if self.btn_loteria.IsShown() != partida.permite_interaccion_humana:
                    self.btn_loteria.Show(partida.permite_interaccion_humana)
                    layout_required = True
                self.btn_loteria.Enable(partida.permite_interaccion_humana and partida.partida_en_curso)

            if self.btn_pausa:
                nuevo_label = "Continuar" if self._pausado else "Pausar"
                if self.btn_pausa.GetLabel() != nuevo_label:
                    self.btn_pausa.SetLabel(nuevo_label)

            if partida.partida_en_curso and not self._pausado and not self.timer.IsRunning():
                self.timer.Start(self.controller.obtener_intervalo_canto_ms())
            if partida.partida_finalizada:
                self.detener_timer()
                self.deshabilitar_controles()

            if layout_required:
                self.Layout()
                self._layout_pending = False
        finally:
            if should_freeze:
                self.Thaw()

        self._reproducir_audio_carta_actual()

    def _render_carton_humano(self) -> None:
        if not self.partida or not self.partida.jugador_principal:
            return

        carta_actual_id = self.partida.carta_actual.id if self.partida.carta_actual else None
        jugador_principal = self.partida.jugador_principal
        assert jugador_principal is not None
        marcador = self.opponent_marker_path if jugador_principal.es_automatico else self.human_marker_path

        for indice, casilla in enumerate(jugador_principal.carton.casillas):
            imagen = casilla.carta.imagen_path
            if indice in self._human_hidden_indices and not casilla.marcada:
                imagen = self.back_image_path
            elif casilla.marcada:
                imagen = marcador

            self._pintar_boton_carta(
                self.botones_humano[indice],
                imagen,
                self.HUMAN_BUTTON_SIZE,
                casilla.carta.nombre,
                marcada=casilla.marcada,
                resaltar=(carta_actual_id == casilla.carta.id and not casilla.marcada),
                habilitado=self.partida.permite_interaccion_humana and self.partida.partida_en_curso,
            )

    def _render_carton_oponente(self) -> None:
        if not self.partida or not self.partida.jugador_oponente:
            return

        visible = self.partida.configuracion.mostrar_cartas_oponente
        carta_actual_id = self.partida.carta_actual.id if self.partida.carta_actual else None

        for indice, casilla in enumerate(self.partida.jugador_oponente.carton.casillas):
            if casilla.marcada:
                imagen = self.opponent_marker_path
            elif visible:
                imagen = casilla.carta.imagen_path
            else:
                imagen = self.back_image_path

            etiqueta = casilla.carta.nombre if visible else "Carta oculta"
            self._pintar_boton_carta(
                self.botones_oponente[indice],
                imagen,
                self.OPPONENT_BUTTON_SIZE,
                etiqueta,
                marcada=casilla.marcada,
                resaltar=(visible and carta_actual_id == casilla.carta.id and not casilla.marcada),
                habilitado=False,
            )

    def _render_carta_actual(self) -> None:
        if not self.current_card_bitmap or not self.current_card_label or not self.partida:
            return

        carta = self.partida.carta_actual
        if carta is None:
            clave = (None, "Esperando primera carta...")
            if self._last_current_card_key == clave:
                return
            self.current_card_label.SetLabel(clave[1])
            self.current_card_bitmap.SetBitmap(wx.Bitmap(*self.CURRENT_CARD_SIZE))
            self._last_current_card_key = clave
            return

        texto = f"#{carta.id:02d} - {carta.nombre}"
        clave = (carta.id, texto)
        if self._last_current_card_key == clave:
            return
        self.current_card_label.SetLabel(texto)
        bitmap = self._load_bitmap(carta.imagen_path, self.CURRENT_CARD_SIZE)
        self.current_card_bitmap.SetBitmap(bitmap or wx.Bitmap(*self.CURRENT_CARD_SIZE))
        self._last_current_card_key = clave

    def _crear_encabezado(
        self,
        panel: wx.Window,
        texto: str,
        color: wx.Colour,
        art_id: str,
        size: str,
    ) -> wx.BoxSizer:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        icon_size = 28 if size in {"xlarge", "title", "huge"} else 24
        icono = wx.ArtProvider.GetBitmap(art_id, wx.ART_OTHER, (icon_size, icon_size))
        if icono.IsOk():
            sizer.Add(wx.StaticBitmap(panel, bitmap=icono), 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 8)

        titulo = wx.StaticText(panel, label=texto)
        set_transparent_text(titulo)
        titulo.SetFont(get_display_font(size))
        titulo.SetForegroundColour(color)
        sizer.Add(titulo, 0, wx.ALIGN_CENTER_VERTICAL)
        return sizer

    def _set_label_if_changed(
        self,
        widget: wx.StaticText,
        nuevo_texto: str,
        cache_attr: str,
    ) -> bool:
        if getattr(self, cache_attr) == nuevo_texto:
            return False

        widget.SetLabel(nuevo_texto)
        setattr(self, cache_attr, nuevo_texto)
        return True

    def _reproducir_audio_carta_actual(self) -> None:
        if not self.partida or not self.partida.carta_actual:
            return

        carta_id = self.partida.carta_actual.id
        if carta_id == self._ultima_carta_reproducida_id:
            return

        ruta_audio = self._seleccionar_audio_carta(carta_id)
        if ruta_audio and ruta_audio.exists():
            self._reproducir_audio(ruta_audio)
            self._ultima_carta_reproducida_id = carta_id

    def _reproducir_audio(self, ruta_audio: Path) -> None:
        if winsound is None:
            return

        try:
            winsound.PlaySound(
                str(ruta_audio),
                winsound.SND_ASYNC | winsound.SND_FILENAME | winsound.SND_NODEFAULT,
            )
        except RuntimeError:
            return

    def _detener_audio(self) -> None:
        if winsound is None:
            return

        try:
            winsound.PlaySound(None, 0)
        except RuntimeError:
            return

    def _render_historial(self) -> None:
        if not self.historial_text or not self.partida:
            return

        lineas = ["Cartas cantadas:", ""]
        for indice, carta in enumerate(self.partida.historial_cartas, start=1):
            lineas.append(f"{indice:02d}. #{carta.id:02d} {carta.nombre}")
        texto = "\n".join(lineas)
        if texto == self._last_historial_text:
            return
        self.historial_text.SetValue(texto)
        self._last_historial_text = texto

    def _render_alineacion(self, definicion: Optional[DefinicionAlineacion]) -> bool:
        if definicion is None:
            return False

        patron_key = (definicion.nombre, definicion.descripcion, *definicion.patron_referencia)
        if patron_key == self._last_pattern_key:
            return False

        if self.pattern_name_label:
            self.pattern_name_label.SetLabel(definicion.nombre)
        if self.pattern_desc_label:
            self.pattern_desc_label.SetLabel(definicion.descripcion)
            self.pattern_desc_label.Wrap(self.PATTERN_WORKSPACE_WIDTH)
        if self.pattern_bitmap:
            self.pattern_bitmap.SetBitmap(self._obtener_bitmap_alineacion(definicion))
        self._render_patron(definicion.patron_referencia)
        self._last_pattern_key = patron_key
        return True

    def _render_patron(self, indices_activos: Tuple[int, ...]) -> None:
        activos = set(indices_activos)
        for indice, cell in enumerate(self.pattern_cells):
            color = AppColors.ACCENT if indice in activos else wx.WHITE
            if cell.GetBackgroundColour() != color:
                cell.SetBackgroundColour(color)

    def _obtener_bitmap_alineacion(self, definicion: DefinicionAlineacion) -> wx.Bitmap:
        if definicion.imagen_referencia:
            ruta = asset_path("alignments", definicion.imagen_referencia)
            bitmap = self._load_bitmap(str(ruta), self.PATTERN_IMAGE_SIZE)
            if bitmap is not None:
                return bitmap
        return self._crear_bitmap_patron(definicion.patron_referencia, self.PATTERN_IMAGE_SIZE)

    def _pintar_boton_carta(
        self,
        boton: wx.Button,
        imagen_path: str,
        size: Tuple[int, int],
        etiqueta: str,
        marcada: bool,
        resaltar: bool,
        habilitado: bool,
    ) -> None:
        clave = id(boton)
        estado = (imagen_path, size[0], size[1], etiqueta, marcada, resaltar, habilitado)
        estado_anterior = self._button_state_cache.get(clave)
        if estado_anterior == estado:
            return

        if estado_anterior is None or estado_anterior[:4] != estado[:4]:
            boton.SetBitmap(wx.NullBitmap)
            bitmap = self._load_bitmap(imagen_path, size)
            if bitmap:
                boton.SetBitmap(bitmap)
                boton.SetLabel("")
            else:
                boton.SetLabel(etiqueta)

        if marcada:
            boton.SetBackgroundColour(AppColors.CELL_MARKED)
        elif resaltar:
            boton.SetBackgroundColour(AppColors.CELL_HIGHLIGHTED)
        else:
            boton.SetBackgroundColour(wx.WHITE)

        boton.SetToolTip(etiqueta)
        boton.SetForegroundColour(AppColors.TEXT_PRIMARY)
        boton.Enable(habilitado)
        self._button_state_cache[clave] = estado

    def _load_bitmap(self, ruta_imagen: str, size: Tuple[int, int]) -> Optional[wx.Bitmap]:
        clave = (ruta_imagen, size[0], size[1])
        if clave in self._cache_bitmaps:
            return self._cache_bitmaps[clave]

        ruta = Path(ruta_imagen)
        if not ruta.exists():
            return None

        try:
            from PIL import Image
        except ImportError:
            return None

        try:
            imagen = Image.open(ruta)
            if imagen.mode == "RGBA":
                fondo = Image.new("RGB", imagen.size, (255, 255, 255))
                fondo.paste(imagen, mask=imagen.split()[3])
                imagen = fondo
            elif imagen.mode != "RGB":
                imagen = imagen.convert("RGB")

            resampling = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
            imagen.thumbnail(size, resampling)
            lienzo = Image.new("RGB", size, (255, 255, 255))
            posicion = (
                (size[0] - imagen.size[0]) // 2,
                (size[1] - imagen.size[1]) // 2,
            )
            lienzo.paste(imagen, posicion)

            wx_image = wx.Image(size[0], size[1])
            wx_image.SetData(lienzo.tobytes())
            bitmap = wx_image.ConvertToBitmap()
            self._cache_bitmaps[clave] = bitmap
            return bitmap
        except Exception:
            return None

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

    def notificar_resultado_marcado(self, indice: int, resultado: ResultadoMarcado) -> None:
        """Muestra feedback breve tras un intento de marcado."""

        carta_nombre = self._obtener_nombre_carta_humana(indice)
        mensajes = {
            ResultadoMarcado.MARCADA: "Carta marcada con frijol correctamente.",
            ResultadoMarcado.SIN_CARTA_ACTUAL: "Todavía no hay una carta activa.",
            ResultadoMarcado.CARTA_NO_ACTUAL: (
                f"Te equivocaste: todavía no se ha mencionado {carta_nombre}."
                if carta_nombre
                else "Te equivocaste: esa carta todavía no se ha mencionado."
            ),
            ResultadoMarcado.CARTA_NO_EN_CARTON: "Esa carta no existe en tu cartón.",
            ResultadoMarcado.YA_MARCADA: "Esa carta ya estaba marcada.",
            ResultadoMarcado.PARTIDA_NO_DISPONIBLE: "La partida ya no acepta marcas.",
        }
        self._mostrar_aviso(mensajes.get(resultado, "Acción no permitida."))

        if resultado == ResultadoMarcado.CARTA_NO_ACTUAL:
            self._mostrar_carta_humana_virada(indice)
        elif resultado != ResultadoMarcado.MARCADA and 0 <= indice < len(self.botones_humano):
            boton = self.botones_humano[indice]
            color_original = wx.Colour(boton.GetBackgroundColour())
            boton.SetBackgroundColour(AppColors.PRIMARY)
            boton.Refresh()
            wx.CallLater(350, self._restaurar_color_boton, boton, color_original)

    def mostrar_error_loteria(self) -> None:
        """Informa que la alineación aún no está completa."""

        if not self.partida:
            return

        wx.MessageBox(
            f"Todavía no completas la alineación requerida:\n{self.partida.nombre_alineacion}",
            "Lotería incompleta",
            wx.OK | wx.ICON_WARNING,
        )

    def _mostrar_aviso(self, mensaje: str) -> None:
        if self.aviso_label:
            self.aviso_label.SetLabel(mensaje)
            # SetLabel recalcula el texto; volvemos a envolverlo para que
            # mensajes largos aprovechen el espacio vertical bajo los botones
            # en lugar de invadir la región central.
            self.aviso_label.Wrap(220)
            self.Layout()
            self._aviso_token += 1
            token = self._aviso_token
            if mensaje:
                wx.CallLater(6000, self._limpiar_aviso, token)

    def _limpiar_aviso(self, token: int) -> None:
        if self.aviso_label and token == self._aviso_token:
            self.aviso_label.SetLabel("")

    def _mostrar_carta_humana_virada(self, indice: int) -> None:
        if not (0 <= indice < len(self.botones_humano)):
            return

        token = self._human_hidden_tokens.get(indice, 0) + 1
        self._human_hidden_tokens[indice] = token
        self._human_hidden_indices.add(indice)
        self._render_carton_humano()
        wx.CallLater(2000, self._restaurar_carta_humana_virada, indice, token)

    def _restaurar_carta_humana_virada(self, indice: int, token: int) -> None:
        if self._human_hidden_tokens.get(indice) != token:
            return

        self._human_hidden_tokens.pop(indice, None)
        self._human_hidden_indices.discard(indice)
        if self and self.partida:
            self._render_carton_humano()

    def _obtener_nombre_carta_humana(self, indice: int) -> str:
        if not self.partida or not self.partida.jugador_principal:
            return ""
        jugador_principal = self.partida.jugador_principal
        assert jugador_principal is not None
        if not (0 <= indice < len(jugador_principal.carton.casillas)):
            return ""
        return jugador_principal.carton.casillas[indice].carta.nombre

    def _restaurar_color_boton(self, boton: wx.Button, color: wx.Colour) -> None:
        boton.SetBackgroundColour(color)
        boton.Refresh()

    def deshabilitar_controles(self) -> None:
        """Deshabilita acciones interactivas tras terminar la partida."""

        for boton in self.botones_humano:
            boton.Enable(False)
        if self.btn_loteria:
            self.btn_loteria.Enable(False)
        if self.btn_pausa:
            self.btn_pausa.Enable(False)

    def detener_timer(self) -> None:
        """Detiene el temporizador automatico."""

        if self.timer.IsRunning():
            self.timer.Stop()

    def _iniciar_primera_carta(self) -> None:
        # Un CallAfter de una vista ya retirada no debe avanzar la partida nueva
        # ni provocar renders sobre controles destruidos.
        if not self._active or self.controller.view is not self:
            return
        self.controller.cantar_siguiente_carta()

    def _on_timer(self, event: wx.Event) -> None:
        if not self._active or self.controller.view is not self:
            return
        self.controller.cantar_siguiente_carta()

    def _on_show(self, event: wx.ShowEvent) -> None:
        event.Skip()
        if event.IsShown() and self._active:
            self._schedule_layout_stabilization()

    def _schedule_layout_stabilization(self) -> None:
        self._layout_refresh_token += 1
        token = self._layout_refresh_token
        wx.CallAfter(self._stabilize_layout, token)

    def _stabilize_layout(self, token: int) -> None:
        if not self._active or token != self._layout_refresh_token:
            return
        # Relayout local y acotado. No relanzamos Layout() del padre desde
        # callbacks de tamaño/visibilidad porque eso puede generar un ciclo
        # EVT_SIZE -> CallAfter -> Layout -> EVT_SIZE en wxWidgets.
        self._layout_pending = True
        self.Layout()
        self.Refresh(False)

    def _on_human_click(self, indice: int) -> None:
        if (
            not self.partida
            or not self.partida.jugador_principal
            or not self.partida.permite_interaccion_humana
        ):
            return

        casilla = self.partida.jugador_principal.carton.casillas[indice]
        self.controller.marcar_carta_humana(casilla.carta.id, indice)

    def _on_loteria(self, event: wx.Event) -> None:
        self.controller.reclamar_loteria()

    def _on_pausar(self, event: wx.Event) -> None:
        if not self.partida or not self.partida.partida_en_curso:
            return

        if self.timer.IsRunning():
            self.timer.Stop()
            self._pausado = True
        else:
            self.timer.Start(self.controller.obtener_intervalo_canto_ms())
            self._pausado = False

        if self.btn_pausa:
            self.btn_pausa.SetLabel("Continuar" if self._pausado else "Pausar")

    def _on_reiniciar(self, event: wx.Event) -> None:
        self.detener_timer()
        self._detener_audio()
        self.controller.reiniciar_partida()

    def _on_menu(self, event: wx.Event) -> None:
        self.detener_timer()
        self._detener_audio()
        self.controller.volver_al_menu()

    def _describir_modo_partida(self, partida: Partida) -> str:
        if partida.configuracion.cantidad_participantes == 1:
            return "Solo humano"
        if partida.permite_interaccion_humana:
            return "Humano vs computadora"
        return "Computadora vs computadora"

    @staticmethod
    def _resolver_recurso(*rutas: Path) -> str:
        for ruta in rutas:
            if ruta.exists():
                return str(ruta.resolve())
        return str(rutas[0].resolve())

    def _seleccionar_audio_carta(self, carta_id: int) -> Optional[Path]:
        opciones = self.audio_paths.get(carta_id, [])
        if not opciones:
            return None
        return random.choice(opciones)

    def _indexar_audios_cartas(self) -> Dict[int, List[Path]]:
        audios: Dict[int, List[Path]] = {}
        if not self.audio_dir.exists():
            return audios

        for archivo in sorted(self.audio_dir.glob("*.wav")):
            prefijo = archivo.stem.split("_", 1)[0]
            if prefijo.isdigit():
                audios.setdefault(int(prefijo), []).append(archivo)

        for carta_id, archivos in list(audios.items()):
            variantes = [archivo for archivo in archivos if "_v" in archivo.stem]
            audios[carta_id] = variantes or archivos
        return audios

    def prepare_for_removal(self) -> None:
        """Cancela actividad diferida antes de retirar la vista del sizer."""

        if not self._active:
            return
        self._active = False
        self._layout_refresh_token += 1
        self.detener_timer()
        self._detener_audio()
        if self.controller.view is self:
            self.controller.view = None

    def __del__(self) -> None:
        if hasattr(self, "_active"):
            self._active = False
        if hasattr(self, "timer") and self.timer:
            self.timer.Stop()
        self._detener_audio()
