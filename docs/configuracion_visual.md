# Configuración Visual y DPI Awareness

## Resumen Técnico

Este documento describe las mejoras implementadas para mejorar la nitidez, apariencia moderna y escalado de la aplicación en sistemas Windows.

---

## Problemas Identificados

### 1. Falta de DPI Awareness (Crítico)

- Windows escala aplicaciones bitmap-based cuando no declaran DPI awareness
- Produce borrosidad en monitores con scaling > 100% (125%, 150%, 200%)
- Solución: Configuración nativa de DPI awareness antes de crear `wx.App`

### 2. Sin Visual Styles de Windows (Alto)

- wxPython no habilita automáticamente los estilos visuales modernos
- Los botones se ven "planos" y antiguos (estilo Win95)
- Solución: Habilitar Common Controls v6

### 3. Fuentes Hardcodeadas (Medio)

- Tamaños fijos (16, 48) no responden a resolución del monitor
- Texto puede verse muy pequeño o desproporcionado
- Solución: Módulo de fuentes con escalado automático

### 4. Botones Sin Estilo Moderno (Medio)

- `wx.Button` estándar tiene bordes gruesos y apariencia antigua
- Solución: `wx.BORDER_NONE` + colores centralizados

---

## Solución Implementada

### Estructura de Archivos

```
src/
├── infrastructure/
│   ├── platform/
│   │   ├── __init__.py
│   │   └── windows.py        # DPI Awareness + Visual Styles
│   └── ui/
│       ├── __init__.py
│       ├── fonts.py           # Escalado DPI-aware de fuentes
│       └── colors.py          # Constantes de color centralizadas
├── widgets/
│   ├── __init__.py
│   └── modern_button.py       # Botón moderno con hover nativo
└── main.py                    # Bootstrap inicial
```

---

## Módulo: `infrastructure/platform/windows.py`

### Funcionalidad

- Configura **DPI Awareness** antes de crear `wx.App`
- Habilita **Visual Styles** nativos de Windows
- Detecta versión de Windows y usa la API más moderna disponible

### Métodos de DPI Awareness

| Windows Version | API Usada                       | Nivel                  |
| --------------- | ------------------------------- | ---------------------- |
| 10 1703+        | `SetProcessDpiAwarenessContext` | Per-monitor v2 (mejor) |
| 8.1+            | `SetProcessDpiAwareness`        | Per-monitor            |
| Vista+          | `SetProcessDPIAware`            | System DPI             |

### Uso

```python
from infrastructure.platform import configure_platform

# Llamar ANTES de importar wx y crear App
configure_platform()
```

### Funciones Principales

- `configure_platform()`: Punto de entrada principal
- `is_windows()`: Verifica si es Windows
- `get_dpi_scale_factor()`: Obtiene factor de escala (1.0 = 100%, 1.25 = 125%)
- `_set_dpi_awareness()`: Configura DPI awareness
- `_enable_visual_styles()`: Habilita Common Controls v6

---

## Módulo: `infrastructure/ui/fonts.py`

### Funcionalidad

- Crea fuentes que se escalan automáticamente según DPI
- Tamaños categorizados para consistencia
- Familia de fuente adaptada por sistema operativo

### Categorías de Tamaño

| Categoría | Puntos Base (96 DPI) | Uso                 |
| --------- | -------------------- | ------------------- |
| `small`   | 9                    | Leyendas, detalles  |
| `normal`  | 11                   | Texto general       |
| `medium`  | 13                   | Subtítulos          |
| `large`   | 16                   | Títulos de sección  |
| `xlarge`  | 20                   | Títulos principales |
| `title`   | 28                   | Título de ventana   |
| `huge`    | 36                   | Decoración grande   |

### Uso

```python
from infrastructure.ui.fonts import get_font

# Fuente normal
font_normal = get_font('normal')

# Fuente bold
font_bold = get_font('medium', bold=True)

# Fuente itálica
font_italic = get_font('small', italic=True)

# Uso en controles
btn.SetFont(get_font('large', bold=True))
```

### Cálculo de Escalado

```python
# Factor de escala basado en DPI del sistema
scale_factor = get_dpi_scale_factor()  # e.g., 1.25 para 125%
scaled_size = int(base_size * scale_factor)
```

---

## Módulo: `infrastructure/ui/colors.py`

### Funcionalidad

- Colores centralizados para consistencia visual
- Elimina definiciones duplicadas en múltiples vistas
- Fácil modificación de paleta desde un solo lugar

### Paleta de Colores

```python
class AppColors:
    # Colores base
    BACKGROUND = wx.Colour(255, 248, 220)       # Crema cálido
    PRIMARY = wx.Colour(231, 76, 60)            # Rojo coral
    SECONDARY = wx.Colour(46, 204, 113)         # Verde esmeralda
    ACCENT = wx.Colour(241, 196, 15)            # Amarillo dorado
    BLUE = wx.Colour(52, 152, 219)              # Azul brillante
    ORANGE = wx.Colour(230, 126, 34)            # Naranja
    PURPLE = wx.Colour(155, 89, 182)            # Púrpura

    # Colores de texto
    TEXT_PRIMARY = wx.Colour(44, 62, 80)        # Azul oscuro
    TEXT_LIGHT = wx.Colour(255, 255, 255)       # Blanco

    # Estados de celda (cartón)
    CELL_NORMAL = wx.WHITE
    CELL_MARKED = wx.Colour(46, 204, 113, 200)
    CELL_HIGHLIGHTED = wx.Colour(241, 196, 15, 150)
```

### Uso

```python
from infrastructure.ui.colors import AppColors

panel.SetBackgroundColour(AppColors.BACKGROUND)
btn.SetForegroundColour(AppColors.TEXT_LIGHT)
```

---

## Módulo: `widgets/modern_button.py`

### Funcionalidad

- Botón con `wx.BORDER_NONE` para bordes limpios
- Efectos hover nativos
- Uso de colores centralizados

### Uso

```python
from widgets.modern_button import ModernButton

btn = ModernButton(
    parent=panel,
    label="Nueva Partida",
    bg_color=AppColors.PRIMARY,
    hover_color=AppColors.PRIMARY_HOVER,
    font_size="large"
)
```

---

## Bootstrap en `main.py`

### Secuencia de Inicio Correcta

```python
# 1. Importar y configurar plataforma ANTES de wx
from infrastructure.platform import configure_platform
configure_platform()

# 2. Importar wx
import wx

# 3. Crear App y habilitar visual styles
app = wx.App(redirect=False)
if hasattr(wx, 'EnableVisualStyles'):
    wx.EnableVisualStyles()

# 4. Crear controlador
controller = AppController(app)
controller.run()
```

---

## Cambios Aplicados a Vistas

| Archivo            | Cambios                                                      |
| ------------------ | ------------------------------------------------------------ |
| `main_menu.py`     | Fuentes escaladas, colores centralizados, `wx.BORDER_NONE`   |
| `game_view.py`     | Fuentes escaladas, colores centralizados, `wx.BORDER_SIMPLE` |
| `settings_view.py` | Fuentes escaladas, colores centralizados, `wx.BORDER_NONE`   |
| `help_view.py`     | Fuentes escaladas, colores centralizados, `wx.BORDER_NONE`   |
| `result_dialog.py` | Fuentes escaladas, colores centralizados, `wx.BORDER_NONE`   |
| `app_window.py`    | Ya usa colores centralizados                                 |

---

## Limitaciones de wxPython

A pesar de estas mejoras, wxPython tiene limitaciones intrínsecas vs JavaFX:

1. **Renderizado nativo del SO**: wxPython usa controles nativos, lo que significa que la apariencia depende del tema de Windows
2. **Sin CSS/temas avanzados**: No hay sistema de temas como en JavaFX/CSS
3. **Scaling de bitmaps**: Las imágenes escaladas pueden perder nitidez
4. **Consistencia multiplataforma**: Cada OS muestra controles ligeramente diferentes

### Mitigaciones Implementadas

- DPI awareness mejora significativamente la nitidez
- `wx.BORDER_NONE` elimina bordes pesados
- Fuentes escaladas aseguran textos legibles
- Colores centralizados mantienen consistencia visual

---

## Pruebas Realizadas

- ✓ Compilación sin errores de sintaxis
- ✓ Ejecución sin crashes en Windows
- ✓ Fuentes escaladas aplicadas correctamente
- ✓ Colores centralizados funcionando
- ✓ `wx.BORDER_NONE` aplicado en botones

---

## Mantenimiento

### Para Modificar Colores

Editar `infrastructure/ui/colors.py` (un solo archivo)

### Para Modificar Escalado de Fuentes

Editar `infrastructure/ui/fonts.py` (categorías y pesos)

### Para Agregar Nuevos Controles

1. Usar `get_font()` para fuentes
2. Usar `AppColors` para colores
3. Usar `wx.BORDER_NONE` para bordes limpios

---

## Referencias Técnicas

- [wxPython DPI Awareness](https://wxpython.org/Phoenix/docs/html/wx.DPIChangedEvent.html)
- [Windows DPI Awareness Docs](https://learn.microsoft.com/en-us/windows/win32/hidpi/high-dpi-desktop-application-development-on-windows)
- [wxPython Visual Styles](https://wxpython.org/Phoenix/docs/html/wx.lib.agw.aui.html)
