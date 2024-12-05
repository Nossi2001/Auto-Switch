# test_edge_router_vlan.py

from edge_router import EdgeRouter
from tmp_router import tmp_router

if __name__ == "__main__":
    # Dane routera
    ip = '192.168.55.50'        # Aktualny adres IP routera
    username = 'user'           # Nazwa użytkownika
    password = 'user'           # Hasło do routera

    # Tworzenie instancji EdgeRouter
    router = tmp_router(ip=ip, username=username, password=password)

    # Nawiązywanie połączenia z routerem
    if router.connect():
        print("Połączono z routerem.")
        # print(router.get_unique_mac_addresses())
        #router.apply_data_configuration_without_bridge(['eth0', 'eth1', 'eth2', 'eth3'])
        # router.apply_lan_dhcp(['eth0', 'eth1', 'eth2', 'eth3'])
        print(router.get_dhcp_server_info())

    else:
        print("Nie udało się połączyć z routerem.")
