import os
import time
import argparse
import glob

import ansys.fluent.core as pyfluent

# GUI file picker
from tkinter import Tk, filedialog
Tk().withdraw()

# Load settings
from config.settings import SETTINGS

# Meshing
from meshing.mesh_pipeline import run_mesh_pipeline

# Solver utilities
from solver.turbulence import enable_GEKO, enable_curvature_correction
from solver.boundary_conditions import apply_boundary_conditions, apply_wheel_motion
from solver.reference_values import set_reference_values
from solver.ramping import ramp_relaxation, ramp_CFL
from solver.auto_restart import check_divergence_and_recover
from solver.projected_area import compute_projected_area
from solver.aero_coeffs import get_fluent_coefficients

# Postprocessing
from post.mesh_quality import (
    get_mesh_quality,
    save_mesh_quality_csv,
    print_mesh_quality_summary,
)

from post.yp_report import (
    get_yplus_statistics,
    print_yplus_summary,
    export_yplus_contour,
)

from post.pressure_maps import export_pressure_map
from post.data_export import export_case_summary_csv


# ======================================================================
#                           CASE PIPELINE
# ======================================================================

def run_case(geometry_path: str, output_dir: str, global_summary_csv: str | None = None):

    os.makedirs(output_dir, exist_ok=True)

    print("\n========================================")
    print("           FSAE CFD PIPELINE")
    print("========================================")
    print(f"Geometry  : {geometry_path}")
    print(f"Output    : {output_dir}")
    print("========================================\n")

    # ------------------------------------------------------------
    # Launch Fluent Meshing
    # ------------------------------------------------------------
    print("[Main] Launching Fluent Meshing...")

    meshing = pyfluent.launch_fluent(
        mode=pyfluent.FluentMode.MESHING,
        precision=pyfluent.Precision.DOUBLE,
        processor_count=60,
        dimension=3,
        mpi_type="intel"
    )

    # Run full mesh pipeline
    run_mesh_pipeline(meshing, geometry_path, SETTINGS)

    # Save mesh
    mesh_file = os.path.join(output_dir, "mesh.msh.h5")
    try:
        meshing.meshing.SaveMesh(file_name=mesh_file)
        print(f"[Main] Mesh saved: {mesh_file}")
    except Exception as e:
        print("[Main] Mesh save error:", e)
        raise

    # ------------------------------------------------------------
    # Launch Fluent Solver
    # ------------------------------------------------------------
    print("\n[Main] Launching Fluent Solver...")

    solver = pyfluent.launch_fluent(
        mode=pyfluent.FluentMode.SOLVER,
        precision=pyfluent.Precision.DOUBLE,
        processor_count=60,
        dimension=3,
        mpi_type="intel"
    )

    solver.solver.File.Read(file_type="mesh", file_name=mesh_file)
    print("[Main] Mesh loaded into solver.")

    # Mesh quality evaluation
    mesh_metrics = get_mesh_quality(solver)
    print_mesh_quality_summary(mesh_metrics)

    save_mesh_quality_csv(mesh_metrics, os.path.join(output_dir, "mesh_quality.csv"))

    # Physics setup
    enable_GEKO(solver)
    apply_boundary_conditions(solver, SETTINGS)
    apply_wheel_motion(solver, SETTINGS)
    set_reference_values(solver, SETTINGS)

    # Solver stabilization
    ramp_relaxation(solver)
    ramp_CFL(solver)

    # Turn curvature correction on after stabilization
    enable_curvature_correction(solver)

    # Main solver run
    max_iters = SETTINGS["max_iterations"]
    print(f"[Main] Running {max_iters} iterations...")
    solver.solution.RunCalculation.iterate(max_iters)

    # Divergence / floating point handler
    check_divergence_and_recover(solver, SETTINGS)

    # Aero properties
    area_full = compute_projected_area(solver, SETTINGS)
    aero = get_fluent_coefficients(solver)
    Cd, Cl = aero["Cd"], aero["Cl"]

    SCx = Cd * area_full if Cd is not None else None
    SCz = Cl * area_full if Cl is not None else None

    print("\n========== FINAL AERO RESULTS ==========")
    print(f"Cd  = {Cd}")
    print(f"Cl  = {Cl}")
    print(f"SCx = {SCx}")
    print(f"SCz = {SCz}")
    print(f"Area (full) = {area_full}")
    print("=========================================\n")

    # y+
    y_stats = get_yplus_statistics(solver)
    print_yplus_summary(y_stats)
    export_yplus_contour(solver, os.path.join(output_dir, "yplus_contour.png"))

    # Pressure map
    export_pressure_map(solver, os.path.join(output_dir, "pressure_map.png"))

    # Save case & data
    try:
        solver.solver.File.Write(file_type="case", file_name=os.path.join(output_dir, "final.cas.h5"))
        solver.solver.File.Write(file_type="data", file_name=os.path.join(output_dir, "final.dat.h5"))
    except Exception as e:
        print("[Main] Case/Data save error:", e)

    # Export summary CSV
    case_name = os.path.splitext(os.path.basename(geometry_path))[0]
    summary_file = (
        global_summary_csv if global_summary_csv is not None else os.path.join(output_dir, "summary.csv")
    )

    export_case_summary_csv(
        file_path=summary_file,
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
    print("        CFD CASE COMPLETE")
    print("========================================\n")

    # The solver is returned for live residual monitoring
    return solver


# ======================================================================
#                            MAIN ENTRYPOINT
# ======================================================================

def main():

    parser = argparse.ArgumentParser(description="FSAE CFD Automation")

    parser.add_argument("--geom", "-g", type=str, help="Path to geometry file")
    parser.add_argument("--out", "-o", type=str, help="Output directory")
    parser.add_argument("--batch-folder", "-bf", type=str, help="Folder of geometries to run")
    parser.add_argument("--resume", action="true", help="Resume from existing case/data")
    parser.add_argument("--live", action="store_true", help="Live residual monitoring")

    args = parser.parse_args()

    # ------------------------------------------------------------------
    # BATCH MODE
    # ------------------------------------------------------------------
    if args.batch_folder:
        folder = args.batch_folder
        if not os.path.isdir(folder):
            print(f"[ERROR] Batch folder not found: {folder}")
            return

        geoms = glob.glob(os.path.join(folder, "*.step")) + \
                glob.glob(os.path.join(folder, "*.stp")) + \
                glob.glob(os.path.join(folder, "*.iges"))

        if not geoms:
            print("[Batch] No geometry files found.")
            return

        result_root = os.path.join(folder, "_results")
        os.makedirs(result_root, exist_ok=True)

        summary_csv = os.path.join(result_root, "batch_summary.csv")

        for geom in geoms:
            name = os.path.splitext(os.path.basename(geom))[0]
            out_dir = os.path.join(result_root, name)
            os.makedirs(out_dir, exist_ok=True)

            print(f"\n[Batch] Running: {geom}")
            run_case(
                geometry_path=geom,
                output_dir=out_dir,
                global_summary_csv=summary_csv
            )
        return

    # ------------------------------------------------------------------
    # SINGLE CASE MODE
    # ------------------------------------------------------------------

    # Geometry path
    if args.geom:
        geom_path = args.geom
    elif SETTINGS["geometry_path"]:
        geom_path = SETTINGS["geometry_path"]
    else:
        # GUI file picker
        print("[Prompt] Select geometry file...")
        geom_path = filedialog.askopenfilename(
            title="Select Geometry",
            filetypes=[("CAD Files", "*.step *.stp *.iges *.igs *.x_t"), ("All Files", "*.*")]
        )
        if not geom_path:
            print("[ERROR] No geometry selected.")
            return

    # Output directory
    output_dir = args.out if args.out else SETTINGS["output_root"]
    os.makedirs(output_dir, exist_ok=True)

    # Run the CFD case
    solver = run_case(
        geometry_path=geom_path,
        output_dir=output_dir,
        global_summary_csv=None
    )

    # ------------------------------------------------------------------
    # LIVE RESIDUAL MONITORING
    # ------------------------------------------------------------------

    if args.live and solver is not None:
        print("[LIVE] Tracking residuals...")
        try:
            while True:
                res = solver.solution.Monitors.Residual.GetValues()
                print(
                    f"[LIVE] continuity={res['continuity']:.3e} | "
                    f"mom-x={res['x-momentum']:.3e}"
                )
                time.sleep(1.5)
        except KeyboardInterrupt:
            print("\n[LIVE] Monitoring stopped by user.")


# ======================================================================
#                    RUN MAIN
# ======================================================================

if __name__ == "__main__":
    main()
