"""Widgets mejorados con apariencia moderna."""

import wx
from infrastructure.ui.colors import AppColors


class ModernButton(wx.Button):
    """Botón con apariencia moderna y mejor manejo de DPI.
    
    Características:
    - Bordes más limpios (wx.BORDER_NONE)
    - Padding consistente
    - Efectos hover nativos mejorados
    - Escalado automático de fuentes
    """
    
    def __init__(
        self,
        parent: wx.Window,
        label: str = "",
        size: tuple = None,
        bg_color: wx.Colour = None,
        hover_color: wx.Colour = None,
        fg_color: wx.Colour = None,
        font_size: str = "medium"
    ) -> None:
        """Inicializa el botón moderno.
        
        Args:
            parent: Ventana padre
            label: Texto del botón
            size: Tamaño (None = auto)
            bg_color: Color de fondo
            hover_color: Color al pasar el mouse
            fg_color: Color de texto
            font_size: Categoría de tamaño de fuente
        """
        # Usar wx.BORDER_NONE para bordes limpios
        style = wx.BORDER_NONE | wx.BU_EXACTFIT
        
        super().__init__(parent, label=label, style=style)
        
        # Colores por defecto
        self._bg_color = bg_color or AppColors.PRIMARY
        self._hover_color = hover_color or self._darken_color(self._bg_color)
        self._fg_color = fg_color or AppColors.TEXT_LIGHT
        self._font_size = font_size
        
        # Aplicar estilo inicial
        self._apply_style()
        
        # Bindings para hover
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        
        # Establecer tamaño si se proporciona
        if size:
            self.SetMinSize(size)
            self.SetSize(size)
    
    def _apply_style(self) -> None:
        """Aplica el estilo visual al botón."""
        self.SetBackgroundColour(self._bg_color)
        self.SetForegroundColour(self._fg_color)
        
        # Configurar fuente escalada
        from infrastructure.ui.fonts import get_font
        font = get_font(self._font_size, bold=True)
        self.SetFont(font)
    
    def _on_enter(self, event: wx.Event) -> None:
        """Maneja el evento mouse enter."""
        self.SetBackgroundColour(self._hover_color)
        self.Refresh()
        event.Skip()
    
    def _on_leave(self, event: wx.Event) -> None:
        """Maneja el evento mouse leave."""
        self.SetBackgroundColour(self._bg_color)
        self.Refresh()
        event.Skip()
    
    @staticmethod
    def _darken_color(color: wx.Colour, factor: float = 0.85) -> wx.Colour:
        """Oscurece un color para el efecto hover.
        
        Args:
            color: Color original
            factor: Factor de oscurecimiento (0-1)
            
        Returns:
            Color oscurecido
        """
        r = int(color.Red() * factor)
        g = int(color.Green() * factor)
        b = int(color.Blue() * factor)
        return wx.Colour(r, g, b)
