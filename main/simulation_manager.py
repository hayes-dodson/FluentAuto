import os

class SimulationManager:
    def __init__(self):
        self.jobs = []
        self.log_cb = print

    def set_log_callback(self, cb):
        self.log_cb = cb

    def add_job(self, job):
        self.jobs.append(job)

    def run_all(self):
        for job in self.jobs:
            self.log_cb(f"Starting {job['sim_name']}")
            pipeline = job["pipeline_class"](job, self.log_cb)
            pipeline.run()
        self.jobs.clear()
