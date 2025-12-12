from pipelines import BasePipeline

class FrontWingPipeline(BasePipeline):
    def run(self):
        session = self.launch_fluent()
        self.log("Meshing Front Wing")

        session.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")
        session.workflow.ImportGeometry(FileName=self.job["geom"])

        self.log("Switching to Solver")
        session.switch_to_solver()

        self.log("Ramp 1: First Order")
        session.solution.methods.order = "first-order"

        self.log("Ramp 2: Curvature Correction ON")
        session.solution.controls.curvature_correction = True

        self.log("Ramp 3: Pressure Second Order")
        session.solution.methods.pressure = "second-order"

        self.log("Running Solver")
        session.solution.run()
