def check_divergence_and_recover(session, settings):
    """
    Checks for floating point error or divergence (residual spike).
    If detected, runs stabilization iterations with low relaxation.
    """

    monitors = session.solution.Monitors.Residual
    vals = monitors.GetValues()

    # simple threshold for divergence
    if vals["continuity"] > 1.0:
        print("Divergence detected! Running auto-recovery...")

        solver = session.solver.Settings.Solution.RelaxationFactors
        solver.set_state({"mom":0.1,"press":0.1,"k":0.1,"omega":0.1})

        session.solution.RunCalculation.iterate(
            settings["floating_point_recovery_iterations"]
        )

        print("Recovered.")
        solver.set_state({"mom":0.5,"press":0.5,"k":0.5,"omega":0.5})
