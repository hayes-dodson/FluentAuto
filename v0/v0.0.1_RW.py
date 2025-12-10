##############################################
# FSAE REAR WING CFD AUTOMATION SCRIPT
# Full Meshing + Solver Pipeline
# Fluent 2025R2 — Watertight Geometry Workflow
# Isolated Rear Wing Geometry (No Wheels)
##############################################

import os
import time
import math
import ansys.fluent.core as pyfluent


###########################################################
# ---- USER INPUT INTERFACE ----
###########################################################

def ask_user_inputs():
    print("\n===========================================")
    print("      FSAE CFD AUTOMATION — REAR WING")
    print("===========================================\n")

    geom = input("Enter full path to REAR WING geometry (.step or .stp): ").strip()
    while not os.path.isfile(geom):
        geom = input("❗ File not found. Enter geometry file path again: ").strip()

    sim_name = input("Enter simulation name (e.g., RW_test01): ").strip()
    if sim_name == "":
        sim_name = "rearwing_sim"

    print("\nENTER VEHICLE BOUNDING BOX DIMENSIONS (M)")
    L = float(input("Vehicle Length  L (m): ").strip())
    W = float(input("Vehicle Width   W (m): ").strip())
    H = float(input("Vehicle Height  H (m): ").strip())

    outdir = os.path.join(os.getcwd(), sim_name)
    os.makedirs(outdir, exist_ok=True)

    return geom, sim_name, outdir, L, W, H


###########################################################
# ---- PRINT + WAIT UTILITIES ----
###########################################################

def print_header(msg):
    print("\n" + "=" * 70)
    print(msg)
    print("=" * 70 + "\n")


def wait():
    time.sleep(0.25)


###########################################################
# ---- RESIDUAL MONITOR ----
###########################################################

def get_continuity_residual(solver):
    try:
        res = solver.solution.Monitors.Residual.GetValues()
        return res.get("continuity", None)
    except:
        return None


def wait_until_converged(solver, target=1e-4, max_wait=1800):
    print("\n[Monitor] Watching continuity until < {:.1e}".format(target))
    start = time.time()

    while True:
        res = get_continuity_residual(solver)
        if res is not None:
            print(f"   continuity = {res:.3e}")
            if res < target:
                print("[Monitor] Converged.\n")
                return True

        if time.time() - start > max_wait:
            print("[Monitor] Timeout waiting for convergence.\n")
            return False

        time.sleep(2)


###########################################################
# ---- SAVE CASE/DATA ----
###########################################################

def save_case_data(solver, outdir):
    try:
        case_file = os.path.join(outdir, "final.cas.h5")
        data_file = os.path.join(outdir, "final.dat.h5")

        solver.solver.File.Write(file_type="case", file_name=case_file)
        solver.solver.File.Write(file_type="data", file_name=data_file)

        print(f"[Save] Case saved → {case_file}")
        print(f"[Save] Data saved → {data_file}\n")

    except Exception as e:
        print(f"[Save] ERROR saving case/data: {e}")


###########################################################
# ---- EXPORT CONTOURS ----
###########################################################

def export_contours(solver, outdir):
    press = os.path.join(outdir, "pressure.png")
    vel = os.path.join(outdir, "velocity.png")

    try:
        solver.tui.display.set_window(1)
        solver.tui.display.contour("pressure", "static-pressure", "yes")
        solver.tui.display.save_picture(press)
        print(f"[Post] Pressure contour saved → {press}")
    except:
        print("[Post] Pressure contour failed.")

    try:
        solver.tui.display.set_window(1)
        solver.tui.display.contour("velocity", "velocity-magnitude", "yes")
        solver.tui.display.save_picture(vel)
        print(f"[Post] Velocity contour saved → {vel}")
    except:
        print("[Post] Velocity contour failed.")


###########################################################
# ---- PROJECTED AREA ----
###########################################################

def compute_projected_area(solver, outdir):
    txt = os.path.join(outdir, "projected_area.txt")
    try:
        solver.tui.solve.reference_values.compute("projected-area")
        area = solver.tui.solve.reference_values.area()

        with open(txt, "w") as f:
            f.write(str(area))

        print(f"[Area] Projected frontal area = {area}\n")
        return float(area)
    except:
        print("[Area] ERROR computing projected area.")
        return None


###########################################################
# ---- AERO COEFFICIENT EXTRACTION ----
###########################################################

def extract_aero_coeffs(solver, outdir, area):
    txt = os.path.join(outdir, "aero_coeffs.txt")

    try:
        cd = solver.tui.report.force_coefficients.c_d()
        cl = solver.tui.report.force_coefficients.c_l()

        scx = cd * area
        scz = cl * area

        with open(txt, "w") as f:
            f.write(f"Cd = {cd}\n")
            f.write(f"Cl = {cl}\n")
            f.write(f"SCx = {scx}\n")
            f.write(f"SCz = {scz}\n")

        print("\n[Aero Results — REAR WING]")
        print(f"   Cd  = {cd}")
        print(f"   Cl  = {cl}")
        print(f"   SCx = {scx}")
        print(f"   SCz = {scz}\n")

        return cd, cl, scx, scz

    except:
        print("[Aero] ERROR extracting aero coefficients.")
        return None, None, None, None

