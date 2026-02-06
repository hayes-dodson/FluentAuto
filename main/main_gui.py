# main_gui_IMPROVED.py
# IMPROVEMENTS:
# - Input validation
# - Domain dimension inputs
# - Progress bar and cancel button
# - Better error messages
# - Output directory selection
# - Multiple pipeline selection
# - Session management

import sys
import os
from datetime import datetime
from PySide6 import QtWidgets, QtCore
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
        self.worker = None
        self.init_ui()
        self.setMinimumSize(700, 800)

    def init_ui(self):
        self.setWindowTitle("Ram Racing FSAE Aero Automation Suite v2.0")
        main_layout = QtWidgets.QVBoxLayout(self)

        # ==================== HEADER ====================
        header = QtWidgets.QLabel("Ram Racing FSAE Aero CFD Automation")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        header.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(header)

        # ==================== SYSTEM INFO ====================
        sys_group = QtWidgets.QGroupBox("System Information")
        sys_layout = QtWidgets.QHBoxLayout(sys_group)

        sys_info_text = (
            f"OS: {self.sysinfo['os']} | "
            f"CPU: {self.sysinfo['display']} | "
            f"Recommended MPI: {self.sysinfo['recommended_mpi']}"
        )
        sys_label = QtWidgets.QLabel(sys_info_text)
        sys_layout.addWidget(sys_label)
        main_layout.addWidget(sys_group)

        # ==================== GEOMETRY INPUT ====================
        geom_group = QtWidgets.QGroupBox("Geometry File")
        geom_layout = QtWidgets.QHBoxLayout(geom_group)

        self.geom_field = QtWidgets.QLineEdit()
        self.geom_field.setPlaceholderText("Select geometry file (.pmdb or .dsco)...")

        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_geometry)
        browse_btn.setMaximumWidth(100)

        geom_layout.addWidget(self.geom_field)
        geom_layout.addWidget(browse_btn)
        main_layout.addWidget(geom_group)

        # ==================== OUTPUT DIRECTORY ====================
        output_group = QtWidgets.QGroupBox("Output Directory")
        output_layout = QtWidgets.QHBoxLayout(output_group)

        self.output_field = QtWidgets.QLineEdit()
        default_output = os.path.join(os.getcwd(), "outputs")
        self.output_field.setText(default_output)

        browse_output_btn = QtWidgets.QPushButton("Browse...")
        browse_output_btn.clicked.connect(self.browse_output)
        browse_output_btn.setMaximumWidth(100)

        output_layout.addWidget(self.output_field)
        output_layout.addWidget(browse_output_btn)
        main_layout.addWidget(output_group)

        # ==================== DOMAIN DIMENSIONS ====================
        domain_group = QtWidgets.QGroupBox("Domain Dimensions")
        domain_layout = QtWidgets.QFormLayout(domain_group)

        self.L_field = QtWidgets.QDoubleSpinBox()
        self.L_field.setRange(0.1, 100.0)
        self.L_field.setValue(3.0)
        self.L_field.setSuffix(" m")
        self.L_field.setDecimals(2)
        self.L_field.setToolTip("Streamwise domain length")

        self.W_field = QtWidgets.QDoubleSpinBox()
        self.W_field.setRange(0.1, 100.0)
        self.W_field.setValue(1.6)
        self.W_field.setSuffix(" m")
        self.W_field.setDecimals(2)
        self.W_field.setToolTip("Lateral domain width")

        self.H_field = QtWidgets.QDoubleSpinBox()
        self.H_field.setRange(0.1, 100.0)
        self.H_field.setValue(1.2)
        self.H_field.setSuffix(" m")
        self.H_field.setDecimals(2)
        self.H_field.setToolTip("Vertical domain height")

        domain_layout.addRow("Length (L):", self.L_field)
        domain_layout.addRow("Width (W):", self.W_field)
        domain_layout.addRow("Height (H):", self.H_field)
        main_layout.addWidget(domain_group)

        # ==================== SIMULATION PARAMETERS ====================
        sim_group = QtWidgets.QGroupBox("Simulation Parameters")
        sim_layout = QtWidgets.QFormLayout(sim_group)

        self.velocity_field = QtWidgets.QDoubleSpinBox()
        self.velocity_field.setRange(1.0, 100.0)
        self.velocity_field.setValue(20.0)
        self.velocity_field.setSuffix(" m/s")
        self.velocity_field.setDecimals(1)

        self.iterations_field = QtWidgets.QSpinBox()
        self.iterations_field.setRange(100, 50000)
        self.iterations_field.setValue(5000)
        self.iterations_field.setSingleStep(500)

        sim_layout.addRow("Freestream Velocity:", self.velocity_field)
        sim_layout.addRow("Max Iterations:", self.iterations_field)
        main_layout.addWidget(sim_group)

        # ==================== PARALLEL SETTINGS ====================
        parallel_group = QtWidgets.QGroupBox("Parallel Computing Settings")
        parallel_layout = QtWidgets.QFormLayout(parallel_group)

        self.cpu_label = QtWidgets.QLabel(self.sysinfo["display"])

        self.mpi_field = QtWidgets.QSpinBox()
        self.mpi_field.setRange(1, self.sysinfo["logical_threads"])
        self.mpi_field.setValue(self.sysinfo["recommended_mpi"])
        self.mpi_field.setToolTip(
            f"Recommended: {self.sysinfo['recommended_mpi']} "
            f"(leave {self.sysinfo['logical_threads'] - self.sysinfo['recommended_mpi']} threads for OS)"
        )

        self.mpi_type = QtWidgets.QComboBox()
        self.mpi_type.addItems(["Intel MPI", "Default MPI"])

        self.fluent_ver = QtWidgets.QComboBox()
        self.fluent_ver.addItems(detect_fluent_versions())

        parallel_layout.addRow("Detected CPU:", self.cpu_label)
        parallel_layout.addRow("MPI Ranks:", self.mpi_field)
        parallel_layout.addRow("MPI Type:", self.mpi_type)
        parallel_layout.addRow("Fluent Version:", self.fluent_ver)
        main_layout.addWidget(parallel_group)

        # ==================== PIPELINE SELECTION ====================
        pipeline_group = QtWidgets.QGroupBox("Select Pipeline")
        pipeline_layout = QtWidgets.QVBoxLayout(pipeline_group)

        self.pipeline_combo = QtWidgets.QComboBox()
        self.pipeline_combo.addItems([
            "Front Wing",
            "Rear Wing",
            "Undertray",
            "Half Car (Full Assembly)"
        ])

        pipeline_descriptions = {
            0: "Front wing only - no wheels, optimized refinement",
            1: "Rear wing only - no wheels, optimized refinement",
            2: "Undertray with wheels - includes rotating boundary conditions",
            3: "Complete half-car assembly - all components with wheels"
        }

        self.pipeline_desc = QtWidgets.QLabel()
        self.pipeline_desc.setWordWrap(True)
        self.pipeline_desc.setStyleSheet("color: #666; font-style: italic;")

        def update_description(index):
            self.pipeline_desc.setText(pipeline_descriptions.get(index, ""))

        self.pipeline_combo.currentIndexChanged.connect(update_description)
        update_description(0)

        pipeline_layout.addWidget(self.pipeline_combo)
        pipeline_layout.addWidget(self.pipeline_desc)
        main_layout.addWidget(pipeline_group)

        # ==================== CONTROL BUTTONS ====================
        button_layout = QtWidgets.QHBoxLayout()

        self.run_btn = QtWidgets.QPushButton("▶ Run Simulation")
        self.run_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.run_btn.clicked.connect(self.start_simulation)

        self.cancel_btn = QtWidgets.QPushButton("⏹ Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_simulation)

        button_layout.addWidget(self.run_btn)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)

        # ==================== PROGRESS BAR ====================
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # ==================== LOG OUTPUT ====================
        log_label = QtWidgets.QLabel("Simulation Log:")
        log_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(log_label)

        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        main_layout.addWidget(self.log_text)

        # ==================== STATUS BAR ====================
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #e0e0e0;")
        main_layout.addWidget(self.status_label)

    def browse_geometry(self):
        """Browse for geometry file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Geometry File",
            "",
            "Geometry Files (*.pmdb *.dsco);;All Files (*.*)"
        )
        if file_path:
            self.geom_field.setText(file_path)
            self.log(f"Selected geometry: {os.path.basename(file_path)}")

    def browse_output(self):
        """Browse for output directory"""
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_field.text()
        )
        if dir_path:
            self.output_field.setText(dir_path)
            self.log(f"Output directory: {dir_path}")

    def validate_inputs(self):
        """Validate all inputs before starting simulation"""
        errors = []

        # Check geometry file
        geom_file = self.geom_field.text().strip()
        if not geom_file:
            errors.append("Please select a geometry file")
        elif not os.path.exists(geom_file):
            errors.append(f"Geometry file not found: {geom_file}")
        elif not (geom_file.endswith('.pmdb') or geom_file.endswith('.dsco')):
            errors.append("Geometry file must be .pmdb or .dsco format")

        # Check output directory
        output_dir = self.output_field.text().strip()
        if not output_dir:
            errors.append("Please specify an output directory")
        else:
            # Try to create output directory
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {str(e)}")

        # Check domain dimensions
        if self.L_field.value() <= 0:
            errors.append("Domain length must be positive")
        if self.W_field.value() <= 0:
            errors.append("Domain width must be positive")
        if self.H_field.value() <= 0:
            errors.append("Domain height must be positive")

        # Check MPI ranks
        if self.mpi_field.value() < 1:
            errors.append("MPI ranks must be at least 1")
        elif self.mpi_field.value() > self.sysinfo["logical_threads"]:
            errors.append(
                f"MPI ranks ({self.mpi_field.value()}) exceeds available threads "
                f"({self.sysinfo['logical_threads']})"
            )

        # Show errors if any
        if errors:
            QtWidgets.QMessageBox.critical(
                self,
                "Validation Error",
                "Please fix the following issues:\n\n" + "\n".join(f"• {e}" for e in errors)
            )
            return False

        return True

    def start_simulation(self):
        """Start the simulation after validation"""
        if not self.validate_inputs():
            return

        # Determine pipeline class
        pipeline_map = {
            0: (FrontWingPipeline, "FrontWing"),
            1: (RearWingPipeline, "RearWing"),
            2: (UndertrayPipeline, "Undertray"),
            3: (HalfCarPipeline, "HalfCar")
        }

        pipeline_class, sim_name = pipeline_map[self.pipeline_combo.currentIndex()]

        # Create timestamped output subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_outdir = os.path.join(
            self.output_field.text(),
            f"{sim_name}_{timestamp}"
        )
        os.makedirs(job_outdir, exist_ok=True)

        # Handle Fluent version
        fluent_ver = self.fluent_ver.currentText()
        if fluent_ver == "Auto-Detect":
            fluent_ver = None

        # Build complete job dictionary
        job = {
            "pipeline_class": pipeline_class,
            "geom": self.geom_field.text(),
            "outdir": job_outdir,
            "L": self.L_field.value(),
            "W": self.W_field.value(),
            "H": self.H_field.value(),
            "velocity": self.velocity_field.value(),
            "iterations": self.iterations_field.value(),
            "mpi_ranks": self.mpi_field.value(),
            "mpi_type": "intel" if "Intel" in self.mpi_type.currentText() else "default",
            "fluent_version": fluent_ver,
            "sim_name": sim_name
        }

        # Add job and start worker
        self.manager.add_job(job)

        # Update UI state
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.update_status("Running simulation...")

        self.log("=" * 60)
        self.log(f"Starting {sim_name} simulation")
        self.log(f"Output: {job_outdir}")
        self.log("=" * 60)

        # Start worker thread
        self.worker = WorkerThread(self.manager)
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_simulation_finished)
        self.worker.start()

    def cancel_simulation(self):
        """Cancel running simulation"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Cancel Simulation",
            "Are you sure you want to cancel the running simulation?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            if self.worker and self.worker.isRunning():
                self.log("Cancelling simulation...")
                self.worker.terminate()
                self.worker.wait()
                self.on_simulation_finished()
                self.log("Simulation cancelled by user")

    def on_simulation_finished(self):
        """Handle simulation completion"""
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.update_status("Ready")
        self.log("=" * 60)
        self.log("Simulation workflow completed")
        self.log("=" * 60)

    def log(self, message):
        """Add message to log"""
        self.log_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_status(self, message):
        """Update status bar"""
        self.status_label.setText(message)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())