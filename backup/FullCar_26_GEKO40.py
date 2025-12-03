import ansys.fluent.core as pyfluent

# ===============================================================
# LAUNCH FLUENT MESHING
# ===============================================================
geometry_path = ""  # <- PUT YOUR GEOMETRY PATH HERE

print("Launching Fluent Meshing...")
meshing_session = pyfluent.launch_fluent(
    mode=pyfluent.FluentMode.MESHING,
    precision=pyfluent.Precision.DOUBLE,
    processor_count=60,
    dimension=3,
    mpi_type="intel",
)

workflow = meshing_session.workflow
workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
tasks = workflow.TaskObject

print("\n=== STARTING WATERTIGHT GEOMETRY WORKFLOW ===\n")

# ===============================================================
# IMPORT GEOMETRY
# ===============================================================
print("Importing geometry...")

import_geometry = tasks["Import Geometry"]
import_geometry.Arguments.set_state(
    {
        "FileName": geometry_path,
        "LengthUnit": "m",
    }
)
import_geometry.Execute()

print("Geometry import complete.\n")

# ===============================================================
# HELPER: LOCAL SIZING
# ===============================================================
def add_local_sizing(labels, min_size, max_size, curvature_angle, growth_rate, scope):
    """Create one local sizing control for a set of labels."""
    add_ls = tasks["Add Local Sizing"]
    add_ls.AddChildToTask()
    add_ls.InsertCompoundChildTask()

    child = tasks[add_ls.ChildNames[-1]]

    child.Arguments.set_state(
        {
            "ControlName": f"LS_{child.Name}",
            "SizeControlType": "Curvature",
            "LocalMin": min_size,
            "MaxSize": max_size,
            "GrowthRate": growth_rate,
            "CurvatureNormalAngle": curvature_angle,
            "Scope": scope,        # "faces" or "faces-and-edges"
            "SelectBy": "label",
            "Labels": labels,
        }
    )

    add_ls.Execute()
    print(f"  → Local sizing applied to labels: {labels}")


# ===============================================================
# AUTO ZONE DISCOVERY
# ===============================================================
print("Discovering face zones from geometry...")
names_dict = meshing_session.meshing.ListNames()
face_zones = names_dict.get("face_zones", [])
print(f"Found {len(face_zones)} face zones.")

# ===============================================================
# AUTOMATIC LOCAL SIZING: WHEELS (BY SUBSTRING 'wheel')
# ===============================================================
print("\nAdding automatic local sizing for wheels (substring 'wheel')...")

wheel_zones = [z for z in face_zones if "wheel" in z.lower()]
if wheel_zones:
    add_local_sizing(
        labels=wheel_zones,
        min_size=0.0005,
        max_size=0.032,
        curvature_angle=18,
        growth_rate=1.2,
        scope="faces",
    )
else:
    print("  → No wheel zones matched 'wheel' in name. (Check labels.)")

# ===============================================================
# EXPLICIT LOCAL SIZING: STUFF + AERO
# ===============================================================
print("\nAdding explicit local sizing for chassis + aero...")

# Stuff (chassis)
stuff_labels = ["chassis"]
add_local_sizing(
    labels=stuff_labels,
    min_size=0.001,
    max_size=0.064,
    curvature_angle=12,
    growth_rate=1.2,
    scope="faces-and-edges",
)

# Aero (front / rear wing + undertray)
aero_labels = ["frontwing", "undertray", "rearwing"]
add_local_sizing(
    labels=aero_labels,
    min_size=0.0005,
    max_size=0.008,
    curvature_angle=9,
    growth_rate=1.2,
    scope="faces-and-edges",
)

print("Local sizing setup complete.\n")

# ===============================================================
# GENERATE SURFACE MESH (BEFORE DESCRIBE GEOMETRY / BOUNDARIES)
# ===============================================================
print("Generating surface mesh...")

surface_mesh = tasks["Generate the Surface Mesh"]
surface_mesh.Arguments.set_state(
    {
        "MinimumSize": 0.002,
        "MaximumSize": 0.256,
        "GrowthRate": 1.19999,
        "SizeFunctions": "Curvature & Proximity",
        "CurvatureNormalAngle": 18,
        "CellsPerGap": 1,
        "ScopeProximityTo": "faces-and-edges",
        "DrawSizeBoxes": True,
        "SeparateBoundaryZonesByAngle": "No",
    }
)

surface_mesh.UpdateChildTasks()
surface_mesh.Execute()

print("Surface mesh complete.")
try:
    print("Surface mesh quality:", surface_mesh.Outputs["Quality"].get_state(), "\n")
except Exception as e:
    print("Could not read surface mesh quality:", e, "\n")

# ===============================================================
# IMPROVE SURFACE MESH
# ===============================================================
print("Improving surface mesh...")

imp_surf = tasks["Improve Surface Mesh"]
imp_surf.AddChildToTask()
imp_surf.InsertCompoundChildTask()

surf_task = tasks[imp_surf.ChildNames[-1]]
surf_task.Arguments.set_state({"FaceQualityLimit": 0.7})

imp_surf.Execute()

print("Surface mesh improvement complete.")
try:
    print("Improved surface mesh quality:", imp_surf.Outputs["Quality"].get_state(), "\n")
except Exception as e:
    print("Could not read improved surface quality:", e, "\n")

# ===============================================================
# DESCRIBE GEOMETRY
# ===============================================================
print("Describing geometry...")

describe_geometry = tasks["Describe Geometry"]
describe_geometry.UpdateChildTasks(SetupTypeChanged=False)
describe_geometry.Arguments.set_state(
    {
        "SetupType": "The geometry consists of only fluid regions with no voids",
    }
)
describe_geometry.UpdateChildTasks(SetupTypeChanged=True)
describe_geometry.Execute()

print("Geometry description complete.\n")

# ===============================================================
# UPDATE BOUNDARIES / REGIONS
# ===============================================================
print("Updating boundaries...")

update_boundaries = tasks["Update Boundaries"]
update_boundaries.Arguments.set_state(
    {
        # example: change wall-inlet from velocity-inlet to wall
        "BoundaryLabelList": ["wall-inlet"],
        "BoundaryLabelTypeList": ["wall"],
        "OldBoundaryLabelList": ["wall-inlet"],
        "OldBoundaryLabelTypeList": ["velocity-inlet"],
    }
)
update_boundaries.Execute()

tasks["Update Regions"].Execute()

print("Boundary and region update complete.\n")

# ===============================================================
# HELPER: BOUNDARY LAYER CONTROL PER REGION
# ===============================================================
def create_BL_control(name, zones, n_layers, last_ratio):
    """Create one boundary-layer control for given zones."""
    if not zones:
        print(f"  → Skipping BL control '{name}' (zone list is empty).")
        return

    add_bl = tasks["Add Boundary Layers"]
    add_bl.AddChildToTask()
    add_bl.InsertCompoundChildTask()

    child = tasks[add_bl.ChildNames[-1]]

    child.Arguments.set_state(
        {
            "BLControlName": name,
            "BoundaryZones": zones,
            "NumberOfLayers": n_layers,
            "LastLayerRatio": last_ratio,
        }
    )

    add_bl.Execute()
    print(f"  → BL control '{name}' added for zones: {zones}")


# ===============================================================
# AUTOMATIC BL CONTROL PER REGION
# ===============================================================
print("Creating boundary-layer controls per region...")

# Recompute wheel_zones (in case face zones updated)
names_dict = meshing_session.meshing.ListNames()
face_zones = names_dict.get("face_zones", [])
wheel_zones = [z for z in face_zones if "wheel" in z.lower()]

BL_regions = {
    "BL_wheels": wheel_zones,
    "BL_undertray": ["undertray"],
    "BL_wings": ["frontwing", "rearwing"],
    "BL_chassis": ["chassis"],
}

for bl_name, bl_zones in BL_regions.items():
    create_BL_control(
        name=bl_name,
        zones=bl_zones,
        n_layers=10,
        last_ratio=10.0,
    )

print("Boundary-layer setup complete.\n")

# ===============================================================
# HEXCORE VOLUME MESH WITH GROWTH TUNING
# ===============================================================
print("Generating poly-hexcore volume mesh with growth tuning...")

hexcore = tasks["Generate the Volume Mesh"]
hexcore.Arguments.set_state(
    {
        "Solver": "Fluent",
        "FillWith": "poly-hexcore",

        # Hexcore growth tuning
        "GrowthRate": 1.25,            # smooth-ish growth
        "TransitionLayers": 4,         # hex layers before transition
        "AnisotropicStretching": True,
        "MinCellLength": 0.0005,
        "MaxCellLength": 0.256,

        # Peel layers near BL
        "PeelLayers": 1,

        # Parallel meshing
        "EnableParallel": True,
    }
)

hexcore.Execute()

print("Volume mesh (hexcore) complete.")
try:
    print("Hexcore volume mesh quality:", hexcore.Outputs["Quality"].get_state(), "\n")
except Exception as e:
    print("Could not read volume mesh quality:", e, "\n")

# ===============================================================
# IMPROVE VOLUME MESH
# ===============================================================
print("Improving volume mesh...")

imp_vol = tasks["Improve Volume Mesh"]
imp_vol.AddChildToTask()
imp_vol.InsertCompoundChildTask()

vol_task = tasks[imp_vol.ChildNames[-1]]
vol_task.Arguments.set_state(
    {
        "QualityMethod": "Orthogonal",
        "CellQualityLimit": 0.2,
        "UseAdditionalCriteria": False,
    }
)

imp_vol.Execute()

print("Volume mesh improvement complete.")
try:
    print("Final volume mesh quality:", hexcore.Outputs["Quality"].get_state(), "\n")
except Exception as e:
    print("Could not read final volume quality:", e, "\n")

print("=== MESHING WORKFLOW COMPLETE ===")
