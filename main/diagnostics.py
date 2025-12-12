import os
import platform
import multiprocessing
import psutil

def detect_system():
    physical = psutil.cpu_count(logical=False)
    logical = psutil.cpu_count(logical=True)

    return {
        "os": platform.system(),
        "physical_cores": physical,
        "logical_threads": logical,
        "display": f"{physical}C / {logical}T",
        "recommended_mpi": min(logical - 4, int(logical * 0.75))
    }

def detect_fluent_versions():
    versions = ["2025R2", "2025R1", "2024R2"]
    return ["Auto-Detect"] + versions
