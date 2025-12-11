# simulation_manager.py
# Updated for PySide6-safe GUI logging

import os
import traceback

class SimulationManager:
    """
    Manages job queue execution for CFD pipelines.
    Provides a log callback for GUI-safe logging.
    """

    def __init__(self):
        self.jobs = []
        self.log_callback = None

    # --------------------------------------------
    # Logging helper
    # --------------------------------------------
    def log(self, msg: str):
        print(msg)  # Always log to console
        if self.log_callback:
            self.log_callback(msg)

    def set_log_callback(self, func):
        """Assigns the GUI logging function."""
        self.log_callback = func

    # --------------------------------------------
    # Job control
    # --------------------------------------------
    def add_job(self, job_dict):
        """Adds a job to the queue."""
        self.jobs.append(job_dict)

    def clear(self):
        """Clears job queue."""
        self.jobs = []

    # --------------------------------------------
    # Execution
    # --------------------------------------------
    def run_all(self):
        """Runs all queued jobs sequentially."""
        if not self.jobs:
            self.log("No jobs in queue.")
            return

        for i, job in enumerate(self.jobs, start=1):
            name = job["sim_name"]
            self.log(f"----- Running job {i}/{len(self.jobs)}: {name} -----")

            try:
                self.run_single(job)
                self.log(f"Job '{name}' completed successfully.")

            except Exception as e:
                self.log(f"ERROR: Job '{name}' failed.\n{e}")
                self.log(traceback.format_exc())

        self.log("All queued simulations finished.")

    # --------------------------------------------
    # Run a single job
    # --------------------------------------------
    def run_single(self, job):
        """Executes one pipeline job."""

        pipeline_class = job["pipeline_class"]
        pipeline = pipeline_class(
            geom_path=job["geom"],
            output_dir=job["outdir"],
            sim_name=job["sim_name"],
            L=job["L"],
            W=job["W"],
            H=job["H"],
            log=self.log,
        )

        # Create directory if needed
        os.makedirs(job["outdir"], exist_ok=True)

        pipeline.run()
