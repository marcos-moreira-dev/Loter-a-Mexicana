![Logo de Lotería Mexicana](images%20readme/logo.png)

# Lotería Mexicana

Juego de escritorio que recrea la experiencia clásica de la **Lotería Mexicana** con una presentación visual cuidada, cantos de voz, modos de juego configurables y soporte para distribución en Windows.

## Vista general

### Pantalla principal

Menú principal rediseñado con acceso directo a nueva partida, configuración, ayuda, reportes y salida.

![Pantalla principal](images%20readme/pantalla%20principal.png)

### Configuración de la partida

Permite elegir el modo de juego, el tipo de alineación, la visibilidad del rival y el tiempo de cambio de carta.

![Configuración de la partida](images%20readme/configuraci%C3%B3n.png)

### Vista de partida

Incluye carta actual, controles, cartón del jugador, cartón del oponente e historial de cartas cantadas.

![Vista de partida](images%20readme/partida.png)

## Experiencia de juego

- Mazo completo de **54 cartas** sin repeticiones.
- Selección manual o aleatoria del tipo de juego.
- Patrones oficiales:
  - línea horizontal
  - cualquier columna
  - cuatro esquinas
  - cuatro juntas en una esquina
  - inside
  - cartón completo
- Modos de partida:
  - solo humano
  - humano vs computadora
  - computadora vs computadora
- Marcado visual con frijol sobre el cartón.
- Canto automático de cartas con **audio**.
- Historial de cartas cantadas en tiempo real.
- Reportes persistidos en `data/reportes_partidas.json`.
- Inicio en pantalla completa con `F11` y salida rápida con `Esc`.
- Icono y branding integrados para ventana e instalador.

## Instalación y ejecución

Instala dependencias:

```bash
pip install -r requirements.txt
```

Ejecuta desde la raíz del proyecto:

```bash
python src/main.py
```

O usa el lanzador de Windows:

```bash
jugar.bat
```

## Instalador MSI

Instala dependencias de build:

```bash
pip install -r requirements-build.txt
```

Genera el instalador:

```bash
python setup.py bdist_msi
```

También puedes usar:

```bash
build_msi.bat
```

El instalador se genera en:

```text
dist/Loteria Mexicana-1.0.0-win64.msi
```

## Detalles técnicos

El código está organizado para mantener separada la lógica del juego de la interfaz:

- separación clara entre dominio, controlador, infraestructura y vistas;
- rutas de recursos compatibles con ejecución normal y ejecutable empaquetado;
- textos visibles corregidos en español;
- flujo de partida mantenible y estable;
- pruebas automatizadas para reglas y lógica principal;
- empaquetado MSI funcional para Windows.

## Tecnologías

- Python 3.12
- wxPython
- Pillow
- cx_Freeze para empaquetado MSI

## Verificación

```bash
python -m compileall src tests
python -m unittest discover -s tests -v
```

## Estructura del proyecto

```text
src/
  controller/
  infrastructure/
  model/
  shared/
  view/
assets/
data/
docs/
tests/
```
