def set_reference_values(session, settings):
    ref = session.solver.Settings.ReferenceValues

    ref.area = 1.0
    ref.length = settings["wheelbase"]
    ref.density = settings["air_density"]
    ref.velocity = settings["inlet_velocity_mph"] * 0.44704

    print("[Ref] Reference values updated.")
