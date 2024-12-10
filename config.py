# config.py

Cisco_Router = {
    'Cisco 1841': {
        'interfaces': [
            "Fa0/0",
            "Fa0/1"
        ],
        'description': "Popularny model do nauki konfiguracji sieci w Packet Tracerze.",
        'method_list': (
            'apply_data_template',
            'restart_router',
            'apply_static_routing',
            'apply_dynamic_routing',
            'apply_nat',
            'apply_dhcp_server',
            'default_interface'
        )
    },
    'Cisco 1941': {
        'interfaces': [
            "Fa0/0",
            "Fa0/1",
            "Gi0/0",
            "Gi0/1"
        ],
        'description': "Nowszy model wspierający VLAN, ACL i technologie WAN.",
        'method_list': (
            'apply_config',
            'update_firmware',
            'apply_static_routing',
            'apply_dynamic_routing',
            'apply_nat',
            'apply_dhcp_server',
            'default_interface'
        )
    },
    'Cisco 2811': {
        'interfaces': [
            "Fa0/0",
            "Fa0/1"
        ],
        'description': "Uniwersalny router dla małych i średnich sieci.",
        'method_list': (
            'apply_config',
            'backup_config',
            'apply_static_routing',
            'apply_dynamic_routing',
            'default_interface'
        )
    },
    'Cisco 2911': {
        'interfaces': [
            "Fa0/0",
            "Fa0/1",
            "Gi0/0",
            "Gi0/1"
        ],
        'description': "Zaawansowany router z obsługą multimediów i QoS.",
        'method_list': (
            'apply_config',
            'monitor_traffic',
            'apply_static_routing',
            'apply_dynamic_routing',
            'apply_qos',
            'default_interface'
        )
    },
    'Cisco ISR 4321': {
        'interfaces': [
            "Gi0/0",
            "Gi0/1"
        ],
        'description': "Router nowej generacji wspierający wirtualizację.",
        'method_list': (
            'apply_config',
            'enable_virtualization',
            'apply_static_routing',
            'apply_dynamic_routing',
            'apply_nat',
            'default_interface'
        )
    }
}

Cisco_Switch = {
    'Cisco Catalyst 2960': {
        'interfaces': [
            "Fa1/0/1",
            "Fa1/0/2",
            "Fa1/0/3",
            "Fa1/0/4",
            "Fa1/0/5",
            "Fa1/0/6",
            "Fa1/0/7",
            "Fa1/0/8",
            "Fa1/0/9",
            "Fa1/0/10",
            "Fa1/0/11",
            "Fa1/0/12",
            "Fa1/0/13",
            "Fa1/0/14",
            "Fa1/0/15",
            "Fa1/0/16",
            "Fa1/0/17",
            "Fa1/0/18",
            "Fa1/0/19",
            "Fa1/0/20",
            "Fa1/0/21",
            "Fa1/0/22",
            "Fa1/0/23",
            "Fa1/0/24",
            "Gi1/0/1",
            "Gi1/0/2"
        ],
        'description': "Najpopularniejszy switch do nauki w Packet Tracerze.",
        'method_list': (
            'apply_config',
            'enable_vlan',
            'apply_dhcp_server',
            'default_interface'
        )
    },
    'Cisco Catalyst 3560': {
        'interfaces': [
            "Fa1/0/1",
            "Fa1/0/2",
            "Gi1/0/1",
            "Gi1/0/2",
            "Gi1/0/3",
            "Gi1/0/4"
        ],
        'description': "Switch warstwy 3 wspierający routing między VLAN-ami.",
        'method_list': (
            'apply_config',
            'enable_routing',
            'apply_static_routing',
            'apply_dynamic_routing',
            'default_interface'
        )
    },
    'Cisco 2950': {
        'interfaces': [
            "Fa1/0/1",
            "Fa1/0/2",
            "Fa1/0/3",
            "Fa1/0/4",
            "Fa1/0/5",
            "Fa1/0/6",
            "Fa1/0/7",
            "Fa1/0/8",
            "Fa1/0/9",
            "Fa1/0/10",
            "Fa1/0/11",
            "Fa1/0/12",
            "Fa1/0/13",
            "Fa1/0/14",
            "Fa1/0/15",
            "Fa1/0/16",
            "Fa1/0/17",
            "Fa1/0/18",
            "Fa1/0/19",
            "Fa1/0/20",
            "Fa1/0/21",
            "Fa1/0/22",
            "Fa1/0/23",
            "Fa1/0/24"
        ],
        'description': "Starszy model switcha, nadal używany w podstawowych sieciach.",
        'method_list': (
            'apply_config',
            'monitor_traffic',
            'default_interface'
        )
    },
    'Cisco Catalyst 3650': {
        'interfaces': [
            "Fa1/0/1",
            "Fa1/0/2",
            "Fa1/0/3",
            "Fa1/0/4",
            "Fa1/0/5",
            "Fa1/0/6",
            "Fa1/0/7",
            "Fa1/0/8",
            "Fa1/0/9",
            "Fa1/0/10",
            "Fa1/0/11",
            "Fa1/0/12",
            "Fa1/0/13",
            "Fa1/0/14",
            "Fa1/0/15",
            "Fa1/0/16",
            "Fa1/0/17",
            "Fa1/0/18",
            "Fa1/0/19",
            "Fa1/0/20",
            "Fa1/0/21",
            "Fa1/0/22",
            "Fa1/0/23",
            "Fa1/0/24",
            "Gi1/0/1",
            "Gi1/0/2",
            "Gi1/0/3",
            "Gi1/0/4"
        ],
        'description': "Zaawansowany switch warstwy 3 dla złożonych topologii.",
        'method_list': (
            'apply_config',
            'enable_qos',
            'apply_static_routing',
            'apply_dynamic_routing',
            'default_interface'
        )
    },
    'Cisco Catalyst 9200': {
        'interfaces': [
            "Gi1/0/1",
            "Gi1/0/2",
            # ... kontynuacja do Gi1/0/48 ...
            "Gi1/0/48"
        ],
        'description': "Nowoczesny switch z wieloma funkcjami VLAN i zarządzania.",
        'method_list': (
            'apply_config',
            'optimize_performance',
            'enable_vlan',
            'enable_qos',
            'default_interface'
        )
    }
}

description_color = {
    "Najpopularniejszy switch do nauki w Packet Tracerze.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'},
    "Switch warstwy 3 wspierający routing między VLAN-ami.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'},
    "Starszy model switcha, nadal używany w podstawowych sieciach.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'},
    "Zaawansowany switch warstwy 3 dla złożonych topologii.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'},
    "Nowoczesny switch z wieloma funkcjami VLAN i zarządzania.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'},
    "Popularny model do nauki konfiguracji sieci w Packet Tracerze.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'},
    "Nowszy model wspierający VLAN, ACL i technologie WAN.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'},
    "Uniwersalny router dla małych i średnich sieci.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'},
    "Zaawansowany router z obsługą multimediów i QoS.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'},
    "Router nowej generacji wspierający wirtualizację.": {'normal': '#5F5F5F', 'hover': '#6F6F6F', 'checked': '#505358'}
}

methods_inputs = {
    'apply_data_template': ["VLAN ID", "Profile Name", "Color", "VLAN Routing", "VLAN Setting", "VLAN IP Address", "Subnet Mask", "DHCP Server", "start", "stop"],
    'apply_static_routing': ["Destination Network", "Subnet Mask", "Next Hop IP"],
    'apply_dynamic_routing': ["Routing Protocol", "Process ID", "Area ID"],
    'apply_nat': ["Inside Interface", "Outside Interface", "Pool Name", "Pool Start IP", "Pool End IP", "Access List"],
    'apply_dhcp_server': ["Pool Name", "Network", "Subnet Mask", "Default Router", "DNS Server", "Lease Time"],
    'apply_config': [],
    'restart_router': [],
    'update_firmware': ["Firmware URL"],
    'backup_config': [],
    'monitor_traffic': [],
    'enable_virtualization': [],
    'apply_qos': [],
    'enable_vlan': ["VLAN ID", "VLAN Name"],
    'enable_routing': [],
    'optimize_performance': [],
    'default_interface': ["Interface"]
}

optional_params = {
    'apply_data_template': ["Color", "DHCP Server", "start", "stop"],
    'apply_static_routing': [],
    'apply_dynamic_routing': ["Area ID"],
    'apply_nat': [],
    'apply_dhcp_server': ["DNS Server"],
    'apply_config': [],
    'restart_router': [],
    'update_firmware': [],
    'backup_config': [],
    'monitor_traffic': [],
    'enable_virtualization': [],
    'apply_qos': [],
    'enable_vlan': [],
    'enable_routing': [],
    'optimize_performance': [],
    'default_interface': []
}
