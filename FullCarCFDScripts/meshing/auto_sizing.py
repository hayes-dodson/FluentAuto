def add_local_sizing(tasks, labels, min_size, max_size, curvature_angle, growth_rate, scope):
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
    print(f"Added local sizing for: {labels}")
