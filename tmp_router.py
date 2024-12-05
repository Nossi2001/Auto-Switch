# tmp_router.py
import ipaddress
import re
import shlex
import time
from collections import Counter
from socket import socket

import paramiko

class RouterBase:
    def __init__(self, ip, username, password, port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port

class tmp_router(RouterBase):
    """
    Klasa reprezentująca router, dziedzicząca po RouterBase.
    """

    def __init__(self, ip, username, password, port=22, default_netmask='24'):
        super().__init__(ip, username, password, port)
        self.client = None
        self.default_netmask = default_netmask

    def connect(self):
        """
        Nawiązuje połączenie SSH z routerem.
        """
        try:
            print(f"Łączenie z urządzeniem {self.ip}...")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.ip,
                port=self.port,
                username=self.username,
                password=self.password,
                look_for_keys=False,
                allow_agent=False
            )
            print("Połączono z urządzeniem.")
            return True
        except Exception as e:
            print(f"Błąd podczas łączenia: {e}")
            return False

    def disconnect(self):
        """
        Zamyka połączenie SSH z routerem.
        """
        if self.client:
            self.client.close()
            self.client = None
            print("Rozłączono z urządzeniem.")

    def execute_commands(self, commands):
        try:
            if not self.client:
                print("Brak połączenia z urządzeniem.")
                return False

            ssh_shell = self.client.invoke_shell()
            for cmd in commands:
                print(f"Wysyłanie komendy: {cmd}")
                ssh_shell.send(cmd + '\n')
                output = self.receive_all(ssh_shell)
                print(output)
            return True
        except Exception as e:
            print(f"Błąd podczas wykonywania komend: {e}")
            return False



    def get_unique_mac_addresses(self):
        """
        Pobiera unikalne adresy MAC z urządzenia, zwracając słownik:
        nazwa_interfejsu: adres_MAC.
        Jeśli ten sam adres MAC występuje na wielu interfejsach, kluczem będzie
        interfejs o krótszej nazwie.
        """
        try:
            if not self.client:
                print("Brak połączenia z urządzeniem.")
                return {}

            # Wykonaj polecenie na zdalnym urządzeniu
            stdin, stdout, stderr = self.client.exec_command('ip link show')

            # Pobierz wynik polecenia
            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                print(f"Błąd podczas wykonywania polecenia 'ip link show': {error}")
                return {}

            # Wzorzec do dopasowania nazw interfejsów i adresów MAC
            interface_pattern = re.compile(
                r"^\d+: (\S+?):.*\n\s+link/ether ([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})",
                re.MULTILINE
            )

            # Znajdź wszystkie interfejsy i ich adresy MAC
            interfaces = interface_pattern.findall(output)

            # Słownik do przechowywania unikalnych adresów MAC z nazwami interfejsów
            mac_to_iface = {}

            for iface, mac in interfaces:
                # Jeśli MAC nie jest jeszcze w słowniku, dodaj
                if mac not in mac_to_iface:
                    mac_to_iface[mac] = iface
                else:
                    # Jeśli MAC już istnieje, sprawdź długość nazw interfejsów
                    existing_iface = mac_to_iface[mac]
                    if len(iface) < len(existing_iface):
                        mac_to_iface[mac] = iface

            # Tworzymy słownik nazwa_interfejsu:adres_MAC
            iface_mac_dict = {iface: mac for mac, iface in mac_to_iface.items()}

            return iface_mac_dict

        except Exception as e:
            print(f"Błąd podczas pobierania adresów MAC: {e}")
            return {}

    def get_unique_physical_interfaces(self):
        keys = self.get_unique_mac_addresses()
        processed_keys = [re.split(r'\d', key)[0] for key in keys.keys()]
        port_counts = Counter(processed_keys)
        most_common_port = port_counts.most_common(1)[0][0]
        physical_interfaces = [key.split('@')[0] for key in keys.keys() if most_common_port in key]
        return physical_interfaces

    def get_unique_physical_interfaces_with_description(self):
        keys = self.get_unique_mac_addresses()
        processed_keys = [re.split(r'\d', key)[0] for key in keys.keys()]
        port_counts = Counter(processed_keys)
        if not port_counts:
            return {}
        most_common_port = port_counts.most_common(1)[0][0]
        phisical_interfaces = [key.split('@')[0] for key in keys.keys() if most_common_port in key]
        interfaces_with_description = {}

        ssh_shell = self.client.invoke_shell()
        cmd = 'configure'
        ssh_shell.send(cmd + '\n')
        for port in phisical_interfaces:
            cmd = f'show interfaces ethernet {port} description'
            ssh_shell.send(cmd + '\n')
            output = self.receive_all(ssh_shell)
            match = re.search(r'"([^"]+)"', output)
            if match:
                description = match.group(1).strip()
            else:
                description = "No description"

            interfaces_with_description[port] = description

        ssh_shell.send('exit\n')
        return interfaces_with_description

    def receive_all(self, shell, timeout=2.5):
        output = ''
        shell.setblocking(0)
        start_time = time.time()
        while True:
            if shell.recv_ready():
                recv_data = shell.recv(1024).decode('utf-8')
                output += recv_data
                start_time = time.time()  # Resetuj licznik po otrzymaniu danych
            else:
                if time.time() - start_time > timeout:
                    break
                time.sleep(0.1)
        return output



    def apply_data_configuration_without_bridge(self, ports):
        """
        Zastosowuje konfigurację dla szablonu "Data" na podanych portach bez bridge.
        """
        print("Zastosowanie konfiguracji Data...")
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return False

        try:
            commands = ["configure"]

            for port in ports:
                # Usunięcie istniejących ustawień z interfejsu
                commands.append(f"delete interfaces ethernet {port}")
                commands.append("commit")
                commands.append(f"set interfaces ethernet {port} description 'Data Port without bridge'")
                commands.append(f"set interfaces ethernet {port} duplex auto")
                commands.append(f"set interfaces ethernet {port} speed auto")
                commands.append(f"set interfaces ethernet {port} mtu 1500")

            # Komendy commit i save
            commands.append("commit")
            commands.append("save")
            commands.append("exit")

            # Wykonanie komend
            success = self.execute_commands(commands)
            if success:
                print("Konfiguracja Data została zastosowana.")
            return success

        except Exception as e:
            print(f"Błąd podczas konfiguracji: {e}")
            return False

    def apply_lan_dhcp(self, ports):
        """
        Zastosowuje konfigurację dla szablonu "Management" na podanych portach bez użycia VLAN-u.

        :param ports: Lista portów Ethernet do skonfigurowania jako porty zarządzania.
        :return: True jeśli konfiguracja została zastosowana poprawnie, False w przeciwnym razie.
        """
        print("Zastosowanie konfiguracji Management bez VLAN-u...")
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return False

        try:
            commands = ["configure"]



            for port in ports:
                # Usunięcie istniejących ustawień z interfejsu
                commands.append(f"delete interfaces ethernet {port}")
                commands.append("commit")
                # Zastosowanie nowych ustawień
                commands.append(f"set interfaces ethernet {port} description 'PORT LAN DHCP'")
                commands.append(f"set interfaces ethernet {port} duplex auto")
                commands.append(f"set interfaces ethernet {port} speed auto")
                commands.append(f"set interfaces ethernet {port} mtu 1500")
                commands.append(f"set interfaces ethernet {port} address dhcp")
                commands.append("commit")


            commands.append("save")
            commands.append("exit")

            # Wykonanie komend
            success = self.execute_commands(commands)
            if success:
                print("Konfiguracja Management została zastosowana bez VLAN-u.")
            else:
                print("Wystąpiły błędy podczas konfiguracji Management bez VLAN-u.")
            return success

        except Exception as e:
            print(f"Błąd podczas konfiguracji Management: {e}")
            return False

    def apply_dhcp_server(self, name_server, gateway, netmask, dhcp_range_start, dhcp_range_stop):
        """
           Konfiguruje serwer DHCP dla sieci zarządzania bez VLAN-u.

           :param name_server: Nazwa puli DHCP (shared-network-name).
           :param gateway: Adres IP routera (default-router), np. '192.168.1.1'.
           :param netmask: Maska sieci w formacie CIDR (np. '24').
           :param dhcp_range_start: Początek zakresu adresów DHCP (np. '192.168.1.100').
           :param dhcp_range_stop: Koniec zakresu adresów DHCP (np. '192.168.1.200').
           :return: True jeśli konfiguracja została zastosowana poprawnie, False w przeciwnym razie.
           """
        print("Tworzenie serwera DHCP...")
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return False

        try:
            commands = ["configure"]
            commands.append(f"set service dhcp-server disabled false")
            commands.append(f"set service dhcp-server shared-network-name LAN1 authoritative enable")
            commands.append(f"set service dhcp-server shared-network-name LAN1 subnet 192.168.55.0/24 default-router 192.168.55.1")
            commands.append(f"set service dhcp-server shared-network-name LAN1 subnet 192.168.55.0/24 dns-server 8.8.8.8")
            commands.append(f"set service dhcp-server shared-network-name LAN1 subnet 192.168.55.0/24 lease 86400")
            commands.append(f"set service dhcp-server shared-network-name LAN1 subnet 192.168.55.0/24 start 192.168.55.60 stop 192.168.55.70")
            commands.append("commit")
            commands.append("save")
            commands.append("exit")

            # Wykonanie komend
            success = self.execute_commands(commands)
            if success:
                print("Stworzono serwer DHCP")
            else:
                print("Wystąpiły błędy podczas tworzeni serwera DHCP")
            return success

        except Exception as e:
            print(f"Błąd podczas tworzeni serwera DHCP: {e}")
            return False






