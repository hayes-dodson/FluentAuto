# frontwing_pipeline.py
# Full Front Wing CFD Pipeline
# Fluent 2024R2+ • Watertight Geometry
# NO wheels

import os
import time
import ansys.fluent.core as pyfluent


class FrontWingPipeline:
    def __init__(self, job, log):
        self.job = job
        self.log = log

        self.geom = job["geom"]
        self.outdir = job["outdir"]
        self.L = job["L"]
        self.W = job["W"]
        self.H = job["H"]

        os.makedirs(self.outdir, exist_ok=True)

    def run(self):
        self.log("Launching Fluent Meshing (Front Wing)...")

        meshing = pyfluent.launch_fluent(
            mode=pyfluent.FluentMode.MESHING,
            precision=pyfluent.Precision.DOUBLE,
            processor_count=16,
            dimension=3,
            mpi_type="intel",
        )

        mesh_file = self._run_meshing(meshing)

        self.log("Meshing complete. Launching solver...")
        self._run_solver(mesh_file)

    # ==========================================================
    # MESHING
    # ==========================================================
    def _run_meshing(self, session):
        wf = session.workflow
        tasks = wf.TaskObject

        self.log("Importing geometry")
        tasks["Import Geometry"].Arguments.set_state({
            "FileName": self.geom,
            "LengthUnit": "m"
        })
        tasks["Import Geometry"].Execute()
        time.sleep(0.2)

        self.log("Creating refinement regions")

        near, mid, far = 0.016, 0.032, 0.064
        zmin, zmax = 0, self.W * 0.5

        boxes = {
            "fw-near": (near, -self.L*0.6, self.L*1.5, 0, self.H*1.2),
            "fw-mid":  (mid,  -self.L*0.7, self.L*3.0, 0, self.H*2.0),
            "fw-far":  (far,  -self.L*0.8, self.L*5.0, 0, self.H*3.0),
        }

        add_ref = tasks["Create Local Refinement Regions"]

        for name, (size, xmin, xmax, ymin, ymax) in boxes.items():
            add_ref.AddChildToTask()
            child = tasks[name]
            child.Arguments.set_state({
                "CoordinateSpecificationMethod": "Direct",
                "MeshSize": size,
                "Xmin": xmin, "Xmax": xmax,
                "Ymin": ymin, "Ymax": ymax,
                "Zmin": zmin, "Zmax": zmax,
            })
            child.Execute()
            time.sleep(0.1)

        self.log("Curvature sizing (front wing only)")
        tasks["Add Local Sizing"].AddChildToTask()
        curv = tasks["curvature_fw"]
        curv.Arguments.set_state({
            "LocalSizingType": "Curvature",
            "MinSize": 0.0005,
            "MaxSize": 0.008,
            "CurvatureNormalAngle": 9,
            "BoundaryNameList": ["frontwing"]
        })
        curv.Execute()

        self.log("Surface mesh")
        surf = tasks["Generate the Surface Mesh"]
        surf.Arguments.set_state({
            "MinimumSize": 0.002,
            "MaximumSize": 0.256,
            "GrowthRate": 1.2,
            "CurvatureNormalAngle": 18,
            "SizeFunctions": "CurvatureProximity"
        })
        surf.Execute()

        tasks["Improve Surface Mesh"].Arguments.set_state({
            "FaceQualityLimit": 0.7
        })
        tasks["Improve Surface Mesh"].Execute()

        tasks["Describe Geometry"].Arguments.set_state({
            "SetupType": "The geometry consists of only fluid regions with no voids"
        })
        tasks["Describe Geometry"].Execute()

        tasks["Update Boundaries"].Execute()
        tasks["Update Regions"].Execute()

        self.log("Boundary layers")
        bl = tasks["Add Boundary Layers"]
        bl.AddChildToTask()
        tasks["last-ratio_1"].Arguments.set_state({
            "BoundaryZones": ["frontwing"],
            "FirstLayerHeight": 0.0005,
            "NumberOfLayers": 10,
            "LastLayerRatio": 1.2
        })
        tasks["last-ratio_1"].Execute()

        self.log("Volume mesh (poly-hexcore)")
        vol = tasks["Generate the Volume Mesh"]
        vol.Arguments.set_state({
            "FillWith": "poly-hexcore",
            "MinCellLength": 0.0005,
            "MaxCellLength": 0.256,
            "EnableParallel": True
        })
        vol.Execute()

        tasks["Improve Volume Mesh"].Arguments.set_state({
            "QualityMethod": "Orthogonal",
            "CellQualityLimit": 0.2
        })
        tasks["Improve Volume Mesh"].Execute()

        mesh_path = os.path.join(self.outdir, "mesh_fw.msh.h5")
        session.meshing.SaveMesh(file_name=mesh_path)

        return mesh_path

    # ==========================================================
    # SOLVER
    # ==========================================================
    def _run_solver(self, mesh):
        solver = pyfluent.launch_fluent(
            mode=pyfluent.FluentMode.SOLVER,
            precision=pyfluent.Precision.DOUBLE,
            processor_count=16,
            dimension=3,
            mpi_type="intel",
        )

        solver.solver.File.Read(file_type="mesh", file_name=mesh)
        solver.solution.RunCalculation.iterate(5000)

        solver.solver.File.Write(
            file_type="case",
            file_name=os.path.join(self.outdir, "final.cas.h5")
        )
        solver.solver.File.Write(
            file_type="data",
            file_name=os.path.join(self.outdir, "final.dat.h5")
        )
