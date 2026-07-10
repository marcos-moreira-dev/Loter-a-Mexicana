"""Punto de entrada principal de la aplicación."""

from __future__ import annotations

import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.paths import get_project_root
from infrastructure.platform import configure_platform
from shared.app_info import APP_ID


configure_platform(APP_ID)

import wx

from controller.app_controller import AppController
from infrastructure.asset_generator import generar_cartas_si_no_existen


def main() -> None:
    """Inicializa la aplicación de escritorio."""

    os.chdir(get_project_root())
    generar_cartas_si_no_existen(verbose=False)

    app = wx.App(redirect=False)
    if hasattr(wx, "EnableVisualStyles"):
        wx.EnableVisualStyles()

    controller = AppController(app)
    controller.run()


if __name__ == "__main__":
    main()
