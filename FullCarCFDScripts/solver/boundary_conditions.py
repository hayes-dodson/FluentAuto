def apply_boundary_conditions(session, settings):
    inlet_vel = settings["final_inlet_velocity_mph"]
    wheel_speed = settings["wheel_rotational_speed_rad_s"]
    wheel_zones = settings["wheel_zone_names"]

    # Inlet
    bc = session.solver.BoundaryConditions["inlet"]
    bc.velocity = inlet_vel
    print("Inlet set to", inlet_vel, "mph")

    # Ground
    ground = session.solver.BoundaryConditions["ground"]
    ground.type = "moving-wall"
    ground.motion = {
        "motion_type": "translational",
        "speed": inlet_vel,
        "direction": [1, 0, 0]
    }
    print("Ground plane moving at", inlet_vel, "mph")

    # Wheels
    for wz in wheel_zones:
        w = session.solver.BoundaryConditions[wz]
        w.type = "moving-wall"
        w.motion = {
            "motion_type": "rotational",
            "spin_rate": wheel_speed,
            "axis_direction": [0,1,0],
        }
        print(f"Wheel {wz} spinning at {wheel_speed} rad/s")
