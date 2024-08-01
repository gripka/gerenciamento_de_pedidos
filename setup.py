import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["tkinter", "tkcalendar"],
    "includes": ["impressao", "gui"],  # Liste os módulos sem a extensão .py
    "include_files": ["config.json"], 
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Gerenciador de Pedidos",
    version="0.1",
    description="Aplicação para gerenciar pedidos",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)] 
)
