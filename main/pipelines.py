# pipelines.py
import os
import time
import ansys.fluent.core as pyfluent

WHEEL_OMEGA = 88.0


class BasePipeline:
    def __init__(
        self,
        geom_path,
        outdir,
        L, W, H,
        cores=20,
        mpi_type="intel",
        fluent_version=None
    ):
        self.geom_path = geom_path
        self.outdir = outdir
        self.L = L
        self.W = W
        self.H = H
        self.cores = cores
        self.mpi_type = mpi_type
        self.fluent_version = fluent_version

        os.makedirs(outdir, exist_ok=True)

    # --------------------------------------------------
    # Utility
    # --------------------------------------------------
    def wait(self, t=0.25):
        time.sleep(t)

    # --------------------------------------------------
    # Wheel centers (override per pipeline if needed)
    # --------------------------------------------------
    def get_wheel_centers(self):
        return {
            "fw": (-0.7874, 0.2032, 0.6096),
            "rw": ( 0.7874, 0.2032, 0.5842)
        }

    # --------------------------------------------------
    # Launch Fluent
    # --------------------------------------------------
    def launch_meshing(self):
        return pyfluent.launch_fluent(
            mode=pyfluent.FluentMode.MESHING,
            precision=pyfluent.Precision.DOUBLE,
            processor_count=self.cores,
            dimension=3,
            mpi_type=self.mpi_type,
            version=self.fluent_version
        )

    def launch_solver(self):
        return pyfluent.launch_fluent(
            mode=pyfluent.FluentMode.SOLVER,
            precision=pyfluent.Precision.DOUBLE,
            processor_count=self.cores,
            dimension=3,
            mpi_type=self.mpi_type,
            version=self.fluent_version
        )
