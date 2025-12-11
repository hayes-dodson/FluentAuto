# -*- mode: python ; coding: utf-8 -*-

import os

project_dir = os.getcwd()

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
    excludes=["PyQt5"],
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
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)
