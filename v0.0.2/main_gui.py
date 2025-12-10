# main_gui.py
# Ram Racing FSAE Aero Automation Suite
# PyQt6 GUI for automated CFD simulation management

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTabWidget,
    QComboBox, QTextEdit, QListWidget, QProgressBar, QGroupBox,
    QMessageBox, QFormLayout, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

# Simulation Manager (import in Part 3/4)
# from simulation_manager import SimulationManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ram Racing FSAE Aero Automation Suite")
        self.setMinimumSize(1200, 800)

        # Central widget + tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tabs
        self.tab_run = QWidget()
        self.tab_queue = QWidget()
        self.tab_results = QWidget()
        self.tab_logs = QWidget()
        self.tab_settings = QWidget()

        # Add tabs
        self.tabs.addTab(self.tab_run, "Run Simulation")
        self.tabs.addTab(self.tab_queue, "Job Queue")
        self.tabs.addTab(self.tab_results, "Results Viewer")
        self.tabs.addTab(self.tab_logs, "Log Viewer")
        self.tabs.addTab(self.tab_settings, "Settings")

        # Build tab UIs
        self.build_run_tab()
        self.build_queue_tab()
        self.build_results_tab()
        self.build_logs_tab()
        self.build_settings_tab()

        # Placeholder simulation manager
        self.sim_manager = None  # Assigned in Part 3


    # -----------------------------------------------------------
    # TAB 1 — RUN SIMULATION
    # -----------------------------------------------------------
    def build_run_tab(self):
        layout = QVBoxLayout()

        title = QLabel("Run New CFD Simulation")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()

        # Geometry file
        self.geom_path = QLineEdit()
        btn_browse_geom = QPushButton("Browse…")
        btn_browse_geom.clicked.connect(self.pick_geometry)
        h_geom = QHBoxLayout()
        h_geom.addWidget(self.geom_path)
        h_geom.addWidget(btn_browse_geom)
        form.addRow("Geometry File:", h_geom)

        # Simulation name
        self.sim_name = QLineEdit()
        form.addRow("Simulation Name:", self.sim_name)

        # Component type
        self.comp_type = QComboBox()
        self.comp_type.addItems(["Front Wing", "Rear Wing", "Undertray", "Half Car"])
        form.addRow("Component Type:", self.comp_type)

        # L, W, H inputs
        self.box_L = QLineEdit()
        self.box_W = QLineEdit()
        self.box_H = QLineEdit()
        form.addRow("L (m):", self.box_L)
        form.addRow("W (m):", self.box_W)
        form.addRow("H (m):", self.box_H)

        # Output folder
        self.out_path = QLineEdit()
        btn_browse_out = QPushButton("Select Folder…")
        btn_browse_out.clicked.connect(self.pick_output_folder)
        h_out = QHBoxLayout()
        h_out.addWidget(self.out_path)
        h_out.addWidget(btn_browse_out)
        form.addRow("Output Folder:", h_out)

        layout.addLayout(form)

        # Buttons
        h_btns = QHBoxLayout()
        btn_run_now = QPushButton("Run Now")
        btn_add_queue = QPushButton("Add to Queue")

        btn_run_now.clicked.connect(self.run_now_clicked)
        btn_add_queue.clicked.connect(self.add_queue_clicked)

        h_btns.addWidget(btn_run_now)
        h_btns.addWidget(btn_add_queue)

        layout.addLayout(h_btns)

        # Progress Bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Status console
        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        layout.addWidget(self.status_box)

        self.tab_run.setLayout(layout)


    # -----------------------------------------------------------
    # TAB 2 — QUEUE SYSTEM
    # -----------------------------------------------------------
    def build_queue_tab(self):
        layout = QVBoxLayout()

        title = QLabel("Simulation Queue")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list)

        btn_start_queue = QPushButton("Start Queue")
        btn_clear_queue = QPushButton("Clear Queue")

        btn_start_queue.clicked.connect(self.start_queue_clicked)
        btn_clear_queue.clicked.connect(self.clear_queue_clicked)

        h = QHBoxLayout()
        h.addWidget(btn_start_queue)
        h.addWidget(btn_clear_queue)

        layout.addLayout(h)

        self.tab_queue.setLayout(layout)


    # -----------------------------------------------------------
    # TAB 3 — RESULTS VIEWER
    # -----------------------------------------------------------
    def build_results_tab(self):
        layout = QVBoxLayout()

        title = QLabel("Results Viewer")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Embedded image preview (set in Part 4)
        self.result_label = QLabel("No results loaded.")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.result_label)

        self.tab_results.setLayout(layout)


    # -----------------------------------------------------------
    # TAB 4 — LOG VIEWER
    # -----------------------------------------------------------
    def build_logs_tab(self):
        layout = QVBoxLayout()

        title = QLabel("Log Viewer")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.tab_logs.setLayout(layout)


    # -----------------------------------------------------------
    # TAB 5 — SETTINGS
    # -----------------------------------------------------------
    def build_settings_tab(self):
        layout = QVBoxLayout()

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        label = QLabel("No advanced settings available in Simple Mode.")
        layout.addWidget(label)

        self.tab_settings.setLayout(layout)


    # -----------------------------------------------------------
    # File pickers
    # -----------------------------------------------------------
    def pick_geometry(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Geometry", "", "STEP Files (*.step *.stp)")
        if file:
            self.geom_path.setText(file)

    def pick_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.out_path.setText(folder)


    # -----------------------------------------------------------
    # Button callbacks (sim manager connected in next phase)
    # -----------------------------------------------------------
    def run_now_clicked(self):
        self.append_status("Run Now clicked (will connect once Pipeline Manager is added).")

    def add_queue_clicked(self):
        self.append_status("Added job to queue list.")
        self.queue_list.addItem(f"{self.sim_name.text()}  |  {self.comp_type.currentText()}")

    def start_queue_clicked(self):
        self.append_status("Starting queue (pipeline added in simulation_manager).")

    def clear_queue_clicked(self):
        self.queue_list.clear()
        self.append_status("Queue cleared.")


    # -----------------------------------------------------------
    # Logging helpers (GUI-only)
    # -----------------------------------------------------------
    def append_status(self, msg):
        self.status_box.append(msg)

    def append_log(self, msg):
        self.log_box.append(msg)


# ---------------------------------------------------------------
# APPLICATION ENTRY POINT
# ---------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
