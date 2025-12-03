SETTINGS = {

    # =============================
    # GEOMETRY
    # =============================
    "geometry_path": "",
    "geometry_root_dir": "C:/FSAE/Geometries/",
    "geometry_extension": ".step",

    # =============================
    # PHYSICS & CAR PARAMETERS
    # =============================
    "air_density": 1.225,
    "inlet_velocity_mph": 40,
    "wheel_rotational_speed": 88.0,   # rad/s
    "wheelbase": 1.5748,
    "tire_diameter": 0.4064,

    # =============================
    # MESHING: SURFACE
    # =============================
    "surf_min_size": 0.002,
    "surf_max_size": 0.256,
    "surf_growth": 1.19999,
    "surf_curvature_angle": 18,
    "surf_cells_per_gap": 1,

    # =============================
    # MESHING: BL LAYERS
    # =============================
    "bl_layers": 10,
    "bl_growth": 1.2,
    "target_yplus": 1,
    "bl_surface_zones": [
        "chassis", "frontwing", "rearwing", "undertray",
        "fw", "fwb", "rw", "rwb"
    ],

    # =============================
    # MESHING: VOLUME (HEXCORE)
    # =============================
    "min_cell_length": 0.0005,
    "max_cell_length": 0.256,

    # =============================
    # REFINEMENT BOXES
    # =============================
    "refinement_padding": 0.05,   # 5 cm padding around wheel box

    # =============================
    # PROJECTED AREA CALC
    # =============================
    "projected_area_zones": [
        "frontwing", "rearwing", "undertray", "chassis",
        "fw", "fwb", "rw", "rwb"
    ],
    "min_feature_size": 0.0001,

    # =============================
    # SOLVER SETTINGS
    # =============================
    "max_iterations": 2000,
    "floating_point_recovery_iterations": 300,

    # =============================
    # BATCH
    # =============================
    "output_root": "C:/FSAE/Results/",
    "batch_size": 50
}
