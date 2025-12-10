# run_undertray.py
import os
from solver_core import run_component_solver

def main():
    geom = input("Enter mesh file (.msh.h5 or .cas.h5) for UNDERTRAY: ").strip()
    sim_name = input("Simulation name (undertray): ").strip() or "undertray_sim"
    outdir = sim_name
    os.makedirs(outdir, exist_ok=True)

    target_zones = ["undertray"]  # ← ONLY UNDERTRAY ZONE

    run_component_solver(
        mesh_path=geom,
        outdir=outdir,
        zones=target_zones,
        sim_name=sim_name
    )

if __name__ == "__main__":
    main()
