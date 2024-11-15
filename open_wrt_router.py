# open_wrt_router.py

from router_base import RouterBase
import paramiko
import time
import os
from datetime import datetime
from scp import SCPClient

class OpenWrtRouter(RouterBase):
    LAN_INTERFACE = 'lan'
    BACKUP_DIRECTORY = r"C:\Users\Mateusz.N\Documents\konf"  # Możesz zmienić na preferowaną ścieżkę

    def __init__(self, ip, username, password, port=22):
        super().__init__(ip, username, password, port)
        self.client = None
        self.current_ip = None
        self.current_netmask = None
        self.current_gateway = None

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

            # Pobieramy aktualne ustawienia sieciowe
            self.get_current_network_settings()

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

    def get_current_network_settings(self):
        try:
            # Pobieramy adres IP
            stdin, stdout, stderr = self.client.exec_command(f'uci get network.{self.LAN_INTERFACE}.ipaddr')
            ipaddr = stdout.read().decode().strip()
            self.current_ip = ipaddr

            # Pobieramy maskę podsieci
            stdin, stdout, stderr = self.client.exec_command(f'uci get network.{self.LAN_INTERFACE}.netmask')
            netmask = stdout.read().decode().strip()
            self.current_netmask = netmask

            # Pobieramy bramę domyślną (opcjonalnie)
            stdin, stdout, stderr = self.client.exec_command(f'uci get network.{self.LAN_INTERFACE}.gateway')
            gateway = stdout.read().decode().strip()
            self.current_gateway = gateway if gateway else None

            print(f"Aktualne ustawienia sieciowe:")
            print(f"IP: {self.current_ip}")
            print(f"Maska podsieci: {self.current_netmask}")
            print(f"Brama domyślna: {self.current_gateway}")

        except Exception as e:
            print(f"Wystąpił błąd podczas pobierania ustawień sieciowych: {e}")

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
            local_backup_dir = self.BACKUP_DIRECTORY
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
                return False

            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas tworzenia kopii zapasowej: {e}")
            return False

    def set_hostname(self, hostname):
        if self.client is None:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            command = f'uci set system.@system[0].hostname="{hostname}" && uci commit system && /etc/init.d/system reload'
            stdin, stdout, stderr = self.client.exec_command(command)
            stdout.channel.recv_exit_status()
            error = stderr.read().decode()
            if error:
                print(f"Błąd: {error}")
            print(f"Nazwa hosta została ustawiona na '{hostname}'.")
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas ustawiania nazwy hosta: {e}")
            return False

    def set_domain(self, domain):
        if self.client is None:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            command = f'uci set dhcp.@dnsmasq[0].domain="{domain}" && uci commit dhcp && /etc/init.d/dnsmasq restart'
            stdin, stdout, stderr = self.client.exec_command(command)
            stdout.channel.recv_exit_status()
            error = stderr.read().decode()
            if error:
                print(f"Błąd: {error}")
            print(f"Domena została ustawiona na '{domain}'.")
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas ustawiania domeny: {e}")
            return False

    def configure_interface(self, interface_name, ip_address=None, netmask=None, description=None, enabled=True,
                            reconnect=True):
        if self.client is None:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            commands = []

            if ip_address:
                commands.append(f'uci set network.{interface_name}.ipaddr="{ip_address}"')
                print(f"Ustawianie adresu IP {ip_address} na interfejsie {interface_name}.")

            if netmask:
                commands.append(f'uci set network.{interface_name}.netmask="{netmask}"')
                print(f"Ustawianie maski podsieci {netmask} na interfejsie {interface_name}.")

            if description:
                commands.append(f'uci set network.{interface_name}.description="{description}"')
                print(f"Ustawianie opisu '{description}' na interfejsie {interface_name}.")

            if enabled:
                commands.append(f'uci set network.{interface_name}.disabled="0"')
                print(f"Włączanie interfejsu {interface_name}.")
            else:
                commands.append(f'uci set network.{interface_name}.disabled="1"')
                print(f"Wyłączanie interfejsu {interface_name}.")

            if commands:
                commands.append('uci commit network')
                # Uruchamiamy restart sieci w tle
                commands.append('/etc/init.d/network restart >/dev/null 2>&1 &')

                for cmd in commands:
                    stdin, stdout, stderr = self.client.exec_command(cmd)
                    stdout.channel.recv_exit_status()
                    error = stderr.read().decode()
                    if error:
                        print(f"Błąd: {error}")
                    print(f"Wykonano: {cmd}")
                    time.sleep(1)
                print(f"Konfiguracja interfejsu {interface_name} została zastosowana.")

                # Aktualizacja bieżących ustawień, jeśli zmieniono interfejs LAN
                if interface_name == self.LAN_INTERFACE:
                    if ip_address:
                        self.current_ip = ip_address
                        # Aktualizacja adresu IP w obiekcie
                        self.ip = ip_address
                    if netmask:
                        self.current_netmask = netmask

                    # Rozłączenie z routerem (połączenie może być przerwane)
                    self.disconnect()

                    # Opcjonalne ponowne połączenie
                    if reconnect:
                        print(f"Ponowne łączenie z nowym adresem IP: {self.ip}")
                        # Dodaj opóźnienie, aby router zdążył zastosować nowe ustawienia
                        time.sleep(10)  # Możesz dostosować czas oczekiwania
                        if self.connect():
                            print("Ponownie połączono z routerem po zmianie adresu IP.")
                        else:
                            print("Nie udało się ponownie połączyć z routerem po zmianie adresu IP.")

                return True
            else:
                print("Nie podano żadnych parametrów do konfiguracji.")
                return False
        except Exception as e:
            print(f"Wystąpił błąd podczas konfiguracji interfejsu {interface_name}: {e}")
            return False

    def change_ip(self, new_ip):
        # Implementacja metody abstrakcyjnej change_ip z RouterBase
        # Wykorzystujemy metodę configure_interface
        return self.configure_interface(
            interface_name=self.LAN_INTERFACE,
            ip_address=new_ip,
            netmask=self.current_netmask,
            reconnect=True
        )

    def create_vlan(self, vlan_id, name=None):
        if self.client is None:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            # Sprawdzenie czy VLAN już istnieje
            check_command = f'uci show network.vlan{vlan_id}'
            stdin, stdout, stderr = self.client.exec_command(check_command)
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                print(f"VLAN {vlan_id} już istnieje.")
                return False

            commands = [
                f'uci set network.vlan{vlan_id}=interface',
                f'uci set network.vlan{vlan_id}.ifname="eth0.{vlan_id}"',
                f'uci set network.vlan{vlan_id}.type="bridge"',
                f'uci set network.vlan{vlan_id}.proto="static"',
                f'uci set network.vlan{vlan_id}.ipaddr="0.0.0.0"',
                f'uci set network.vlan{vlan_id}.netmask="255.255.255.0"'
            ]
            if name:
                commands.append(f'uci set network.vlan{vlan_id}.name="{name}"')

            commands.append('uci commit network')
            commands.append('/etc/init.d/network restart >/dev/null 2>&1 &')

            for cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(cmd)
                stdout.channel.recv_exit_status()
                error = stderr.read().decode()
                if error:
                    print(f"Błąd: {error}")
                print(f"Wykonano: {cmd}")
                time.sleep(1)

            print(f"VLAN {vlan_id} został utworzony.")
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas tworzenia VLAN {vlan_id}: {e}")
            return False

    def assign_vlan_to_interface(self, vlan_id, interface_name, tagged=False):
        if self.client is None:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            # Pobranie aktualnej listy interfejsów dla danego interfejsu logicznego
            get_ifname_cmd = f'uci get network.{interface_name}.ifname'
            stdin, stdout, stderr = self.client.exec_command(get_ifname_cmd)
            stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode()

            if error:
                print(f"Błąd podczas pobierania interfejsu: {error}")
                return False

            # Przygotowanie nazwy interfejsu VLAN
            if tagged:
                vlan_interface = f"eth0.{vlan_id}"
            else:
                vlan_interface = f"eth0"

            # Dodanie interfejsu VLAN do listy ifname
            ifname_list = output.replace("'", "").split()
            if vlan_interface not in ifname_list:
                ifname_list.append(vlan_interface)

            # Aktualizacja konfiguracji interfejsu
            new_ifname = ' '.join(ifname_list)
            set_ifname_cmd = f'uci set network.{interface_name}.ifname="{new_ifname}"'
            stdin, stdout, stderr = self.client.exec_command(set_ifname_cmd)
            stdout.channel.recv_exit_status()
            error = stderr.read().decode()
            if error:
                print(f"Błąd: {error}")

            # Zapisanie konfiguracji i restart sieci
            commands = [
                'uci commit network',
                '/etc/init.d/network restart >/dev/null 2>&1 &'
            ]
            for cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(cmd)
                stdout.channel.recv_exit_status()
                error = stderr.read().decode()
                if error:
                    print(f"Błąd: {error}")
                print(f"Wykonano: {cmd}")
                time.sleep(1)

            print(f"VLAN {vlan_id} został przypisany do interfejsu {interface_name} ({'tagged' if tagged else 'untagged'}).")
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas przypisywania VLAN {vlan_id} do interfejsu {interface_name}: {e}")
            return False

    def configure_trunk(self, interface_name, vlan_ids):
        if self.client is None:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            # Przygotowanie listy interfejsów VLAN
            vlan_interfaces = [f"eth0.{vlan_id}" for vlan_id in vlan_ids]

            # Aktualizacja konfiguracji interfejsu
            vlan_ifnames = ' '.join(vlan_interfaces)
            set_ifname_cmd = f'uci set network.{interface_name}.ifname="{vlan_ifnames}"'
            stdin, stdout, stderr = self.client.exec_command(set_ifname_cmd)
            stdout.channel.recv_exit_status()
            error = stderr.read().decode()
            if error:
                print(f"Błąd: {error}")

            # Ustawienie typu interfejsu na bridge
            set_type_cmd = f'uci set network.{interface_name}.type="bridge"'
            stdin, stdout, stderr = self.client.exec_command(set_type_cmd)
            stdout.channel.recv_exit_status()
            error = stderr.read().decode()
            if error:
                print(f"Błąd: {error}")

            # Zapisanie konfiguracji i restart sieci
            commands = [
                'uci commit network',
                '/etc/init.d/network restart >/dev/null 2>&1 &'
            ]
            for cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(cmd)
                stdout.channel.recv_exit_status()
                error = stderr.read().decode()
                if error:
                    print(f"Błąd: {error}")
                print(f"Wykonano: {cmd}")
                time.sleep(1)

            print(f"Interfejs {interface_name} został skonfigurowany jako trunk dla VLAN-ów: {vlan_ids}.")
            return True
        except Exception as e:
            print(f"Wystąpił błąd podczas konfiguracji trunkingu na interfejsie {interface_name}: {e}")
            return False
