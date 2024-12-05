# threads/configuration_thread.py

from PyQt6.QtCore import QThread, pyqtSignal


class ConfigurationThread(QThread):
    configuration_result = pyqtSignal(bool, str)

    def __init__(self, router, template, config_params):
        super().__init__()
        self.router = router
        self.template = template
        self.config_params = config_params

    def run(self):
        try:
            if not self.router.connect():
                self.configuration_result.emit(False, "Nie udało się połączyć z urządzeniem.")
                return

            # Implementacja logiki konfiguracji dla wybranych szablonów
            if self.template == "dhcp_server":
                success = self.router.apply_dhcp_server(
                    name_server=self.config_params.get("name_server"),
                    gateway=self.config_params.get("gateway"),
                    netmask=self.config_params.get("netmask"),
                    dhcp_range_start=self.config_params.get("dhcp_range_start"),
                    dhcp_range_stop=self.config_params.get("dhcp_range_stop")
                )
            elif self.template == "dhcp":
                success = self.router.apply_dhcp(
                    ports=self.config_params.get("ports", [])
                )
            elif self.template == "data_configuration_without_bridge":
                success = self.router.apply_data_configuration_without_bridge(
                    ports=self.config_params.get("ports", [])
                )
            else:
                self.configuration_result.emit(False, "Nieznany szablon konfiguracji.")
                return

            # Wyświetlenie komunikatu o sukcesie
            if success:
                config_message = f"Zastosowano '{self.template}' z podanymi parametrami."
                self.configuration_result.emit(True, config_message)
            else:
                self.configuration_result.emit(False, "Wystąpiły błędy podczas konfiguracji.")

        except Exception as e:
            self.configuration_result.emit(False, f"Błąd podczas konfiguracji: {e}")
        finally:
            self.router.disconnect()
