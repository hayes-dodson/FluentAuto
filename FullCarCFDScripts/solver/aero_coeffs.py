def get_fluent_coefficients(session):
    """
    Pull final Cd and Cl directly from Fluent monitors.
    """

    drag_mon = session.solution.Monitors.DragMonitor
    lift_mon = session.solution.Monitors.LiftMonitor

    try:
        Cd = drag_mon.GetData()[-1]
    except:
        Cd = None

    try:
        Cl = lift_mon.GetData()[-1]
    except:
        Cl = None

    return {"Cd": Cd, "Cl": Cl}
