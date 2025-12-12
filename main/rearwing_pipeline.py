# rearwing_pipeline.py
# Full Rear Wing CFD Pipeline
# NO wheels

import os
import time
import ansys.fluent.core as pyfluent


class RearWingPipeline:
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
        meshing = pyfluent.launch_fluent(
            mode=pyfluent.FluentMode.MESHING,
            precision=pyfluent.Precision.DOUBLE,
            processor_count=16,
            dimension=3,
            mpi_type="intel",
        )
        mesh = self._mesh(meshing)
        self._solve(mesh)

    def _mesh(self, session):
        wf = session.workflow
        tasks = wf.TaskObject

        tasks["Import Geometry"].Arguments.set_state({
            "FileName": self.geom,
            "LengthUnit": "m"
        })
        tasks["Import Geometry"].Execute()

        tasks["Add Local Sizing"].AddChildToTask()
        curv = tasks["curvature_rw"]
        curv.Arguments.set_state({
            "LocalSizingType": "Curvature",
            "MinSize": 0.0005,
            "MaxSize": 0.008,
            "CurvatureNormalAngle": 9,
            "BoundaryNameList": ["rearwing"]
        })
        curv.Execute()

        tasks["Generate the Surface Mesh"].Execute()
        tasks["Improve Surface Mesh"].Execute()
        tasks["Describe Geometry"].Execute()
        tasks["Update Boundaries"].Execute()
        tasks["Update Regions"].Execute()

        bl = tasks["Add Boundary Layers"]
        bl.AddChildToTask()
        tasks["last-ratio_1"].Arguments.set_state({
            "BoundaryZones": ["rearwing"],
            "FirstLayerHeight": 0.0005,
            "NumberOfLayers": 10,
            "LastLayerRatio": 1.2
        })
        tasks["last-ratio_1"].Execute()

        tasks["Generate the Volume Mesh"].Execute()
        tasks["Improve Volume Mesh"].Execute()

        mesh = os.path.join(self.outdir, "mesh_rw.msh.h5")
        session.meshing.SaveMesh(file_name=mesh)
        return mesh

    def _solve(self, mesh):
        solver = pyfluent.launch_fluent(
            mode=pyfluent.FluentMode.SOLVER,
            precision=pyfluent.Precision.DOUBLE,
            processor_count=16,
            dimension=3,
            mpi_type="intel",
        )
        solver.solver.File.Read(file_type="mesh", file_name=mesh)
        solver.solution.RunCalculation.iterate(5000)
