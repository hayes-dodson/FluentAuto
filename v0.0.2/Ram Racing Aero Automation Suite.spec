# -*- mode: python ; coding: utf-8 -*-
import os
import glob
import ansys

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# =========================================================
# 1) COLLECT EVERY ANSYS MODULE IN EXISTENCE
# =========================================================
hidden = []
hidden += collect_submodules('ansys')
hidden += collect_submodules('ansys.fluent')
hidden += collect_submodules('ansys.fluent.core')
hidden += collect_submodules('ansys.fluent.core.solver')
hidden += collect_submodules('ansys.fluent.core.generated')
hidden += collect_submodules('ansys.fluent.core.solver.settings_builtin')
hidden += collect_submodules('ansys.fluent.core.solver.settings_builtin_bases')
hidden += collect_submodules('ansys.units')
hidden += collect_submodules('ansys.units.systems')
hidden += collect_submodules('ansys.geometry')
hidden += collect_submodules('ansys.platform')
hidden += collect_submodules('ansys.dpf')
hidden += collect_submodules('ansys.tools')

# =========================================================
# 2) COLLECT EVERY DATA FILE (YAML, CFG, TXT) INSIDE ANSYS
# =========================================================
data = []
data += collect_data_files('ansys')
data += collect_data_files('ansys.fluent')
data += collect_data_files('ansys.units')

# =========================================================
# 3) FORCE IMPORT OF EVERY FLUENT/UNITS CONFIG FILE
# =========================================================
units_root = ansys.units.__path__[0]
for f in glob.glob(os.path.join(units_root, "**", "*.*"), recursive=True):
    rel = os.path.relpath(f, units_root)
    data.append((f, os.path.join("ansys/units", rel)))

# =========================================================
# 4) ADD YOUR PIPELINE SCRIPTS
# =========================================================
project_files = [
    ('main_gui.py', '.'),
    ('diagnostics.py', '.'),
    ('simulation_manager.py', '.'),
    ('report_gen.py', '.'),
    ('worker_thread.py', '.'),

    ('frontwing_pipeline.py', '.'),
    ('rearwing_pipeline.py', '.'),
    ('undertray_pipeline.py', '.'),
    ('halfcar_pipeline.py', '.'),
    ('pipelines.py', '.'),
]

for src, dest in project_files:
    data.append((src, dest))

# =========================================================
# 5) FINAL BUILD
# =========================================================
a = Analysis(
    ['main_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=data,
    hiddenimports=hidden,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Ram Racing Aero Automation Suite',
    console=False,
    icon=None,
)
