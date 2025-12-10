# run_rearwing.py
import os
from solver_core import run_component_solver

def main():
    geom = input("Enter mesh file (.msh.h5 or .cas.h5) for REAR WING: ").strip()
    sim_name = input("Simulation name (rear wing): ").strip() or "rearwing_sim"
    outdir = sim_name
    os.makedirs(outdir, exist_ok=True)

    target_zones = ["rearwing"]  # ← ONLY REAR WING ZONE

    run_component_solver(
        mesh_path=geom,
        outdir=outdir,
        zones=target_zones,
        sim_name=sim_name
    )

if __name__ == "__main__":
    main()
