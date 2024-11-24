# edge_router.py

import paramiko
import time
from router_base import RouterBase
import ipaddress
import re
import os
class EdgeRouter(RouterBase):
    """
    Klasa reprezentująca router Ubiquiti EdgeRouter z systemem EdgeOS.
    Implementuje metody abstrakcyjne z klasy RouterBase.
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

    def get_basic_info(self):
        """
        Pobiera podstawowe informacje o routerze:
        - Adresy IP interfejsów
        - Ustawienia DNS
        - Brama domyślna
        """
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return None
        try:
            info = {}

            # Pobieranie informacji o interfejsach
            cmd_interfaces = '/opt/vyatta/bin/vyatta-op-cmd-wrapper show interfaces'
            stdin, stdout, stderr = self.client.exec_command(cmd_interfaces)
            interfaces_output = stdout.read().decode()
            info['interfaces'] = interfaces_output

            # Pobieranie ustawień DNS (system name-server)
            cmd_dns_system = '/opt/vyatta/bin/vyatta-op-cmd-wrapper show system name-server'
            stdin, stdout, stderr = self.client.exec_command(cmd_dns_system)
            dns_system_output = stdout.read().decode().strip()

            # Pobieranie ustawień DNS (service dns forwarding name-server)
            stdin, stdout, stderr = self.client.exec_command('cat /etc/resolv.conf')
            dns_system_output = stdout.read().decode().strip()

            # Sprawdzenie, które polecenie zwróciło dane
            if dns_system_output:
                info['dns'] = dns_system_output
            else:
                info['dns'] = "Brak skonfigurowanych serwerów DNS."

            # Pobieranie bramy domyślnej
            stdin, stdout, stderr = self.client.exec_command('ip route | grep default')
            gateway_output = stdout.read().decode()
            info['gateway'] = gateway_output

            return info
        except Exception as e:
            print(f"Błąd podczas pobierania informacji: {e}")
            return None

    def get_management_interface(self):
        """
        Znajduje interfejs, którego używamy do konfiguracji (interfejs zarządzający).
        """
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return None
        try:
            cmd = "ip addr show"
            stdin, stdout, stderr = self.client.exec_command(cmd)
            output = stdout.read().decode()
            interfaces = {}
            current_interface = None
            for line in output.splitlines():
                if line:
                    # Sprawdzamy, czy linia zawiera nazwę interfejsu
                    match_interface = re.match(r'\d+:\s+(\S+):', line)
                    if match_interface:
                        # Nowy interfejs
                        current_interface = match_interface.group(1).split('@')[0]
                    elif 'inet ' in line and current_interface:
                        # Znaleziono adres inet na interfejsie
                        match_ip = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/\d+', line)
                        if match_ip:
                            ip_address = match_ip.group(1)
                            interfaces[ip_address] = current_interface

            # Sprawdzamy, czy self.ip jest wśród adresów IP interfejsów
            if self.ip in interfaces:
                management_interface = interfaces[self.ip]
                print(f"Interfejs zarządzający to: {management_interface}")
                return management_interface
            else:
                print("Nie znaleziono interfejsu zarządzającego.")
                return None
        except Exception as e:
            print(f"Błąd podczas wyszukiwania interfejsu zarządzającego: {e}")
            return None

    def reconnect(self, new_ip=None):
        """
        Ponownie łączy się z routerem.
        Jeśli podano `new_ip`, aktualizuje adres IP przed próbą połączenia.
        """
        self.disconnect()
        print("Rozłączono z routerem")
        print("Próba ponownego połączenia z routerem")
        if new_ip:
            self.ip = new_ip
        return self.connect()

    def change_ip(self, interface_name, new_ip, netmask=None):
        """
        Zmienia adres IP na podanym interfejsie.
        """
        if netmask is None:
            netmask = self.default_netmask

        try:
            # Konwersja netmask do CIDR jeśli to konieczne
            if '/' in str(netmask):
                cidr_netmask = str(netmask).replace('/', '')
            else:
                cidr_netmask = self.netmask_to_cidr(netmask)
                if cidr_netmask is None:
                    print("Nieprawidłowa maska podsieci.")
                    return False

            # Pobierz interfejs zarządzający przed zmianami
            management_interface = self.get_management_interface()

            # Pobierz obecne adresy IP interfejsu
            current_ips = self.get_interface_ips(interface_name)

            # Przygotowanie komend
            commands = ['/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin']

            # Usuń obecne adresy IP
            for ip in current_ips:
                commands.append(
                    f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper delete interfaces ethernet {interface_name} address {ip}/{cidr_netmask}')

            # Ustaw nowy adres IP
            commands.append(
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set interfaces ethernet {interface_name} address {new_ip}/{cidr_netmask}')

            commands.extend([
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ])

            # Wykonaj wszystkie komendy jako jedno polecenie
            full_cmd = '; '.join(commands)
            stdin, stdout, stderr = self.client.exec_command(full_cmd)
            # Nie czekamy na exit_status ani nie czytamy stdout/stderr, ponieważ połączenie może zostać zerwane

            print(f"Adres IP interfejsu {interface_name} został zmieniony na {new_ip}/{cidr_netmask}.")

            # Jeśli zmieniliśmy adres IP interfejsu zarządzającego, musimy ponownie się połączyć
            if interface_name == management_interface:
                print("Adres IP interfejsu zarządzającego został zmieniony. Próba ponownego połączenia...")
                self.disconnect()
                self.ip = new_ip  # Aktualizujemy adres IP routera

                # Pętla próbująca ponownie nawiązać połączenie
                max_attempts = 100  # Maksymalna liczba prób
                attempt = 0
                connected = False
                while attempt < max_attempts and not connected:
                    attempt += 1
                    try:
                        print(f"Próba {attempt} połączenia z {self.ip}...")
                        time.sleep(5)  # Czekamy 5 sekund przed każdą próbą
                        connected = self.connect()
                        if connected:
                            print("Ponownie połączono z routerem.")
                        else:
                            print(f"Próba {attempt} nieudana.")
                    except Exception as e:
                        print(f"Błąd podczas próby ponownego połączenia: {e}")
                if not connected:
                    print("Nie udało się ponownie połączyć z routerem.")
                    return False
            return True
        except Exception as e:
            print(f"Błąd podczas zmiany adresu IP: {e}")
            return False

    def change_dns(self, new_dns):
        """
        Zmienia ustawienia DNS routera.
        """
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            if isinstance(new_dns, str):
                dns_servers = [new_dns]
            elif isinstance(new_dns, list):
                dns_servers = new_dns
            else:
                print("Nieprawidłowy format adresów DNS.")
                return False

            # Usunięcie istniejących serwerów DNS
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper delete system name-server'
            ]

            # Dodanie nowych serwerów DNS
            for dns in dns_servers:
                commands.append(f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set system name-server {dns}')

            commands.extend([
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ])

            for cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(cmd)
                exit_status = stdout.channel.recv_exit_status()
                error = stderr.read().decode().strip()
                if exit_status != 0:
                    print(f"Błąd podczas wykonywania '{cmd}': {error}")
                    return False
                time.sleep(1)
            print(f"Ustawienia DNS zostały zmienione na: {', '.join(dns_servers)}")
            return True
        except Exception as e:
            print(f"Błąd podczas zmiany ustawień DNS: {e}")
            return False

    def change_gateway(self, new_gateway):
        """
        Zmienia bramę domyślną routera.
        """
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            # Usunięcie istniejącej trasy domyślnej
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper delete protocols static route 0.0.0.0/0',
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set protocols static route 0.0.0.0/0 next-hop {new_gateway}',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ]

            for cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(cmd)
                exit_status = stdout.channel.recv_exit_status()
                error = stderr.read().decode().strip()
                if exit_status != 0 and "Nothing to delete" not in error:
                    print(f"Błąd podczas wykonywania '{cmd}': {error}")
                    return False
                time.sleep(1)
            print(f"Bramę domyślną ustawiono na {new_gateway}")
            return True
        except Exception as e:
            print(f"Błąd podczas zmiany bramy domyślnej: {e}")
            return False

    def disable_dhcp(self):
        """
        Wyłącza serwer DHCP na routerze.
        """
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper delete service dhcp-server',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ]

            for cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(cmd)
                exit_status = stdout.channel.recv_exit_status()
                error = stderr.read().decode().strip()
                if exit_status != 0 and "Nothing to delete" not in error:
                    print(f"Błąd podczas wykonywania '{cmd}': {error}")
                    return False
                time.sleep(1)
            print("Serwer DHCP został wyłączony.")
            return True
        except Exception as e:
            print(f"Błąd podczas wyłączania serwera DHCP: {e}")
            return False

    def get_interface_ips(self, interface_name):
        """
        Zwraca listę adresów IP przypisanych do interfejsu.
        """
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return []
        try:
            cmd = f"/opt/vyatta/bin/vyatta-op-cmd-wrapper show interfaces ethernet {interface_name} brief"
            stdin, stdout, stderr = self.client.exec_command(cmd)
            output = stdout.read().decode()
            ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)/\d+', output)
            return ips
        except Exception as e:
            print(f"Błąd podczas pobierania adresów IP interfejsu {interface_name}: {e}")
            return []

    def netmask_to_cidr(self, netmask):
        """
        Konwertuje maskę podsieci (np. 255.255.255.0) na notację CIDR (np. 24).
        """
        try:
            cidr = ipaddress.IPv4Network(f'0.0.0.0/{netmask}').prefixlen
            return str(cidr)
        except Exception as e:
            print(f"Błąd podczas konwersji maski podsieci: {e}")
            return None

    def enable_interface(self, interface_name):
        """
        Włącza interfejs.
        """
        return self._set_interface_disable_state(interface_name, disable=False)

    def disable_interface(self, interface_name):
        """
        Wyłącza interfejs.
        """
        return self._set_interface_disable_state(interface_name, disable=True)

    def _set_interface_disable_state(self, interface_name, disable):
        """
        Ustawia stan interfejsu (włączony/wyłączony).
        """
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            action = 'set' if disable else 'delete'
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper {action} interfaces ethernet {interface_name} disable',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ]

            for cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(cmd)
                exit_status = stdout.channel.recv_exit_status()
                error = stderr.read().decode().strip()
                if exit_status != 0 and "Nothing to delete" not in error and "Nothing to set" not in error:
                    print(f"Błąd podczas wykonywania '{cmd}': {error}")
                    return False
                time.sleep(1)

            state = "wyłączony" if disable else "włączony"
            print(f"Interfejs {interface_name} został {state}.")
            return True
        except Exception as e:
            print(f"Błąd podczas zmiany stanu interfejsu: {e}")
            return False

    def set_interface_description(self, interface_name, description):
        """
        Ustawia opis interfejsu.
        """
        if not self.client:
            print("Brak połączenia z urządzeniem.")
            return False
        try:
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set interfaces ethernet {interface_name} description "{description}"',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ]

            for cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(cmd)
                exit_status = stdout.channel.recv_exit_status()
                error = stderr.read().decode().strip()
                if exit_status != 0:
                    print(f"Błąd podczas wykonywania '{cmd}': {error}")
                    return False
                time.sleep(1)

            print(f"Opis interfejsu {interface_name} został ustawiony na '{description}'.")
            return True
        except Exception as e:
            print(f"Błąd podczas ustawiania opisu interfejsu: {e}")
            return False

    def restore_configuration(self, backup_file):
        """
        Przywraca konfigurację routera z podanego pliku kopii zapasowej.

        :param backup_file: Ścieżka do pliku z kopią zapasową konfiguracji
        """
        if not self.client or not self.client.get_transport() or not self.client.get_transport().is_active():
            print("Brak aktywnego połączenia z urządzeniem.")
            return False
        try:
            # Sprawdź, czy plik kopii zapasowej istnieje
            if not os.path.exists(backup_file):
                print(f"Plik kopii zapasowej '{backup_file}' nie istnieje.")
                return False

            # Prześlij plik na router (do katalogu /config)
            sftp = self.client.open_sftp()
            remote_backup_file = '/config/' + os.path.basename(backup_file)
            sftp.put(backup_file, remote_backup_file)
            sftp.close()

            # Przygotuj komendy do wczytania konfiguracji
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper load {remote_backup_file}',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ]

            # Wykonaj wszystkie komendy jako jedno polecenie
            full_cmd = '; '.join(commands)
            stdin, stdout, stderr = self.client.exec_command(full_cmd)

            # Odczytaj wyjście i błędy
            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                print(f"Błąd podczas przywracania konfiguracji: {error}")
                return False

            print("Konfiguracja została przywrócona z kopii zapasowej.")

            # Po przywróceniu konfiguracji adres IP routera zmienia się
            # Aktualizujemy adres IP w obiekcie
            old_ip = self.ip  # Zapamiętaj obecny adres IP
            self.ip = '192.168.55.50'  # Ustawiamy adres IP z kopii zapasowej

            # Rozłączamy obecne połączenie (które jest nieaktualne)
            self.disconnect()

            # Próba ponownego połączenia z routerem pod nowym adresem IP
            print("Próba ponownego połączenia z routerem po przywróceniu konfiguracji...")
            max_attempts = 10
            attempt = 0
            connected = False
            while attempt < max_attempts and not connected:
                attempt += 1
                try:
                    print(f"Próba {attempt} połączenia z {self.ip}...")
                    time.sleep(5)  # Czekamy 5 sekund przed każdą próbą
                    connected = self.connect()
                    if connected:
                        print("Ponownie połączono z routerem po przywróceniu konfiguracji.")
                    else:
                        print(f"Próba {attempt} nieudana.")
                except Exception as e:
                    print(f"Błąd podczas próby ponownego połączenia: {e}")
            if not connected:
                print("Nie udało się ponownie połączyć z routerem po przywróceniu konfiguracji.")
                return False

            return True
        except Exception as e:
            print(f"Błąd podczas przywracania konfiguracji: {e}")
            return False

    def backup_configuration(self, backup_file='router_backup.cfg'):
        """
        Tworzy kopię zapasową konfiguracji routera, pobierając plik /config/config.boot.

        :param backup_file: Nazwa pliku, do którego zostanie zapisana konfiguracja (domyślnie 'router_backup.cfg')
        """
        if not self.client or not self.client.get_transport() or not self.client.get_transport().is_active():
            print("Brak aktywnego połączenia z urządzeniem.")
            return False
        try:
            # Otwórz sesję SFTP
            sftp = self.client.open_sftp()
            remote_config_file = '/config/config.boot'
            # Pobierz plik z routera
            sftp.get(remote_config_file, backup_file)
            sftp.close()
            print(f"Kopia zapasowa konfiguracji została zapisana do pliku '{backup_file}'.")
            return True
        except Exception as e:
            print(f"Błąd podczas tworzenia kopii zapasowej: {e}")
            return False

    def create_vlan_interface(self, parent_interface, vlan_id, address=None, description=None):
        """
        Tworzy podinterfejs VLAN na podanym interfejsie fizycznym.

        :param parent_interface: Fizyczny interfejs, do którego zostanie dodany VLAN (np. 'eth1')
        :param vlan_id: ID VLAN-u (np. 100)
        :param address: Opcjonalny adres IP do przypisania do interfejsu VLAN (np. '192.168.100.1/24')
        :param description: Opcjonalny opis dla interfejsu VLAN
        """
        if not self.client or not self.client.get_transport() or not self.client.get_transport().is_active():
            print("Brak aktywnego połączenia z urządzeniem.")
            return False
        try:
            vlan_interface = f"{parent_interface}.{vlan_id}"
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set interfaces ethernet {vlan_interface}'
            ]
            if address:
                commands.append(
                    f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set interfaces ethernet {vlan_interface} address {address}')
            if description:
                commands.append(
                    f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set interfaces ethernet {vlan_interface} description "{description}"')
            commands.extend([
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ])

            full_cmd = '; '.join(commands)
            stdin, stdout, stderr = self.client.exec_command(full_cmd)
            # Opcjonalnie możesz sprawdzić wyjście lub błędy

            print(f"Utworzono interfejs VLAN: {vlan_interface}")
            return True
        except Exception as e:
            print(f"Błąd podczas tworzenia interfejsu VLAN: {e}")
            return False

    def delete_vlan_interface(self, parent_interface, vlan_id):
        """
        Usuwa podinterfejs VLAN z podanego interfejsu fizycznego.

        :param parent_interface: Fizyczny interfejs, z którego zostanie usunięty VLAN (np. 'eth1')
        :param vlan_id: ID VLAN-u do usunięcia (np. 100)
        """
        if not self.client or not self.client.get_transport() or not self.client.get_transport().is_active():
            print("Brak aktywnego połączenia z urządzeniem.")
            return False
        try:
            vlan_interface = f"{parent_interface}.{vlan_id}"
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper delete interfaces ethernet {vlan_interface}',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ]

            full_cmd = '; '.join(commands)
            stdin, stdout, stderr = self.client.exec_command(full_cmd)
            # Opcjonalnie możesz sprawdzić wyjście lub błędy

            print(f"Usunięto interfejs VLAN: {vlan_interface}")
            return True
        except Exception as e:
            print(f"Błąd podczas usuwania interfejsu VLAN: {e}")
            return False

    def delete_vlan_interface(self, parent_interface, vlan_id):
        """
        Usuwa podinterfejs VLAN z podanego interfejsu fizycznego.

        :param parent_interface: Fizyczny interfejs, z którego zostanie usunięty VLAN (np. 'eth1')
        :param vlan_id: ID VLAN-u do usunięcia (np. 100)
        """
        if not self.client or not self.client.get_transport() or not self.client.get_transport().is_active():
            print("Brak aktywnego połączenia z urządzeniem.")
            return False
        try:
            vlan_interface = f"{parent_interface}.{vlan_id}"
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper delete interfaces ethernet {vlan_interface}',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ]

            full_cmd = '; '.join(commands)
            stdin, stdout, stderr = self.client.exec_command(full_cmd)
            # Opcjonalnie możesz sprawdzić wyjście lub błędy

            print(f"Usunięto interfejs VLAN: {vlan_interface}")
            return True
        except Exception as e:
            print(f"Błąd podczas usuwania interfejsu VLAN: {e}")
            return False

    def configure_access_port(self, interface_name, vlan_id):
        """
        Konfiguruje interfejs jako port dostępu dla podanego VLAN-u.

        :param interface_name: Fizyczny interfejs do konfiguracji (np. 'eth2')
        :param vlan_id: ID VLAN-u do przypisania do interfejsu (np. 100)
        """
        if not self.client or not self.client.get_transport() or not self.client.get_transport().is_active():
            print("Brak aktywnego połączenia z urządzeniem.")
            return False
        try:
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                # Ustawienie trybu switcha
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set interfaces ethernet {interface_name} switch-port mode access',
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set interfaces ethernet {interface_name} switch-port access vlan {vlan_id}',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ]

            full_cmd = '; '.join(commands)
            stdin, stdout, stderr = self.client.exec_command(full_cmd)
            # Opcjonalnie możesz sprawdzić wyjście lub błędy

            print(f"Skonfigurowano interfejs {interface_name} jako port dostępu dla VLAN {vlan_id}")
            return True
        except Exception as e:
            print(f"Błąd podczas konfiguracji portu dostępu: {e}")
            return False

    def configure_trunk_port(self, interface_name, allowed_vlans):
        """
        Konfiguruje interfejs jako port trunk, obsługujący podane VLAN-y.

        :param interface_name: Fizyczny interfejs do konfiguracji (np. 'eth3')
        :param allowed_vlans: Lista ID VLAN-ów dozwolonych na trunku (np. [100, 200, 300])
        """
        if not self.client or not self.client.get_transport() or not self.client.get_transport().is_active():
            print("Brak aktywnego połączenia z urządzeniem.")
            return False
        try:
            vlan_list = ','.join(map(str, allowed_vlans))
            commands = [
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper begin',
                # Ustawienie trybu switcha
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set interfaces ethernet {interface_name} switch-port mode trunk',
                f'/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper set interfaces ethernet {interface_name} switch-port trunk allowed vlan {vlan_list}',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper commit',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper save',
                '/opt/vyatta/sbin/vyatta-cfg-cmd-wrapper end'
            ]

            full_cmd = '; '.join(commands)
            stdin, stdout, stderr = self.client.exec_command(full_cmd)
            # Opcjonalnie możesz sprawdzić wyjście lub błędy

            print(f"Skonfigurowano interfejs {interface_name} jako port trunk, dozwolone VLAN-y: {vlan_list}")
            return True
        except Exception as e:
            print(f"Błąd podczas konfiguracji portu trunk: {e}")
            return False
