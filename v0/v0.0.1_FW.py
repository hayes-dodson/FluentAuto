# run_frontwing.py
import os
from solver_core import run_component_solver

def main():
    geom = input("Enter mesh file (.msh.h5 or .cas.h5) for FRONT WING: ").strip()
    sim_name = input("Simulation name (front wing): ").strip() or "frontwing_sim"
    outdir = sim_name
    os.makedirs(outdir, exist_ok=True)

    target_zones = ["frontwing"]   # ← ONLY FRONT WING ZONE

    run_component_solver(
        mesh_path=geom,
        outdir=outdir,
        zones=target_zones,
        sim_name=sim_name
    )

if __name__ == "__main__":
    main()
