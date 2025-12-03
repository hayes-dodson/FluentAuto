from config.settings import SETTINGS

from meshing.mesh_pipeline import run_mesh_pipeline
from solver.turbulence import enable_GEKO, enable_curvature_correction
from solver.boundary_conditions import apply_boundary_conditions
from solver.reference_values import set_reference_values
from solver.ramping import ramp_relaxation, ramp_CFL

from post.forces import export_forces
from post.contours import export_contour
from post.residuals import export_residuals

import ansys.fluent.core as pyfluent


def main():

    geom = SETTINGS["geometry_path"]

    # ----------------------------------------------------------
    #  MESHING SESSION
    # ----------------------------------------------------------
    print("\n=== Launching Fluent Meshing ===\n")

    meshing = pyfluent.launch_fluent(
        mode=pyfluent.FluentMode.MESHING,
        precision=pyfluent.Precision.DOUBLE,
        processor_count=60,
        mpi_type="intel",
        dimension=3,
    )

    run_mesh_pipeline(meshing, geom, SETTINGS)


    # ----------------------------------------------------------
    #  SOLVER SESSION
    # ----------------------------------------------------------
    print("\n=== Launching Fluent Solver ===\n")

    session = pyfluent.launch_fluent(
        mode=pyfluent.FluentMode.SOLVER,
        precision=pyfluent.Precision.DOUBLE,
        processor_count=60,
        mpi_type="intel",
        dimension=3,
    )

    # --- Models ---
    enable_GEKO(session)

    # --- BCs ---
    apply_boundary_conditions(session, SETTINGS)

    # --- Ref Values ---
    set_reference_values(session)

    # ----------------------------------------------------------
    # RAMP SEQUENCE (FLOATING-POINT SAFE)
    # ----------------------------------------------------------
    print("\n=== Solver Stabilization Ramps ===\n")

    # Relaxation ramp (0.1 → 0.3 → 0.5)
    ramp_relaxation(session)

    # CFL ramp (1 → 5 → 20)
    ramp_CFL(session)

    # ----------------------------------------------------------
    # TURN ON CURVATURE CORRECTION HERE
    # ----------------------------------------------------------
    enable_curvature_correction(session)

    # ----------------------------------------------------------
    # FINAL SOLVE
    # ----------------------------------------------------------
    print("\n=== Final Solve (2000+ iterations) ===\n")

    session.solution.RunCalculation.iterate(2000)

    # ----------------------------------------------------------
    # POSTPROCESS
    # ----------------------------------------------------------
    print("\n=== Postprocessing ===\n")

    # Forces
    export_forces(session,
                  zones=["frontwing", "rearwing", "undertray", "chassis"],
                  file="forces.csv")

    # Contour
    export_contour(session,
                   variable="pressure",
                   plane="xy",
                   file="pressure.png")

    # Residuals
    export_residuals(session, "residuals.csv")

    print("\n=== CFD Pipeline Complete ===\n")


if __name__ == "__main__":
    main()
