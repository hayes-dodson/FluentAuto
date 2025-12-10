# simulation_manager.py
# Controls simulation execution & queueing for the
# Ram Racing FSAE Aero Automation Suite (PyQt6 GUI)

import os
import threading
import traceback
import datetime
from PyQt6.QtCore import QObject, pyqtSignal

# Pipelines (added in next phase)
# from pipelines import (
#     FrontWingPipeline, RearWingPipeline,
#     UndertrayPipeline, HalfCarPipeline
# )


# ---------------------------------------------------------------
# DATA MODEL FOR QUEUE JOB
# ---------------------------------------------------------------

class SimulationJob:
    def __init__(self, geom_path, sim_name, comp_type, L, W, H, outdir):
        self.geom_path = geom_path
        self.sim_name = sim_name
        self.comp_type = comp_type
        self.L = L
        self.W = W
        self.H = H
        self.outdir = outdir


# ---------------------------------------------------------------
# SIMULATION MANAGER — RUNS JOBS IN BACKGROUND THREADS
# ---------------------------------------------------------------

class SimulationManager(QObject):
    # Signals for GUI updates
    sig_status = pyqtSignal(str)
    sig_log = pyqtSignal(str)
    sig_progress = pyqtSignal(int)
    sig_results_ready = pyqtSignal(str)   # path to results folder
    sig_job_finished = pyqtSignal(str)    # simulation name
    sig_queue_finished = pyqtSignal()     # all jobs done

    def __init__(self):
        super().__init__()
        self.queue = []
        self.running = False
        self.stop_requested = False


    # -----------------------------------------------------------
    # ADD JOB TO QUEUE
    # -----------------------------------------------------------
    def add_job(self, job: SimulationJob):
        self.queue.append(job)
        self.sig_status.emit(f"Job added to queue: {job.sim_name}")


    # -----------------------------------------------------------
    # START QUEUE EXECUTION (SEQUENTIAL)
    # -----------------------------------------------------------
    def start_queue(self):
        if self.running:
            self.sig_status.emit("Queue already running.")
            return

        if len(self.queue) == 0:
            self.sig_status.emit("Queue empty — nothing to run.")
            return

        self.stop_requested = False
        self.running = True

        threading.Thread(target=self._run_queue_thread, daemon=True).start()


    # -----------------------------------------------------------
    # EXECUTE QUEUE IN BACKGROUND THREAD
    # -----------------------------------------------------------
    def _run_queue_thread(self):
        self.sig_status.emit("Queue started.")

        while self.queue and not self.stop_requested:
            job = self.queue.pop(0)
            self._run_single_job(job)

        self.running = False
        self.sig_queue_finished.emit()
        self.sig_status.emit("Queue execution completed.")


    # -----------------------------------------------------------
    # RUN A SINGLE JOB
    # -----------------------------------------------------------
    def _run_single_job(self, job: SimulationJob):
        self.sig_status.emit(f"Starting simulation: {job.sim_name}")

        try:
            # Create simulation directory
            sim_dir = os.path.join(job.outdir, job.sim_name)
            os.makedirs(sim_dir, exist_ok=True)

            # Log setup
            log_path = os.path.join(sim_dir, "logs")
            os.makedirs(log_path, exist_ok=True)
            log_file = os.path.join(log_path, "event.log")

            def log(msg):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                line = f"[{timestamp}] {msg}"
                with open(log_file, "a") as f:
                    f.write(line + "\n")
                self.sig_log.emit(line)

            log("Simulation started.")

            # -----------------------------------------
            # Select pipeline class
            # -----------------------------------------
            if job.comp_type == "Front Wing":
                pipeline = FrontWingPipeline(job.geom_path, sim_dir, job.L, job.W, job.H)

            elif job.comp_type == "Rear Wing":
                pipeline = RearWingPipeline(job.geom_path, sim_dir, job.L, job.W, job.H)

            elif job.comp_type == "Undertray":
                pipeline = UndertrayPipeline(job.geom_path, sim_dir, job.L, job.W, job.H)

            elif job.comp_type == "Half Car":
                pipeline = HalfCarPipeline(job.geom_path, sim_dir, job.L, job.W, job.H)

            else:
                raise ValueError("Unknown component type.")

            log(f"Pipeline selected: {pipeline.__class__.__name__}")

            # -----------------------------------------
            # RUN MESHING
            # -----------------------------------------
            self.sig_status.emit("Meshing started...")
            self.sig_progress.emit(5)
            mesh_path = pipeline.run_meshing()
            log("Meshing completed.")

            # -----------------------------------------
            # RUN SOLVER
            # -----------------------------------------
            self.sig_status.emit("Solver started...")
            self.sig_progress.emit(40)
            results = pipeline.run_solver(mesh_path)
            log("Solver completed.")

            # -----------------------------------------
            # EXPORT RESULTS (CONTROLS, CSV, etc.)
            # -----------------------------------------
            self.sig_status.emit("Exporting results...")
            self.sig_progress.emit(90)
            report_path = pipeline.export_results(results)
            log("Results exported.")

            self.sig_progress.emit(100)
            self.sig_results_ready.emit(sim_dir)

            # Job finished
            self.sig_job_finished.emit(job.sim_name)
            self.sig_status.emit(f"Simulation completed: {job.sim_name}")
            log("Simulation finished successfully.")

        except Exception as e:
            tb = traceback.format_exc()
            self.sig_status.emit(f"ERROR in simulation {job.sim_name}: {e}")
            self.sig_log.emit(tb)


    # -----------------------------------------------------------
    # STOP QUEUE REQUEST
    # -----------------------------------------------------------
    def stop_queue(self):
        self.stop_requested = True
        self.sig_status.emit("Queue stop requested.")
