def ramp_relaxation(session):
    """
    Momentum, pressure, k, and omega relaxation ramp
    to prevent early floating point errors.
    """

    rf = session.solver.Settings.Solution.RelaxationFactors

    print("[Ramp] Relaxation stage 1...")
    rf.set_state({"mom": 0.1, "press": 0.1, "k": 0.1, "omega": 0.1})
    session.solution.RunCalculation.iterate(200)

    print("[Ramp] Relaxation stage 2...")
    rf.set_state({"mom": 0.3, "press": 0.3, "k": 0.3, "omega": 0.3})
    session.solution.RunCalculation.iterate(300)

    print("[Ramp] Relaxation stage 3...")
    rf.set_state({"mom": 0.5, "press": 0.5, "k": 0.5, "omega": 0.5})
    session.solution.RunCalculation.iterate(400)

    print("[Ramp] Relaxation ramp complete.")


def ramp_CFL(session):
    """
    Pseudo-transient CFL ramp.
    """

    pt = session.solver.Settings.Solution.PseudoTransient

    print("[Ramp] CFL stage 1 (CFL = 1)")
    pt.set_state({"enabled": True, "cfl": 1.0})
    session.solution.RunCalculation.iterate(300)

    print("[Ramp] CFL stage 2 (CFL = 5)")
    pt.cfl = 5.0
    session.solution.RunCalculation.iterate(300)

    print("[Ramp] CFL stage 3 (CFL = 20)")
    pt.cfl = 20.0
    session.solution.RunCalculation.iterate(500)

    print("[Ramp] CFL ramp complete.")
