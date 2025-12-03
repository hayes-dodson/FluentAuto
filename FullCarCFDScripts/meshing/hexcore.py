def generate_hexcore(tasks):
    vol = tasks["Generate the Volume Mesh"]

    vol.Arguments.set_state({
        "Solver": "Fluent",
        "FillWith": "poly-hexcore",
        "GrowthRate": 1.25,
        "TransitionLayers": 4,
        "AnisotropicStretching": True,
        "MinCellLength": 0.0005,
        "MaxCellLength": 0.256,
        "PeelLayers": 1,
        "EnableParallel": True,
    })

    vol.UpdateChildTasks()
    vol.Execute()
    print("Hexcore volume mesh complete.")

    try:
        print("Hexcore quality:", vol.Outputs["Quality"].get_state())
    except:
        print("Could not read hexcore quality.")
