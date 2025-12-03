def check_divergence_and_recover(session, settings):

    res = session.solution.Monitors.Residual
    vals = res.GetValues()

    if vals["continuity"] > 1.0:
        print("[Divergence] Detected! Running recovery...")

        rf = session.solver.Settings.Solution.RelaxationFactors
        rf.set_state({"mom": 0.1, "press": 0.1, "k": 0.1, "omega": 0.1})

        session.solution.RunCalculation.iterate(
            settings["floating_point_recovery_iterations"]
        )

        rf.set_state({"mom": 0.5, "press": 0.5, "k": 0.5, "omega": 0.5})

        print("[Divergence] Recovery complete.")
