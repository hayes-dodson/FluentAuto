# -*- mode: python ; coding: utf-8 -*-
import os
import glob
import importlib.util
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# ------------------------------------------------------------
# 1) Locate ansys.units safely using importlib (no namespace errors)
# ------------------------------------------------------------
spec = importlib.util.find_spec("ansys.units")
if spec is None or not spec.submodule_search_locations:
    raise RuntimeError("ansys.units is not installed or not visible to PyInstaller")

units_root = spec.submodule_search_locations[0]

# Collect ALL YAML files under ansys.units
unit_yaml_files = []
for path in glob.glob(os.path.join(units_root, "**", "*.yaml"), recursive=True):
    rel = os.path.relpath(path, units_root).replace("\\", "/")
    dest = os.path.join("ansys/units", rel).replace("\\", "/")
    unit_yaml_files.append((path, dest))

# ------------------------------------------------------------
# 2) Collect ALL Ansys modules (maximum safety)
# ------------------------------------------------------------
hiddenimports = []
hiddenimports += collect_submodules("ansys")
hiddenimports += collect_submodules("ansys.fluent")
hiddenimports += collect_submodules("ansys.fluent.core")
hiddenimports += collect_submodules("ansys.fluent.core.solver")
hiddenimports += collect_submodules("ansys.fluent.core.generated")
hiddenimports += collect_submodules("ansys.units")

# ------------------------------------------------------------
# 3) Collect all Ansys data files (YAML, cfg, tables…)
# ------------------------------------------------------------
datas = []
datas += collect_data_files("ansys")
datas += collect_data_files("ansys.fluent")
datas += collect_data_files("ansys.units")
datas += unit_yaml_files  # Force-include all YAML files

# ------------------------------------------------------------
# 4) Include your pipeline files
# ------------------------------------------------------------
project_files = [
    ('main_gui.py', '.'),
    ('diagnostics.py', '.'),
    ('simulation_manager.py', '.'),
    ('worker_thread.py', '.'),
    ('report_gen.py', '.'),

    ('frontwing_pipeline.py', '.'),
    ('rearwing_pipeline.py', '.'),
    ('undertray_pipeline.py', '.'),
    ('halfcar_pipeline.py', '.'),
    ('pipelines.py', '.'),
]

for src, dest in project_files:
    datas.append((src, dest))

# ------------------------------------------------------------
# 5) Build
# ------------------------------------------------------------
a = Analysis(
    ['main_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="Ram Racing Aero Automation Suite",
    console=False,
)
