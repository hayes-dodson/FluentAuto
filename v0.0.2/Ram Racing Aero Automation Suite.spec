# -*- mode: python ; coding: utf-8 -*-

import os
import ansys.fluent.core
import ansys.units
import PySide6

project_root = os.path.abspath(os.getcwd())

# -----------------------------
# PACKAGE ROOTS
# -----------------------------
fluent_root = os.path.dirname(ansys.fluent.core.__file__)
units_root  = os.path.dirname(ansys.units.__file__)
pyside_root = os.path.dirname(PySide6.__file__)

# -----------------------------
# DATA FILE COLLECTION
# -----------------------------
datas = [
    # PySide6 plugins
    (os.path.join(pyside_root, "plugins"), "PySide6/plugins"),

    # Ansys Fluent units YAMLs
    (os.path.join(units_root, "quantity_tables"), "ansys/units/quantity_tables"),
    (os.path.join(units_root, "cfg.yaml"), "ansys/units"),

    # Fluent generated YAML schemas (prevents missing settings_builtin errors)
    (os.path.join(fluent_root, "generated"), "ansys/fluent/core/generated"),

    # Include local pipeline modules
    (os.path.join(project_root, "pipelines"), "pipelines"),

    # Diagnostics + manager
    (os.path.join(project_root, "diagnostics.py"), "."),
    (os.path.join(project_root, "simulation_manager.py"), "."),
]

# -----------------------------
# HIDDEN IMPORTS
# -----------------------------
hidden_imports = [
    # PySide6
    "PySide6",
    "PySide6.QtWidgets",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtNetwork",

    # Fluent
    "ansys.fluent.core",
    "ansys.fluent.core.ui",
    "ansys.fluent.core.report",
    "ansys.fluent.core.file_session",
    "ansys.fluent.core.session_solver_lite",

    # Fluent post objects
    "ansys.fluent.interface",
    "ansys.fluent.interface.post_objects",
    "ansys.fluent.visualization",
    "ansys.fluent.visualization.contour",
    "ansys.fluent.visualization.matplotlib",
    "ansys.fluent.visualization.pyvista",

    # Units
    "ansys.units",
    "ansys.units._constants",
    "ansys.units.common",
    "ansys.units.quantity",
    "ansys.units.systems",
]

# -----------------------------
# EXCLUDES (CRITICAL!)
# -----------------------------
excludes = [
    "PyQt5",
    "PyQt5.QtWidgets",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
]

# -----------------------------
# ANALYSIS BLOCK
# -----------------------------
a = Analysis(
    ["main_gui.py"],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False
)

# -----------------------------
# FREEZER
# -----------------------------
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# -----------------------------
# EXECUTABLE
# -----------------------------
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="Ram Racing Aero Automation Suite",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,   # hides console window
)

