def add_local_refinement_region(session, name, size, bounds=None, labels=None):
    task = session.workflow.TaskObject["Add Local Refinement"]
    task.AddChildToTask()
    task.InsertCompoundChildTask()

    child = session.workflow.TaskObject[task.ChildNames[-1]]

    args = {"Name": name, "MeshSize": size}

    if labels:
        args.update({
            "Type": "box",
            "CoordinateSpecificationMethod": "ratio-relative-to-geometry-size",
            "SelectBy": "label",
            "LabelList": labels
        })
    else:
        args.update({
            "Type": "box",
            "CoordinateSpecificationMethod": "direct-coordinates",
            "Xmin": bounds["xmin"],
            "Xmax": bounds["xmax"],
            "Ymin": bounds["ymin"],
            "Ymax": bounds["ymax"],
            "Zmin": bounds["zmin"],
            "Zmax": bounds["zmax"],
        })

    child.Arguments.set_state(args)
    task.Execute()
    print(f"[Refinement] Added region: {name}")


def add_all_local_refinements(session):
    # Near
    add_local_refinement_region(
        session, "near", 0.032,
        bounds={"xmin": -2.029, "xmax": 6.89, "ymin": 0, "ymax": 1.803,
                "zmin": 0, "zmax": 1.283}
    )

    # Mid
    add_local_refinement_region(
        session, "mid", 0.064,
        bounds={"xmin": -2.229, "xmax": 12.732, "ymin": 0, "ymax": 2.646,
                "zmin": 0, "zmax": 1.88}
    )

    # Far
    add_local_refinement_region(
        session, "far", 0.128,
        bounds={"xmin": -2.429, "xmax": 18.574, "ymin": 0, "ymax": 3.489,
                "zmin": 0, "zmax": 2.477}
    )

    # Wheel refinements
    add_local_refinement_region(session, "fw-zone", 0.032, labels=["fw"])
    add_local_refinement_region(session, "rw-zone", 0.032, labels=["rw"])
