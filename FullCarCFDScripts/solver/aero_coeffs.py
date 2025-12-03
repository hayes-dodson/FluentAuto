def get_fluent_coefficients(session):
    drag = session.solution.Monitors.DragMonitor
    lift = session.solution.Monitors.LiftMonitor

    try:
        Cd = drag.GetData()[-1]
    except:
        Cd = None

    try:
        Cl = lift.GetData()[-1]
    except:
        Cl = None

    print(f"[Aero] Cd={Cd}, Cl={Cl}")
    return {"Cd": Cd, "Cl": Cl}
