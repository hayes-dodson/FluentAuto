# undertray_pipeline.py
import os
from pipelines import BasePipeline, WHEEL_OMEGA


class UndertrayPipeline(BasePipeline):

    def run(self):
        mesh = self.run_meshing()
        self.run_solver(mesh)

    # ==================================================
    # MESHING
    # ==================================================
    def run_meshing(self):
        session = self.launch_meshing()
        wf = session.workflow
        tasks = wf.TaskObject

        # ---------------- IMPORT GEOMETRY ----------------
        tasks["Import Geometry"].Arguments.set_state({
            "FileName": self.geom_path,
            "LengthUnit": "m"
        })
        tasks["Import Geometry"].Execute()
        self.wait()

        # ---------------- GLOBAL REFINEMENT ----------------
        zmax = self.W * 0.5

        regions = {
            "near": (0.016, -self.L*0.65, self.L*2.2, 0, self.H*1.5),
            "mid":  (0.032, -self.L*0.72, self.L*4.1, 0, self.H*2.2),
            "far":  (0.064, -self.L*0.78, self.L*6.0, 0, self.H*3.0),
        }

        for name, (size, xmin, xmax, ymin, ymax) in regions.items():
            tasks["Create Local Refinement Regions"].AddChildToTask()
            t = tasks[f"refine-{name}"]
            t.Arguments.set_state({
                "MeshSize": size,
                "Xmin": xmin,
                "Xmax": xmax,
                "Ymin": ymin,
                "Ymax": ymax,
                "Zmin": 0,
                "Zmax": zmax
            })
            t.Execute()
            self.wait()

        # ---------------- WHEEL REFINEMENT ----------------
        for name, (x, y, z) in self.get_wheel_centers().items():
            tasks["Create Local Refinement Regions"].AddChildToTask()
            cyl = tasks[f"wheel-cyl-{name}"]
            cyl.Arguments.set_state({
                "RegionType": "Cylinder",
                "CenterX": x,
                "CenterY": y,
                "CenterZ": z,
                "Radius": 0.254,
                "Height": 0.25,
                "MeshSize": 0.016
            })
            cyl.Execute()
            self.wait()

        # ---------------- CURVATURE SIZING ----------------
        for label, zones, min_s, max_s, ang in [
            ("ut", ["undertray"], 0.0005, 0.008, 9),
            ("w", ["fw", "rw"], 0.0005, 0.032, 18),
            ("b", ["fwb", "rwb"], 0.0005, 0.032, 18),
        ]:
            tasks["Add Local Sizing"].AddChildToTask()
            t = tasks[f"curv-{label}"]
            t.Arguments.set_state({
                "LocalSizingType": "Curvature",
                "MinSize": min_s,
                "MaxSize": max_s,
                "CurvatureNormalAngle": ang,
                "BoundaryNameList": zones
            })
            t.Execute()
            self.wait()

        # ---------------- SURFACE MESH ----------------
        tasks["Generate the Surface Mesh"].Arguments.set_state({
            "MinimumSize": 0.002,
            "MaximumSize": 0.256,
            "GrowthRate": 1.2,
            "CurvatureNormalAngle": 18
        })
        tasks["Generate the Surface Mesh"].Execute()
        self.wait()

        tasks["Improve Surface Mesh"].Arguments.set_state({
            "FaceQualityLimit": 0.7
        })
        tasks["Improve Surface Mesh"].Execute()
        self.wait()

        # ---------------- BL + VOLUME ----------------
        tasks["Add Boundary Layers"].AddChildToTask()
        bl = tasks["bl"]
        bl.Arguments.set_state({
            "BoundaryZones": ["undertray", "fw", "rw", "fwb", "rwb"],
            "FirstLayerHeight": 0.0005,
            "NumberOfLayers": 10,
            "LastLayerRatio": 1.2
        })
        bl.Execute()
        self.wait()

        tasks["Generate the Volume Mesh"].Arguments.set_state({
            "FillWith": "poly-hexcore",
            "MinCellLength": 0.0005,
            "MaxCellLength": 0.256,
            "EnableParallel": True
        })
        tasks["Generate the Volume Mesh"].Execute()
        self.wait()

        mesh_file = os.path.join(self.outdir, "mesh_undertray.msh.h5")
        session.meshing.SaveMesh(file_name=mesh_file)
        return mesh_file

    # ==================================================
    # SOLVER
    # ==================================================
    def run_solver(self, mesh):
        solver = self.launch_solver()
        solver.solver.File.Read(file_type="mesh", file_name=mesh)

        # GEKO ramp logic preserved
        solver.tui.define.models.viscous.ke_gko("yes")
        solver.tui.define.models.viscous.ke_gko.options.curvature_correction("no")

        solver.solution.RunCalculation.iterate(1000)
        solver.solution.RunCalculation.iterate(1000)

        solver.tui.define.models.viscous.ke_gko.options.curvature_correction("yes")
        solver.solution.RunCalculation.iterate(5000)

        solver.solver.File.Write(
            file_type="case-data",
            file_name=os.path.join(self.outdir, "final.cas.h5")
        )
