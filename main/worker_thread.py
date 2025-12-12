from PySide6.QtCore import QThread, Signal

class WorkerThread(QThread):
    log_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def run(self):
        self.manager.set_log_callback(self.log_signal.emit)
        self.manager.run_all()
        self.finished_signal.emit()
