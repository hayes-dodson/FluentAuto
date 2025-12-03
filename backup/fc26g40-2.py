import ansys.fluent.core as pyfluent

# ------------------------------------------------------------------------------
# Launch Fluent Meshing
# ------------------------------------------------------------------------------
print("Launching Fluent Meshing...")
meshing_session = pyfluent.launch_fluent(
    mode=pyfluent.FluentMode.MESHING,
    precision=pyfluent.Precision.DOUBLE,
    processor_count=60,
    dimension=3,
    mpi_type="intel"
)

workflow = meshing_session.workflow
tasks = workflow.TaskObject

workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")


# ------------------------------------------------------------------------------
# Import Geometry
# ------------------------------------------------------------------------------
print("Importing geometry...")
import_geometry = tasks["Import Geometry"]
import_geometry.Arguments.set_state({
    "FileName": "",      # <--- add your file path
    "LengthUnit": "m"
})
import_geometry.Execute()
print("Geometry imported.\n")


# ------------------------------------------------------------------------------
# Add Local Sizing: stuff / wheels / aero
# ------------------------------------------------------------------------------

def add_local_sizing(labels, min_size, max_size, curvature_angle, growth_rate, scope):
    """Creates one local sizing control."""
    add_ls = tasks["Add Local Sizing"]
    add_ls.AddChildToTask()
    add_ls.InsertCompoundChildTask()

    child = tasks[add_ls.ChildNames[-1]]

    child.Arguments.set_state({
        "ControlName": f"LS_{child.Name}",
        "SizeControlType": "Curvature",
        "LocalMin": min_size,
        "MaxSize": max_size,
        "GrowthRate": growth_rate,
        "CurvatureNormalAngle": curvature_angle,
        "Scope": scope,
        "SelectBy": "label",
        "Labels": labels,
    })

    add_ls.Execute()
    print(f"  → Added local sizing on: {labels}")


print("Adding local sizing controls...")

# 1️⃣ STUFF
add_local_sizing(
    labels=["chassis"],
    min_size=0.001,
    max_size=0.064,
    curvature_angle=12,
    growth_rate=1.2,
    scope="faces-and-edges"
)

# 2️⃣ WHEELS
add_local_sizing(
    labels=["fw", "rw", "fwb", "rwb"],
    min_size=0.0005,
    max_size=0.032,
    curvature_angle=18,
    growth_rate=1.2,
    scope="faces"
)

# 3️⃣ AERO
add_local_sizing(
    labels=["frontwing", "undertray", "rearwing"],
    min_size=0.0005,
    max_size=0.008,
    curvature_angle=9,
    growth_rate=1.2,
    scope="faces-and-edges"
)

print("Local sizing complete.\n")


# ------------------------------------------------------------------------------
# Generate Surface Mesh (must be BEFORE Describe Geometry)
# ------------------------------------------------------------------------------
print("Generating surface mesh...")

surface_mesh = tasks["Generate the Surface Mesh"]

surface_mesh.Arguments.set_state({
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

surface_mesh.UpdateChildTasks()
surface_mesh.Execute()

print("Surface mesh complete.")
print("Surface mesh quality:", surface_mesh.Outputs["Quality"].get_state(), "\n")


# ------------------------------------------------------------------------------
# Describe Geometry
# ------------------------------------------------------------------------------
print("Describing geometry...")

describe_geometry = tasks["Describe Geometry"]
describe_geometry.UpdateChildTasks(SetupTypeChanged=False)
describe_geometry.Arguments.set_state({
    "SetupType": "The geometry consists of only fluid regions with no voids"
})
describe_geometry.UpdateChildTasks(SetupTypeChanged=True)
describe_geometry.Execute()

print("Geometry description complete.\n")


# ------------------------------------------------------------------------------
# Update Boundaries
# ------------------------------------------------------------------------------
print("Updating boundaries...")

update_boundaries = tasks["Update Boundaries"]
update_boundaries.Arguments.set_state({
    "BoundaryLabelList": ["wall-inlet"],
    "BoundaryLabelTypeList": ["wall"],
    "OldBoundaryLabelList": ["wall-inlet"],
    "OldBoundaryLabelTypeList": ["velocity-inlet"],
})
update_boundaries.Execute()

tasks["Update Regions"].Execute()

print("Boundary update complete.\n")


# ------------------------------------------------------------------------------
# Add Boundary Layers
# ------------------------------------------------------------------------------
print("Adding boundary layers...")

add_boundary_layers = tasks["Add Boundary Layers"]
add_boundary_layers.AddChildToTask()
add_boundary_layers.InsertCompoundChildTask()

bl = tasks["last-ratio_1"]
bl.Arguments.set_state({
    "BLControlName": "last-ratio_1",
    "BoundaryZones": ["frontwing", "chassis", "fw", "fwb", "rw", "rwb", "undertray", "rearwing"],
    "NumberOfLayers": 10,
    "LastLayerRatio": 10.0
})

add_boundary_layers.Arguments.set_state({})
bl.Execute()

print("Boundary layers added.\n")


# ------------------------------------------------------------------------------
# Generate Volume Mesh
# ------------------------------------------------------------------------------
print("Generating volume mesh...")

vol_mesh = tasks["Generate the Volume Mesh"]
vol_mesh.Arguments.set_state({
    "Solver": "Fluent",
    "FillWith": "poly-hexcore",
    "PeelLayers": 1,
    "MinCellLength": 0.0005,
    "MaxCellLength": 0.256,
    "EnableParallel": True
})

vol_mesh.Execute()

print("Volume mesh created.")
print("Volume mesh quality:", vol_mesh.Outputs["Quality"].get_state(), "\n")


# ------------------------------------------------------------------------------
# Improve Volume Mesh
# ------------------------------------------------------------------------------
print("Improving volume mesh...")

imp_vol = tasks["Improve Volume Mesh"]
imp_vol.AddChildToTask()
imp_vol.InsertCompoundChildTask()

vol_child = tasks[imp_vol.ChildNames[0]]
vol_child.Arguments.set_state({
    "QualityMethod": "Orthogonal",
    "CellQualityLimit": 0.2,
    "UseAdditionalCriteria": False
})

imp_vol.Execute()

print("Volume mesh improvement complete.")
print("Final volume mesh quality:",
      vol_mesh.Outputs["Quality"].get_state(), "\n")

print("Meshing process complete.")
