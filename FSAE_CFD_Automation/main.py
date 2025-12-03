import os
import ansys.fluent.core as pyfluent

from config.settings import SETTINGS

# Meshing
from meshing.mesh_pipeline import run_mesh_pipeline

# Solver
from solver.turbulence import enable_GEKO, enable_curvature_correction
from solver.boundary_conditions import apply_boundary_conditions, apply_wheel_motion
from solver.reference_values import set_reference_values
from solver.ramping import ramp_relaxation, ramp_CFL
from solver.auto_restart import check_divergence_and_recover
from solver.projected_area import compute_projected_area
from solver.aero_coeffs import get_fluent_coefficients

# Post
from post.mesh_quality import (
    get_mesh_quality,
    save_mesh_quality_csv,
    print_mesh_quality_summary
)

from post.yp_report import (
    get_yplus_statistics,
    print_yplus_summary,
    export_yplus_contour
)

from post.pressure_maps import export_pressure_map
from post.data_export import export_case_summary_csv


# ========================================================================
#                      SINGLE CASE RUN PIPELINE
# ========================================================================

def run_case(geometry_path: str, output_dir: str, global_summary_csv: str | None = None):

    os.makedirs(output_dir, exist_ok=True)

    print("\n========================================")
    print("         FSAE CFD PIPELINE START")
    print("========================================")
    print(f"Geometry : {geometry_path}")
    print(f"Output   : {output_dir}")
    print("========================================\n")

    # =====================================================================
    #                           MESHING SESSION
    # =====================================================================

    print("[Main] Launching Fluent Meshing...")

    meshing = pyfluent.launch_fluent(
        mode=pyfluent.FluentMode.MESHING,
        precision=pyfluent.Precision.DOUBLE,
        processor_count=60,
        dimension=3,
        mpi_type="intel",
    )

    # Run mesh pipeline (imports geometry, refinement, boundary layers, mesh)
    run_mesh_pipeline(meshing, geometry_path, SETTINGS)

    # Save mesh to file
    mesh_file = os.path.join(output_dir, "mesh.msh.h5")
    try:
        meshing.meshing.SaveMesh(file_name=mesh_file)
        print(f"[Main] Saved mesh: {mesh_file}")
    except Exception as e:
        print("[Main] Failed to save mesh:", e)
        raise

    # =====================================================================
    #                           SOLVER SESSION
    # =====================================================================

    print("\n[Main] Launching Fluent Solver...")

    solver = pyfluent.launch_fluent(
        mode=pyfluent.FluentMode.SOLVER,
        precision=pyfluent.Precision.DOUBLE,
        processor_count=60,
        dimension=3,
        mpi_type="intel",
    )

    solver.solver.File.Read(file_type="mesh", file_name=mesh_file)
    print("[Main] Mesh read into solver.")

    # Mesh quality analysis
    mesh_metrics = get_mesh_quality(solver)
    print_mesh_quality_summary(mesh_metrics)

    mesh_q_csv = os.path.join(output_dir, "mesh_quality.csv")
    save_mesh_quality_csv(mesh_metrics, mesh_q_csv)

    # Turbulence model
    enable_GEKO(solver)

    # Boundary conditions
    apply_boundary_conditions(solver, SETTINGS)
    apply_wheel_motion(solver, SETTINGS)

    # Reference values
    set_reference_values(solver, SETTINGS)

    # =====================================================================
    #                               RAMPING
    # =====================================================================

    print("\n[Main] Running relaxation and CFL ramp...")
    ramp_relaxation(solver)
    ramp_CFL(solver)

    # Enable curvature correction after stabilization
    enable_curvature_correction(solver)

    # Main steady-state solve
    max_iters = SETTINGS["max_iterations"]
    print(f"[Main] Running main solve: {max_iters} iterations...")
    solver.solution.RunCalculation.iterate(max_iters)

    # Floating point recovery
    check_divergence_and_recover(solver, SETTINGS)

    # =====================================================================
    #                          POSTPROCESSING
    # =====================================================================

    # Projected area (half → full)
    area_full = compute_projected_area(solver, SETTINGS)

    # Cd & Cl from Fluent
    aero = get_fluent_coefficients(solver)
    Cd = aero["Cd"]
    Cl = aero["Cl"]

    SCx = Cd * area_full if Cd is not None else None
    SCz = Cl * area_full if Cl is not None else None

    print("\n===== FINAL AERO RESULTS =====")
    print(f"Cd  = {Cd}")
    print(f"Cl  = {Cl}")
    print(f"SCx = {SCx}")
    print(f"SCz = {SCz}")
    print(f"Area (full) = {area_full}")
    print("=============================\n")

    # y+ data
    y_stats = get_yplus_statistics(solver)
    print_yplus_summary(y_stats)

    yplus_png = os.path.join(output_dir, "yplus_contour.png")
    export_yplus_contour(solver, yplus_png)

    # Pressure map
    pressure_png = os.path.join(output_dir, "pressure_map.png")
    export_pressure_map(solver, pressure_png)

    # Save case+data
    try:
        solver.solver.File.Write(file_type="case", file_name=os.path.join(output_dir, "final.cas.h5"))
        solver.solver.File.Write(file_type="data", file_name=os.path.join(output_dir, "final.dat.h5"))
    except Exception as e:
        print("[Main] Failed writing case/data:", e)

    # Write summary row
    case_name = os.path.splitext(os.path.basename(geometry_path))[0]

    summary_csv = (
        global_summary_csv
        if global_summary_csv is not None
        else os.path.join(output_dir, "summary.csv")
    )

    export_case_summary_csv(
        file_path=summary_csv,
        case_name=case_name,
        Cd=Cd,
        Cl=Cl,
        SCx=SCx,
        SCz=SCz,
        area_full=area_full,
        yplus_stats=y_stats,
        mesh_metrics=mesh_metrics,
    )

    print("\n========================================")
    print("          PIPELINE COMPLETE")
    print("========================================\n")


# ========================================================================
#                      MAIN ENTRYPOINT (single case)
# ========================================================================

def main():
    geom = SETTINGS["geometry_path"]

    if not geom:
        print("Error: SETTINGS['geometry_path'] is empty.\n"
              "Set a geometry file path in config/settings.py.")
        return

    output_dir = SETTINGS["output_root"]
    os.makedirs(output_dir, exist_ok=True)

    run_case(geometry_path=geom, output_dir=output_dir, global_summary_csv=None)


if __name__ == "__main__":
    main()
