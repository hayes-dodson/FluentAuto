# FSAE CFD Automation – Feature Overview

A fully automated end-to-end CFD pipeline for FSAE vehicle aerodynamic development using ANSYS Fluent + PyFluent.
Supports single-case runs, batch runs, solver stabilization, mesh automation, post-processing, and EXE distribution.

# ⚙️ Core Functionality
Mesh Automation

Automated Fluent Meshing launch (DOUBLE precision + MPI)

Watertight geometry workflow

Automatic geometry import

Automatic zone discovery

Local sizing generation:

Curvature-based sizing sets (stuff, wheels, aero)

Multiple sizing regions with separate parameters

Automatic wheel refinement boxes

Global & local refinement zones:

Near-field, mid-field, far-field boxes

Wheel-region refinement

Boundary layer automation:

BL height computed from Reynolds number

Automatic first-layer height for y+ ≈ 1

Per-zone BL creation

Surface mesh generation with full UI-equivalent settings

Volume mesh generation (poly-hexcore, peel layers, min/max sizes)

Mesh improvement (surface + volume quality targets)

Mesh quality reporting + CSV export

# 🧮 Solver Automation

Automatic Fluent Solver launch

GEKO turbulence model initialization

Optional curvature correction (on/off logic)

Wheel rotation setup based on real tire radii

Automated BC assignment:

Inlet at target MPH

Moving ground plane

Wheel rotation & origins (FL/FR/RL/RR)

Automatic reference values:

Projected frontal area computation (UI-identical)

Automatic selection of aero-relevant surfaces

Solver stabilization:

Relaxation ramp

CFL ramp

Floating-point / divergence auto-recovery

Automatic re-run after crash

# 📊 Aero & Physics Outputs

Extract Cd, Cl directly from Fluent

Compute aerodynamic coefficients:

SCx = Cd × Area

SCz = Cl × Area

Projected frontal area (full-car) computation

y+ statistics and summary

Wall y+ contour export (PNG)

Pressure map export

Mesh quality summary (console + CSV)

Full case summary CSV export per geometry

# 📁 Batch Processing & Case Management

Run 1–100+ geometries automatically

Batch mode via:
