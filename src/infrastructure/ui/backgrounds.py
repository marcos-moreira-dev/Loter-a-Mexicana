"""Helpers de fondo ilustrado y paneles translúcidos."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import wx


def set_transparent_text(widget: wx.Window) -> None:
    """Intenta que una etiqueta herede visualmente el fondo del panel."""

    try:
        widget.SetBackgroundStyle(wx.BG_STYLE_TRANSPARENT)
    except Exception:
        return


class ImageBackgroundPanel(wx.Panel):
    """Panel que pinta una imagen de fondo suavizada."""

    def __init__(
        self,
        parent: wx.Window,
        image_path: Path | str,
        *,
        image_opacity: float = 0.5,
        overlay_color: Optional[wx.Colour] = None,
        base_color: Optional[wx.Colour] = None,
    ) -> None:
        super().__init__(parent)
        self.image_path = Path(image_path)
        self.image_opacity = max(0.0, min(image_opacity, 1.0))
        self.overlay_color = overlay_color
        self.base_color = base_color or wx.Colour(255, 255, 255)
        self._bitmap_cache: Dict[Tuple[int, int], wx.Bitmap] = {}

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_SIZE, self._on_size)

    def paint_background(self, dc: wx.DC, target_window: Optional[wx.Window] = None) -> None:
        """Pinta el fondo completo o la porción correspondiente a un hijo."""

        width, height = self.GetClientSize()
        if width <= 0 or height <= 0:
            return

        bitmap = self._get_background_bitmap(width, height)
        if target_window is None or target_window is self:
            dc.DrawBitmap(bitmap, 0, 0, True)
            return

        try:
            origen_fondo = self.ClientToScreen((0, 0))
            origen_objetivo = target_window.ClientToScreen((0, 0))
            dx = origen_objetivo.x - origen_fondo.x
            dy = origen_objetivo.y - origen_fondo.y
        except Exception:
            dx = 0
            dy = 0
        dc.DrawBitmap(bitmap, -dx, -dy, True)

    def _on_paint(self, event: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        self.paint_background(dc, self)

    def _on_size(self, event: wx.SizeEvent) -> None:
        self._bitmap_cache.clear()
        event.Skip()

    def refresh_visual_tree(self) -> None:
        """Fuerza el repintado del fondo y sus hijos tras un resize fuerte."""

        self.Refresh(False)
        for child in self.GetChildren():
            child.Refresh(False)

    def _get_background_bitmap(self, width: int, height: int) -> wx.Bitmap:
        cache_key = (width, height)
        if cache_key in self._bitmap_cache:
            return self._bitmap_cache[cache_key]

        bitmap = self._build_background_bitmap(width, height)
        self._bitmap_cache[cache_key] = bitmap
        return bitmap

    def _build_background_bitmap(self, width: int, height: int) -> wx.Bitmap:
        if not self.image_path.exists():
            return self._fallback_bitmap(width, height)

        try:
            from PIL import Image, ImageOps
        except ImportError:
            return self._fallback_bitmap(width, height)

        try:
            image = Image.open(self.image_path).convert("RGBA")
            image = ImageOps.fit(image, (width, height), method=getattr(getattr(Image, "Resampling", Image), "LANCZOS"))
            base = Image.new(
                "RGBA",
                image.size,
                (
                    self.base_color.Red(),
                    self.base_color.Green(),
                    self.base_color.Blue(),
                    255,
                ),
            )
            image = Image.alpha_composite(base, image)

            if self.image_opacity < 1.0:
                image = Image.blend(base, image, self.image_opacity)

            if self.overlay_color is not None:
                overlay = Image.new(
                    "RGBA",
                    image.size,
                    (
                        self.overlay_color.Red(),
                        self.overlay_color.Green(),
                        self.overlay_color.Blue(),
                        self.overlay_color.Alpha(),
                    ),
                )
                image = Image.alpha_composite(image, overlay)

            rgb_image = image.convert("RGB")
            wx_image = wx.Image(width, height)
            wx_image.SetData(rgb_image.tobytes())
            return wx_image.ConvertToBitmap()
        except Exception:
            return self._fallback_bitmap(width, height)

    def _fallback_bitmap(self, width: int, height: int) -> wx.Bitmap:
        bitmap = wx.Bitmap(width, height)
        dc = wx.MemoryDC()
        dc.SelectObject(bitmap)
        color = self.overlay_color or self.base_color
        dc.SetBackground(wx.Brush(color))
        dc.Clear()
        dc.SelectObject(wx.NullBitmap)
        return bitmap


class GlassPanel(wx.Panel):
    """Panel con efecto de vidrio para dejar ver el fondo."""

    def __init__(
        self,
        parent: wx.Window,
        *,
        tint: wx.Colour,
        border: Optional[wx.Colour] = None,
        radius: int = 20,
    ) -> None:
        super().__init__(parent)
        self.tint = tint
        self.border = border or wx.Colour(255, 255, 255, 170)
        self.radius = radius

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_SIZE, self._on_size)

    def _on_paint(self, event: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        self._paint_base(dc)
        self._paint_glass(dc)

    def _paint_base(self, dc: wx.DC) -> None:
        background_host = self._find_background_host()
        if background_host is not None:
            background_host.paint_background(dc, self)
            return

        dc.SetBackground(wx.Brush(wx.Colour(250, 245, 230)))
        dc.Clear()

    def _on_size(self, event: wx.SizeEvent) -> None:
        event.Skip()

    def _paint_glass(self, dc: wx.DC) -> None:
        width, height = self.GetClientSize()
        if width <= 0 or height <= 0:
            return

        gc = self._create_graphics_context(dc)
        radius = min(self.radius, max(6, min(width, height) // 4))
        if gc is None:
            dc.SetPen(wx.Pen(self.border, 1))
            dc.SetBrush(wx.Brush(self.tint))
            dc.DrawRoundedRectangle(0, 0, max(width - 1, 1), max(height - 1, 1), radius)
            return

        path = gc.CreatePath()
        path.AddRoundedRectangle(0.5, 0.5, max(width - 1.0, 1.0), max(height - 1.0, 1.0), radius)
        gc.SetBrush(wx.Brush(self.tint))
        gc.SetPen(wx.Pen(self.border, 1))
        gc.FillPath(path)
        gc.StrokePath(path)

    def _find_background_host(self) -> Optional[ImageBackgroundPanel]:
        current = self.GetParent()
        while current is not None:
            if isinstance(current, ImageBackgroundPanel):
                return current
            current = current.GetParent()
        return None

    @staticmethod
    def _create_graphics_context(dc: wx.DC) -> Optional[wx.GraphicsContext]:
        try:
            gcdc = wx.GCDC(dc)
            return gcdc.GetGraphicsContext()
        except Exception:
            try:
                return wx.GraphicsContext.Create(dc)
            except Exception:
                return None
