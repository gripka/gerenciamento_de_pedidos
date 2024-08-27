import sys
from cx_Freeze import setup, Executable
import os

# Caminho para a pasta onde as DLLs estão localizadas
dlls_folder = os.path.join('libs')

def copy_dlls():
    import shutil
    import glob
    
    build_dir = 'build/exe.win-amd64-3.12'  # Ajuste conforme necessário
    dll_files = glob.glob(os.path.join(dlls_folder, '*.dll'))
    for dll in dll_files:
        shutil.copy(dll, build_dir)

build_exe_options = {
    "packages": ["tkinter", "tkcalendar"],
    "includes": ["impressao", "gui"],  # Liste os módulos sem a extensão .py
    "include_files": [
        ("icons/icogerenciamento2.ico", "icons/icogerenciamento2.ico"),
        (dlls_folder, 'libs')  # Inclua a pasta de DLLs
    ],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Gerenciador de Pedidos",
    version="0.8",
    description="Gerenciador de Pedidos",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        "main.py",
        base=base,
        target_name="Pedidos.exe",
        icon="icons/icogerenciamento2.ico"
    )]
)

# Copie as DLLs após o build
copy_dlls()