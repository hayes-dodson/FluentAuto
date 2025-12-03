def create_BL_control(tasks, name, zones, n_layers, last_ratio):
    if not zones:
        print(f"Skipping BL control {name}, no zones.")
        return

    add_bl = tasks["Add Boundary Layers"]
    add_bl.AddChildToTask()
    add_bl.InsertCompoundChildTask()

    child = tasks[add_bl.ChildNames[-1]]

    child.Arguments.set_state({
        "BLControlName": name,
        "BoundaryZones": zones,
        "NumberOfLayers": n_layers,
        "LastLayerRatio": last_ratio,
    })

    add_bl.Execute()
    print(f"Created BL control {name} for zones: {zones}")
