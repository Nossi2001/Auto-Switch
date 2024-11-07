# open_wrt_router.py

from router_base import RouterBase
import paramiko
import time
import os
from datetime import datetime
from scp import SCPClient
class OpenWrtRouter(RouterBase):
    def connect(self):
        try:
            print(f"Łączenie z urządzeniem {self.ip}...")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Dodajemy konfigurację akceptowanych algorytmów
            self.client.connect(
                hostname=self.ip,
                port=self.port,
                username=self.username,
                password=self.password,
                look_for_keys=False,
                allow_agent=False,
                disabled_algorithms={
                    'pubkeys': [],
                    'keys': []
                }
            )
            print("Połączono z urządzeniem.")
            return True
        except paramiko.ssh_exception.AuthenticationException as e:
            print(f"Błąd uwierzytelniania: {e}")
            return False
        except paramiko.ssh_exception.SSHException as e:
            print(f"Błąd SSH: {e}")
            return False
        except Exception as e:
            print(f"Wystąpił błąd podczas łączenia: {e}")
            return False

    def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            print("Rozłączono z urządzeniem.")

    def change_ip(self, new_ip):
        if self.client is None:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            print(f"Zmiana adresu IP na {new_ip} dla GL-SFT1200...")
            commands = [
                f'uci set network.lan.ipaddr="{new_ip}"',
                'uci commit network',
                '/etc/init.d/network restart'
            ]
            for cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(cmd)
                stdout.channel.recv_exit_status()
                output = stdout.read().decode()
                error = stderr.read().decode()
                if output:
                    print(f"Wynik: {output}")
                if error:
                    print(f"Błąd: {error}")
                print(f"Wykonano: {cmd}")
                time.sleep(1)

            print("Adres IP został zmieniony. Urządzenie może być niedostępne przez chwilę.")
            self.disconnect()
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas zmiany adresu IP: {e}")
            return False

    def backup_configuration(self):
        if self.client is None:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            # Generowanie pliku kopii zapasowej na routerze
            remote_backup_file = "/tmp/backup.tar.gz"
            backup_command = f"sysupgrade -b {remote_backup_file}"

            print("Generowanie kopii zapasowej na routerze...")
            stdin, stdout, stderr = self.client.exec_command(backup_command)
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error = stderr.read().decode()
                print(f"Błąd podczas tworzenia kopii zapasowej: {error}")
                return False

            # Używamy stałej ścieżki do katalogu kopii zapasowych
            local_backup_dir = r"C:\Users\Mateusz.N\Documents\konf"
            if not os.path.exists(local_backup_dir):
                os.makedirs(local_backup_dir)

            # Tworzymy unikalną nazwę pliku z datą i godziną
            date_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            local_backup_file = os.path.join(local_backup_dir, f"backup_{date_str}.tar.gz")

            # Pobieranie pliku kopii zapasowej za pomocą SCP
            print(f"Pobieranie pliku kopii zapasowej do {local_backup_file}...")
            with SCPClient(self.client.get_transport()) as scp:
                scp.get(remote_backup_file, local_backup_file)

            # Usuwanie pliku kopii zapasowej z routera
            stdin, stdout, stderr = self.client.exec_command(f"rm {remote_backup_file}")
            stdout.channel.recv_exit_status()

            # Sprawdzamy, czy plik został pobrany
            if os.path.isfile(local_backup_file):
                print(f"Kopia zapasowa została pomyślnie pobrana i zapisana w: {local_backup_file}")
            else:
                print("Nie udało się znaleźć pliku kopii zapasowej w oczekiwanej lokalizacji.")

            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas tworzenia kopii zapasowej: {e}")
            return False

