# threads/configuration_thread.py

from PyQt6 import QtCore

class ConfigurationThread(QtCore.QThread):
    configuration_result = QtCore.pyqtSignal(bool, str)

    def __init__(self, router, template, ports, config_params):
        super().__init__()
        self.router = router
        self.template = template
        self.ports = ports
        self.config_params = config_params

    def run(self):
        try:
            if not self.router.connect():
                self.configuration_result.emit(False, "Nie udało się połączyć z urządzeniem.")
                return

            # Implementacja logiki konfiguracji dla wybranych szablonów
            if self.template == "dhcp_server":
                self.router.apply_dhcp_server(
                    name_server=self.config_params.get("name_server"),
                    gateway=self.config_params.get("gateway"),
                    netmask=self.config_params.get("netmask"),
                    dhcp_range_start=self.config_params.get("dhcp_range_start"),
                    dhcp_range_stop=self.config_params.get("dhcp_range_stop")
                )
            elif self.template == "lan_dhcp":
                self.router.apply_lan_dhcp(
                    ports=self.config_params.get("ports")
                )
            elif self.template == "data_configuration_without_bridge":
                self.router.apply_data_configuration_without_bridge(
                    ports=self.config_params.get("ports")
                )
            else:
                self.configuration_result.emit(False, "Nieznany szablon konfiguracji.")
                return

            # Wyświetlenie komunikatu o sukcesie
            config_message = f"Zastosowano '{self.template}' na portach: {', '.join(self.ports)}."
            self.configuration_result.emit(True, config_message)
        except Exception as e:
            self.configuration_result.emit(False, f"Błąd podczas konfiguracji: {e}")
        finally:
            self.router.disconnect()
