def ramp_relaxation(session):
    solver = session.solver.Settings.Solution.RelaxationFactors

    print("Relaxation ramp start...")

    solver.set_state({"mom":0.1,"press":0.1,"k":0.1,"omega":0.1})
    session.solution.RunCalculation.iterate(200)

    solver.set_state({"mom":0.3,"press":0.3,"k":0.3,"omega":0.3})
    session.solution.RunCalculation.iterate(400)

    solver.set_state({"mom":0.5,"press":0.5,"k":0.5,"omega":0.5})
    session.solution.RunCalculation.iterate(600)

    print("Relaxation ramp complete.")


def ramp_CFL(session):
    ps = session.solver.Settings.Solution.PseudoTransient

    print("Pseudo-transient CFL ramp start...")
    ps.set_state({"enabled": True, "cfl": 1.0})
    session.solution.RunCalculation.iterate(300)

    ps.cfl = 5.0
    session.solution.RunCalculation.iterate(400)

    ps.cfl = 20.0
    session.solution.RunCalculation.iterate(600)

    print("CFL ramp complete.")
