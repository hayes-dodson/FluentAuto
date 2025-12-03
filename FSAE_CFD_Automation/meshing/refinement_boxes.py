from config.wheel_centers import WHEEL_CENTERS

def generate_wheel_refinement_boxes(session, settings):
    pad = settings["refinement_padding"]
    dia = settings["tire_diameter"]

    for zone, (x, y, z) in WHEEL_CENTERS.items():

        xmin = x - dia/2 - pad
        xmax = x + dia/2 + pad
        ymin = y - dia/2 - pad
        ymax = y + dia/2 + pad
        zmin = z - dia/2 - pad
        zmax = z + dia/2 + pad

        print(f"[WheelBox] {zone}: [{xmin},{xmax}] x [{ymin},{ymax}] x [{zmin},{zmax}]")

        task = session.workflow.TaskObject["Add Local Refinement"]
        task.AddChildToTask()
        task.InsertCompoundChildTask()

        child = session.workflow.TaskObject[task.ChildNames[-1]]
        child.Arguments.set_state({
            "Name": f"ref-{zone}",
            "Type": "box",
            "MeshSize": 0.032,
            "CoordinateSpecificationMethod": "direct-coordinates",
            "Xmin": xmin, "Xmax": xmax,
            "Ymin": ymin, "Ymax": ymax,
            "Zmin": zmin, "Zmax": zmax
        })

        task.Execute()
