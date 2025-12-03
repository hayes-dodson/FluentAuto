def compute_projected_area(session, settings):
    """
    Computes projected frontal area for half-car and returns full-car value.
    Uses Fluent surface integral with minimum feature size.
    """
    zones = settings["projected_area_zones"]
    min_len = settings["min_feature_size"]

    rep = session.post.ReportsSurfaceIntegrals
    rep["proj_area"] = {
        "report_type": "projected-area",
        "direction": [1, 0, 0],   # frontal direction (+X)
        "zones": zones,
        "min_length": min_len
    }

    A_half = rep["proj_area"].Compute()
    A_full = 2 * A_half
    return A_full
