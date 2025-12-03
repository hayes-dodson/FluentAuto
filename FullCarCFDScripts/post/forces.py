def export_forces(session, zones, file="forces.csv"):
    rep = session.post.ReportsForces
    rep["force"] = {
        "zones": zones,
        "x_dir": [1,0,0],
        "y_dir": [0,1,0],
        "z_dir": [0,0,1],
    }
    rep["force"].ComputeAndExport(file)
    print("Exported forces:", file)
