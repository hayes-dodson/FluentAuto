# FSAE Aerodynamics — Automated CFD Pipeline (ANSYS Fluent 2025R2)

### Fully Automated Meshing + Solver Execution for Front Wing, Rear Wing, and Undertray Systems  
#### Built for ANSYS Fluent 2025R2 with Python 3.12 / PyFluent

---

## ⭐ Overview

This repository contains **three fully automated CFD pipelines** for performing aerodynamic analysis on FSAE vehicle components:

- **Front Wing (`fsae_frontwing.py`)**  
- **Rear Wing (`fsae_rearwing.py`)**  
- **Undertray + Wheels + Bargeboards (`fsae_undertray.py`)**

Each script:

- Uses **Fluent Watertight Geometry workflow** for meshing  
- Applies **consistent refinement and BL strategies** across all tests  
- Runs **GEKO turbulence modeling** with curvature correction  
- Automatically handles **ramp-up stability** to avoid floating-point errors  
- Computes **Cd, Cl, SCx, SCz**, projected area, mesh statistics  
- Saves **case/data, contours, and postprocessing outputs**  
- Is designed for **batch EXE execution** or standalone manual use  

The pipeline ensures **repeatability, robustness, and consistent physics** for all aero simulations.

---

## 📁 Repository Structure

```
/ (root)
│
├── fsae_frontwing.py        # Automated CFD simulation for front wing
├── fsae_rearwing.py         # Automated CFD simulation for rear wing
├── fsae_undertray.py        # Automated CFD simulation for undertray + wheels
│
├── README.md                # Documentation (this file)
└── /example_output/         # (Optional) Example pictures and result files
```

---

## ⚙️ Requirements

### Software  
- **Python 3.12**
- **ANSYS Fluent 2025R2**  
- **PyFluent** (included with Ansys)

### Python Packages  

```
ansys-fluent-core
```

---

## 🧠 How the Pipeline Works

Each simulation follows the same overall sequence:

---

### 1️⃣ User Input

The script asks for:

- Geometry file (`.step` or `.stp`)
- Simulation name  
- Vehicle bounding box dimensions:
  - `L` (length)
  - `W` (width)
  - `H` (height)

Output files are stored in a folder with the simulation name.

---

### 2️⃣ Meshing Pipeline (Watertight Geometry)

All scripts use the same meshing philosophy:

#### ✔ Global refinement regions
- Near-field  
- Mid-field  
- Far-field  

#### ✔ Curvature-based local sizing  
Per component:
- Front Wing  
- Rear Wing  
- Undertray  
- Wheels  
- Wheel blocks  
- Bargeboard  

#### ✔ Wheel refinement regions  
Includes:
- Cylindrical refinement  
- Front refinement box  
- Wake refinement box  

#### ✔ Surface mesh + improvement  
#### ✔ Boundary layers  
#### ✔ Poly-Hexcore volume mesh  

---

### 3️⃣ Solver Pipeline

Includes:

- Unit Setup (mph, lbf)
- GEKO turbulence  
- Wheel rotation (Undertray only)
- Ramp algorithm: **1000 → 1000 → 5000 iterations**
- Curvature correction ON in final ramp  
- Convergence on continuity < **1e−4**  
- Aero extraction  

---

### 4️⃣ Output Files

Each run exports:

```
final.cas.h5
final.dat.h5
pressure.png
velocity.png
projected_area.txt
aero_coeffs.txt
```

---

## 🛠 Usage

Run from the terminal:

```
python fsae_frontwing.py
python fsae_rearwing.py
python fsae_undertray.py
```

Outputs will appear in:

```
/<sim_name>/
```

---

## 🧩 Component-Specific Behaviors

### Front Wing  
- No wheels  
- BL only on front wing  

### Rear Wing  
- No wheels  
- BL only on rear wing  

### Undertray  
- Wheels rotate at 88 rad/s  
- Wheel blocks stationary  
- BL on undertray, wheels, blocks, bargeboard  

---

## 🚀 Packaging as EXE

Example:

```
pyinstaller --onefile fsae_undertray.py
```

---

## 🎯 Summary

This repository provides:

- Fully automated WT meshing  
- Fully automated solvers  
- Consistent meshing standards  
- SCx / SCz calculation  
- Projected area computation  
- Robust stability ramp  
- Production-ready CFD workflow  

---

If you'd like—
- A **batch runner**
- A **unified master tool**
- GUI version  
- Automatic y+ calculator  
- Python logging  
- Report generator

Just ask!

