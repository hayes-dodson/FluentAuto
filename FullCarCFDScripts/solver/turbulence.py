def enable_GEKO(session):
    """Enable GEKO turbulence model with curvature correction OFF initially."""
    session.solver.Settings.Models.Turbulence = {
        "model": "k-omega",
        "k-omega_model": "GEKO",
        "geko_production_limiter": True,
        "geko_curvature_correction": False      # OFF for early stability
    }
    print("GEKO turbulence model enabled (curvature correction OFF).")


def enable_curvature_correction(session):
    """Turn ON curvature correction AFTER solver has stabilized."""
    print("Enabling GEKO curvature correction...")
    try:
        turb = session.solver.Settings.Models.Turbulence
        turb.geko_curvature_correction = True
        print("Curvature correction ON.")
    except Exception as e:
        print("Failed to enable curvature correction:", e)
