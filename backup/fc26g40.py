import ansys.fluent.core as pyfluent

# Import File
import_file_name = ""
meshing_session = pyfluent.launch_fluent(
    mode=pyfluent.FluentMode.MESHING, precision=pyfluent.Precision.DOUBLE, processor_count=60, dimension=3, mpi_type="intel"
)
workflow = meshing_session.workflow
workflow.InitializeWorkflow(WorkflowType='Watertight Geometry')
tasks = workflow.TaskObject
import_geometry = tasks['Import Geometry']
import_geometry.Arguments.set_state({
    'FileName': import_file_name, 'LengthUnit': 'm'
})
import_geometry.Execute()

# Add Local Sizing
add_local_sizing = tasks['Add Local Sizing']
add_local_sizing.AddChildToTask()
add_local_sizing.Execute()

# Generate Surface Mesh
create_surface_mesh = tasks['Generate the Surface Mesh']
create_surface_mesh.Arguments = {
    'CFDSurfaceMeshControls': {'MaxSize': 0.3}
}
create_surface_mesh.Execute()

# Improve Surface Mesh
imp_surf = tasks["Improve Surface Mesh"]
imp_surf.AddChildToTask()
imp_surf.InsertCompoundChildTask()
surf_task = tasks[imp_surf.ChildNames[0]]
surf_task.Arguments.set_state({
    "FaceQualityLimit": 0.7
})
imp_surf.Execute()

# Describe Geometry
describe_geometry = tasks["Describe Geometry"]
describe_geometry.UpdateChildTasks(SetupTypeChanged=False)
describe_geometry.Arguments.set_state({
    "SetupType": "The geometry consists of only fluid regions with no voids"
})
describe_geometry.UpdateChildTasks(SetupTypeChanged=True)
describe_geometry.Execute()

# Update Boundaries
update_boundaries = tasks["Update Boundaries"]
update_boundaries.Arguments.set_state({
    "BoundaryLabelList": ["wall-inlet"],
    "BoundaryLabelTypeList": ["wall"],
    "OldBoundaryLabelList": ["wall-inlet"],
    "OldBoundaryLabelTypeList": ["velocity-inlet"],
})
update_boundaries.Execute()

# Update Regions
tasks["Update Regions"].Execute()

# Add Boundary Layers
add_boundary_layers = tasks["Add Boundary Layers"]
add_boundary_layers.AddChildToTask()
add_boundary_layers.InsertCompoundChildTask()
transition = tasks["last-ratio_1"]
transition.Arguments.set_state({
    "BLControlName": "last-ratio_1",
    "BoundaryZones": ["frontwing", "chassis", "fw", "fwb", "rw", "rwb", "undertray", "rearwing"],  # ← your zones
    "NumberOfLayers": 10,                   # ← number of layers
    "LastLayerRatio": 10.0                  # ← last-layer ratio
})
add_boundary_layers.Arguments.set_state({})
transition.Execute()

# Generate Volume Mesh
create_volume_mesh = tasks["Generate the Volume Mesh"]
create_volume_mesh.Arguments = {
    "Solver": "Fluent",                  # Solver type
    "FillWith": "poly-hexcore",          # Fill with poly-hexcore
    "PeelLayers": 1,                     # Peel layers
    "MinCellLength": 0.0005,             # Min cell length [m]
    "MaxCellLength": 0.256,              # Max cell length [m]
    "EnableParallel": True               # Enable parallel meshing
}
create_volume_mesh.Execute()

# Improve Volumetric Mesh
imp_vol = tasks["Improve Volume Mesh"]
imp_vol.AddChildToTask()
imp_vol.InsertCompoundChildTask()
vol_task = tasks[imp_vol.ChildNames[0]]
vol_task.Arguments.set_state({
    "QualityMethod": "Orthogonal",   # options: "Orthogonal", "Skewness"
    "CellQualityLimit": 0.2,
    "UseAdditionalCriteria": False   # UI: “No”
})
imp_vol.Execute()