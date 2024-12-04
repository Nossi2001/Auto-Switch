# threads/interface_thread.py

from PyQt6 import QtCore

class InterfaceThread(QtCore.QThread):
    interfaces_result = QtCore.pyqtSignal(bool, list, str)

    def __init__(self, router):
        super().__init__()
        self.router = router

    def run(self):
        try:
            if not self.router.connect():
                self.interfaces_result.emit(False, [], "Nie udało się połączyć z urządzeniem.")
                return
            interfaces = self.router.get_unique_phisical_interfaces()
            self.router.disconnect()
            if interfaces:
                self.interfaces_result.emit(True, interfaces, "")
            else:
                self.interfaces_result.emit(False, [], "Nie znaleziono interfejsów.")
        except Exception as e:
            self.interfaces_result.emit(False, [], str(e))
