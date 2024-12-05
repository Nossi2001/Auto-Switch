# threads/interface_thread.py

from PyQt6.QtCore import QThread, pyqtSignal


class InterfaceThread(QThread):
    interfaces_result = pyqtSignal(bool, dict, str)  # Zmieniono list na dict

    def __init__(self, router):
        super().__init__()
        self.router = router

    def run(self):
        try:
            if not self.router.connect():
                self.interfaces_result.emit(False, {}, "Nie udało się połączyć z urządzeniem.")
                return
            interfaces = self.router.get_unique_physical_interfaces_with_description()  # Nowa metoda
            self.router.disconnect()
            if interfaces:
                self.interfaces_result.emit(True, interfaces, "")
            else:
                self.interfaces_result.emit(False, {}, "Nie znaleziono interfejsów.")
        except Exception as e:
            self.interfaces_result.emit(False, {}, str(e))
