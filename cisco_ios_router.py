# cisco_ios_router.py

from router_base import RouterBase
from netmiko import ConnectHandler
import time
import os
from datetime import datetime

class CiscoIOSRouter(RouterBase):
    def connect(self):
        try:
            print(f"Łączenie z urządzeniem {self.ip}...")
            self.connection = ConnectHandler(
                device_type='cisco_ios',
                ip=self.ip,
                username=self.username,
                password=self.password,
                secret=self.password,  # Jeśli hasło enable jest takie samo
                port=self.port
            )
            self.connection.enable()  # Przejście do trybu uprzywilejowanego
            print("Połączono z urządzeniem.")
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas łączenia: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None
            print("Rozłączono z urządzeniem.")

    def change_ip(self, new_ip):
        if not self.connection:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            print(f"Zmiana adresu IP na {new_ip} dla urządzenia Cisco IOS...")
            commands = [
                'configure terminal',
                'interface GigabitEthernet0/0',  # Zmień na odpowiedni interfejs
                f'ip address {new_ip} 255.255.255.0',  # Ustaw odpowiednią maskę
                'no shutdown',
                'exit',
                'exit',
                'write memory'
            ]
            output = self.connection.send_config_set(commands)
            print(output)
            print("Adres IP został zmieniony.")
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas zmiany adresu IP: {e}")
            return False

    def backup_configuration(self):
        if not self.connection:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            print("Pobieranie konfiguracji bieżącej...")
            running_config = self.connection.send_command('show running-config')

            # Używamy stałej ścieżki do katalogu kopii zapasowych
            local_backup_dir = r"C:\Users\Mateusz.N\Documents\konf"
            if not os.path.exists(local_backup_dir):
                os.makedirs(local_backup_dir)

            # Tworzymy unikalną nazwę pliku z datą i godziną
            date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            local_backup_file = os.path.join(local_backup_dir, f"cisco_backup_{date_str}.cfg")

            # Zapisujemy konfigurację do pliku
            with open(local_backup_file, 'w') as f:
                f.write(running_config)

            print(f"Kopia zapasowa została zapisana w: {local_backup_file}")
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas tworzenia kopii zapasowej: {e}")
            return False