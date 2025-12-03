def enable_GEKO(session):
    """
    Enables GEKO turbulence model with production limiter on
    and curvature correction initially OFF.
    """
    turb = session.solver.Settings.Models.Turbulence

    turb.model = "k-omega"
    turb.k_omega_model = "GEKO"

    turb.geko_production_limiter = True
    turb.geko_curvature_correction = False

    print("[Turbulence] GEKO enabled (curvature correction OFF)")


def enable_curvature_correction(session):
    """
    Turn ON curvature correction after relaxation & CFL ramp.
    """
    turb = session.solver.Settings.Models.Turbulence

    turb.geko_curvature_correction = True
    print("[Turbulence] GEKO curvature correction ON")
