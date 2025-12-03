from config.wheel_centers import WHEEL_CENTERS

def apply_boundary_conditions(session, settings):
    vel = settings["inlet_velocity_mph"] * 0.44704

    bc = session.solver.BoundaryConditions

    # ------------------------
    # Inlet
    # ------------------------
    if "inlet" in bc:
        bc["inlet"].type = "velocity-inlet"
        bc["inlet"].vmag = vel
        bc["inlet"].turb_intensity = 0.05
        bc["inlet"].length_scale = 0.1
        print(f"[BC] Inlet velocity: {vel} m/s")

    # ------------------------
    # Ground (moving wall)
    # ------------------------
    if "ground" in bc:
        bc["ground"].type = "moving-wall"
        bc["ground"].vmag = vel
        bc["ground"].direction = [1, 0, 0]
        print("[BC] Ground moving at inlet velocity")

    # ------------------------
    # Symmetry plane
    # ------------------------
    if "symmetry" in bc:
        bc["symmetry"].type = "symmetry"
        print("[BC] Symmetry plane applied")

    # ------------------------
    # Pressure outlet
    # ------------------------
    if "outlet" in bc:
        bc["outlet"].type = "pressure-outlet"
        bc["outlet"].gauge_pressure = 0
        print("[BC] Pressure outlet")


def apply_wheel_motion(session, settings):
    speed = settings["wheel_rotational_speed"]

    bc = session.solver.BoundaryConditions

    for zone, origin in WHEEL_CENTERS.items():

        if zone not in bc:
            print(f"[Wheel] Zone '{zone}' not found — skipping")
            continue

        bc_zone = bc[zone]
        bc_zone.type = "moving-wall"

        bc_zone.motion = {
            "motion_type": "rotational",
            "axis_origin": origin,
            "axis_direction": [0, 1, 0],
            "spin_rate": speed
        }

        print(f"[Wheel] {zone}: spin={speed} rad/s at {origin}")
