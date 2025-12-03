import os
import ansys.fluent.core as pyfluent
import argparse
import glob
import time
from tkinter import Tk, filedialog

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

    return solver


# ========================================================================
#                      MAIN ENTRYPOINT (single case)
# ========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="FSAE CFD Automation — Single Case / Batch Runner"
    )

    # -------------------------
    # INPUT OVERRIDES
    # -------------------------
    parser.add_argument(
        "--geom", "-g",
        type=str,
        default=None,
        help="Path to a single geometry file (STEP/IGES/Parasolid/etc)."
    )

    parser.add_argument(
        "--out", "-o",
        type=str,
        default=None,
        help="Output directory for results."
    )

    # -------------------------
    # BATCH MODE
    # -------------------------
    parser.add_argument(
        "--batch-folder", "-bf",
        type=str,
        default=None,
        help="Folder containing multiple geometry files for batch processing."
    )

    # -------------------------
    # RESUME MODE
    # -------------------------
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume a crashed simulation from case/data files if available."
    )

    # -------------------------
    # INTERACTIVE LIVE DISPLAY
    # -------------------------
    parser.add_argument(
        "--live",
        action="store_true",
        help="Show residuals and ETA live while solver is running."
    )

    args = parser.parse_args()

    # -------------------------
    # BATCH MODE HANDLER
    # -------------------------
    if args.batch_folder is not None:
        folder = args.batch_folder
        if not os.path.isdir(folder):
            print(f"[ERROR] Batch folder does not exist: {folder}")
            return

        geoms = glob.glob(os.path.join(folder, "*.step")) + \
                glob.glob(os.path.join(folder, "*.iges")) + \
                glob.glob(os.path.join(folder, "*.stp"))

        if not geoms:
            print("[Batch] No geometry files found in folder.")
            return

        print(f"[Batch] Found {len(geoms)} geometries.")
        for geom in geoms:
            name = os.path.splitext(os.path.basename(geom))[0]
            out_dir = os.path.join(folder, "_results", name)
            os.makedirs(out_dir, exist_ok=True)

            print(f"\n[BATCH RUN] Geometry: {geom}")
            run_case(
                geometry_path=geom,
                output_dir=out_dir,
                global_summary_csv=os.path.join(folder, "_results", "batch_summary.csv")
            )
        return

    # -------------------------
    # NORMAL SINGLE-CASE MODE
    # -------------------------

    # 1. Determine geometry path
    if args.geom is not None:
        geom_path = args.geom
        print(f"[CLI] Using geometry: {geom_path}")

    else:
        # If settings file has a path, use it
        if SETTINGS["geometry_path"]:
            geom_path = SETTINGS["geometry_path"]
            print(f"[Settings] Using geometry: {geom_path}")
        else:
            print("[Prompt] No geometry provided. Opening file picker...")
            geom_path = filedialog.askopenfilename(
                title="Select Geometry File",
                filetypes=[
                    ("CAD files", "*.step *.stp *.iges *.igs *.x_t *.x_b"),
                    ("All files", "*.*")
                ]
            )
            if not geom_path:
                print("[ERROR] No geometry selected.")
                return

    # 2. Determine output directory
    if args.out is not None:
        output_dir = args.out
        print(f"[CLI] Output directory: {output_dir}")
    else:
        output_dir = SETTINGS["output_root"]

    os.makedirs(output_dir, exist_ok=True)

    # -------------------------
    # RESUME MODE
    # -------------------------
    if args.resume:
        casefile = os.path.join(output_dir, "final.cas.h5")
        datafile = os.path.join(output_dir, "final.dat.h5")

        if os.path.exists(casefile) and os.path.exists(datafile):
            print("[Resume] Restarting from previous case/data files.")
            solver = pyfluent.launch_fluent(
                mode=pyfluent.FluentMode.SOLVER,
                precision=pyfluent.Precision.DOUBLE,
                processor_count=60,
                dimension=3
            )
            solver.solver.File.Read(file_type="case", file_name=casefile)
            solver.solver.File.Read(file_type="data", file_name=datafile)

            # Continue solving
            print("[Resume] Continuing for 400 more iterations...")
            solver.solution.RunCalculation.iterate(400)

            return
        else:
            print("[Resume] No restart files found. Running fresh simulation.")

    # -------------------------
    # RUN THE CFD CASE
    # -------------------------
    solver = run_case(
        geometry_path=geom_path,
        output_dir=output_dir,
        global_summary_csv=None
    )

    # -------------------------
    # LIVE INTERACTION MODE
    # (This simply shows solver progress)
    # -------------------------
    if args.live and solver is not None:
        print("[LIVE] Tracking residuals...")
        try:
            while True:
                res = solver.solution.Monitors.Residual.GetValues()
                print(f"[LIVE] continuity={res['continuity']:.3e}  "
                      f"mom-x={res['x-momentum']:.3e}")
                time.sleep(1.5)
        except KeyboardInterrupt:
            print("\n[LIVE] Stopped monitoring.")


if __name__ == "__main__":
    main()
