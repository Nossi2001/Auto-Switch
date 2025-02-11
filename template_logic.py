# template_logic.py
import ipaddress
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.uic.properties import QtGui


class TemplateError(Exception):
    """Custom exception for template errors."""
    pass


def is_valid_ipv4(address):
    try:
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


def validate_color(c):
    """Validate if the color string is in #RRGGBB format."""
    if isinstance(c, str) and c.startswith('#') and len(c) == 7:
        try:
            int(c[1:], 16)
            return True
        except ValueError:
            return False
    return False


def assign_interface_labels(interfaces):
    """Assign labels to interfaces based on their type."""
    labeled_interfaces = []
    for iface_name in interfaces:
        if iface_name.startswith("FastEthernet"):
            iface_type = "Fa"
            iface_label = iface_name  # Używaj pełnej nazwy
        elif iface_name.startswith("GigabitEthernet"):
            iface_type = "Gi"
            iface_label = iface_name  # Używaj pełnej nazwy
        else:
            iface_type = "Fa"  # Default to FastEthernet if unknown
            iface_label = iface_name
        labeled_interfaces.append({
            "type": iface_type,
            "name": iface_name,
            "label": iface_label
        })
    return labeled_interfaces


def apply_data_template(params, selected_ports, used_vlans=None):
    if used_vlans is None:
        used_vlans = {}

    # Pobieranie i walidacja VLAN ID
    vlan_id = params.get("VLAN ID")
    if not vlan_id or not isinstance(vlan_id, int):
        raise TemplateError("VLAN ID jest wymagany i musi być liczbą całkowitą.")
    if vlan_id < 1 or vlan_id > 4094:
        raise TemplateError("VLAN ID musi być w zakresie 1-4094.")

    if vlan_id in used_vlans:
        raise TemplateError(f"VLAN ID {vlan_id} jest już w użyciu.")

    # Pobieranie nazwy profilu
    profile_name = params.get("Profile Name", "").strip()
    if not profile_name:
        raise TemplateError("Profile Name jest wymagane.")

    # Walidacja koloru
    color = params.get("Color", "").strip()
    if color and not validate_color(color):
        color = "#5F5F5F"
    elif not color:
        color = "#5F5F5F"

    # Pobieranie i walidacja parametrów routingu
    vlan_routing = params.get("VLAN Routing", False)
    vlan_mode = params.get("VLAN Mode", "Static")
    vlan_ip = params.get("VLAN IP Address", "").strip()
    subnet_mask = params.get("Subnet Mask", "").strip()

    if vlan_routing and vlan_mode == "Static":
        if not vlan_ip or not subnet_mask:
            raise TemplateError("Dla statycznego routingu VLAN wymagane są VLAN IP Address i Subnet Mask.")

    # Walidacja parametrów DHCP
    dhcp_server = params.get("DHCP Server", False)
    start = params.get("start", "").strip()
    stop = params.get("stop", "").strip()

    if dhcp_server:
        if not vlan_ip or not subnet_mask:
            raise TemplateError("Dla DHCP Server wymagane są VLAN IP Address i Subnet Mask.")
        if not start or not stop:
            raise TemplateError("Dla DHCP Server wymagane są parametry start i stop.")
        if not start.isdigit() or not stop.isdigit():
            raise TemplateError("Lease Time (start/stop) musi być liczbą całkowitą.")

    # Tworzenie konfiguracji VLAN
    lines = [
        "configure terminal",
        f"vlan {vlan_id}",
        f" name {profile_name}",
        "exit"
    ]

    # Tworzenie interfejsu VLAN
    lines.append(f"interface vlan {vlan_id}")
    if vlan_ip and subnet_mask:
        lines.append(f" ip address {vlan_ip} {subnet_mask}")
    else:
        lines.append(f" description VLAN{vlan_id} - no IP assigned")
    lines.append(" no shutdown")
    lines.append("exit")

    # Konfiguracja DHCP jeśli włączone
    if dhcp_server:
        try:
            network = ipaddress.IPv4Network(f"{vlan_ip}/{subnet_mask}", strict=False)
        except ValueError:
            raise TemplateError("Nieprawidłowy VLAN IP Address lub Subnet Mask.")

        lease_start = int(start)
        lease_stop = int(stop)
        lines.extend([
            f"ip dhcp pool {profile_name}_pool",
            f" network {network.network_address} {subnet_mask}",
            f" default-router {vlan_ip}",
            " dns-server 8.8.8.8",
            f" lease {lease_start} {lease_stop}",
            "exit"
        ])

    # Przypisanie VLAN do portów
    for p in selected_ports:
        lines.extend([
            f"interface {p}",
            f" description {profile_name} ({'Routing' if vlan_routing else 'DHCP' if dhcp_server else 'Access'})",
            " switchport mode access",
            f" switchport access vlan {vlan_id}",
            " no shutdown",
            "exit"
        ])

    # Wyjście z konfiguracji terminala
    lines.append("exit")

    # Aktualizacja używanych VLAN-ów
    used_vlans[vlan_id] = {
        'name': profile_name,
        'color': color,
        'description': f"VLAN {vlan_id}",
        'method': 'apply_data_template'
    }

    return "\n".join(lines)






def set_access_vlan(params, selected_ports, used_vlans=None):
    if not selected_ports:
        raise TemplateError("Nie wybrano interfejsów dla Access VLAN.")

    vlan_id = params.get("VLAN ID")
    if not vlan_id or not isinstance(vlan_id, int):
        raise TemplateError("Niepoprawny VLAN ID.")
    if vlan_id < 1 or vlan_id > 4094:
        raise TemplateError("VLAN ID musi być w zakresie 1-4094.")

    description = params.get("Description", "").strip()
    color = params.get("Color", "").strip()
    if not color or not validate_color(color):
        color = "#5F5F5F"

    if used_vlans is None:
        used_vlans = {}

    if vlan_id in used_vlans:
        raise TemplateError(f"VLAN ID {vlan_id} jest już w użyciu.")

    used_vlans[vlan_id] = {
        'name': f"VLAN {vlan_id}",
        'color': color,
        'description': description,
        'method': 'set_access_vlan'
    }

    lines = ["configure terminal",
             f"vlan {vlan_id}",
             f" name VLAN_{vlan_id}",
             "exit"]

    for port in selected_ports:
        lines.append(f"interface {port}")
        if description:
            lines.append(f" description {description}")
        lines.append(" switchport mode access")
        lines.append(f" switchport access vlan {vlan_id}")
        lines.append(" no shutdown")
        lines.append("exit")


    return "\n".join(lines)


def set_trunk_vlan(params, selected_ports, used_vlans=None):
    if not selected_ports:
        raise TemplateError("Nie wybrano interfejsów dla Trunk VLAN.")

    allowed_vlans_str = params.get("Allowed VLANs", "").strip()
    description = params.get("Description", "").strip()

    if not allowed_vlans_str:
        raise TemplateError("Allowed VLANs jest wymagane (np. 10,20,30).")

    # Sprawdzenie poprawności VLANów
    allowed_vlans = [v.strip() for v in allowed_vlans_str.split(',') if v.strip().isdigit()]
    if not allowed_vlans:
        raise TemplateError("Brak poprawnych VLANów w Allowed VLANs.")

    allowed_vlans_out = ",".join(allowed_vlans)

    if used_vlans is None:
        used_vlans = {}

    # Sprawdzenie, czy wszystkie VLANy są już utworzone
    for vid_str in allowed_vlans:
        vid = int(vid_str)
        if vid not in used_vlans:
            raise TemplateError(f"VLAN ID {vid} nie istnieje. Utwórz VLAN przed przypisaniem do trunku.")

    lines = ["configure terminal"]

    for port in selected_ports:
        lines.append(f"interface {port}")
        if description:
            lines.append(f" description {description}")
        lines.append(" switchport trunk encapsulation dot1q")
        lines.append(" switchport mode trunk")
        lines.append(f" switchport trunk allowed vlan {allowed_vlans_out}")
        lines.append(" no shutdown")
        lines.append("exit")
        lines.append("ip routing")


    return "\n".join(lines)


def set_native_vlan(params, selected_ports, used_vlans=None):
    """
    Konfiguruje Native VLAN na wybranych interfejsach trunk.

    Parameters:
        params (dict): Parametry zawierające ID Native VLAN, opis, kolor i allowed VLANs.
        selected_ports (list): Lista wybranych interfejsów.
        used_vlans (dict, optional): Słownik VLAN-ów używanych w konfiguracji.
    Returns:
        str: Wygenerowana konfiguracja CLI.
    """
    if not selected_ports:
        raise TemplateError("Nie wybrano interfejsów dla Native VLAN.")

    native_vlan = params.get("Native VLAN ID")
    if not native_vlan or not isinstance(native_vlan, int):
        raise TemplateError("Niepoprawny Native VLAN ID.")
    if native_vlan < 1 or native_vlan > 4094:
        raise TemplateError("Native VLAN ID musi być w zakresie 1-4094.")

    description = params.get("Description", "").strip()
    color = params.get("Color", "").strip()
    if not color or not validate_color(color):
        color = "#5F5F5F"

    # Pobierz allowed VLANs z parametrów
    allowed_vlans = params.get("Allowed VLANs", "").strip()
    if allowed_vlans:
        # Walidacja listy VLANs
        try:
            vlan_list = [int(v.strip()) for v in allowed_vlans.split(",") if v.strip().isdigit()]
            if any(v < 1 or v > 4094 for v in vlan_list):
                raise ValueError
        except ValueError:
            raise TemplateError("Lista Allowed VLANs zawiera nieprawidłowe wartości.")
        allowed_vlans = ",".join(map(str, vlan_list))  # Konwersja na poprawny format CLI

    if used_vlans is None:
        used_vlans = {}

    if native_vlan in used_vlans:
        raise TemplateError(f"VLAN ID {native_vlan} jest już w użyciu.")

    used_vlans[native_vlan] = {
        'name': f"VLAN {native_vlan}",
        'color': color,
        'description': description,
        'method': 'set_native_vlan'
    }

    # Generowanie konfiguracji CLI
    lines = ["configure terminal",
             f"vlan {native_vlan}",
             f" name VLAN_{native_vlan}",
             "exit"]

    for port in selected_ports:
        lines.append(f"interface {port}")
        if description:
            lines.append(f" description {description}")
        lines.append(" switchport mode trunk")
        lines.append(f" switchport trunk native vlan {native_vlan}")
        if allowed_vlans:
            lines.append(f" switchport trunk allowed vlan {allowed_vlans}")
        lines.append(" no shutdown")
        lines.append("exit")


    return "\n".join(lines)


def apply_nat(params, selected_ports):
    # Pobieramy parametry:
    role = params.get("Interface Role", "").strip()  # "Inside" lub "Outside"
    pool_name = params.get("Pool Name", "").strip()
    pool_start = params.get("Pool Start IP", "").strip()
    pool_end = params.get("Pool End IP", "").strip()
    acl = params.get("Access List", "").strip()
    netmask = params.get("Netmask", "255.255.255.0").strip()

    # Walidacja podstawowa
    if role not in ("Inside", "Outside"):
        raise TemplateError("Musisz wybrać rolę interfejsu: Inside lub Outside.")
    if not pool_name or not pool_start or not pool_end or not acl:
        raise TemplateError("Pool Name, Pool Start IP, Pool End IP i Access List są wymagane.")
    if not selected_ports:
        raise TemplateError("Wybierz co najmniej jeden port.")

    lines = ["configure terminal"]

    # Konfiguracja ACL i NAT Pool
    # Zakładamy, że niezależnie od Inside/Outside zawsze konfigurujemy pool i ACL
    lines.append(f"access-list {acl} permit ip any any")
    lines.append(f"ip nat pool {pool_name} {pool_start} {pool_end} netmask {netmask}")
    lines.append(f"ip nat inside source list {acl} pool {pool_name} overload")

    # Interfejsy
    for iface in selected_ports:
        lines.append(f"interface {iface}")
        if role == "Inside":
            lines.append(" ip nat inside")
        else:  # Outside
            lines.append(" ip nat outside")
        lines.append(" no shutdown")
        lines.append("exit")


    return "\n".join(lines)


def apply_static_routing(params, selected_ports):
    """
    Apply static routing configuration based on the provided parameters.

    Parameters:
        params (dict): Dictionary containing configuration parameters.
            - "Destination Network": Destination network address (e.g., "192.168.2.0")
            - "Subnet Mask": Subnet mask for the destination network (e.g., "255.255.255.0")
            - "Next Hop IP": IP address of the next hop router (e.g., "203.0.113.1")
        selected_ports (list): List of interface names to apply the static routing (optional, can be empty).

    Returns:
        str: Generated static routing configuration commands.
    """
    destination_network = params.get("Destination Network", "").strip()
    subnet_mask = params.get("Subnet Mask", "").strip()
    next_hop_ip = params.get("Next Hop IP", "").strip()

    # Basic validation
    if not destination_network:
        raise TemplateError("Destination Network jest wymagany.")
    if not subnet_mask:
        raise TemplateError("Subnet Mask jest wymagany.")
    if not next_hop_ip:
        raise TemplateError("Next Hop IP jest wymagany.")

    # Validate IP formats
    try:
        ipaddress.IPv4Address(destination_network)
    except ipaddress.AddressValueError:
        raise TemplateError(f"Destination Network '{destination_network}' jest niepoprawnym adresem IP.")

    try:
        ipaddress.IPv4Address(subnet_mask)
    except ipaddress.AddressValueError:
        raise TemplateError(f"Subnet Mask '{subnet_mask}' jest niepoprawnym adresem IP.")

    try:
        ipaddress.IPv4Address(next_hop_ip)
    except ipaddress.AddressValueError:
        raise TemplateError(f"Next Hop IP '{next_hop_ip}' jest niepoprawnym adresem IP.")

    # Validate network
    try:
        network = ipaddress.IPv4Network(f"{destination_network}/{subnet_mask}", strict=False)
    except ipaddress.NetmaskValueError:
        raise TemplateError(f"Subnet Mask '{subnet_mask}' jest niepoprawną maską podsieci.")

    lines = ["configure terminal"]

    # Add static route
    lines.append(f"ip route {destination_network} {subnet_mask} {next_hop_ip}")


    return "\n".join(lines)


def apply_dynamic_routing(params, selected_ports):
    """
    Apply dynamic routing configuration based on the provided parameters.

    Parameters:
        params (dict): Dictionary containing configuration parameters.
            - "Routing Protocol": Routing protocol to use (e.g., "OSPF", "EIGRP")
            - "Process ID": Process ID for the routing protocol
            - "Area ID": Area ID for OSPF (ignored for EIGRP)
            - "Network 1": First network to advertise
            - "Netmask 1": Netmask for first network
            - "Network 2": Second network to advertise (optional)
            - "Netmask 2": Netmask for second network (optional)
            - "Network 3": Third network to advertise (optional)
            - "Netmask 3": Netmask for third network (optional)
            - "Network 4": Fourth network to advertise (optional)
            - "Netmask 4": Netmask for fourth network (optional)
        selected_ports (list): List of interface names to apply the dynamic routing.

    Returns:
        str: Generated dynamic routing configuration commands.
    """
    routing_protocol = params.get("Routing Protocol", "").strip().upper()
    process_id = params.get("Process ID", "")
    area_id = params.get("Area ID", "")

    # Basic validation
    if not routing_protocol:
        raise TemplateError("Routing Protocol jest wymagany.")
    if not process_id:
        raise TemplateError("Process ID jest wymagany.")

    # Validate Routing Protocol
    if routing_protocol not in ("OSPF", "EIGRP"):
        raise TemplateError("Routing Protocol musi być 'OSPF' lub 'EIGRP'.")

    # Validate Process ID
    process_id_int = int(process_id)
    if not (1 <= process_id_int <= 65535):
        raise TemplateError("Process ID musi być w zakresie 1-65535.")

    # Validate Area ID for OSPF
    if routing_protocol == "OSPF":
        if not area_id:
            area_id = 0
        area_id_int = int(area_id)
        if not (0 <= area_id_int <= 65535):
            raise TemplateError("Area ID dla OSPF musi być w zakresie 0-65535.")

    # Collect and validate networks
    validated_networks = []
    for i in range(1, 5):  # Check all 4 possible network fields
        network = params.get(f"Network {i}", "").strip()
        netmask = params.get(f"Netmask {i}", "").strip()

        if network and netmask:  # Only process when both network and netmask are provided
            try:
                # Validate network address
                network_addr = ipaddress.IPv4Address(network)
                # Validate netmask
                netmask_addr = ipaddress.IPv4Address(netmask)
                # Calculate wildcard mask correctly
                netmask_octets = [int(octet) for octet in netmask.split('.')]
                wildcard_octets = [str(255 - octet) for octet in netmask_octets]
                wildcard_mask = '.'.join(wildcard_octets)
                validated_networks.append(f"network {network} {wildcard_mask}")
            except (ipaddress.AddressValueError, ValueError):
                raise TemplateError(f"Network '{network}' lub Netmask '{netmask}' jest niepoprawny.")

    if not validated_networks:
        raise TemplateError("Co najmniej jedna sieć z maską musi być skonfigurowana.")

    lines = ["configure terminal"]

    if routing_protocol == "OSPF":
        lines.append(f"router ospf {process_id}")
        lines.extend(validated_networks)
    elif routing_protocol == "EIGRP":
        lines.append(f"router eigrp {process_id}")
        lines.extend(validated_networks)


    return "\n".join(lines)


def apply_dhcp_server(params, selected_ports):
    """Generuje konfigurację DHCP Server na wybranych portach."""
    # Pobieramy parametry:
    pool_name = params.get("Pool Name", "").strip()
    network = params.get("Network", "").strip()
    subnet_mask = params.get("Subnet Mask", "").strip()
    default_router = params.get("Default Router", "").strip()
    dns_server = params.get("DNS Server", "").strip()
    lease_time = params.get("Lease Time", "")

    # Walidacja podstawowa
    if not pool_name:
        raise TemplateError("Pool Name jest wymagane.")
    if not network:
        raise TemplateError("Network jest wymagane.")
    if not subnet_mask:
        raise TemplateError("Subnet Mask jest wymagana.")
    if not default_router:
        raise TemplateError("Default Router jest wymagany.")
    # walidacja ip
    if not is_valid_ipv4(network):
        raise TemplateError("Network nie jest ip")
    if not is_valid_ipv4(subnet_mask):
        raise TemplateError("subnet_mask nie jest ip")
    if not is_valid_ipv4(default_router):
        raise TemplateError("default_router nie jest ip")
    if lease_time:
        lease_time_value = int(lease_time)
        if lease_time_value <= 0:
            raise TemplateError("Lease Time musi być większy od zera.")

    lines = [
        "configure terminal",
        f"ip dhcp excluded-address {default_router}",
        f"ip dhcp pool {pool_name}",
        f" network {network} {subnet_mask}",
        f" default-router {default_router}"
    ]

    if dns_server:
        lines.append(f" dns-server {dns_server}")
    # if lease_time:
    #     lines.append(f" lease {lease_time}")

    lines.append("exit")

    # Opcjonalnie, dodajemy opisy do interfejsów
    for port in selected_ports:
        lines.append(f"interface {port}")
        lines.append(f" description DHCP Server: {default_router}")
        lines.append(f" ip add {default_router} {subnet_mask}")
        lines.append(" no shutdown")
        lines.append("exit")

    return "\n".join(lines)


def restart_device(params, selected_ports):
    used_vlans = {}
    lines = [
        "!Imoportant blank line"
        "write erase",
        " ",
        "erase startup-config",
        " ",
        "reload",
        "yes ",
        " "
    ]
    return "\n".join(lines)


def update_firmware(params, selected_ports):
    """
    Update the firmware of the device.

    Parameters:
        params (dict): Dictionary containing configuration parameters.
            - "Firmware Server IP": IP address of the firmware server
            - "Firmware Image Name": Name of the firmware image file
        selected_ports (list): List of interface names to use for firmware update (e.g., management interface).

    Returns:
        str: Generated firmware update configuration commands.
    """
    firmware_server_ip = params.get("Firmware Server IP", "").strip()
    firmware_image = params.get("Firmware Image Name", "").strip()

    if not firmware_server_ip or not firmware_image:
        raise TemplateError("Firmware Server IP oraz Firmware Image Name są wymagane.")

    # Sprawdzenie poprawności IP
    try:
        ipaddress.IPv4Address(firmware_server_ip)
    except ipaddress.AddressValueError:
        raise TemplateError("Firmware Server IP jest niepoprawnym adresem IP.")

    if not selected_ports:
        raise TemplateError("Wybierz interfejs do użycia podczas aktualizacji firmware.")

    # Zakładamy, że wybrany port jest interfejsem zarządzającym, np. GigabitEthernet0/1
    # Generujemy polecenie kopiowania firmware z TFTP na urządzenie
    interface = selected_ports[0]  # Używamy pierwszego zaznaczonego interfejsu

    lines = [
        "configure terminal",
        f"interface {interface}",
        " no shutdown",
        " exit",
        f"copy tftp://{firmware_server_ip}/{firmware_image} flash:",
        "end"
    ]

    return "\n".join(lines)


def enable_vlan(params, selected_ports):
    """
    Enable and configure a VLAN on the switch, and assign selected ports to it.

    Parameters:
        params (dict): Dictionary containing configuration parameters.
            - "VLAN ID": ID of the VLAN (1-4094)
            - "VLAN Name": Name of the VLAN
        selected_ports (list): List of interface names to assign to the VLAN.

    Returns:
        str: Generated VLAN configuration commands.
    """
    vlan_id = params.get("VLAN ID")
    vlan_name = params.get("VLAN Name", "").strip()

    # Walidacja VLAN ID
    if not vlan_id or not isinstance(vlan_id, int):
        raise TemplateError("VLAN ID jest wymagany i musi być liczbą całkowitą.")
    if vlan_id < 1 or vlan_id > 4094:
        raise TemplateError("VLAN ID musi być w zakresie 1-4094.")

    if not vlan_name:
        raise TemplateError("VLAN Name jest wymagane.")

    if not selected_ports:
        raise TemplateError("Wybierz co najmniej jeden port do przypisania do VLAN.")

    lines = ["configure terminal"]

    # Tworzenie VLAN
    lines.append(f"vlan {vlan_id}")
    lines.append(f" name {vlan_name}")
    lines.append("exit")

    # Przypisywanie VLAN do portów
    for iface in selected_ports:
        lines.append(f"interface {iface}")
        lines.append(" switchport mode access")
        lines.append(f" switchport access vlan {vlan_id}")
        lines.append(" no shutdown")
        lines.append("exit")


    return "\n".join(lines)


def default_interface(params, selected_ports):
    """
    Reset the specified interfaces to their default configurations.

    Parameters:
        params (dict): Dictionary containing configuration parameters.
            - (No additional parameters required)
        selected_ports (list): List of interface names to reset.

    Returns:
        str: Generated commands to reset interfaces to default.
    """
    if not selected_ports:
        raise TemplateError("Wybierz co najmniej jeden interfejs do zresetowania.")

    lines = ["configure terminal"]

    for iface in selected_ports:
        lines.append(f"default interface {iface}")
        lines.append("exit")

    return "\n".join(lines)


TEMPLATE_FUNCTIONS = {
    'apply_data_template': apply_data_template,
    'set_access_vlan': set_access_vlan,
    'set_trunk_vlan': set_trunk_vlan,
    'set_native_vlan': set_native_vlan,
    'apply_nat': apply_nat,
    'apply_static_routing': apply_static_routing,
    'apply_dynamic_routing': apply_dynamic_routing,
    'apply_dhcp_server': apply_dhcp_server,
    'restart_device': restart_device,
    'update_firmware': update_firmware,

    'enable_vlan': enable_vlan,
    'default_interface': default_interface
}
