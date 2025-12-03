SETTINGS = {

    # ------------------------------
    # Geometry Inputs
    # ------------------------------
    "geometry_root_dir": "C:/FSAE/Geometries/",   # folder containing all geometry files
    "geometry_extension": ".step",                # or .igs, .x_t, .parasolid, .stp

    # ------------------------------
    # Car Physical Settings
    # ------------------------------
    "final_inlet_velocity_mph": 40,
    "air_density": 1.225,                 # kg/m^3
    "wheel_rotational_speed_rad_s": 88,   # from 8 in radius at 40 mph

    # half car geometry
    "wheelbase_m": 1.5748,                # 62 inches
    "tire_diameter_m": 0.4064,            # 16 inches

    # wheel + wheel block zones
    "wheel_zone_names": ["fw", "rw", "fwb", "rwb"],

    # ------------------------------
    # Meshing Settings
    # ------------------------------
    "target_y_plus": 1,
    "bl_layers": 10,
    "bl_growth": 1.2,

    # ------------------------------
    # Refinement Boxes
    # ------------------------------
    "ref_box_padding_m": 0.05,

    # ------------------------------
    # Solver Settings
    # ------------------------------
    "precision": "double",
    "max_final_iterations": 2000,
    "floating_point_recovery_iterations": 200,

    # ------------------------------
    # Batch Runner
    # ------------------------------
    "batch_size": 50,
    "output_root": "C:/FSAE/Results/",

    # ------------------------------
    # Projected Area Calc
    # ------------------------------
    "min_feature_size": 0.0001,   # 0.1 mm
    "projected_area_zones": [
        "frontwing", "rearwing", "undertray", "chassis",
        "fw", "fwb", "rw", "rwb"
    ]
}
