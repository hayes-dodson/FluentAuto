import os
import ansys.fluent.core as pyfluent

from config.settings import SETTINGS, WHEEL_CENTERS

# Meshing
from meshing.mesh_pipeline import run_mesh_pipeline
from meshing.local_refinement_regions import add_all_local_refinements
from meshing.refinement_boxes import generate_wheel_refinement_boxes
from meshing.boundary_layer_tools import compute_first_layer_height, compute_bl_height

# Solver
from solver.turbulence import enable_GEKO, enable_curvature_correction
from solver.boundary_conditions import apply_boundary_conditions, apply_wheel_motion
from solver.reference_values import set_reference_values
from solver.ramping import ramp_relaxation, ramp_CFL
from solver.auto_restart import check_divergence_and_recover
from solver.projected_area import compute_projected_area
from solver.aero_coeffs import get_fluent_coefficients

# Post
from post.pressure_maps import export_pressure_map
from batch.excel_writer import append_results_to_excel


def main():

    geom = SETTINGS["geometry_path"]
    output_dir = SETTINGS["output_root"]
    os.makedirs(output_dir, exist_ok=True)

    print("\n========================================")
    print("      STARTING FSAE CFD PIPELINE")
    print("========================================\n")

    # ----------------------------------------------------------
    #              FLUENT MESHING SESSION
    # ----------------------------------------------------------
    print("Launching Fluent Meshing...")

    meshing = pyfluent.launch_fluent(
        mode=pyfluent.FluentMode.MESHING,
        precision=pyfluent.Precision.DOUBLE,
        processor_count=60,
        dimension=3,
        mpi_type="intel"
    )

    # ---------- IMPORT GEOMETRY ----------
    run_mesh_pipeline(meshing, geom, SETTINGS)

    # ---------- ADD GLOBAL REFINEMENT REGIONS ----------
    print("Adding local refinement regions...")
    add_all_local_refinements(meshing)

    # ---------- WHEEL REFINEMENT BOXES ----------
    print("Adding wheel refinement boxes...")
    generate_wheel_refinement_boxes(meshing, SETTINGS)

    # ---------- SURFACE MESH ----------
    print("Generating surface mesh...")
    surface_task = meshing.workflow.TaskObject["Generate the Surface Mesh"]
    surface_task.Execute()

    # ---------- OVERSET: VOLUME MESH ----------
    print("Generating volume mesh...")
    volume_task = meshing.workflow.TaskObject["Generate the Volume Mesh"]
    volume_task.Execute()

    # Save mesh
    mesh_file = os.path.join(output_dir, "mesh.msh.h5")
    meshing.meshing.SaveMesh(file_path=mesh_file)
    print("Saved mesh to:", mesh_file)


    # ----------------------------------------------------------
    #                 FLUENT SOLVER SESSION
    # ----------------------------------------------------------
    print("\nLaunching Fluent Solver...")

    solver = pyfluent.launch_fluent(
        mode=pyfluent.FluentMode.SOLVER,
        precision=pyfluent.Precision.DOUBLE,
        processor_count=60,
        dimension=3,
        mpi_type="intel"
    )

    solver.solver.File.Read(file_type="mesh", file_name=mesh_file)

    # ---------- TURBULENCE MODEL ----------
    enable_GEKO(solver)

    # ---------- BOUNDARY CONDITIONS ----------
    apply_boundary_conditions(solver, SETTINGS)

    # ---------- WHEEL MOTION ----------
    apply_wheel_motion(solver, SETTINGS)

    # ---------- REFERENCE VALUES ----------
    set_reference_values(solver, SETTINGS)

    # ---------- RAMP STAGE ----------
    print("\nRunning relaxation & CFL ramps...")
    ramp_relaxation(solver)
    ramp_CFL(solver)

    # ---------- ADD CURVATURE CORRECTION ----------
    enable_curvature_correction(solver)

    # ---------- MAIN SOLVE ----------
    print("\nRunning main solve...")
    solver.solution.RunCalculation.iterate(SETTINGS["max_final_iterations"])

    # ---------- DIVERGENCE CHECK ----------
    check_divergence_and_recover(solver, SETTINGS)

    # ----------------------------------------------------------
    #                  POSTPROCESSING
    # ----------------------------------------------------------

    # ---------- PROJECTED AREA ----------
    A_full = compute_projected_area(solver, SETTINGS)

    # ---------- AERO COEFFICIENTS ----------
    coeffs = get_fluent_coefficients(solver)
    Cd = coeffs["Cd"]
    Cl = coeffs["Cl"]
    SCx = Cd * A_full
    SCz = Cl * A_full

    print("\n===== FINAL RESULTS =====")
    print(f"Cd  = {Cd}")
    print(f"Cl  = {Cl}")
    print(f"SCx = {SCx}")
    print(f"SCz = {SCz}")
    print("=========================\n")

    # ---------- PRESSURE MAP ----------
    export_pressure_map(solver, file=os.path.join(output_dir, "pressure_map.png"))

    # ---------- SAVE CASE & DATA ----------
    case_file = os.path.join(output_dir, "final.cas.h5")
    data_file = os.path.join(output_dir, "final.dat.h5")

    solver.solver.File.Write(file_type="case", file_name=case_file)
    solver.solver.File.Write(file_type="data", file_name=data_file)
    print("Saved:", case_file)
    print("Saved:", data_file)

    # ---------- EXCEL SUMMARY ----------
    excel_path = os.path.join(output_dir, "summary.xlsx")
    append_results_to_excel(
        excel_path,
        {
            "Cd": Cd,
            "Cl": Cl,
            "SCx": SCx,
            "SCz": SCz,
            "Fx": None,   # optional, can be added later
            "Fz": None,
            "Area": A_full
        },
        case_name=os.path.basename(geom)
    )

    print("\nPipeline complete. Results saved to:", output_dir)


if __name__ == "__main__":
    main()
