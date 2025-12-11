# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# --- FIX: __file__ is not defined when PyInstaller reads spec ---
project_dir = os.getcwd()   # This is YOUR v0.0.2 directory

# --- Hidden imports for Ansys Fluent + PySide6 ---
hidden_imports = [
    "ansys.units.common",
    "ansys.fluent.core.session_solver_lite",
    "ansys.fluent.core.utils.dump_session_data",
    "ansys.fluent.core.utils.event_loop",
    "ansys.fluent.core.utils.test_grpc_connection",
    "ansys.fluent.visualization",
    "ansys.fluent.visualization.contour",
    "ansys.fluent.visualization.matplotlib",
    "ansys.fluent.visualization.pyvista",
]

# --- Collect all your pipeline scripts ---
datas = [
    (os.path.join(project_dir, "frontwing_pipeline.py"), "."),
    (os.path.join(project_dir, "rearwing_pipeline.py"), "."),
    (os.path.join(project_dir, "halfcar_pipeline.py"), "."),
    (os.path.join(project_dir, "undertray_pipeline.py"), "."),
    (os.path.join(project_dir, "simulation_manager.py"), "."),
    (os.path.join(project_dir, "diagnostics.py"), "."),
    (os.path.join(project_dir, "worker_thread.py"), "."),
    (os.path.join(project_dir, "report_gen.py"), "."),
    (os.path.join(project_dir, "pipelines.py"), "."),
]

block_cipher = None

a = Analysis(
    ["main_gui.py"],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PyQt5"],     # FIX Qt conflict
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- ONEFILE MODE ---
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
    upx=True,
    console=False,   # GUI app (no console window)
    icon=None,       # Add your icon path here if needed
)

# --- Onefile bundle ---
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="Ram Racing Aero Automation Suite",
)

# --- Build SINGLE EXE ---
app = BUNDLE(
    coll,
    name="Ram Racing Aero Automation Suite",
    bundle_identifier=None,
    icon=None,
)
