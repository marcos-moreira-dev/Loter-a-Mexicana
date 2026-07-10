"""Factory de configuración de plataforma."""

from .windows import configure_platform, get_dpi_scale_factor, is_windows

__all__ = ["configure_platform", "is_windows", "get_dpi_scale_factor"]
