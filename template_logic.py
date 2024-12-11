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

    vlan_id = params.get("VLAN ID")
    if not vlan_id or not isinstance(vlan_id, int):
        raise TemplateError("VLAN ID jest wymagany i musi być liczbą.")
    if vlan_id < 1 or vlan_id > 4094:
        raise TemplateError("VLAN ID musi być w zakresie 1-4094.")

    if vlan_id in used_vlans:
        raise TemplateError(f"VLAN ID {vlan_id} jest już w użyciu.")

    profile_name = params.get("Profile Name", "").strip()
    if not profile_name:
        raise TemplateError("Profile Name jest wymagane.")

    color = params.get("Color", "").strip()
    if color and not validate_color(color):
        color = "#5F5F5F"
    elif not color:
        color = "#5F5F5F"

    vlan_routing = params.get("VLAN Routing", False)
    vlan_mode = params.get("VLAN Mode", "Static")
    vlan_ip = params.get("VLAN IP Address", "").strip()
    subnet_mask = params.get("Subnet Mask", "").strip()
    dhcp_server = params.get("DHCP Server", False)
    start = params.get("start", "").strip()
    stop = params.get("stop", "").strip()

    # Budowa konfiguracji VLAN
    lines = ["configure terminal",
             f"vlan {vlan_id}",
             f" name {profile_name}",
             "exit"]

    # Routing VLAN jeśli wymagany i statyczny
    if vlan_routing and vlan_mode == "Static":
        if not vlan_ip or not subnet_mask:
            raise TemplateError("Dla statycznego routingu VLAN wymagane są VLAN IP Address i Subnet Mask.")
        lines.append(f"interface vlan {vlan_id}")
        lines.append(f" ip address {vlan_ip} {subnet_mask}")
        lines.append(" no shutdown")
        lines.append("exit")

    # DHCP jeśli zaznaczono
    if dhcp_server:
        if not vlan_ip or not subnet_mask:
            raise TemplateError("Dla DHCP Server wymagane są VLAN IP Address i Subnet Mask.")
        if not start or not stop:
            raise TemplateError("Dla DHCP Server wymagane są parametry start i stop.")
        if not start.isdigit() or not stop.isdigit():
            raise TemplateError("Lease Time (start/stop) musi być liczbą całkowitą.")
        lease_start = int(start)
        lease_stop = int(stop)
        lines.append(f"ip dhcp pool {profile_name}_pool")
        lines.append(f" network {vlan_ip} {subnet_mask}")
        lines.append(f" default-router {vlan_ip}")
        lines.append(" dns-server 8.8.8.8")
        lines.append(f" lease {lease_start} {lease_stop}")
        lines.append("exit")

    # Przypisanie VLAN do portów
    for p in selected_ports:
        lines.append(f"interface {p}")
        if vlan_routing:
            lines.append(f" description {profile_name} (Routing)")
        elif dhcp_server:
            lines.append(f" description {profile_name} (DHCP)")
        else:
            lines.append(f" description {profile_name}")
        lines.append(" switchport mode access")
        lines.append(f" switchport access vlan {vlan_id}")
        lines.append(" no shutdown")
        lines.append("exit")

    lines.append("end")

    # Zapis do used_vlans
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

    lines.append("end")

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

    # Sprawdzenie, czy którykolwiek z VLANów jest już używany
    for vid_str in allowed_vlans:
        vid = int(vid_str)
        if vid in used_vlans:
            raise TemplateError(f"VLAN ID {vid} jest już w użyciu.")

    # Wybieramy pierwszy VLAN do koloru
    first_vlan_id = int(allowed_vlans[0])
    if used_vlans is None:
        used_vlans = {}

    color = "#5F5F5F"  # Domyślny kolor

    used_vlans[first_vlan_id] = {
        'name': f"VLAN {first_vlan_id}",
        'color': color,
        'description': description,
        'method': 'set_trunk_vlan'
    }

    lines = ["configure terminal"]

    # Upewnienie się, że VLANy istnieją
    for vid_str in allowed_vlans:
        vid = int(vid_str)
        lines.append(f"vlan {vid}")
        lines.append(f" name VLAN_{vid}")
        lines.append("exit")

    for port in selected_ports:
        lines.append(f"interface {port}")
        if description:
            lines.append(f" description {description}")
        lines.append(" switchport mode trunk")
        lines.append(f" switchport trunk allowed vlan {allowed_vlans_out}")
        lines.append(" no shutdown")
        lines.append("exit")

    lines.append("end")

    return "\n".join(lines)


def set_native_vlan(params, selected_ports, used_vlans=None):
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
        lines.append(" no shutdown")
        lines.append("exit")

    lines.append("end")

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

    lines.append("end")

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

    lines.append("end")

    return "\n".join(lines)


def apply_dynamic_routing(params, selected_ports):
    """
    Apply dynamic routing configuration based on the provided parameters.

    Parameters:
        params (dict): Dictionary containing configuration parameters.
            - "Routing Protocol": Routing protocol to use (e.g., "OSPF", "EIGRP")
            - "Process ID": Process ID for the routing protocol (e.g., "1" for OSPF, "100" for EIGRP)
            - "Area ID": Area ID for OSPF (ignored for EIGRP)
            - "Networks": Networks to advertise (comma-separated, e.g., "192.168.1.0 0.0.0.255,10.0.0.0 0.255.255.255")
        selected_ports (list): List of interface names to apply the dynamic routing (optional, can be empty).

    Returns:
        str: Generated dynamic routing configuration commands.
    """
    routing_protocol = params.get("Routing Protocol", "").strip().upper()
    process_id = params.get("Process ID", "").strip()
    area_id = params.get("Area ID", "").strip()
    networks = params.get("Networks", "").strip()

    # Basic validation
    if not routing_protocol:
        raise TemplateError("Routing Protocol jest wymagany.")
    if not process_id:
        raise TemplateError("Process ID jest wymagany.")
    if not networks:
        raise TemplateError("Networks są wymagane.")

    # Validate Routing Protocol
    if routing_protocol not in ("OSPF", "EIGRP"):
        raise TemplateError("Routing Protocol musi być 'OSPF' lub 'EIGRP'.")

    # Validate Process ID
    if not process_id.isdigit():
        raise TemplateError("Process ID musi być liczbą całkowitą.")
    process_id_int = int(process_id)
    if not (1 <= process_id_int <= 65535):
        raise TemplateError("Process ID musi być w zakresie 1-65535.")

    # Validate Area ID for OSPF
    if routing_protocol == "OSPF":
        if not area_id:
            raise TemplateError("Area ID jest wymagane dla OSPF.")
        if not area_id.isdigit():
            raise TemplateError("Area ID dla OSPF musi być liczbą całkowitą.")
        area_id_int = int(area_id)
        if not (0 <= area_id_int <= 65535):
            raise TemplateError("Area ID dla OSPF musi być w zakresie 0-65535.")

    # Validate Networks
    network_entries = [n.strip() for n in networks.split(",") if n.strip()]
    if not network_entries:
        raise TemplateError("Podano niepoprawne Networks.")

    validated_networks = []
    for entry in network_entries:
        parts = entry.split()
        if len(parts) != 2:
            raise TemplateError(f"Network entry '{entry}' jest niepoprawny. Powinien mieć format 'Network Wildcard'.")
        network, wildcard = parts
        try:
            ipaddress.IPv4Network(f"{network}/{wildcard}", strict=False)
            validated_networks.append(f"network {network} {wildcard}")
        except ipaddress.NetmaskValueError:
            raise TemplateError(f"Network '{network} {wildcard}' jest niepoprawny.")

    lines = ["configure terminal"]

    if routing_protocol == "OSPF":
        lines.append(f"router ospf {process_id}")
        lines.append(f" area {area_id} stub")  # Example configuration
        lines.extend(validated_networks)
    elif routing_protocol == "EIGRP":
        lines.append(f"router eigrp {process_id}")
        lines.append(" network 0.0.0.0 255.255.255.255")  # Example configuration
        lines.extend(validated_networks)

    lines.append("end")

    return "\n".join(lines)

def apply_dhcp_server(params, selected_ports):
    """Generuje konfigurację DHCP Server na wybranych portach."""
    # Pobieramy parametry:
    pool_name = params.get("Pool Name", "").strip()
    network = params.get("Network", "").strip()
    subnet_mask = params.get("Subnet Mask", "").strip()
    default_router = params.get("Default Router", "").strip()
    dns_server = params.get("DNS Server", "").strip()
    lease_time = params.get("Lease Time", "").strip()

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
        f"ip dhcp pool {pool_name}",
        f" network {network} {subnet_mask}",
        f" default-router {default_router}"
    ]

    if dns_server:
        lines.append(f" dns-server {dns_server}")
    if lease_time:
        lines.append(f" lease {lease_time}")

    lines.append("exit")

    # Opcjonalnie, dodajemy opisy do interfejsów
    for port in selected_ports:
        lines.append(f"interface {port}")
        lines.append(f" description DHCP Server: {pool_name}")
        lines.append(" no shutdown")
        lines.append("exit")

    lines.append("end")

    return "\n".join(lines)


def restart_router(params, selected_ports):
    lines = [
        "write erase",
        "erase startup-config",
        "reload"
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

    lines.append("end")

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
        lines.append(f"interface {iface}")
        lines.append(" default switchport")
        lines.append(" no shutdown")
        lines.append("exit")

    lines.append("end")

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
    'restart_router': restart_router,
    'update_firmware': update_firmware,

    'enable_vlan': enable_vlan,

    'default_interface': default_interface
}
