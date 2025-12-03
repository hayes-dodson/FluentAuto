def export_residuals(session, file="residuals.csv"):
    session.solution.Monitors.Residual.Export(file)
    print("Residuals exported:", file)
