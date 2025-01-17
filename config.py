# config.py

Cisco_Router = {
    'Cisco 1841': {'interfaces': ["Fa0/0", "Fa0/1"],
                       'description': "Popularny model do nauki konfiguracji sieci w Packet Tracerze.",
                       'method_list': ('restart_device', 'apply_static_routing', 'apply_dynamic_routing', 'apply_nat', 'apply_dhcp_server', 'default_interface')},
    'Cisco 1941': {'interfaces': ["Fa0/0", "Fa0/1", "Gi0/0", "Gi0/1"],
                       'description': "Nowszy model wspierający VLAN, ACL i technologie WAN.",
                       'method_list': ('apply_dhcp_server', 'default_interface')},
    'Cisco 2811': {'interfaces': ["Fa0/0", "Fa0/1"],
                       'description': "Uniwersalny router dla małych i średnich sieci.",
                       'method_list': ('apply_data_template', 'restart_device', 'apply_static_routing', 'apply_dynamic_routing', 'apply_nat', 'apply_dhcp_server', 'default_interface')},
    'Cisco 2911': {'interfaces': ["Fa0/0", "Fa0/1", "Gi0/0", "Gi0/1"],
                       'description': "Zaawansowany router z obsługą multimediów i QoS.",
                       'method_list': ('apply_data_template', 'restart_device', 'apply_static_routing', 'apply_dynamic_routing', 'apply_nat', 'apply_dhcp_server', 'set_trunk_vlan', 'default_interface')},
    'Cisco ISR 4321': {'interfaces': ["Gi0/0", "Gi0/1"],
                       'description': "Router nowej generacji wspierający wirtualizację.",
                       'method_list': ('apply_data_template', 'restart_device', 'apply_static_routing', 'apply_dynamic_routing', 'apply_nat', 'apply_dhcp_server', 'default_interface')}
}

Cisco_Switch = {
    'Cisco Catalyst 2960': {'interfaces': ["Fa1/0/1", "Fa1/0/2", "Fa1/0/3", "Fa1/0/4", "Fa1/0/5", "Fa1/0/6", "Fa1/0/7", "Fa1/0/8", "Fa1/0/9", "Fa1/0/10", "Fa1/0/11", "Fa1/0/12", "Fa1/0/13", "Fa1/0/14", "Fa1/0/15", "Fa1/0/16", "Fa1/0/17", "Fa1/0/18", "Fa1/0/19", "Fa1/0/20", "Fa1/0/21", "Fa1/0/22", "Fa1/0/23", "Fa1/0/24", "Gi1/0/1", "Gi1/0/2"],
                            'description': "Najpopularniejszy switch do nauki w Packet Tracerze.",
                            'method_list': ('set_access_vlan', 'apply_dhcp_server', 'set_trunk_vlan', 'set_native_vlan', 'default_interface')},
    'Cisco Catalyst 3560': {'interfaces': ["Fa0/1", "Fa0/2", "Fa0/3", "Fa0/4", "Fa0/5", "Fa0/6", "Fa0/7", "Fa0/8", "Fa0/9", "Fa0/10", "Fa0/11", "Fa0/12", "Fa0/13", "Fa0/14", "Fa0/15", "Fa0/16", "Fa0/17", "Fa0/18", "Fa0/19", "Fa0/20", "Fa0/21", "Fa0/22", "Fa0/23", "Fa0/24", "Gi0/1", "Gi0/2"],
                            'description': "Switch warstwy 3 wspierający routing między VLAN-ami.",
                            'method_list': ('set_access_vlan', 'apply_dhcp_server', 'set_trunk_vlan', 'set_native_vlan', 'apply_data_template', 'default_interface')},
    'Cisco 2960': {'interfaces': ["Fa0/1", "Fa0/2", "Fa0/3", "Fa0/4", "Fa0/5", "Fa0/6", "Fa0/7", "Fa0/8", "Fa0/9", "Fa0/10", "Fa0/11", "Fa0/12", "Fa0/13", "Fa0/14", "Fa0/15", "Fa0/16", "Fa0/17", "Fa0/18", "Fa0/19", "Fa0/20", "Fa0/21", "Fa0/22", "Fa0/23", "Fa0/24", "Gi0/1", "Gi0/2"],
                   'description': "Najpopularniejszy switch do nauki w Packet Tracerze.",
                   'method_list': ('restart_device', 'apply_dhcp_server', 'set_access_vlan', 'set_trunk_vlan', 'set_native_vlan', 'default_interface')},
    'Cisco Catalyst 3650': {'interfaces': ["Fa1/0/1", "Fa1/0/2", "Fa1/0/3", "Fa1/0/4", "Fa1/0/5", "Fa1/0/6", "Fa1/0/7", "Fa1/0/8", "Fa1/0/9", "Fa1/0/10", "Fa1/0/11", "Fa1/0/12", "Fa1/0/13", "Fa1/0/14", "Fa1/0/15", "Fa1/0/16", "Fa1/0/17", "Fa1/0/18", "Fa1/0/19", "Fa1/0/20", "Fa1/0/21", "Fa1/0/22", "Fa1/0/23", "Fa1/0/24", "Gi1/0/1", "Gi1/0/2", "Gi1/0/3", "Gi1/0/4"],
                            'description': "Zaawansowany switch warstwy 3 dla złożonych topologii.",
                            'method_list': ('set_access_vlan', 'set_trunk_vlan', 'set_native_vlan', 'apply_data_template' ,'apply_dhcp_server', 'default_interface')},
    'Cisco Catalyst 9200': {'interfaces': ["Gi1/0/1", "Gi1/0/2", "Gi1/0/3", "Gi1/0/4", "Gi1/0/5", "Gi1/0/6", "Gi1/0/7", "Gi1/0/8", "Gi1/0/9", "Gi1/0/10", "Gi1/0/11", "Gi1/0/12", "Gi1/0/13", "Gi1/0/14", "Gi1/0/15", "Gi1/0/16", "Gi1/0/17", "Gi1/0/18", "Gi1/0/19", "Gi1/0/20", "Gi1/0/21", "Gi1/0/22", "Gi1/0/23", "Gi1/0/24", "Gi1/0/25", "Gi1/0/26", "Gi1/0/27", "Gi1/0/28", "Gi1/0/29", "Gi1/0/30", "Gi1/0/31", "Gi1/0/32", "Gi1/0/33", "Gi1/0/34", "Gi1/0/35", "Gi1/0/36", "Gi1/0/37", "Gi1/0/38", "Gi1/0/39", "Gi1/0/40", "Gi1/0/41", "Gi1/0/42", "Gi1/0/43", "Gi1/0/44", "Gi1/0/45", "Gi1/0/46", "Gi1/0/47", "Gi1/0/48"],
                            'description': "Nowoczesny switch z wieloma funkcjami VLAN i zarządzania.",
                            'method_list': ('set_access_vlan', 'set_trunk_vlan', 'set_native_vlan', 'apply_dhcp_server', 'default_interface')}
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

