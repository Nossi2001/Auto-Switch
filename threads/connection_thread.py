# threads/connection_thread.py

from PyQt6 import QtCore
from tmp_router import tmp_router

class ConnectionThread(QtCore.QThread):
    connection_result = QtCore.pyqtSignal(bool, str)

    def __init__(self, ip, username, password):
        super().__init__()
        self.ip = ip
        self.username = username
        self.password = password

    def run(self):
        router = tmp_router(ip=self.ip, username=self.username, password=self.password)
        try:
            success = router.connect()
            router.disconnect()
            if success:
                self.connection_result.emit(True, "")
            else:
                self.connection_result.emit(False, "Nie udało się połączyć z urządzeniem.")
        except Exception as e:
            self.connection_result.emit(False, str(e))
