from .auto_sizing import add_local_sizing
from .auto_boundary_layers import create_BL_control
from .hexcore import generate_hexcore
from .utils_detect_zones import detect_enclosure_zone

def run_mesh_pipeline(meshing_session, geometry_path, settings):
    print("Starting mesh pipeline...")

    workflow = meshing_session.workflow
    workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
    tasks = workflow.TaskObject

    # -----------------------------
    # Import Geometry
    # -----------------------------
    import_geo = tasks["Import Geometry"]
    import_geo.Arguments.set_state({
        "FileName": geometry_path,
        "LengthUnit": "m"
    })
    import_geo.Execute()
    print("Geometry imported.")

    # -----------------------------
    # Auto zone discovery
    # -----------------------------
    zone_list = meshing_session.meshing.ListNames()["face_zones"]
    wheel_zones = [z for z in zone_list if "wheel" in z.lower()]

    # -----------------------------
    # Local Sizing
    # -----------------------------
    # Stuff
    add_local_sizing(tasks, ["chassis"], 0.001, 0.064, 12, 1.2, "faces-and-edges")

    # Aero
    add_local_sizing(tasks, ["frontwing","undertray","rearwing"],
                     0.0005, 0.008, 9, 1.2, "faces-and-edges")

    # Wheels (auto via substring)
    add_local_sizing(tasks, wheel_zones,
                     0.0005, 0.032, 18, 1.2, "faces")

    # -----------------------------
    # Surface Mesh
    # -----------------------------
    surf = tasks["Generate the Surface Mesh"]
    surf.Arguments.set_state({
        "MinimumSize": 0.002,
        "MaximumSize": 0.256,
        "GrowthRate": 1.19999,
        "SizeFunctions": "Curvature & Proximity",
        "CurvatureNormalAngle": 18,
        "CellsPerGap": 1,
        "ScopeProximityTo": "faces-and-edges",
        "DrawSizeBoxes": True,
        "SeparateBoundaryZonesByAngle": "No",
    })
    surf.UpdateChildTasks()
    surf.Execute()
    print("Surface mesh complete.")

    # Surface improvement
    imp_surf = tasks["Improve Surface Mesh"]
    imp_surf.AddChildToTask()
    imp_surf.InsertCompoundChildTask()
    child = tasks[imp_surf.ChildNames[-1]]
    child.Arguments.set_state({"FaceQualityLimit": 0.7})
    imp_surf.Execute()
    print("Surface mesh improved.")

    # -----------------------------
    # BL Creation
    # -----------------------------
    BL_regions = {
        "BL_wheels": wheel_zones,
        "BL_undertray": ["undertray"],
        "BL_wings": ["frontwing", "rearwing"],
        "BL_chassis": ["chassis"],
    }
    for name, zones in BL_regions.items():
        create_BL_control(tasks, name, zones, 10, 10.0)

    # -----------------------------
    # Hexcore
    # -----------------------------
    generate_hexcore(tasks)

    print("Meshing pipeline complete.")
