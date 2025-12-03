def get_mesh_quality(session):
    """
    Extracts mesh quality metrics from Fluent.
    Works for volume mesh after meshing stage or inside solver.
    """

    mesh = session.mesh

    try:
        q = mesh.GetQualityMetrics()
    except:
        print("Mesh quality metrics unavailable.")
        return None

    metrics = {}

    # Orthogonal quality
    if "orthogonal-quality" in q:
        ortho = q["orthogonal-quality"]
        metrics["ortho_min"] = ortho["minimum"]
        metrics["ortho_max"] = ortho["maximum"]
        metrics["ortho_avg"] = ortho["average"]
    else:
        metrics["ortho_min"] = None

    # Skewness
    if "skewness" in q:
        skew = q["skewness"]
        metrics["skew_min"] = skew["minimum"]
        metrics["skew_max"] = skew["maximum"]
        metrics["skew_avg"] = skew["average"]
    else:
        metrics["skew_max"] = None

    # Count poor cells
    bad_cells = 0
    if metrics["ortho_min"] is not None:
        if metrics["ortho_min"] < 0.1:
            bad_cells += 1

    metrics["bad_cells"] = bad_cells

    return metrics


def save_mesh_quality_csv(metrics, file_path):
    """Exports mesh quality metrics to a CSV file."""
    if metrics is None:
        return

    with open(file_path, "w") as f:
        f.write("metric,value\n")
        for key, value in metrics.items():
            f.write(f"{key},{value}\n")

    print("Saved mesh quality report:", file_path)
