import sys, os
from PySide6 import QtWidgets
from diagnostics import detect_system, detect_fluent_versions
from simulation_manager import SimulationManager
from worker_thread import WorkerThread

from frontwing_pipeline import FrontWingPipeline
from rearwing_pipeline import RearWingPipeline
from undertray_pipeline import UndertrayPipeline
from halfcar_pipeline import HalfCarPipeline

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.manager = SimulationManager()
        self.sysinfo = detect_system()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ram Racing FSAE Aero Automation Suite")
        layout = QtWidgets.QVBoxLayout(self)

        # Geometry
        self.geom = QtWidgets.QLineEdit()
        browse = QtWidgets.QPushButton("Browse PMDB / DSCO")
        browse.clicked.connect(self.browse_geom)

        # CPU Panel
        cpu_box = QtWidgets.QGroupBox("Parallel Settings")
        cpu_layout = QtWidgets.QFormLayout(cpu_box)

        self.cpu_label = QtWidgets.QLabel(self.sysinfo["display"])
        self.mpi_field = QtWidgets.QSpinBox()
        self.mpi_field.setValue(self.sysinfo["recommended_mpi"])

        self.mpi_type = QtWidgets.QComboBox()
        self.mpi_type.addItems(["Intel MPI", "Default MPI"])

        self.fluent_ver = QtWidgets.QComboBox()
        self.fluent_ver.addItems(detect_fluent_versions())

        cpu_layout.addRow("Detected:", self.cpu_label)
        cpu_layout.addRow("MPI Ranks:", self.mpi_field)
        cpu_layout.addRow("MPI Type:", self.mpi_type)
        cpu_layout.addRow("Fluent Version:", self.fluent_ver)

        # Buttons
        run = QtWidgets.QPushButton("Run Front Wing")
        run.clicked.connect(lambda: self.start_job("fw"))

        self.log = QtWidgets.QTextEdit(readOnly=True)

        layout.addWidget(self.geom)
        layout.addWidget(browse)
        layout.addWidget(cpu_box)
        layout.addWidget(run)
        layout.addWidget(self.log)

    def browse_geom(self):
        f, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Geometry", "", "Geometry (*.pmdb *.dsco)"
        )
        if f:
            self.geom.setText(f)

    def start_job(self, kind):
        job = {
            "pipeline_class": FrontWingPipeline,
            "geom": self.geom.text(),
            "mpi_ranks": self.mpi_field.value(),
            "mpi_type": "intel" if "Intel" in self.mpi_type.currentText() else "default",
            "fluent_version": self.fluent_ver.currentText(),
            "sim_name": "FrontWing"
        }
        self.manager.add_job(job)

        self.worker = WorkerThread(self.manager)
        self.worker.log_signal.connect(self.log.append)
        self.worker.start()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
