# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

# ----- Correct project directory (v0.0.2 folder) -----
project_dir = os.path.abspath(os.path.dirname(__file__))

# ----- Collect PySide6 components -----
pyside6_binaries, pyside6_datas, pyside6_hidden = collect_all("PySide6")

# ----- Bundle ansys.units YAML files -----
import ansys.units
units_path = ansys.units.__path__[0]

datas = [
    (units_path, "ansys/units"),
] + pyside6_datas

# ----- Hidden imports needed for Fluent core -----
hiddenimports = [
    "ansys.units",
    "ansys.units._version",
    "ansys.units.common",
    "ansys.units.quantity",
    "ansys.units._constants",
    "ansys.units.systems",

    "ansys.fluent.core",
    "ansys.fluent.visualization",
    "ansys.fluent.visualization.contour",
    "ansys.fluent.visualization.matplotlib",
    "ansys.fluent.visualization.pyvista",

    "ansys.fluent.core.session_solver_lite",
    "ansys.fluent.core.utils.dump_session_data",
    "ansys.fluent.core.utils.event_loop",
    "ansys.fluent.core.utils.test_grpc_connection",
] + pyside6_hidden


block_cipher = None

a = Analysis(
    ['main_gui.py'],       # entrypoint
    pathex=[project_dir],  # your actual folder
    binaries=pyside6_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=[
        "PyQt5",    # prevent PyQt vs PySide conflicts
        "PyQt6",
        "qtpy"
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Ram Racing Aero Automation Suite",
    debug=False,
    strip=False,
    upx=False,
    console=False  # GUI mode
)
