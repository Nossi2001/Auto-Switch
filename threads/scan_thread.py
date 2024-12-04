# threads/scan_thread.py

from PyQt6 import QtCore
from Auto_Finder_Router import Auto_Finder_Router

class ScanThread(QtCore.QThread):
    scan_result = QtCore.pyqtSignal(list)

    def run(self):
        devices = Auto_Finder_Router()
        self.scan_result.emit(devices)
