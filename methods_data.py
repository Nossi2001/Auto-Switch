# methods_data.py

methods_inputs = {
    'apply_data_template': ["VLAN ID", "Profile Name", "Color", "VLAN Routing", "VLAN Mode", "VLAN IP Address", "Subnet Mask", "DHCP Server", "start", "stop"],
    'apply_static_routing': ["Destination Network", "Subnet Mask", "Next Hop IP"],
    'apply_dynamic_routing': ["Routing Protocol", "Process ID", "Area ID", "Networks"],
    'apply_nat': ["Interface Role", "Pool Name", "Pool Start IP", "Pool End IP", "Access List", "Netmask"],
    'apply_dhcp_server': ["Pool Name", "Network", "Subnet Mask", "Default Router", "DNS Server", "Lease Time"],
    'apply_config': [],
    'restart_router': [],
    'update_firmware': ["Firmware URL"],
    'backup_config': [],
    'monitor_traffic': ["Session ID", "Source", "Destination"],
    'enable_virtualization': [],
    'apply_qos': [],
    'enable_vlan': ["VLAN ID", "VLAN Name"],
    'enable_routing': [],
    'optimize_performance': [],
    'default_interface': [],
    'set_access_vlan': ["VLAN ID", "Description", "Color"],
    'set_trunk_vlan': ["Allowed VLANs", "Description"],
    'set_native_vlan': ["Native VLAN ID", "Allowed VLANs", "Description", "Color"],
    'copy_vlan_settings': ["VLAN ID"]
}

optional_params = {
    'apply_data_template': ["Color", "DHCP Server", "start", "stop"],
    'apply_static_routing': [],
    'apply_dynamic_routing': ["Area ID"],
    'apply_nat': [],
    'apply_dhcp_server': ["DNS Server", "Lease Time"],
    'apply_config': [],
    'restart_router': [],
    'update_firmware': [],
    'backup_config': [],
    'monitor_traffic': [],
    'enable_virtualization': [],
    'apply_qos': [],
    'enable_vlan': ["Description"],
    'enable_routing': [],
    'optimize_performance': [],
    'default_interface': [],
    'set_access_vlan': ["Description"],
    'set_trunk_vlan': ["Description"],
    'set_native_vlan': ["Allowed VLANs", "Description"],
    'copy_vlan_settings': []
}
