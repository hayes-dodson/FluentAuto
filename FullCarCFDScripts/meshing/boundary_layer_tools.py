import math

def compute_bl_height(settings, mu=1.8e-5):
    rho = settings["air_density"]
    V = settings["inlet_velocity_mph"] * 0.44704
    L = settings["wheelbase"]

    Re = rho * V * L / mu
    delta = 0.37 * L / (Re ** 0.2)

    return delta


def compute_first_layer_height(settings, mu=1.8e-5):
    rho = settings["air_density"]
    V = settings["inlet_velocity_mph"] * 0.44704
    L = settings["wheelbase"]

    ReL = rho * V * L / mu
    Cf = 0.0576 / (ReL ** 0.2)

    tau_w = Cf * 0.5 * rho * V**2
    u_tau = (tau_w / rho)**0.5

    y = (settings["target_yplus"] * mu) / (rho * u_tau)
    return y
