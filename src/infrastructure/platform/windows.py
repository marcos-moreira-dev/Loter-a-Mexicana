"""Configuración de plataforma Windows para mejorar la apariencia nativa."""

from __future__ import annotations

import platform


def is_windows() -> bool:
    """Verifica si el sistema operativo es Windows."""

    return platform.system() == "Windows"


def configure_windows_platform(app_id: str | None = None) -> None:
    """Configura Windows para mejor apariencia visual e identidad de la app."""

    if not is_windows():
        return

    try:
        _set_dpi_awareness()
        _enable_visual_styles()
        if app_id:
            _set_app_user_model_id(app_id)
    except Exception:
        # Si algo falla, la app sigue funcionando con el comportamiento por defecto.
        return


def _set_dpi_awareness() -> None:
    """Configura DPI awareness para evitar escalado borroso."""

    try:
        import ctypes

        user32 = ctypes.windll.user32

        dpi_awareness_context_per_monitor_v2 = -4

        try:
            user32.SetProcessDpiAwarenessContext(dpi_awareness_context_per_monitor_v2)
            return
        except AttributeError:
            pass

        try:
            shcore = ctypes.windll.shcore
            shcore.SetProcessDpiAwareness(2)
            return
        except (AttributeError, OSError):
            pass

        user32.SetProcessDPIAware()
    except Exception:
        return


def _enable_visual_styles() -> None:
    """Habilita estilos visuales nativos de Windows."""

    try:
        import ctypes

        ctypes.windll.uxtheme.SetThemeAppProperties(0x00000001)
    except Exception:
        return


def _set_app_user_model_id(app_id: str) -> None:
    """Registra un AppUserModelID explícito para la barra de tareas."""

    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        return


def get_dpi_scale_factor() -> float:
    """Obtiene el factor de escala DPI actual."""

    if not is_windows():
        return 1.0

    try:
        import ctypes

        user32 = ctypes.windll.user32
        hdc = user32.GetDC(0)
        if hdc:
            gdi32 = ctypes.windll.gdi32
            dpi = gdi32.GetDeviceCaps(hdc, 88)
            user32.ReleaseDC(0, hdc)
            return dpi / 96.0
    except Exception:
        return 1.0

    return 1.0


def configure_platform(app_id: str | None = None) -> None:
    """Aplica la configuración específica de la plataforma actual."""

    if is_windows():
        configure_windows_platform(app_id)
