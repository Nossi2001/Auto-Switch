# template_logic.py

class TemplateError(Exception):
    pass

def validate_color(c):
    if isinstance(c, str) and c.startswith('#') and len(c) == 7:
        try:
            int(c[1:], 16)
            return True
        except ValueError:
            return False
    return False

def assign_interface_labels(interfaces):
    """
    Jeśli chcesz użyć MAC adresów do sortowania, możesz dodać klucze "mac" do interfejsów.
    W tym przykładzie zakładamy, że interfejsy są już w pełni nazwane i nie wymagają sortowania.
    Jeżeli chcesz użyć sortowania wg MAC, dodaj to i klucze do interfejsów.
    Tutaj zakładamy, że interfejsy są już gotowe do użycia.
    """
    # Jeśli nie potrzebujesz zmian, możesz zwrócić interfejsy w postaci przykładowej struktury:
    labeled_interfaces = []
    # Przykład: sprawdzanie typu na podstawie nazwy
    for iface_name in interfaces:
        if iface_name.startswith("FastEthernet"):
            iface_type = "FastEthernet"
        elif iface_name.startswith("GigabitEthernet"):
            iface_type = "GigabitEthernet"
        elif iface_name.startswith("TenGigabitEthernet"):
            iface_type = "TenGigabitEthernet"
        else:
            iface_type = "FastEthernet"  # domyślnie
        labeled_interfaces.append({
            "type": iface_type,
            "name": iface_name,
            "label": iface_name  # Skoro mamy pełne nazwy, label może być taki sam jak name
        })
    return labeled_interfaces

def apply_data_template(params, selected_ports, used_vlans_ids=None, used_vlans_names=None):
    if used_vlans_ids is None:
        used_vlans_ids = set()
    if used_vlans_names is None:
        used_vlans_names = set()

    vlan_id = params.get("VLAN ID")
    pn = params.get("Profile Name", "").strip()
    color = params.get("Color", "").strip()
    vr = params.get("VLAN Routing", False)
    vs = params.get("VLAN Setting", "")
    vi = params.get("VLAN IP Address", "").strip()
    sm = params.get("Subnet Mask", "").strip()
    ds = params.get("DHCP Server", False)
    st = params.get("start", "").strip()
    sp = params.get("stop", "").strip()

    if not vlan_id or not isinstance(vlan_id, int):
        raise TemplateError("Invalid VLAN ID")
    if vlan_id < 1 or vlan_id > 1024:
        raise TemplateError("VLAN ID out of range")
    if vlan_id in used_vlans_ids:
        raise TemplateError("VLAN ID used")
    if not pn:
        raise TemplateError("Profile Name required")
    if pn in used_vlans_names:
        raise TemplateError("VLAN Name used")
    if vr:
        if vs not in ("Static", "Dynamic"):
            raise TemplateError("Invalid VLAN Setting")
        if vs == "Static" and (not vi or not sm):
            raise TemplateError("VLAN IP and Subnet required")
    if ds:
        if not st or not sp:
            raise TemplateError("DHCP start/stop required")
    if color and not validate_color(color):
        raise TemplateError("Invalid color")

    lines = []
    lines.append("configure terminal")
    lines.append(f"vlan {vlan_id}")
    lines.append(f" name {pn}")
    if vr and vs == "Static":
        lines.append(f"interface vlan {vlan_id}")
        lines.append(f" ip address {vi} {sm}")
    if ds:
        lines.append(f"ip dhcp pool {pn}_pool")
        lines.append(f" network {vi} {sm}")
        lines.append(f" default-router {vi}")
        lines.append(" dns-server 8.8.8.8")
        lines.append(f" lease {st} {sp}")
    for p in selected_ports:
        lines.append(f"interface {p}")
        lines.append(f" description VLAN {vlan_id}")
        lines.append(" no shutdown")
    lines.append("end")
    return "\n".join(lines)

def apply_static_routing(params, selected_ports):
    dn = params.get("Destination Network", "").strip()
    sm = params.get("Subnet Mask", "").strip()
    nh = params.get("Next Hop IP", "").strip()
    if not dn or not sm or not nh:
        raise TemplateError("Missing static route parameters")
    lines = []
    lines.append("configure terminal")
    lines.append(f"ip route {dn} {sm} {nh}")
    lines.append("end")
    return "\n".join(lines)

def apply_dynamic_routing(params, selected_ports):
    protocol = params.get("Routing Protocol", "").strip()
    pid = params.get("Process ID", "")
    area = params.get("Area ID", "")
    if protocol not in ("OSPF", "EIGRP"):
        raise TemplateError("Invalid protocol")
    if not pid:
        raise TemplateError("Missing process ID")
    if protocol == "OSPF" and not area:
        raise TemplateError("Missing area ID")
    lines = []
    lines.append("configure terminal")
    if protocol == "OSPF":
        lines.append(f"router ospf {pid}")
        lines.append(f" network 0.0.0.0 255.255.255.255 area {area}")
    else:
        lines.append(f"router eigrp {pid}")
        lines.append(" network 0.0.0.0")
    lines.append("end")
    return "\n".join(lines)

def apply_nat(params, selected_ports):
    iif = params.get("Inside Interface", "").strip()
    oif = params.get("Outside Interface", "").strip()
    pn = params.get("Pool Name", "").strip()
    ps = params.get("Pool Start IP", "").strip()
    pe = params.get("Pool End IP", "").strip()
    acl = params.get("Access List", "").strip()
    if not iif or not oif or not pn or not ps or not pe or not acl:
        raise TemplateError("Missing NAT parameters")
    lines = []
    lines.append("configure terminal")
    lines.append(f"access-list {acl} permit ip any any")
    lines.append(f"ip nat inside source list {acl} pool {pn} overload")
    lines.append(f"ip nat pool {pn} {ps} {pe} netmask 255.255.255.0")
    lines.append(f"interface {iif}")
    lines.append(" ip nat inside")
    lines.append(f"interface {oif}")
    lines.append(" ip nat outside")
    lines.append("end")
    return "\n".join(lines)

def apply_dhcp_server(params, selected_ports):
    pname = params.get("Pool Name", "").strip()
    nw = params.get("Network", "").strip()
    sm = params.get("Subnet Mask", "").strip()
    dr = params.get("Default Router", "").strip()
    dns = params.get("DNS Server", "").strip()
    lt = params.get("Lease Time", "").strip()
    if not pname or not nw or not sm or not dr or not dns or not lt:
        raise TemplateError("Missing DHCP server parameters")
    lines = []
    lines.append("configure terminal")
    lines.append(f"ip dhcp pool {pname}")
    lines.append(f" network {nw} {sm}")
    lines.append(f" default-router {dr}")
    lines.append(f" dns-server {dns}")
    lines.append(f" lease {lt}")
    lines.append("end")
    return "\n".join(lines)

def apply_config(params, selected_ports):
    lines = []
    lines.append("configure terminal")
    for p in selected_ports:
        lines.append(f"interface {p}")
        lines.append(" description configured")
        lines.append(" no shutdown")
    lines.append("end")
    return "\n".join(lines)

def restart_router(params, selected_ports):
    lines = []
    lines.append("reload")
    return "\n".join(lines)

def update_firmware(params, selected_ports):
    fw = params.get("Firmware URL", "").strip()
    if not fw:
        raise TemplateError("No firmware URL")
    lines = []
    lines.append("configure terminal")
    lines.append(f"! download firmware from {fw}")
    lines.append("end")
    return "\n".join(lines)

def backup_config(params, selected_ports):
    lines = []
    lines.append("copy running-config startup-config")
    return "\n".join(lines)

def monitor_traffic(params, selected_ports):
    lines = []
    lines.append("configure terminal")
    for p in selected_ports:
        lines.append(f"interface {p}")
        lines.append(" description monitoring")
        lines.append(" no shutdown")
    lines.append("end")
    return "\n".join(lines)

def enable_virtualization(params, selected_ports):
    lines = []
    lines.append("configure terminal")
    lines.append("virtualization on")
    lines.append("end")
    return "\n".join(lines)

def apply_qos(params, selected_ports):
    lines = []
    lines.append("configure terminal")
    for p in selected_ports:
        lines.append(f"interface {p}")
        lines.append(" qos trust cos")
    lines.append("end")
    return "\n".join(lines)

def enable_vlan(params, selected_ports):
    vid = params.get("VLAN ID", "").strip()
    vna = params.get("VLAN Name", "").strip()
    if not vid or not vna:
        raise TemplateError("Missing VLAN params")
    lines = []
    lines.append("configure terminal")
    lines.append(f"vlan {vid}")
    lines.append(f" name {vna}")
    lines.append("end")
    return "\n".join(lines)

def enable_routing(params, selected_ports):
    lines = []
    lines.append("configure terminal")
    lines.append("ip routing")
    lines.append("end")
    return "\n".join(lines)

def optimize_performance(params, selected_ports):
    lines = []
    lines.append("configure terminal")
    lines.append("system optimization high-performance")
    lines.append("end")
    return "\n".join(lines)

def default_interface(params, selected_ports):
    if not selected_ports:
        raise TemplateError("No interfaces selected for defaulting.")
    lines = []
    lines.append("configure terminal")
    for iface in selected_ports:
        lines.append(f"default interface {iface}")
    lines.append("end")
    return "\n".join(lines)

TEMPLATE_FUNCTIONS = {
    'apply_data_template': apply_data_template,
    'apply_static_routing': apply_static_routing,
    'apply_dynamic_routing': apply_dynamic_routing,
    'apply_nat': apply_nat,
    'apply_dhcp_server': apply_dhcp_server,
    'apply_config': apply_config,
    'restart_router': restart_router,
    'update_firmware': update_firmware,
    'backup_config': backup_config,
    'monitor_traffic': monitor_traffic,
    'enable_virtualization': enable_virtualization,
    'apply_qos': apply_qos,
    'enable_vlan': enable_vlan,
    'enable_routing': enable_routing,
    'optimize_performance': optimize_performance,
    'default_interface': default_interface
}
