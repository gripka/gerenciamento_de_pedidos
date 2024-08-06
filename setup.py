import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["tkinter", "tkcalendar"],
    "includes": ["impressao", "gui"],  # Liste os módulos sem a extensão .py
    "include_files": [("icons/icogerenciamento.ico", "icons/icogerenciamento.ico")],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Gerenciador de Pedidos",
    version="0.4",
    description="Aplicação para gerenciar pedidos",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        "main.py",
        base=base,
        target_name="Pedidos.exe",
        icon="icons/icogerenciamento.ico"
    )]
)
