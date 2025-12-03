import math

def compute_bl_height(settings, viscosity=1.8e-5):
    """
    BL thickness from Reynolds number:
    δ ≈ 0.37 * x / Re_x^(1/5)
    Using wheelbase as characteristic length.
    """
    rho = settings["air_density"]
    V = settings["final_inlet_velocity_mph"] * 0.44704
    L = settings["wheelbase_m"]

    Re = rho * V * L / viscosity
    delta = 0.37 * L / (Re ** 0.2)
    return delta


def compute_first_layer_height(settings, viscosity=1.8e-5):
    """
    Computes y distance for y+ = 1.
    uτ estimated via skin friction relation.
    """
    rho = settings["air_density"]
    V = settings["final_inlet_velocity_mph"] * 0.44704

    Cf = 0.0576 / ( (rho*V*settings["wheelbase_m"]/viscosity) ** 0.2 )
    tau_w = Cf * 0.5 * rho * V**2
    u_tau = (tau_w / rho)**0.5

    y = (settings["target_y_plus"] * viscosity) / (rho * u_tau)
    return y
