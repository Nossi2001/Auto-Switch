# threads/dhcp_info_thread.py

from PyQt6.QtCore import QThread, pyqtSignal


class DHCPInfoThread(QThread):
    """
    Wątek do pobierania informacji o serwerach DHCP.
    """
    dhcp_info_result = pyqtSignal(str)  # Sygnał do przesłania wyniku do GUI

    def __init__(self, router):
        super().__init__()
        self.router = router

    def run(self):
        """
        Pobiera informacje o serwerach DHCP.
        """
        try:
            # Połączenie z routerem
            if not self.router.connect():
                self.dhcp_info_result.emit("Failed to connect to the device.")
                return

            # Pobranie informacji o DHCP
            dhcp_info = self.router.get_dhcp_server_info()
            self.router.disconnect()

            # Jeśli brak informacji o serwerach DHCP
            if not dhcp_info:
                self.dhcp_info_result.emit("No DHCP server information available.")
                return

            # Formatowanie wyników
            info_text = "Existing DHCP Servers:\n"
            for dhcp_server in dhcp_info:
                info_text += f"Name: {dhcp_server['server_name']}, Range: {dhcp_server['range']}\n"

            self.dhcp_info_result.emit(info_text)

        except Exception as e:
            # Obsługa błędów
            self.dhcp_info_result.emit(f"Error fetching DHCP server information: {e}")
