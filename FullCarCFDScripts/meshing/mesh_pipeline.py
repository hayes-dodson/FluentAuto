import time
from meshing.local_refinement_regions import add_all_local_refinements
from meshing.refinement_boxes import generate_wheel_refinement_boxes
from meshing.boundary_layer_tools import compute_bl_height, compute_first_layer_height


def run_mesh_pipeline(session, geometry_path, settings):

    tasks = session.workflow.TaskObject

    # -------------------------
    # Import geometry
    # -------------------------
    print("\n[Meshing] Importing geometry...")
    imp = tasks["Import Geometry"]
    imp.Arguments.set_state({"FileName": geometry_path, "LengthUnit": "m"})
    imp.Execute()

    # -------------------------
    # Describe geometry
    # -------------------------
    tasks["Describe Geometry"].Arguments.set_state({
        "SetupType": "The geometry consists of only fluid regions with no voids"
    })
    tasks["Describe Geometry"].Execute()

    tasks["Update Boundaries"].Execute()
    tasks["Update Regions"].Execute()

    # -------------------------
    # Refinement regions
    # -------------------------
    print("\n[Meshing] Adding refinement regions...")
    add_all_local_refinements(session)

    # -------------------------
    # Wheel refinement boxes
    # -------------------------
    print("\n[Meshing] Adding wheel refinement boxes...")
    generate_wheel_refinement_boxes(session, settings)

    # -------------------------
    # Boundary layer
    # -------------------------
    bl_height = compute_bl_height(settings)
    y1 = compute_first_layer_height(settings)

    print(f"[BL] Thickness={bl_height:.6f} m, First layer={y1:.6f} m")

    bl = tasks["Add Boundary Layers"]
    bl.AddChildToTask()
    bl.InsertCompoundChildTask()

    bl_child = tasks[bl.ChildNames[-1]]
    bl_child.Arguments.set_state({
        "BLControlName": "BL-Auto",
        "BoundaryZones": settings["bl_surface_zones"],
        "NumberOfLayers": settings["bl_layers"],
        "FirstLayerHeight": y1,
        "GrowthRate": settings["bl_growth"]
    })
    bl.Execute()

    # -------------------------
    # Surface mesh
    # -------------------------
    print("\n[Meshing] Generating surface mesh...")
    surf = tasks["Generate the Surface Mesh"]
    surf.Arguments.set_state({
        "CFDSurfaceMeshControls": {
            "MinSize": settings["surf_min_size"],
            "MaxSize": settings["surf_max_size"],
            "CurvatureNormalAngle": settings["surf_curvature_angle"],
            "GrowthRate": settings["surf_growth"],
            "CellsPerGap": settings["surf_cells_per_gap"],
        }
    })
    surf.Execute()

    # Surface improve
    imp_surf = tasks["Improve Surface Mesh"]
    imp_surf.AddChildToTask()
    imp_surf.InsertCompoundChildTask()
    c = tasks[imp_surf.ChildNames[-1]]
    c.Arguments.set_state({"FaceQualityLimit": 0.7})
    imp_surf.Execute()

    # -------------------------
    # Volume mesh
    # -------------------------
    print("\n[Meshing] Volume mesh (Hexcore)...")
    vol = tasks["Generate the Volume Mesh"]
    vol.Arguments.set_state({
        "FillWith": "poly-hexcore",
        "PeelLayers": 1,
        "MinCellLength": settings["min_cell_length"],
        "MaxCellLength": settings["max_cell_length"],
    })
    vol.Execute()

    # Improve volume mesh
    imp_vol = tasks["Improve Volume Mesh"]
    imp_vol.AddChildToTask()
    imp_vol.InsertCompoundChildTask()
    vc = tasks[imp_vol.ChildNames[-1]]
    vc.Arguments.set_state({
        "QualityMethod": "Orthogonal",
        "CellQualityLimit": 0.2,
        "UseAdditionalCriteria": False
    })
    imp_vol.Execute()

    print("\n[Meshing] Pipeline complete.")
