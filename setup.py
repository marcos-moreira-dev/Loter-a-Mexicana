"""Configuración de empaquetado para generar el instalador MSI."""

from __future__ import annotations

from pathlib import Path

from cx_Freeze import Executable, setup


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"


def _read_module_constants() -> dict[str, str]:
    namespace: dict[str, str] = {}
    app_info_path = SRC_ROOT / "shared" / "app_info.py"
    exec(app_info_path.read_text(encoding="utf-8"), namespace)
    return namespace


APP_INFO = _read_module_constants()
ICON_PATH = PROJECT_ROOT / "assets" / "branding" / "logo.ico"

build_exe_options = {
    "build_exe": str(PROJECT_ROOT / "build_msi" / "exe"),
    "packages": [
        "controller",
        "infrastructure",
        "model",
        "shared",
        "view",
        "pygame",
    ],
    "includes": [
        "PIL._imaging",
        "PIL._imagingft",
    ],
    "excludes": [
        "tkinter",
        "numpy",
        "matplotlib",
        "pandas",
        "scipy",
        "sympy",
        "IPython",
        "jupyter",
        "notebook",
        "prompt_toolkit",
        "pygments",
        "jedi",
        "cairo",
        "OpenGL",
        "moderngl",
        "wx.py",
        "wx.tools",
        "wx.media",
        "wx.html2",
        "wx.ribbon",
        "wx.propgrid",
        "wx.richtext",
        "wx.stc",
        "wx.svg",
    ],
    "include_files": [
        ("assets", "assets"),
        ("data", "data"),
    ],
    "include_msvcr": True,
    "optimize": 2,
}

bdist_msi_options = {
    "all_users": False,
    "install_icon": str(ICON_PATH),
    "initial_target_dir": rf"[ProgramFilesFolder]\{APP_INFO['APP_INSTALL_DIR']}",
    "summary_data": {
        "author": APP_INFO["APP_COMPANY"],
        "comments": APP_INFO["APP_DESCRIPTION"],
        "keywords": "loteria,wxpython,juego,mexico",
    },
}

executables = [
    Executable(
        script=str(SRC_ROOT / "main.py"),
        base="Win32GUI",
        target_name="LoteriaMexicana.exe",
        icon=str(ICON_PATH),
        shortcut_name=APP_INFO["APP_NAME_ASCII"],
        shortcut_dir="ProgramMenuFolder",
    )
]

setup(
    name=APP_INFO["APP_NAME_ASCII"],
    version=APP_INFO["APP_VERSION"],
    description=APP_INFO["APP_DESCRIPTION"],
    executables=executables,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
)
