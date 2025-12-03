def compute_projected_area(session, settings):
    ri = session.post.ReportsSurfaceIntegrals

    ri["proj"] = {
        "report_type": "projected-area",
        "direction": [1, 0, 0],
        "zones": settings["projected_area_zones"],
        "min_length": settings["min_feature_size"]
    }

    A_half = ri["proj"].Compute()
    A_full = 2 * A_half

    print(f"[Area] Half area = {A_half}")
    print(f"[Area] Full area = {A_full}")

    return A_full
