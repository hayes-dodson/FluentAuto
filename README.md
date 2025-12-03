# Ram Racing Ansys Fluent Automation

FSAE_CFD_Automation/
│
├── main.py
│
├── config/
│   ├── settings.py
│
├── meshing/
│   ├── mesh_pipeline.py
│   ├── auto_sizing.py
│   ├── auto_boundary_layers.py
│   ├── hexcore.py
│   ├── utils_detect_zones.py
│   ├── refinement_boxes.py        <-- NEW
│   ├── boundary_layer_tools.py    <-- NEW (y+, Re, BL height)
│
├── solver/
│   ├── solver_setup.py
│   ├── boundary_conditions.py
│   ├── reference_values.py
│   ├── turbulence.py
│   ├── ramping.py
│   ├── auto_restart.py            <-- NEW (floating point recovery)
│   ├── projected_area.py          <-- NEW
│   ├── aero_coeffs.py             <-- NEW
│
├── post/
│   ├── contours.py
│   ├── pathlines.py
│   ├── forces.py
│   ├── residuals.py
│   ├── data_export.py
│   ├── pressure_maps.py           <-- NEW
│
└── batch/
    ├── batch_runner.py            <-- NEW (10–100 geometry queue)
    ├── excel_writer.py            <-- NEW
