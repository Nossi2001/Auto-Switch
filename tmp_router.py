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
        self.client = None
        self._interfaces_cache = None  # Cache wyników
        self._cache_timestamp = None  # Znacznik czasu cache
        self._cache_ttl = 60  # Czas życia cache w sekundach

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
        Nawiązuje połączenie SSH z routerem i czyści cache.
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
            # Czyszczenie cache po nowym połączeniu
            self._interfaces_cache = None
            self._cache_timestamp = None
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
        """
        Pobiera unikalne interfejsy fizyczne z opisami z cache, jeśli są aktualne,
        w przeciwnym razie pobiera je z urządzenia.
        """
        current_time = time.time()

        # Sprawdzenie, czy dane w cache są aktualne
        if self._interfaces_cache and (current_time - self._cache_timestamp < self._cache_ttl):
            print("Zwracanie danych z cache.")
            return self._interfaces_cache

        print("Pobieranie danych z urządzenia.")
        try:
            keys = self.get_unique_mac_addresses()
            processed_keys = [re.split(r'\d', key)[0] for key in keys.keys()]
            port_counts = Counter(processed_keys)

            if not port_counts:
                return {}

            most_common_port = port_counts.most_common(1)[0][0]
            physical_interfaces = [key.split('@')[0] for key in keys.keys() if most_common_port in key]
            interfaces_with_description = {}

            ssh_shell = self.client.invoke_shell()
            ssh_shell.send('configure\n')
            for port in physical_interfaces:
                cmd = f'show interfaces ethernet {port} description\n'
                ssh_shell.send(cmd)
                output = self.receive_all(ssh_shell)
                match = re.search(r'"([^"]+)"', output)
                description = match.group(1).strip() if match else "No description"
                interfaces_with_description[port] = description

            ssh_shell.send('exit\n')

            # Aktualizacja cache
            self._interfaces_cache = interfaces_with_description
            self._cache_timestamp = current_time

            return interfaces_with_description

        except Exception as e:
            print(f"Błąd podczas pobierania interfejsów z opisem: {e}")
            return {}

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

    def apply_dhcp(self, ports):
        """
        :param ports: Lista portów Ethernet do skonfigurowania jako porty DHCP.
        :return: True jeśli konfiguracja została zastosowana poprawnie, False w przeciwnym razie.
        """
        if not self.client:
            return False
        try:
            commands = ["configure"]



            for port in ports:
                # Usunięcie istniejących ustawień z interfejsu
                commands.append(f"delete interfaces ethernet {port}")
                commands.append("commit")
                # Zastosowanie nowych ustawień
                commands.append(f"set interfaces ethernet {port} description 'PORT DHCP'")
                commands.append(f"set interfaces ethernet {port} duplex auto")
                commands.append(f"set interfaces ethernet {port} speed auto")
                commands.append(f"set interfaces ethernet {port} mtu 1500")
                commands.append(f"set interfaces ethernet {port} address dhcp")
                commands.append("commit")

            commands.append("save")
            commands.append("exit")

            # Wykonanie komend
            success = self.execute_commands(commands)
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
            commands.append(f"set service dhcp-server shared-network-name {name_server} authoritative enable")
            commands.append(f"set service dhcp-server shared-network-name {name_server} subnet {gateway}/{netmask} default-router {gateway}")
            commands.append(f"set service dhcp-server shared-network-name {name_server} subnet {gateway}/{netmask} dns-server 8.8.8.8")
            commands.append(f"set service dhcp-server shared-network-name {name_server} subnet {gateway}/{netmask} lease 86400")
            commands.append(f"set service dhcp-server shared-network-name {name_server} subnet {gateway}/{netmask} start {dhcp_range_start} stop {dhcp_range_stop}")
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

    def get_dhcp_server_info(self):
        """
        Pobiera informacje o wszystkich serwerach DHCP, w tym ich nazwę i zakres adresów IP.

        :return: Lista słowników z nazwami serwerów DHCP i zakresami adresów IP
                 [{'server_name': 'DHCP_Server1', 'range': '192.168.1.100-192.168.1.200'},
                  {'server_name': 'DHCP_Server2', 'range': '10.0.0.50-10.0.0.100'}]
                 lub None w przypadku błędu.
        """
        try:
            ssh_shell = self.client.invoke_shell()
            cmd = 'configure'
            ssh_shell.send(cmd + '\n')
            cmd = "show service dhcp-server"
            ssh_shell.send(cmd + '\n')
            output = self.receive_all(ssh_shell)

            # Debug: Wypisz pełne wyjście
            print(output)

            # Parsowanie wszystkich nazw serwerów DHCP
            server_names = re.findall(r"shared-network-name\s+(\S+)", output)

            # Parsowanie wszystkich zakresów DHCP
            range_starts = re.findall(r"start\s+(\d+\.\d+\.\d+\.\d+)", output)
            range_stops = re.findall(r"stop\s+(\d+\.\d+\.\d+\.\d+)", output)

            # Upewnij się, że liczba nazw i zakresów jest spójna
            if len(server_names) != len(range_starts) or len(range_starts) != len(range_stops):
                print("Nieprawidłowy format danych DHCP w wyjściu.")
                return None

            # Tworzenie listy słowników
            dhcp_servers = []
            for i in range(len(server_names)):
                dhcp_servers.append({
                    "server_name": server_names[i],
                    "range": f"{range_starts[i]}-{range_stops[i]}"
                })

            return dhcp_servers

        except Exception as e:
            print(f"Błąd podczas pobierania informacji o serwerze DHCP: {e}")
            return None




