"""Controladores principales de la aplicación."""

from __future__ import annotations

from typing import Optional, cast

import wx

from infrastructure.music_manager import MusicManager
from model.configuracion import ConfiguracionPartida, ModoPartida
from model.mazo import Mazo
from model.partida import Partida, ResultadoLoteria, ResultadoMarcado
from model.reglas import Alineacion
from model.reportes import RepositorioReportes
from shared.app_info import APP_NAME
from view.app_window import AppWindow
from view.contact_view import ContactDialog
from view.game_view import GamePanel
from view.help_view import HelpDialog
from view.main_menu import MainMenuPanel
from view.report_view import ReportDialog
from view.result_dialog import ResultDialog
from view.settings_view import SettingsDialog


_UNSET = object()


class AppController:
    """Controlador raíz de la aplicación."""

    def __init__(self, app: Optional[wx.App] = None) -> None:
        self.app: Optional[wx.App] = app
        self.window: Optional[AppWindow] = None
        self.mazo: Optional[Mazo] = None
        self.partida: Optional[Partida] = None
        self.game_controller: Optional["GameController"] = None
        self.repositorio_reportes = RepositorioReportes()
        self.music_manager = MusicManager(enabled=True, volume=0.25)

        self.nombre_jugador = "Jugador 1"
        self.modo_partida = ModoPartida.HUMANO_VS_COMPUTADORA
        self.mostrar_cartas_oponente = False
        self.intervalo_canto_ms = 6000
        self.alineacion_preferida: Optional[Alineacion] = None
        self.musica_fondo_habilitada = True
        self.volumen_musica = 0.25

    def run(self) -> None:
        """Inicia la aplicación."""

        if self.app is None:
            self.app = wx.App(redirect=False)
            if hasattr(wx, "EnableVisualStyles"):
                wx.EnableVisualStyles()

        self.window = AppWindow(APP_NAME, self)
        self.mostrar_menu_principal()
        self.window.Show()
        self.app.MainLoop()

    def mostrar_menu_principal(self) -> None:
        """Muestra el menu principal."""

        self.music_manager.play_menu()
        if self.window:
            menu = MainMenuPanel(self.window.main_panel, self)
            self.window.set_content(menu)

    def iniciar_nueva_partida(self) -> None:
        """Construye una partida nueva con la configuración activa."""

        self.mazo = Mazo()
        configuracion = ConfiguracionPartida(
            nombre_jugador=self.nombre_jugador,
            modo_partida=self.modo_partida,
            mostrar_cartas_oponente=self.mostrar_cartas_oponente,
            intervalo_canto_ms=self.intervalo_canto_ms,
            alineacion_preferida=self.alineacion_preferida,
        )
        self.partida = Partida(
            mazo=self.mazo,
            configuracion=configuracion,
            repositorio_reportes=self.repositorio_reportes,
        )
        self.partida.iniciar()
        self.music_manager.play_gameplay()

        self.game_controller = GameController(self.partida, self)

        if self.window:
            game_view = GamePanel(self.window.main_panel, self.game_controller)
            self.window.set_content(game_view)
            self.game_controller.set_view(game_view)

    def mostrar_configuracion(self) -> None:
        """Abre el diálogo de configuración."""

        if self.window:
            dialog = SettingsDialog(self.window, self)
            dialog.ShowModal()
            dialog.Destroy()

    def mostrar_ayuda(self) -> None:
        """Abre el diálogo de ayuda."""

        if self.window:
            dialog = HelpDialog(self.window)
            dialog.ShowModal()
            dialog.Destroy()

    def mostrar_reporte(self) -> None:
        """Abre el reporte histórico de partidas."""

        if self.window:
            dialog = ReportDialog(self.window, self.repositorio_reportes)
            dialog.ShowModal()
            dialog.Destroy()

    def mostrar_creditos(self) -> None:
        """Muestra créditos breves."""

        wx.MessageBox(
            "Lotería Mexicana\n\n"
            "Aplicación de escritorio desarrollada en Python con wxPython.\n"
            "Incluye reglas del juego, reportes y flujo de partida completo.",
            "Créditos",
            wx.OK | wx.ICON_INFORMATION,
        )

    def salir(self) -> None:
        """Cierra la aplicación."""

        self.music_manager.shutdown()
        if self.window:
            self.window.Close()

    def mostrar_contacto(self) -> None:
        """Abre una ventana con los datos de contacto del autor."""

        if self.window:
            dialog = ContactDialog(self.window)
            dialog.ShowModal()
            dialog.Destroy()

    def actualizar_configuracion(
        self,
        nombre: Optional[str] = None,
        incluir_oponente_automatico: Optional[bool] = None,
        mostrar_cartas_oponente: Optional[bool] = None,
        intervalo_canto_ms: Optional[int] = None,
        alineacion_preferida: object = _UNSET,
        modo_partida: object = _UNSET,
        musica_fondo_habilitada: Optional[bool] = None,
        volumen_musica: Optional[float] = None,
    ) -> None:
        """Actualiza la configuración persistente de la aplicación."""

        if nombre is not None:
            self.nombre_jugador = nombre.strip() or "Jugador 1"
        if modo_partida is not _UNSET:
            self.modo_partida = cast(ModoPartida, modo_partida)
        elif incluir_oponente_automatico is not None:
            self.modo_partida = (
                ModoPartida.HUMANO_VS_COMPUTADORA
                if incluir_oponente_automatico
                else ModoPartida.SOLO_HUMANO
            )
        if mostrar_cartas_oponente is not None:
            self.mostrar_cartas_oponente = mostrar_cartas_oponente
        if intervalo_canto_ms is not None:
            self.intervalo_canto_ms = intervalo_canto_ms
        if alineacion_preferida is not _UNSET:
            self.alineacion_preferida = cast(Optional[Alineacion], alineacion_preferida)
        if volumen_musica is not None:
            self.volumen_musica = max(0.0, min(1.0, float(volumen_musica)))
            self.music_manager.set_volume(self.volumen_musica)
        if musica_fondo_habilitada is not None:
            self.musica_fondo_habilitada = bool(musica_fondo_habilitada)
            self.music_manager.set_enabled(self.musica_fondo_habilitada)

    @property
    def incluir_oponente_automatico(self) -> bool:
        return self.modo_partida != ModoPartida.SOLO_HUMANO


class GameController:
    """Controlador específico de la partida en curso."""

    def __init__(self, partida: Partida, app_controller: AppController) -> None:
        self.partida = partida
        self.app_controller = app_controller
        self.view: Optional[GamePanel] = None
        self._dialogo_mostrado = False

    def set_view(self, view: GamePanel) -> None:
        """Asocia la vista al controlador."""

        self.view = view
        self._actualizar_vista()

    def cantar_siguiente_carta(self) -> None:
        """Avanza la partida cantando una nueva carta."""

        if not self.partida.partida_en_curso:
            return

        self.partida.cantar_siguiente_carta()
        self._actualizar_vista()

        if self.partida.partida_finalizada:
            self._finalizar_partida()

    def marcar_carta_humana(self, id_carta: int, indice: int) -> ResultadoMarcado:
        """Procesa el clic del humano sobre una carta del cartón."""

        resultado = self.partida.marcar_carta_humano(id_carta)
        self._actualizar_vista()

        if self.view:
            self.view.notificar_resultado_marcado(indice, resultado)

        return resultado

    def reclamar_loteria(self) -> ResultadoLoteria:
        """Permite al humano reclamar lotería."""

        resultado = self.partida.cantar_loteria_humano()
        self._actualizar_vista()

        if resultado == ResultadoLoteria.GANADA:
            self._finalizar_partida()
        elif self.view:
            self.view.mostrar_error_loteria()

        return resultado

    def reiniciar_partida(self) -> None:
        """Reinicia la experiencia completa de juego."""

        self.app_controller.iniciar_nueva_partida()

    def volver_al_menu(self) -> None:
        """Regresa al menú principal."""

        self.app_controller.mostrar_menu_principal()

    def obtener_intervalo_canto_ms(self) -> int:
        """Retorna el intervalo oficial del temporizador."""

        return self.partida.configuracion.intervalo_canto_ms

    def _actualizar_vista(self) -> None:
        """Sincroniza la vista con el estado del dominio."""

        if self.view:
            if hasattr(wx, "IsMainThread") and not wx.IsMainThread():
                wx.CallAfter(self.view.render, self.partida)
                return
            self.view.render(self.partida)

    def _finalizar_partida(self) -> None:
        """Bloquea controles y muestra el resultado final una sola vez."""

        if self._dialogo_mostrado:
            return

        self._dialogo_mostrado = True
        if hasattr(wx, "IsMainThread") and not wx.IsMainThread():
            wx.CallAfter(self._mostrar_dialogo_final)
            return
        self._mostrar_dialogo_final()

    def _mostrar_dialogo_final(self) -> None:
        if self.view:
            self.view.deshabilitar_controles()
            self.view.detener_timer()

        self.app_controller.music_manager.play_menu()

        if self.app_controller.window:
            dialog = ResultDialog(self.app_controller.window, self.partida, self.app_controller)
            dialog.ShowModal()
            dialog.Destroy()
